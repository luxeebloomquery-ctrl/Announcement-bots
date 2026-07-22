# config.py
# ----------------------------------------------------------------------
# Multi-User Announcement Bot Configuration
# No admin authentication - everyone can use the bot!
# Each user gets their own private control panel.
# ----------------------------------------------------------------------

import os
from dotenv import load_dotenv

load_dotenv()

# Bot token from environment or direct assignment
BOT_TOKEN = os.getenv("BOT_TOKEN", "8671669994:AAH53wveuygHM-2R_uu1eWVzJ3c7IDB8VJc")

# No authentication needed - multi-user bot!
# Each user can add their own groups and send announcements
