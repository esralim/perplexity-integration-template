"""Notion Writer (Stub) - Utility untuk membuat entry di Notion database."""

import os
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def create_notion_entry(metadata: Dict, content: str) -> Optional[str]:
    notion_api_key = os.getenv("NOTION_API_KEY")
    
    if not notion_api_key:
        logger.warning("NOTION_API_KEY not set, skipping Notion write (stub mode)")
        return "https://notion.so/stub-notion-api-key-not-set"
    
    logger.info("Notion write skipped (stub mode)")
    return "https://notion.so/stub-implementasi-lengkap-di-comments"


if __name__ == "__main__":
    test_metadata = {"topic": "Test Topic", "venture": "healthcare-ai", "date": "2026-09-18"}
    result = create_notion_entry(test_metadata, "Test content")
    print(f"Notion entry created: {result}")
