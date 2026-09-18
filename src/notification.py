"""Notification (Stub) - Email & Slack notification"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def send_email_notification(metadata: dict, obsidian_path: Optional[str], notion_link: Optional[str]):
    if not os.getenv("SMTP_HOST"):
        logger.info("Email notification skipped")
        return
    logger.info("Email notification sent (stub)")


def send_slack_notification(metadata: dict, obsidian_path: Optional[str], notion_link: Optional[str]):
    if not os.getenv("SLACK_WEBHOOK_URL"):
        logger.info("Slack notification skipped")
        return
    logger.info("Slack notification sent (stub)")
