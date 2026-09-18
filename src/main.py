#!/usr/bin/env python3
"""
Perplexity Integration - Main Entry Point

CLI untuk menjalankan riset otomatis dari Perplexity API ke Obsidian, Notion, dan Google Drive.
"""

import os
import sys
import yaml
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import click

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from perplexity_client import PerplexityClient
from obsidian_writer import write_to_obsidian
from notion_writer import create_notion_entry
from drive_writer import upload_to_drive
from notification import send_email_notification, send_slack_notification

load_dotenv()

def setup_logging():
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE", "logs/research.log")
    Path("logs").mkdir(exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def load_config():
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_prompts():
    prompts_path = Path(__file__).parent.parent / "config" / "prompts.yaml"
    with open(prompts_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def format_for_obsidian(result: dict, metadata: dict) -> str:
    sources = "\n".join([f"{i+1}. {url}" for i, url in enumerate(result.get("citations", []))])
    return f"""# Perplexity API Research: {metadata['topic']}

## Metadata

- **Tanggal:** {metadata['date']}
- **Venture:** [[{metadata['venture']}]]
- **Project:** {metadata.get('project', 'N/A')}
- **Query:** {metadata['query']}
- **Model:** {metadata['model']}
- **Tokens:** {metadata['tokens']}
- **Sources:** {metadata['sources_count']}

## Output

{result['content']}

## Sumber

{sources}

## Insight dan Analisis

### Insight Utama

1. [Insight 1]
2. [Insight 2]

### Pattern yang Terlihat

- [Pattern 1]
- [Pattern 2]

### Rekomendasi Action

1. [Action 1]
2. [Action 2]

## Link Terkait

- [[{metadata['venture']}-Thesis]]

---

## Learning Loop

### Apakah riset ini ditindaklanjuti?

- [ ] Ya → [Link]
- [ ] Tidak → [Alasan]
"""

def run_research(topic: str, venture: str, project: str = None, prompt_type: str = None):
    logger.info(f"🚀 Starting research: topic='{topic}', venture='{venture}'")
    
    try:
        config = load_config()
        prompts = load_prompts()
        
        prompt_template = prompts.get(prompt_type or venture, prompts.get("default", ""))
        prompt = prompt_template.format(topic=topic, venture=venture)
        
        perplexity = PerplexityClient()
        logger.info("🔍 Querying Perplexity API...")
        result = perplexity.query(prompt)
        logger.info(f"✅ Response received ({result['tokens']} tokens)")
        
        metadata = {
            "topic": topic, "venture": venture, "project": project,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "query": prompt[:200], "tokens": result["tokens"],
            "model": result["model"], "sources_count": len(result.get("citations", [])),
            "status": "processed"
        }
        
        content = format_for_obsidian(result, metadata)
        
        obsidian_path = None
        if config["storage"]["save_to_obsidian"]:
            vault_path = os.getenv("OBSIDIAN_VAULT_PATH")
            if vault_path:
                obsidian_path = write_to_obsidian(content, metadata, vault_path)
                logger.info(f"✅ Written to Obsidian: {obsidian_path}")
        
        notion_link = None
        if config["storage"]["save_to_notion"]:
            notion_link = create_notion_entry(metadata, result["content"])
            logger.info(f"✅ Created Notion entry: {notion_link}")
        
        drive_link = None
        if config["storage"]["save_to_drive"]:
            drive_link = upload_to_drive(content, metadata)
            logger.info(f"✅ Uploaded to Drive: {drive_link}")
        
        logger.info("🎉 Research completed successfully!")
        
        return {"success": True, "obsidian": obsidian_path, "notion": notion_link, "drive": drive_link, "tokens": result["tokens"]}
    
    except Exception as e:
        logger.error(f"❌ Research failed: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}

@click.command()
@click.option("--topic", "-t", required=True, help="Topik riset")
@click.option("--venture", "-v", required=True, help="Venture terkait")
@click.option("--project", "-p", default=None, help="Project terkait (opsional)")
@click.option("--type", "-ty", default=None, help="Tipe prompt khusus")
@click.option("--dry-run", is_flag=True, help="Dry run mode")
def main(topic, venture, project, type, dry_run):
    if dry_run:
        print(f"\n🧪 DRY RUN\nTopic: {topic}\nVenture: {venture}\nProject: {project or 'N/A'}\n")
        return
    
    result = run_research(topic, venture, project, type)
    
    if result["success"]:
        print(f"\n✅ Research completed!\n   Tokens: {result['tokens']}\n   Obsidian: {result['obsidian']}\n   Notion: {result['notion']}\n   Drive: {result['drive']}")
        sys.exit(0)
    else:
        print(f"\n❌ Research failed: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
