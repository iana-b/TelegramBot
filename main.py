import telebot
import requests
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

bot = telebot.TeleBot(API_TOKEN)

WEATHER_URL = f'https://api.openweathermap.org/data/2.5/weather?appid={WEATHER_API_KEY}&units=metric&lang=ru'


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_weather = telebot.types.KeyboardButton('Узнать погоду 🌤')
    markup.row(item_weather)
    bot.reply_to(message, f'Привет, {message.from_user.first_name}! 💕', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Узнать погоду 🌤')
def select_city(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_weather_ykt = telebot.types.KeyboardButton('Якутск ❄️')
    item_weather_waw = telebot.types.KeyboardButton('Варшава 🌱')
    markup.row(item_weather_ykt)
    markup.row(item_weather_waw)
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


bot.infinity_polling()
