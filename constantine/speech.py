import random
import string
from functools import partial

SEE_NO_EVIL_MONKEY = '🙈'
OK_HAND_SIGN = '👌'

commands = u"""
/build_test - Обновление тестового ФК сервера
/build_demo - Обновление demo сервера
/build_demo2 - Обновление demo2 сервера
/build_demo3 - Обновление demo3 сервера
/build_demo4 - Обновление demo4 сервера
"""


def reply_speech(constantine, message):
    text = message.text.lower()
    reply = partial(constantine.bot.reply_to, message)
    send_sticker = partial(constantine.bot.send_sticker, message.chat.id,
                           reply_to_message_id=message.message_id)

    if 'константин' in text:
        if not any(('мсье' in text, 'месье' in text)):
            words = text.split(' ')
            for word in words:
                if u'константин' in word:
                    konstantin = word.strip().capitalize()
                    for char in string.punctuation:
                        konstantin = konstantin.replace(char, '')
                    reply(text=u'Мсье {}.'.format(konstantin))
                    break

        elif text == u'мсье константин':
            reply(text=OK_HAND_SIGN)

        elif u'денис' in text:
            reply(text=SEE_NO_EVIL_MONKEY)

        elif u'обнов' in text:
            if u'тест' in text:
                constantine.build_job(message, constantine.jobs_names['test'])
            elif u'демо' in text:
                reply(text=u'''Выбирай:
                /build_demo
                /build_demo2
                /build_demo3
                /build_demo4''')
            else:
                reply(text=commands)

        elif 'мсье константин' in text or 'месье константин' in text:
            if 'умни' in text or 'молод' in text:
                val = random.randint(0, 1)
                if val == 0:
                    send_sticker('BQADAgADQwADyIsGAAHUqBXNeq718gI')
                elif val == 1:
                    send_sticker('BQADAgAD9wEAAtJaiAHE9Y6Dr-OFCgI')

            elif 'спасибо' in text or 'благодар' in text:
                val = random.randint(0, 1)
                if val == 0:
                    send_sticker('BQADBAAD9gEAAk9mWQAB6IGF9lTvnfIC')
                elif val == 1:
                    send_sticker('BQADAgADugEAAtJaiAHZdepX3bZ-VgI')

            elif 'хороши' in text or 'краса' in text:
                send_sticker('BQADAgAD_gAD9HsZAAHbV7rs2RBy4wI')

            else:
                reply(text=u'Мин белмим дөресен.')
