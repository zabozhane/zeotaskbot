import telebot
import pypyodbc
from telebot import types
from telebot import apihelper
import datetime

now = datetime.datetime.now()

bot = telebot.TeleBot('')

apihelper.proxy = {'https': 'Socks5://198.27.75.152:1080'}

keyboard1 = telebot.types.ReplyKeyboardMarkup(True,True)
keyboard1.row('/create')
keyboard1.row('/completed','/not_completed')

keyboard3 = telebot.types.InlineKeyboardMarkup(True)
taskbutton = types.InlineKeyboardButton(text='Завершить',callback_data='completed')
keyboard3.add(taskbutton)

mySQLServer = "\SQLEXPRESS"
myDatabase = "db"

connect = pypyodbc.connect('Driver={SQL Server};'
                            'Server=' + mySQLServer + ';'
                            'Database=' + myDatabase + ';')

cursor = connect.cursor()

print('База подключена!')

@bot.message_handler(commands=['start'])
def start_message(message):
    if now.hour > 18 and now.hour<24:
        bot.send_message(message.chat.id, 'Добрый вечер. Здесь Вы можете добавить свою задачу и отслеживать её прогресс.', reply_markup=keyboard1)
    elif now.hour > 24 and now.hour < 6:
        bot.send_message(message.chat.id, 'Доброй ночи. Здесь Вы можете добавить свою задачу и отслеживать её прогресс.' , reply_markup=keyboard1)
    elif now.hour > 6 and now.hour < 10:
        bot.send_message(message.chat.id, 'Доброе утро. Здесь Вы можете добавить свою задачу и отслеживать её прогресс.',reply_markup=keyboard1)
    elif now.hour > 10 and now.hour <18:
        bot.send_message(message.chat.id, 'Добрый день. Здесь Вы можете добавить свою задачу и отслеживать её прогресс.',reply_markup=keyboard1)

@bot.message_handler(content_types=['text'])

def send_text(message):
    if message.text.lower() == '/create':
        bot.send_message(message.chat.id,'Введите описание задания:')
        bot.register_next_step_handler(message,create_task)

    elif message.text.lower() == '/not_completed':
            get_task(message)

    elif message.text.lower() == '/completed':
            get_complete(message)

    elif message.text.lower() == '/help':
        bot.send_message(message.chat.id,'Список команд : \n /completed \n /not_completed \n /create')
    else:
        bot.send_message(message.chat.id,'Я не понимаю вашей команды. \n Для получения набора команд введите /help')

@bot.callback_query_handler(func=lambda call:True)
def callback_inline(call):
    if call.data == "completed":
        bot.edit_message_text(chat_id=call.message.chat.id,message_id=call.message.message_id,text="Задание завершено")
        text = call.message.text
        i = "'" + text[0:36:1] + "'"
        chatid = str(call.message.chat.id)
        message = i + ' ' + chatid
        complete_task(message)


def create_task(message):
    description = "N'" + message.text + "'"
    print(description)
    userz = "N'" + str(message.from_user.id) + "'"
    tabl = '[dbo].[task]'
    polya = '(description,[user])'
    query = 'insert into ' + str(tabl) + ' ' + polya + '\n' + 'values(' + str(description) + ',' + str(userz) + ')'
    cursor.execute(query)
    cursor.commit()
    bot.send_message(message.chat.id,'Задание зарегистрированно!')


def get_task(message):
    userz = "N'" + str(message.from_user.id) + "'"
    tabl = '[dbo].[task]'
    query = 'select id,description,[user],[status],[date] from ' + str(tabl) + ' where [user]=' + str(userz) + ' and [status] = 0'
    cursor.execute(query)
    result = cursor.fetchall()
    if result == []:
        bot.send_message(message.chat.id,'У Вас нет незавершенных задач')
    else:
        bot.send_message(message.chat.id, 'Список незавершенных задач:')
        for i in result:
            id = i[0]
            description = i[1]
            status = str(i[3])
            taskdate = str(i[4])
            if status == 'False':
                status = 'Не завершена'
            else:
                status = 'Завершена'

            mes = id + '\n' + 'Задача : ' + description + '\n' + 'Статус : ' + str(status) + '\n' + 'Дата регистрации: ' + taskdate
            bot.send_message(message.chat.id, mes, reply_markup=keyboard3)

def complete_task(message):
    message =message[0:38:1]

    tabl = '[dbo].[task]'
    query = 'update ' + str(tabl) + ' set [status] = 1 where id = ' + message
    cursor.execute(query)
    cursor.commit()

def get_complete(message):
    userz = "N'" + str(message.from_user.id) + "'"
    tabl = '[dbo].[task]'
    query = 'select id,description,[user],[status],[date] from ' + str(tabl) + ' where [user]=' + str(userz) + ' and [status] = 1'
    cursor.execute(query)
    result = cursor.fetchall()
    if result == []:
        bot.send_message(message.chat.id,'У Вас нет завершенных задач')
    else:
        bot.send_message(message.chat.id, 'Список завершенных задач:')
        for i in result:
            description = i[1]
            status = str(i[3])
            taskdate = str(i[4])
            if status == 'False':
                status = 'Не завершена'
            else:
                status = 'Завершена'

            mes = 'Задача : ' + description + '\n' + 'Статус : ' + str(status) + '\n' + 'Дата регистрации: ' + taskdate
            bot.send_message(message.chat.id, mes)



if __name__ == "__main__":
    bot.polling(none_stop=True)
    connect.close()
    print('Database shutdown:C')