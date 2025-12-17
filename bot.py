"""
Main Bot Module.
Initializes and configures the Telegram bot using pyTelegramBotAPI.
"""

from telebot.async_telebot import AsyncTeleBot

from config import TELEGRAM_BOT_TOKEN
from utils.logging import logger


# Create bot instance without default parse_mode to avoid Markdown parsing errors
bot = AsyncTeleBot(TELEGRAM_BOT_TOKEN, parse_mode=None)

logger.info("Bot instance created")
