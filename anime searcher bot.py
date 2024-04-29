import requests
import telebot
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import timedelta
import json

TOKEN = '6534511997:AAH66ugDr5q2DpZGRRb8roKyAhmBM6aK3ok'
bot = telebot.TeleBot(TOKEN)
animeData = {}
page = 0
VideoMoment = False


@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = '''🌟 Welcome to our Anime Search Bot! 🌟

This bot is designed to help you find your favorite anime using images. With advanced  algorithms, we can quickly and accurately identify anime series from images you provide.

To get started, simply send us an image of the anime you're looking for. You can send images directly from your device or share them from the web.

Once we receive the image, we'll analyze it and provide you with detailed information about the anime, including its title, English name, episode number, airtime, and more!

Our bot is constantly learning and improving, so the more images you send, the better we can serve you. 

We're committed to providing you with the best possible experience, so if you have any questions or feedback, please don't hesitate to let us know.

Happy searching, and we hope you enjoy using our Anime Search Bot! 😊

Send an image of the anime you're looking for.

Receive detailed information about the anime.

Enjoy using our bot.

Provide feedback or questions to help us improve.

🤖 Anime Search Bot Features 🤖

Fast and accurate image analysis.

Detailed anime information.

Continuous learning and improvement.

User-friendly interface.

24/7 availability.

💡 Tips and Tricks 💡

Use high-quality images for best results.

Send images with clear views of the anime.

Try sending images from different angles or scenes.

Be patient while our bot analyzes the image.

Made with ❤  by me 💻

Feel free to reach out to us for any questions, feedback, or suggestions. We're always here to help! 😊

Thank you for choosing our Anime Search Bot! We look forward to helping you find your favorite anime. 😊'''
    bot.reply_to(message, welcome_text, parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    req = call.data.split('_')
    # Обработка кнопок - вперед и назад
    if 'pagination' in req[0]:
        # Расспарсим полученный JSON
        json_string = json.loads(req[0])
        count = json_string['CountPage']
        page = json_string['NumberPage']
        # Пересоздаем markup
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(text='Подробнее', url='https://anilist.co/anime/{}'.format(
            animeData['result'][page - 1]['anilist']['id'])))
        # markup для первой страницы
        if page == 1:
            markup.add(InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                       InlineKeyboardButton(text=f'Вперёд --->',
                                            callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                                page + 1) + ",\"CountPage\":" + str(count) + "}"))
        # markup для второй страницы
        elif page == count:
            markup.add(InlineKeyboardButton(text=f'<--- Назад',
                                            callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                                page - 1) + ",\"CountPage\":" + str(count) + "}"),
                       InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '))
        # markup для остальных страниц
        else:
            markup.add(InlineKeyboardButton(text=f'<--- Назад',
                                            callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                                page - 1) + ",\"CountPage\":" + str(count) + "}"),
                       InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                       InlineKeyboardButton(text=f'Вперёд --->',
                                            callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                                page + 1) + ",\"CountPage\":" + str(count) + "}"))

        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_video(  # Отправка результата
            call.message.chat.id,
            video=animeData['result'][page - 1]['video'],
            caption=f'''<u>Результаты поиска:</u>
🇯🇵Название: {animeData['result'][page - 1]['anilist']['title']['native']} 
🇺🇸Название: {animeData['result'][page - 1]['anilist']['title']['english'] if animeData['result'][page - 1]['anilist']['title']['english'] != None else 'нет'}
📺Серия: {animeData['result'][page - 1]['episode']}
🕒Фрагмент: <b>{timedelta(seconds=round(animeData['result'][page - 1]['from']))}</b> - <b>{timedelta(seconds=round(animeData['result'][page - 1]['to']))}</b> 
📊Сходство: {round(float(animeData['result'][page - 1]['similarity']) * 100, 2)}%
{'🔞' if animeData['result'][page - 1]['anilist']['isAdult'] else ''}
''',
            reply_markup=markup,
            parse_mode='HTML'
        )


@bot.message_handler(content_types=['photo'])
def Sarcher(message):
    try:
        photo_id = message.photo[len(message.photo) - 1].file_id
        file_info = bot.get_file(photo_id)
        print(file_info.file_path)
        print(f'http://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}')
        response = requests.get(
            f'https://api.trace.moe/search?anilistInfo&url=http://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}')
        global animeData
        animeData = response.json()

        count = 10
        page = 1
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(text='Подробнее', url='https://anilist.co/anime/{}'.format(
            animeData['result'][page - 1]['anilist']['id'])))
        markup.add(InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                   InlineKeyboardButton(text=f'Вперёд --->',
                                        callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                            page + 1) + ",\"CountPage\":" + str(count) + "}"))

        bot.send_video(  # Отправка результата с видео
            message.chat.id,
            video=animeData['result'][page - 1]['video'],
            caption=f'''<u>Результаты поиска:</u>
🇯🇵Название: {animeData['result'][page - 1]['anilist']['title']['native']} 
🇺🇸Название: {animeData['result'][page - 1]['anilist']['title']['english'] if animeData['result'][page - 1]['anilist']['title']['english'] != None else 'нет'}
📺Серия: {animeData['result'][page - 1]['episode']}
🕒Фрагмент: <b>{timedelta(seconds=round(animeData['result'][page - 1]['from']))}</b> - <b>{timedelta(seconds=round(animeData['result'][page - 1]['to']))}</b> 
📊Сходство: {round(float(animeData['result'][page - 1]['similarity']) * 100, 2)}%
{'🔞' if animeData['result'][page - 1]['anilist']['isAdult'] else ''}
''',
            reply_markup=markup,
            parse_mode='HTML'
        )
    except:
        bot.send_message(message.chat.id, 'Ошибка')


@bot.message_handler(content_types=['text'])
def text(message):
    bot.send_message(message.chat.id, 'Ошибка: Отправьте картинку для распознавания')


bot.polling()
