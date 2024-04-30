import json
from datetime import timedelta

import re

import requests

import telebot

import wikipedia

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = '7033029505:AAHqkMN1_j-GbQOTviKfx3-cYkdYOK0MJrw'
bot = telebot.TeleBot(TOKEN)
animeData = {}
page = 0
VideoMoment = False
# Устанавливаем русский язык в Wikipedia
wikipedia.set_lang("ru")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = '''🌟 Yo, what's good, fam?! 🌟

I'm your go-to bot, here to help you out with all sorts of things. I can help you find your favorite anime, explain the meaning of words, give you that extra motivation you need, and even rate your outfit. 💯

Today's April 30, 2024, and I'm here to make your life easier and more fun. Just hit me up with a message, and I'll get right on it.

📺 Anime Time: I'm all over anime, from classic series to the latest shows. Just send me an image or a description, and I'll give you the details – title, English name, episode number, airtime, and more. I'm always learning and improving, so the more you use me, the better I get.

📚 Word Up: Need to know the meaning of a word? I got you covered. Just ask me, and I'll give you the definition, synonyms, and even examples of how to use it.

💪 Motivation: Sometimes we all need a little boost. I'm here to help you stay focused and motivated, whether you're working on a project, hitting the gym, or just need a positive vibe.

💼 Outfit Game: Not sure about your outfit? Send me a pic, and I'll rate it for you. I'll give you an honest opinion, so you can step out in style.

So, what are you waiting for? Let's get this conversation started and make your day better. And remember, I'm here 24/7, so don't hesitate to reach out.

🤖 What can Vince do 🤖

🔍 Anime and word search

💪 Motivation and outfit rating

💻 Continuous learning and improvement

💬 User-friendly interface

🕒 24/7 availability

🔥 Tips and Tricks 🔥

📷 Use clear images for anime and outfit search

💭 Be specific with your requests

🤝 Feel free to give feedback or suggestions

💻 I'm always here to help! 😊

Thanks for choosing me as your Bro! I'm looking forward to assisting you with all your needs. Let's do this brother! 💪🔥'''
    bot.reply_to(message, welcome_text, parse_mode='HTML')


# Чистим текст статьи в Wikipedia и ограничиваем его тысячей символов
def getwiki(s):
    try:
        ny = wikipedia.page(s)
        # Получаем первую тысячу символов
        wikitext = ny.content[:1000]
        # Разделяем по точкам
        wikimas = wikitext.split('.')
        # Отбрасываем всЕ после последней точки
        wikimas = wikimas[:-1]
        # Создаем пустую переменную для текста
        wikitext2 = ''
        # Проходимся по строкам, где нет знаков «равно» (то есть все, кроме заголовков)
        for x in wikimas:
            if not('==' in x):
                    # Если в строке осталось больше трех символов, добавляем ее к нашей переменной и возвращаем утерянные при разделении строк точки на место
                if len((x.strip())) > 3:
                   wikitext2 = wikitext2+x+'.'
            else:
                break
        # Теперь при помощи регулярных выражений убираем разметку
        wikitext2 = re.sub('\([^()]*\)', '', wikitext2)
        wikitext2 = re.sub('\([^()]*\)', '', wikitext2)
        wikitext2 = re.sub('\{[^\{\}]*\}', '', wikitext2)
        # Возвращаем текстовую строку
        return wikitext2
    # Обрабатываем исключение, которое мог вернуть модуль wikipedia при запросе
    except Exception as e:
        return 'no info bout that '


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

    bot.send_message(message.chat.id, getwiki(message.text))

    bot.send_message(message.chat.id, 'Для поиска информации об аниме отправьте картинку, для поиска информации на википедии отправьте слово.'
                                      'Для порции мотивации')

# @bot.message_handler(commands=['motivate'])
# def motivate(message):
#     bot.send_video('https://www.youtube.com/watch?v=RJQisT_dndc')


bot.polling()
