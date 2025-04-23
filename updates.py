updates = [
"""**[v5]**
- Major refactor: migrated logic from `main.py` into a structured `TelegramBot` class
- Modularized code into separate components: `bot.py`, `utils.py`, `log_channel.py`
- Improved overall readability and maintainability
- Centralized configuration and lifecycle management
- Restructured for easier scaling (e.g. multi-bot support, future extensions)
- Updated negative keywords for better rug pull detection
""",

"""**[v3.2.2-alpha]**
- Fixed rate limit bug causing logging issues (FloodWait on forward)
- Corrected media detection logic in logger
- Streamlined log formatting: shortened chat titles and timestamps
""",

"""**[v3.2.1-alpha]**
- Fixed issue where deleted messages were not logged to the private channel
""",

"""**[v3.2-alpha]**
- Added logging functionality: all processed messages now logged to a private channel
""",

"""**[v3.1-alpha]**
- Resolved bug with sender username detection
- Introduced `Logger` bot for enhanced visibility
- Added address-building utility script
""",

"""**[v3.0-alpha]**
- Integrated external bot controller for real-time input and management
""",

"""**[v2.3]**
- Fixed group chat compatibility issues
- Improved detection logic for split Coin Addresses (CA)
""",

"""**[v2.2]**
- Added full support for private groups and private channels
- Introduced dynamic allowlist: only messages from approved users are processed
""",

"""**[v2.1]**
- Extended support for Solana Coin Addresses (CA) with 43-character format
- Enabled group chat monitoring (initial integration for `cryptoyeezus`)
""",

"""**[v2.0]**
- Enhanced rug pull detection logic
- Implemented split CA reconstruction
- Added KING keyword removal
- Validated Solana addresses using Base58 decoding
- Enforced strict CA length validation (43–44 characters)
- Added timestamped debug logging
- Ensured flagged (rug pull) CA are properly excluded and logged
""",

"""**[v1.2]**
- Implemented basic rug pull detection logic
- Added keyword filtering and removal functionality
""",

"""**[v1.0]**
- Initial release: basic Telegram channel monitoring
- Detected Coin Addresses (CA) from message content
- Forwarded valid CAs to Trojan bot channel
"""
]

def all_updates():
    """
    Returns all updates concatenated into one string, starting from the bottom-most update.
    Each update is separated by a single line gap.
    """
    return "\n".join(reversed(updates))