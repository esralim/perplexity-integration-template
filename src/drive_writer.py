"""Google Drive Writer (Stub)"""

import os
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def upload_to_drive(content: str, metadata: Dict) -> Optional[str]:
    if not os.getenv("GOOGLE_CREDENTIALS_FILE"):
        logger.warning("GOOGLE_CREDENTIALS_FILE not set, skipping Drive upload")
        return "https://drive.google.com/stub"
    logger.info("Drive upload skipped (stub mode)")
    return "https://drive.google.com/stub"
