# NFL Cosplay Discord Bot

A Discord bot designed for NFL x Character integration. This bot provides the ability to merge both NFL and character in a funny and interestign way.

## Features

- NFL Team & Character information lookup
- Customisable NFL x Character mapping
- Ability to generate story from each gameweek
- API Cache to meet under NFL API Daily Limit (100 API Calls per day)

## Setup

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/nfl-cosplay-discord-bot.git
   cd nfl-cosplay-discord-bot
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Configure your bot:**
   - Copy `.env.example` to `.env` and fill in your Discord bot token and other settings.

4. **Run the bot:**
   ```sh
   python bot.py
   ```

## Usage

Invite the bot to your Discord server and use commands such as:
- `!nfl gameweek [previous|current|next]` — Get info about particular NFL gameweek
- `!char team [char_name]` — Find which character is assigned to a NFL team
- `!story gameweek [previous|current|next]` - Generate storyline from each gameweek 
- `!help` — List all available commands

## Contributing

Pull requests are welcome! Please open an issue first to discuss major changes.

## License

This project is licensed under the MIT License.

---

**Made with ❤️ for NFL