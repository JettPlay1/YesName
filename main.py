# подключаем модуль для Телеграма
import telebot

# указываем токен для доступа к боту
bot = telebot.TeleBot('7046702771:AAF0xYLHNRy946VDICTNVqCE8c2U-lZuksg')

# приветственный текст
start_txt = 'Привет! Это журнал «Код». \n\nТеперь у бота появился бэкенд.'


# обрабатываем старт бота
@bot.message_handler(commands=['start'])
def start(message):
    # выводим приветственное сообщение
    bot.send_message(message.from_user.id, start_txt, parse_mode='Markdown')

# запускаем бота
if __name__ == '__main__':
    while True:
        # в бесконечном цикле постоянно опрашиваем бота — есть ли новые сообщения
        try:
            bot.polling(none_stop=True, interval=0)
        # если возникла ошибка — сообщаем про исключение и продолжаем работу
        except Exception as e: 
            print('❌❌❌❌❌ Сработало исключение! ❌❌❌❌❌')