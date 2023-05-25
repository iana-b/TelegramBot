import telebot
import requests
import os
import random
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
MOVIE_API_KEY = os.getenv('MOVIE_API_KEY')

bot = telebot.TeleBot(API_TOKEN)

WEATHER_URL = f'https://api.openweathermap.org/data/2.5/weather?appid={WEATHER_API_KEY}&units=metric&lang=ru'
MOVIE_URL = f'https://api.themoviedb.org'


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_weather = telebot.types.KeyboardButton('Узнать погоду 🌤')
    markup.row(item_weather)
    item_movie = telebot.types.KeyboardButton('Случайный фильм 📽')
    markup.row(item_movie)
    bot.reply_to(message, f'Привет, {message.from_user.first_name}! 💕', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Узнать погоду 🌤')
def select_city(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_weather_ykt = telebot.types.KeyboardButton('Якутск ❄️')
    item_weather_waw = telebot.types.KeyboardButton('Варшава 🌱')
    item_back = telebot.types.KeyboardButton('Назад 🔙')
    markup.row(item_weather_ykt)
    markup.row(item_weather_waw)
    markup.row(item_back)
    bot.reply_to(message, f'Выберите город', reply_markup=markup)


def get_weather_in(message, url, tz):
    r = requests.get(url=url)
    if r.status_code == 200:
        data = r.json()
        time = datetime.now(tz=ZoneInfo(tz)).strftime('%H:%M')
        bot.reply_to(message, f"{round(data['main']['temp'])}°C, {data['weather'][0]['description']}\n\n⏰ {time}")


@bot.message_handler(func=lambda message: message.text == 'Варшава 🌱')
@bot.message_handler(func=lambda message: message.text == 'Якутск ❄️')
def get_weather(message):
    if message.text == 'Варшава 🌱':
        get_weather_in(message, f'{WEATHER_URL}&lat={52.2298}&lon={21.0118}', 'Europe/Warsaw')
    elif message.text == 'Якутск ❄️':
        get_weather_in(message, f'{WEATHER_URL}&lat={62.0339}&lon={129.7331}', 'Asia/Yakutsk')


@bot.message_handler(func=lambda message: message.text == 'Назад 🔙')
def send_choose(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_weather = telebot.types.KeyboardButton('Узнать погоду 🌤')
    markup.row(item_weather)
    item_movie = telebot.types.KeyboardButton('Случайный фильм 📽')
    markup.row(item_movie)
    bot.reply_to(message, f'Выберите команду', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Случайный фильм 📽')
def get_movie(message):
    url = f'{MOVIE_URL}/3/movie/top_rated?language=ru-RU'
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {MOVIE_API_KEY}"
    }
    r = requests.get(url=url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        random_movie = random.randint(0, 19)
        movie = data['results'][random_movie]
        poster = f"https://image.tmdb.org/t/p/w780{movie['poster_path']}"
        photo = Image.open(requests.get(poster, stream=True).raw)
        caption = f"{movie['title']}, {movie['release_date'][:4]}\nРейтинг {movie['vote_average']}"
        bot.send_photo(message.chat.id, photo, caption)


bot.infinity_polling()
