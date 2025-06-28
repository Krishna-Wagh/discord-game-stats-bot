# Game Stats Discord Bot

A feature-rich Discord bot that provides player stats for popular games including Valorant, Fortnite, Chess.com, and BGMI. Built using Python, discord.py, and aiohttp for asynchronous performance.

## Features

- Valorant: Current rank, peak rank, level, K/D ratio, win percentage.
- Chess.com: Blitz, Rapid, Bullet, Daily ratings with W/L/D records.
- Fortnite: Matches played, kills, wins, win rate, K/D.
- BGMI: UID verification and device binding info.
- Dynamic region detection for Valorant.
- API integration using environment variables to keep keys secure.

## Setup Instructions

1. **Clone this repository:**

   ```
   git clone https://github.com/Krishna-Wagh/discord-game-stats-bot.git
   cd discord-game-stats-bot
   ```

2. **Install dependencies:**

   ```
   pip install -r requirements.txt
   ```

3. **Environment Variables Setup:**

   - A sample file is provided as `.env_sample`.
   - Copy it and rename to `.env`.

   ```
   copy .env_sample .env
   ```

   - Fill in your personal API keys and bot token in the `.env` file like this:

   ```
   DISCORD_TOKEN=your_discord_bot_token
   VALORANT_API_KEY=your_valorant_api_key
   BGMI_API_KEY=your_bgmi_api_key
   BGMI_DEV_UID=your_bgmi_dev_uid
   FORTNITE_API_KEY=your_fortnite_api_key
   ```

   Make sure to **never share your `.env` file** or upload it publicly.

4. **Run the bot:**

   ```
   python Stat_Checker.py
   ```

## Commands

- `!valorant username#tag` — Get Valorant stats (auto-detects region).
- `!chess username` — Get Chess.com stats.
- `!fortnite username` — Get Fortnite BR stats.
- `!bgmi uid` — Verifies BGMI UID and device binding.

## Folder Structure

```
your-bot-folder/
│
├── .env_sample         # Template for API keys and tokens
├── .env                # (Not shared) Your actual API keys
├── Stat_Checker.py     # Main Discord bot code
├── README.md           # This help file
├── requirements.txt    # Required packages
```

## Notes

- Ensure your `.env` file is present in the same directory as your Python script.
- Some APIs may have rate limits or downtime (especially BGMI).
- The bot must be invited to your server with correct message/content permissions.
- The BGMI API is provided by a third party and can be unstable or limited.

## License

MIT License  
© 2025 Krishna Wagh
