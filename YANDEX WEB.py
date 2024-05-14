import json
from datetime import timedelta

import random

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

@bot.message_handler(commands=['motivate'])
def motivate(message):
    motivation = ['https://www.youtube.com/watch?v=QpgVyAUihlo', 'https://www.youtube.com/watch?v=jHnX-nMl59U', 'https://www.youtube.com/watch?v=rPVlKOc0-rs', 'https://www.youtube.com/watch?v=wnHW6o8WMas']
    bot.send_message(message.chat.id, random.choice(motivation))


@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = ''' Привет🌟



Я твой бро, который всегда готов помочь с любыми делами. Я могу помочь найти аниме, объяснить значение слов, поднять настроение. 💯


Сегодня суббота, 11 мая 2024 года, и я здесь, чтобы сделать твою жизнь легче и более интересной. Просто отправьте мне сообщение, и я займусь этим.


📺 Аниме: Я знаю все об аниме, от классических сериалов до последних шоу. Просто отправьте мне изображение, и я дам подробности - название, английское название, номер эпизода, время эфира и многое другое. Я постоянно учусь и улучшаюсь, поэтому чем больше вы используете меня, тем лучше я становлюсь.


📚 Словарь: Нужно знать значение слова? Я готов помочь. Просто спросите меня, и я дам вам определение.


💪 Мотивация: Иногда мы все нуждаемся в небольшом импульсе. Я здесь, чтобы помочь вам оставаться сфокусированными и мотивированными, будь то работа над проектом, тренировка в спортзале или просто нужны положительные эмоции.


Так что вы ждете? Давайте начнем этот разговор и сделаем ваш день лучше. И помните, я здесь 24/7, так что не стесняйтесь обращаться.


🤖 Что я могу 🤖


🔍 Поиск аниме и слов


💪 Мотивация


💻 Непрерывное обучение и улучшение


💬 Пользовательский интерфейс


🕒 Доступность 24/7

🔥 Советы и фишки 🔥


📷 Используйте четкие изображения для поиска аниме


💭 Будьте конкретными в своих запросах


🤝 Не стесняйтесь оставлять отзывы или предложения


💻 Я всегда здесь, чтобы помочь! 😊


Спасибо за выбор меня в качестве вашего друга! Я с нетерпением жду, чтобы помочь вам со всеми вашими потребностями💪🔥'''

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
def Searcher(message):
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
                                      )



bot.polling()
