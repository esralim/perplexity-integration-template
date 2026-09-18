"""Obsidian Writer - Utility untuk menulis file Markdown ke Obsidian vault dengan frontmatter."""

import yaml
from pathlib import Path
from typing import Dict


def write_to_obsidian(content: str, metadata: Dict, vault_path: str) -> str:
    filename = f"Perplexity-{metadata['topic'].replace(' ', '-').replace('/', '-')}-{metadata['date']}.md"
    research_folder = Path(vault_path) / "04-Research-Notes"
    research_folder.mkdir(parents=True, exist_ok=True)
    filepath = research_folder / filename
    
    frontmatter = {
        "type": "perplexity-api-research",
        "topic": metadata["topic"],
        "venture": metadata["venture"],
        "date": metadata["date"],
        "status": "processed",
        "tags": ["research", "perplexity"],
        "sources_count": metadata.get("sources_count", 0),
        "tokens": metadata.get("tokens", 0)
    }
    
    frontmatter_yaml = yaml.dump(frontmatter, sort_keys=False)
    full_content = f"---\n{frontmatter_yaml}---\n\n{content}"
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(full_content)
    
    return str(filepath)
