# !python3
# !/usr/bin/python3
# -*- coding: utf-8 -*-

import time

import telebot
from pykeepass import PyKeePass
from telebot import types
from telebot.types import InlineKeyboardButton

import config

bot = telebot.TeleBot(config.token, parse_mode="MARKDOWN")
DENIED_NAMES = ('Recycle Bin')
MENU_ITEMS = ['Получить файл', 'Показать группы', 'Обновить запись', 'Добавить запись']
STOP_WORDS = ['Выйти', 'Отмена', 'Выход', 'выйти', 'отмена', 'выход']
ALLOWED_ID = [722227]
db_file = 'vault13.kdbx'
kp = PyKeePass(db_file, password=config.pass_to_db)


class Responser():
    delimiter = ' '

    def __init__(self, config, default):
        self.config = config
        self.default = default
        self.cache = {}
        self._load_config(config)

    def _load_config(self, config):
        # CACHE tuple with all the words
        for section, data in self.config.items():
            for w in data.get('markers', []):
                if w not in self.cache:
                    self.cache[w] = section

    def get_message(self, input):
        # IN Cache?
        index = self.default
        for word in input.split(self.delimiter):
            if self.cache.get(word):
                index = self.cache[word]
                break
        return self.config[index]['message']


def pure_groups():
    groups = []
    for item in kp.groups:
        if item.name not in DENIED_NAMES:
            groups.append(item.name)
    groups_output = '\n'.join(groups)
    return groups_output, groups


def pure_entries(target_group):
    entries = []
    group = kp.find_groups(name=target_group, first=True)
    for item in group.entries:
        entries.append(item.title)
    entries_output = '\n'.join(entries)
    return entries_output, entries


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id in ALLOWED_ID:
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}')
        make_keyboard(message)
    else:
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}. '
                                          f'Похоже тебя еще не зачислили в Хогвартс. Приходи попозже')
        return


def make_keyboard(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for each in MENU_ITEMS:
        markup.add(each)
    bot.send_message(message.chat.id,
                     f'Воспользуйся для работы встроенной клавиатурой',
                     reply_markup=markup)


def make_inline_keyboard(message):
    (str_groups, list_groups) = pure_groups()
    markup = types.InlineKeyboardMarkup()
    for each in list_groups:
        markup.add(InlineKeyboardButton(text=each, callback_data=each))
    bot.send_message(message.chat.id, f'Выберите одну из следующих групп:', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    (str_groups, list_groups) = pure_groups()
    str_entries = ''
    for index in list_groups:
        if call.data == index:
            (str_entries, list_entries) = pure_entries(index)
    bot.send_message(call.message.chat.id, f'В группе содержатся следующие записи:\n{str_entries}')
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)


@bot.message_handler(func=lambda message: message.text == "Получить файл")
def get_file(message):
    if message.chat.id in ALLOWED_ID:
        bot.send_document(message.chat.id, open(db_file, 'rb'))
    else:
        return


@bot.message_handler(func=lambda message: message.text == "Показать группы")
def show_groups(message):
    if message.chat.id in ALLOWED_ID:
        make_inline_keyboard(message)
    else:
        return


@bot.message_handler(func=lambda message: message.text == "Обновить запись")
def update_entries(message):
    if message.chat.id in ALLOWED_ID:
        msg = bot.send_message(message.chat.id, f'Введи данные в формате: "Название записи, новый пароль"')
        bot.register_next_step_handler(msg, update_entry)
    else:
        return


def update_entry(message):
    s = message.text
    if s in STOP_WORDS:
        bot.send_message(message.chat.id, f'Ок, отмена режима обновления')
        return
    else:
        source = [x.strip() for x in s.split(',')]
        if len(source) != 2:
            bot.send_message(message.chat.id, f'Введенные данные не соответствуют необходимым условиям!')
            update_entries(message)
            return
        else:
            if (kp.find_entries(title=source[0], first=True)):
                entry = kp.find_entries(title=source[0], first=True)
                entry.password = source[1]
                kp.save()
                current_time = time.strftime("%H:%M:%S %d.%m.%Y", time.localtime())
                for each_id in ALLOWED_ID:
                    bot.send_message(each_id, f'Запись *{source[0]}* обновлена в *{current_time}* '
                                              f'пользователем *{message.from_user.first_name}* '
                                              f'\nНе забудь скачать обновленный *{db_file}*')
            else:
                bot.send_message(message.chat.id, f'Не нашел такой записи. Внимательнее посмотри на название записи')
                return
            

@bot.message_handler(func=lambda message: message.text == "Добавить запись")
def new_entries(message):
    if message.chat.id in ALLOWED_ID:
        msg = bot.send_message(message.chat.id, f'Введи данные в формате: "Имя группы, название записи,'
                                                f' учетная запись, пароль"')
        bot.register_next_step_handler(msg, add_new_entry)
    else:
        return


def add_new_entry(message):
    s = message.text
    if s in STOP_WORDS:
        bot.send_message(message.chat.id, f'Ок, отмена режима добавления')
        return
    else:
        source = [x.strip() for x in s.split(',')]
        if len(source) != 4:
            bot.send_message(message.chat.id, f'Введенные данные не соответствуют необходимым условиям!')
            new_entries(message)
            return
        else:
            group = kp.find_groups(name=source[0], first=True)
            kp.add_entry(group, source[1], source[2], source[3])
            kp.save()
            current_time = time.strftime("%H:%M:%S %d.%m.%Y", time.localtime())
            for each_id in ALLOWED_ID:
                bot.send_message(each_id, f'Запись *{source[1]}* добавлена в *{current_time}* '
                                          f'пользователем *{message.from_user.first_name}* '
                                          f'\nНе забудь скачать обновленный *{db_file}*')
  

# default handler for every other text
@bot.message_handler(func=lambda message: True, content_types=['text'])
def command_default(m):
    # this is the standard reply to a normal message
    i = m.text.lower()
    r = Responser(config.RESPONSES, config.DEFAULT)
    bot.send_message(m.chat.id, r.get_message(i))


bot.polling(none_stop=True)
