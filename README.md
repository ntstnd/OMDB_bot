````markdown
# 🎬 Movie Search Telegram Bot

A Telegram bot that allows users to search for movies using the OMDb API, view detailed information, and analyze their movie preferences with visual statistics.

The bot supports interactive inline buttons, stores user search history, and generates charts based on IMDb ratings, genres, and release years.

---

## ✨ Features

- 🔍 Search movies by title
- 🎬 View detailed movie information (IMDb rating, plot, cast, etc.)
- 🖼️ Display movie posters
- 📊 Generate visual statistics:
  - IMDb rating distribution
  - Genre distribution
  - Movies by release year
- 🧠 Personal statistics for each user
- 🧹 Clear search history
- ⚡ Asynchronous Telegram bot (python-telegram-bot v20+)

---

## 🛠️ Tech Stack

- Python 3.10+
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- OMDb API
- Requests
- Matplotlib
- python-dotenv

---

## 📦 Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/ntstnd/OMDB_bot.git
cd OMDB_bot
````

### 2️⃣ Create and activate a virtual environment

```bash
python -m venv venv
```

**Windows**

```bash
venv\Scripts\activate
```

**macOS / Linux**

```bash
source venv/bin/activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OMDB_API_KEY=your_omdb_api_key
```

* Telegram Bot Token: [https://t.me/BotFather](https://t.me/BotFather)
* OMDb API Key: [https://www.omdbapi.com/apikey.aspx](https://www.omdbapi.com/apikey.aspx)

---

## ▶️ Running the Bot

```bash
python main.py
```

You should see:

```text
Bot is running...
```

---

## 🤖 Bot Commands

| Command                | Description                            |
| ---------------------- | -------------------------------------- |
| `/start`               | Start the bot and show welcome message |
| `/search <movie name>` | Search for a movie                     |
| `/stats`               | Show statistics and charts             |
| `/clear`               | Clear search history                   |
| `/help`                | Show help message                      |

You can also send a movie name directly without using `/search`.

---

## 📊 Visualizations

The bot generates charts using **matplotlib**:

* Histogram of IMDb ratings
* Pie chart of genres
* Bar chart of release years

Charts are generated in memory and sent directly to the user as images.

---

## 🧠 Project Structure

```text
.
├── main.py
├── requirements.txt
├── README.md
├── .env
└── logs/
```

---

## ⚠️ Notes

* User search history is stored in memory (dictionary).
* Data is lost when the bot restarts.
* The project is intended for educational and demonstration purposes.

---

## 🚀 Possible Improvements

* Store user data in a database
* Use async HTTP client (`aiohttp`)
* Add movie recommendations
* Deploy the bot to a server (Docker, VPS)

---

## 📄 License

This project is licensed for educational use.

---

## 👩‍💻 Author

Created as a learning project to practice:

* API integration
* Asynchronous programming
* Telegram bot development
* Data visualization

```


