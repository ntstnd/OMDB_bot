import os
import requests
import io
import matplotlib
matplotlib.use('Agg') # no GUI window
import matplotlib.pyplot as plt
from collections import Counter # easier stats
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# token handling
from dotenv import load_dotenv
load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OMDB_BASE_URL = "http://www.omdbapi.com/"

user_searches = {}


def search_movie(title):
    """Search for a movie by title"""
    params = {
        "apikey": OMDB_API_KEY,
        "s": title,
        "type": "movie"
    }
    response = requests.get(OMDB_BASE_URL, params=params)
    data = response.json()
    return data.get("Search", [])[:10] if data.get("Response") == "True" else [] # handling empty results


def get_movie_details(imdb_id):
    """Get detailed information about a specific movie"""
    params = {
        "apikey": OMDB_API_KEY,
        "i": imdb_id,
        "plot": "full"
    }
    response = requests.get(OMDB_BASE_URL, params=params)
    return response.json()


def format_movie_info(movie):
    """Format movie information for display"""
    if movie.get("Response") == "False":
        return "Movie not found."
    
    title = movie.get("Title", "N/A")
    year = movie.get("Year", "N/A")
    rated = movie.get("Rated", "N/A")
    runtime = movie.get("Runtime", "N/A")
    genre = movie.get("Genre", "N/A")
    director = movie.get("Director", "N/A")
    actors = movie.get("Actors", "N/A")
    plot = movie.get("Plot", "N/A")
    imdb_rating = movie.get("imdbRating", "N/A")
    metascore = movie.get("Metascore", "N/A")
    
    info = f"🎬 *{title}* ({year})\n\n"
    info += f"⭐ IMDb: {imdb_rating}/10\n"
    info += f"📊 Metascore: {metascore}/100\n"
    info += f"🎭 Genre: {genre}\n"
    info += f"⏱️ Runtime: {runtime}\n"
    info += f"🎫 Rated: {rated}\n"
    info += f"🎥 Director: {director}\n"
    info += f"👥 Cast: {actors}\n\n"
    info += f"📖 *Plot:*\n{plot}"
    
    return info


def create_rating_chart(user_id):
    """Create a chart showing rating distribution of movies searched by user"""
    if user_id not in user_searches:
        return None
    
    ratings = [float(m['imdbRating']) for m in user_searches[user_id] 
               if m.get('imdbRating') and m['imdbRating'] != 'N/A']
    
    if not ratings:
        return None
    
    plt.figure(figsize=(10, 6))
    plt.hist(ratings, bins=10, color='#3498db', edgecolor='black', alpha=0.7)
    plt.xlabel('IMDb Rating', fontsize=12)
    plt.ylabel('Number of Movies', fontsize=12)
    plt.title('Rating Distribution of Your Searched Movies', fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    
    # store the pic in RAM
    buf = io.BytesIO() 
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return buf


def create_genre_chart(user_id):
    """Create a pie chart showing genre distribution"""
    if user_id not in user_searches:
        return None
    
    all_genres = []
    for movie in user_searches[user_id]:
        if movie.get('Genre') and movie['Genre'] != 'N/A':
            genres = [g.strip() for g in movie['Genre'].split(',')]
            all_genres.extend(genres)
    
    if not all_genres:
        return None
    
    genre_counts = Counter(all_genres)
    top_genres = dict(genre_counts.most_common(8))
    
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', 
              '#1abc9c', '#34495e', '#e67e22']
    
    plt.figure(figsize=(10, 8))
    plt.pie(top_genres.values(), labels=top_genres.keys(), autopct='%1.1f%%',
            colors=colors, startangle=90)
    plt.title('Genre Distribution of Your Searched Movies', fontsize=14, fontweight='bold')
    
    buf = io.BytesIO() 
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return buf


def create_year_chart(user_id):
    """Create a bar chart showing movies by release year"""
    if user_id not in user_searches:
        return None
    
    years = []
    for movie in user_searches[user_id]:
        year = movie.get('Year', '')
        years.append(year)
    
    if not years:
        return None
    
    year_counts = Counter(years)
    sorted_years = sorted(year_counts.items())
    
    plt.figure(figsize=(12, 6))
    plt.bar([str(y) for y, _ in sorted_years], [c for _, c in sorted_years],
            color='#9b59b6', edgecolor='black', alpha=0.7)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Number of Movies', fontsize=12)
    plt.title('Movies Searched by Release Year', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45)
    plt.grid(axis='y', alpha=0.3)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return buf


# Bot command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_message = (
        "🎬 *Welcome to Movie Bot!*\n\n"
        "I can help you discover movies and analyze your preferences.\n\n"
        "*Commands:*\n"
        "/search <movie name> - Search for a movie\n"
        "/stats - See visualizations of your searches\n"
        "/clear - Clear your search history\n"
        "/help - Show this message\n\n"
        "Or just send me a movie name to search!"
    )
    await update.message.reply_text(welcome_message, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await start(update, context)


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search for movies"""
    if not context.args:
        await update.message.reply_text("Please provide a movie name. Example: /search Inception")
        return
    
    query = " ".join(context.args)
    await update.message.reply_text(f"🔍 Searching for '{query}'...")
    
    movies = search_movie(query)
    
    if not movies:
        await update.message.reply_text(f"No movies found for '{query}'. Try a different search!")
        return
    
    keyboard = []
    for movie in movies:
        title = movie.get("Title", "Unknown")
        year = movie.get("Year", "")
        button_text = f"{title} ({year})" if year else title
        callback_data = f"movie_{movie['imdbID']}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"🎬 *Search Results for '{query}':*\n\nTap a movie to see details:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show visualization statistics"""
    message = update.message or update.callback_query.message
    user_id = update.effective_user.id

    if user_id not in user_searches or not user_searches[user_id]:
        await message.reply_text(
            "You haven't searched for any movies yet! 🎬\n"
            "Search for some movies first, then use /stats to see cool visualizations."
        )
        return

    await message.reply_text("📊 Generating your movie statistics...")

    rating_chart = create_rating_chart(user_id)
    if rating_chart:
        await message.reply_photo(
            photo=rating_chart,
            caption="⭐ Rating Distribution of Movies You've Searched"
        )

    genre_chart = create_genre_chart(user_id)
    if genre_chart:
        await message.reply_photo(
            photo=genre_chart,
            caption="🎭 Your Genre Preferences"
        )

    year_chart = create_year_chart(user_id)
    if year_chart:
        await message.reply_photo(
            photo=year_chart,
            caption="📅 Movies by Release Year"
        )

    total_movies = len(user_searches[user_id])
    ratings = [
        float(m['imdbRating']) for m in user_searches[user_id]
        if m.get('imdbRating') and m['imdbRating'] != 'N/A'
    ]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0

    await message.reply_text(
        f"📊 *Your Movie Stats:*\n\n"
        f"Total movies searched: {total_movies}\n"
        f"Average IMDb rating: {avg_rating:.1f}/10",
        parse_mode="Markdown"
    )



async def clear_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear user's search history"""
    user_id = update.effective_user.id
    user_searches[user_id] = []
    await update.message.reply_text("✅ Your search history has been cleared!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages as movie searches"""
    query = update.message.text
    context.args = query.split()
    await search(update, context)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    if callback_data.startswith("movie_"):
        imdb_id = callback_data.split("_")[1]
        movie = get_movie_details(imdb_id)
        
        # add to search history
        user_id = update.effective_user.id
        if user_id not in user_searches:
            user_searches[user_id] = []
        user_searches[user_id].append(movie)
        
        movie_info = format_movie_info(movie)
        
        # buttons
        keyboard = [
            [InlineKeyboardButton("📊 View My Stats", callback_data="stats")],
            [InlineKeyboardButton("🔗 View on IMDb", 
                                url=f"https://www.imdb.com/title/{imdb_id}/")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # send poster if available
        poster_url = movie.get("Poster")
        if poster_url and poster_url != "N/A":
            await query.message.reply_photo(
                photo=poster_url,
                caption=f"🎬 *{movie.get('Title', 'Movie')}*",
                parse_mode="Markdown"
            )

           # then send text separately
            await query.message.reply_text(
                movie_info,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )

        else:
            await query.message.reply_text(
                movie_info,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    
    elif callback_data == "stats":
        # stats command
        await stats(update, context)


def main():
    """Start the bot"""
    if not OMDB_API_KEY or not TELEGRAM_BOT_TOKEN:
        print("Error: Please set OMDB_API_KEY and TELEGRAM_BOT_TOKEN environment variables")
        return
    
    # create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("clear", clear_history))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # start the bot
    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()