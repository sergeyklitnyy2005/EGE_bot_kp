import telebot
from telebot import types
import sqlite3 as sl
from random import choice
import matplotlib.pyplot as plt
import smtplib

plt.use('Agg')


class UserInteraction:
    def __init__(self, bot_method, ege_bot):
        self.bot = bot_method
        self.ege_bot = ege_bot

    def handle_text_message(self, message):
        username = message.from_user.username
        if message.text == 'Пройти тест по заданию':
            self.ege_bot.menu_test_input(message)
            self.ege_bot.user_state[message.chat.id] = 'AWAITING_TEST_SELECTION'

        elif self.ege_bot.user_state.get(message.chat.id) == 'AWAITING_TEST_SELECTION':
            if message.text in [str(i) for i in range(1, 27)]:
                self.ege_bot.test_len = 1
                self.ege_bot.increment_errors_in_tasks[username] = 0
                self.ege_bot.increment_correct_tasks[username] = 0
                self.ege_bot.task[username] = int(message.text)
                self.ege_bot.start_test(message)
            elif message.text == 'меню':
                self.ege_bot.main_menu(message)
                self.ege_bot.user_state[message.chat.id] = 'NONE'

        elif message.text == 'add':
            self.bot.send_message(message.chat.id, "Пожалуйста, введите номер задания ключ админа.")
            self.ege_bot.user_state[message.chat.id] = 'ADMIN_KEY1'

        elif self.ege_bot.user_state.get(message.chat.id) == 'ADMIN_KEY1':
            self.ege_bot.task[username] = int(message.text)
            self.ege_bot.user_state[message.chat.id] = 'ADMIN_KEY'

        elif self.ege_bot.user_state.get(message.chat.id) == 'IN_TEST':
            if message.text == 'меню':
                self.bot.send_message(message.chat.id, "Тест закончен")
                if 0 != (self.ege_bot.increment_correct_tasks[username] +
                         self.ege_bot.increment_errors_in_tasks[username]):
                    self.ege_bot.add_or_update_user_task(message)
                    self.ege_bot.static_eque_diagram(message, self.ege_bot.increment_correct_tasks[username],
                                                     self.ege_bot.increment_errors_in_tasks[username])
                self.ege_bot.main_menu(message)
                self.ege_bot.user_state[message.chat.id] = 'NONE'
            elif message.text.lower().replace('.', '', 1) in str(self.ege_bot.user_tasks[username]['answer']).split(
                    '/') and self.ege_bot.test_len != 100:
                self.bot.send_message(message.chat.id, "Ваш ответ правильный!")
                self.ege_bot.increment_correct_tasks[username] += 1
            elif self.ege_bot.test_len != 100:
                self.bot.send_message(message.chat.id, "Ваш ответ неправильный. Правильный ответ: " +
                                      str(self.ege_bot.user_tasks[username]['answer']))
                self.ege_bot.increment_errors_in_tasks[username] += 1
            if self.ege_bot.test_len < 5 and self.ege_bot.user_state[message.chat.id] != 'NONE':
                self.ege_bot.test_len += 1
                self.ege_bot.start_test(message)
            elif self.ege_bot.user_state[message.chat.id] != 'NONE':
                self.bot.send_message(message.chat.id, "Тест закончен")
                self.ege_bot.add_or_update_user_task(message)
                self.ege_bot.static_eque_diagram(message, self.ege_bot.increment_correct_tasks[username],
                                                 self.ege_bot.increment_errors_in_tasks[username])
                self.ege_bot.main_menu(message)
                self.ege_bot.user_state[message.chat.id] = 'NONE'

        elif self.ege_bot.user_state.get(message.chat.id) == "ADMIN_KEY":
            if message.text == self.ege_bot.admin_key:
                self.bot.send_message(message.chat.id, "Пожалуйста, введите задание.")
                self.ege_bot.user_state[message.chat.id] = 'AWAITING_EXERCISE'
            else:
                self.bot.send_message(message.chat.id, "Отказ в доступе. Неправильный ключ.")
                self.ege_bot.main_menu(message)
                self.ege_bot.user_state[message.chat.id] = 'NONE'

        elif self.ege_bot.user_state.get(message.chat.id) == 'AWAITING_EXERCISE':
            self.ege_bot.exercise = message.text
            self.bot.send_message(message.chat.id, "Пожалуйста, введите вопрос.")
            self.ege_bot.user_state[message.chat.id] = 'AWAITING_QUESTION'

        elif self.ege_bot.user_state.get(message.chat.id) == 'AWAITING_QUESTION':
            self.ege_bot.question = message.text
            self.ege_bot.user_state[message.chat.id] = 'AWAITING_ANSWER'

        elif self.ege_bot.user_state.get(message.chat.id) == 'AWAITING_ANSWER':
            self.ege_bot.answer = message.text
            self.ege_bot.add_question(message)
            self.bot.send_message(message.chat.id, "Задание успешно добавлено!")
            self.ege_bot.user_state[message.chat.id] = 'NONE'
            self.ege_bot.main_menu(message)

        elif message.text == 'Сбросить статистику':
            self.ege_bot.menu_test_input(message)
            self.ege_bot.user_state[message.chat.id] = 'DELETE_PROGRES'

        elif self.ege_bot.user_state.get(message.chat.id) == 'DELETE_PROGRES':
            self.ege_bot.user_state[message.chat.id] = 'NONE'
            if message.text in [str(i) for i in range(1, 27)]:
                self.ege_bot.task[username] = int(message.text)
                self.ege_bot.delete_progres(message)
                self.bot.send_message(message.chat.id, "Прогресс очищен.")
                self.ege_bot.main_menu(message)
                self.ege_bot.user_state[message.chat.id] = 'NONE'
            elif message.text == 'меню':
                self.ege_bot.main_menu(message)
                self.ege_bot.user_state[message.chat.id] = 'NONE'

        elif message.text == 'Статистика':
            self.ege_bot.all_static_eque_diagram(message)
            self.ege_bot.main_menu(message)
            self.ege_bot.user_state[message.chat.id] = 'NONE'

        elif message.text == "Помочь автору создавать":
            self.bot.send_message(message.chat.id, "Спасибо за вашу поддержку!\n Ваш вклад помогает"
                                                   " мне создавать и делиться своим творчеством. Вы можете поддержать "
                                                   "меня, сделав перевод на мой банковский счет. Номер моей карты:"
                                                   " **** **** **** ****. Благодарю вас за поддержку!")
            self.ege_bot.user_state[message.chat.id] = 'NONE'
            self.ege_bot.main_menu(message)

        elif message.text == 'Статистика по заданиям':
            self.bot.send_message(message.chat.id, "Пожалуйста, введите по какому заданию построить диаграмму.")
            self.ege_bot.menu_test_input(message)
            self.ege_bot.user_state[message.chat.id] = 'ENTERING_TASK_DIAGRAM'

        elif self.ege_bot.user_state.get(message.chat.id) == 'ENTERING_TASK_DIAGRAM':
            self.ege_bot.user_state[message.chat.id] = 'NONE'
            if message.text in [str(i) for i in range(1, 27)]:
                self.ege_bot.task[username] = int(message.text)
                self.ege_bot.all_in_task_static_eque_diagram(message)
                self.ege_bot.user_state[message.chat.id] = 'NONE'
                self.ege_bot.main_menu(message)
            elif message.text == 'меню':
                self.ege_bot.main_menu(message)
                self.ege_bot.user_state[message.chat.id] = 'NONE'

        elif message.text == 'Оставить отзыв/жалобу':
            self.bot.send_message(message.chat.id, "Пожалуйста, напишите отзыв/жалобу в следующем сообщении")
            self.ege_bot.user_state[message.chat.id] = 'SEND_MAIL'

        elif self.ege_bot.user_state.get(message.chat.id) == "SEND_MAIL":
            self.ege_bot.user_state[message.chat.id] = 'NONE'
            if message.text == 'меню':
                self.ege_bot.main_menu(message)
                self.ege_bot.user_state[message.chat.id] = 'NONE'
            else:
                self.ege_bot.send_email(message)
                self.bot.send_message(message.chat.id, "Спасибо! Ваша поддержка и отзывы"
                                                       " помогают нам совершенствоваться.")
                self.ege_bot.user_state[message.chat.id] = 'NONE'
                self.ege_bot.main_menu(message)

        elif message.text == 'меню':
            self.ege_bot.main_menu(message)
            self.ege_bot.user_state[message.chat.id] = 'NONE'

        else:
            self.bot.reply_to(message, message.text)
            self.ege_bot.user_state[message.chat.id] = 'NONE'


def send_email(message):
    try:
        sender_email = 'почта с которой отправляем (gmail)'
        password = 'пароль от неё'
        receiver_email = 'почта, на которую отправляем'
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(sender_email, password)
        message = f'Subject: Отзыв/жалоба на телеграмм бот по подготовке к егэ по русскому языку\n' \
                  f'Content-Type: text/plain; charset=utf-8\n\n{message.text}'
        server.sendmail(sender_email, receiver_email, message.encode('utf-8'))
        print('Email sent successfully')
    except Exception as e:
        print(f'Error: {e}')


class EgeBot:
    def __init__(self, token):
        self.question = None
        self.answer = None
        self.exercise = None
        self.test_len = None
        self.bot = telebot.TeleBot(token)
        self.user_interaction = UserInteraction(self.bot, self)
        self.user_tasks = {}
        self.task = {}
        self.rows = {}
        self.increment_errors_in_tasks = {}
        self.increment_correct_tasks = {}
        self.answered = [[] for _ in range(27)]
        self.admin_key = "31082022_22082023"
        self.user_state = {}
        self.conn = sl.connect('users.db')
        self.c = self.conn.cursor()
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                ''' + ', '.join(f'correct_task_{i} INTEGER, errors_in_task_{i} INTEGER' for i in range(1, 27)) + '''
            )
        ''')
        self.conn_test = sl.connect('test.db')
        self.c = self.conn_test.cursor()
        for i in range(1, 27):
            self.c.execute(f'''
                CREATE TABLE IF NOT EXISTS test_{i} (
                    id INTEGER PRIMARY KEY,
                    exercise TEXT,
                    question TEXT,
                    answer TEXT
                )
            ''')

    def add_or_update_user_task(self, message):
        username = message.from_user.username
        conn = sl.connect('users.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO users (username, ''' + ', '.join(
            f'correct_task_{i}, errors_in_task_{i}' for i in range(1, 27)) + ''')
            VALUES (?, ''' + ', '.join('?' for _ in range(1, 27 * 2 - 1)) + f''')
            ON CONFLICT(username) DO UPDATE SET correct_task_{self.task[username]} = correct_task_{self.task[username]}
             + ?, errors_in_task_{self.task[username]} = errors_in_task_{self.task[username]} + ? 
        ''', (username, *(0,) * 52, self.increment_correct_tasks[username], self.increment_errors_in_tasks[username]))
        conn.commit()

    def delete_progres(self, message):
        username = message.from_user.username  # получаем имя пользователя, который отправил сообщение (проходил тест)
        conn = sl.connect('users.db')
        c = conn.cursor()
        c.execute(f'''
            INSERT INTO users (username, correct_task_{self.task[username]}, errors_in_task_{self.task[username]})
            VALUES (?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET correct_task_{self.task[username]}
             = 0, errors_in_task_{self.task[username]} = 0
            ''', (username, 0, 0))
        conn.commit()

    def add_question(self, message):
        username = message.from_user.username
        connection = sl.connect('test.db')
        cursor = connection.cursor()
        cursor.execute(f"INSERT INTO test_{self.task[username]} (exercise, question, answer) VALUES (?, ?, ?)",
                       (self.exercise, self.question, self.answer))
        connection.commit()
        connection.close()

    def main_menu(self, message):
        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtn1 = types.KeyboardButton('Пройти тест по заданию')
        itembtn2 = types.KeyboardButton('Статистика')
        itembtn3 = types.KeyboardButton('Статистика по заданиям')
        itembtn4 = types.KeyboardButton('Помочь автору создавать')
        itembtn5 = types.KeyboardButton('Оставить отзыв/жалобу')
        itembtn6 = types.KeyboardButton('Сбросить статистику')
        itembtn7 = types.KeyboardButton('меню')
        markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6, itembtn7)
        self.bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

    def menu_test_input(self, message):
        markup = types.ReplyKeyboardMarkup(row_width=3)
        itembtns = [types.KeyboardButton(str(i)) for i in range(1, 27)]
        itembtns.append(types.KeyboardButton('меню'))
        markup.add(*itembtns)
        self.bot.send_message(message.chat.id, "Выберите задание:", reply_markup=markup)

    def start_test(self, message):
        try:
            username = message.from_user.username
            self.get_question(message)
            self.bot.send_message(message.chat.id, self.user_tasks[username]['question'])
            self.bot.send_message(message.chat.id, self.user_tasks[username]['exercise'])
            self.user_state[message.chat.id] = 'IN_TEST'
        except IndexError:
            self.bot.send_message(message.chat.id, "Все задания данного типа решены, сбросьте, пожалуйста,"
                                                   "прогресс по данному заданий.")
            self.test_len = 100

    def get_question(self, message):
        username = message.from_user.username
        if username not in self.user_tasks:
            self.user_tasks[username] = {'tasks': [[] for _ in range(27)]}

        conn = sl.connect('test.db')
        cur = conn.cursor()
        cur.execute(f"SELECT COUNT(*) FROM test_{self.task[username]}")
        rows = cur.fetchone()

        question_id = choice(
            [i for i in range(1, rows[0] + 1) if i not in self.user_tasks[username]['tasks'][self.task[username]]])

        self.user_tasks[username]['tasks'][self.task[username]].append(question_id)
        cur.execute(f"SELECT * FROM test_{self.task[username]} WHERE id=?", (question_id,))
        row = cur.fetchone()
        conn.close()
        self.user_tasks[username]['question'] = row[1]
        self.user_tasks[username]['exercise'] = row[2]
        self.user_tasks[username]['answer'] = row[3]

    @staticmethod
    def get_user_data(message):
        username = message.from_user.username
        con = sl.connect('users.db')
        c = con.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_data = c.fetchone()
        con.commit()
        con.close()
        return user_data

    def all_in_task_static_eque_diagram(self, message):
        username = message.from_user.username
        data = self.get_user_data(message)
        labels = ['Правильно', 'Неправильно']
        try:
            sizes = [data[self.task[username] * 2 - 1],
                     data[self.task[username] * 2]]
            colors = ['lightgreen', 'pink']
            fig1, ax1 = plt.subplots()
            ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')
            plt.savefig('plot.png')
            self.bot.send_photo(message.chat.id, open('plot.png', 'rb'))
            self.bot.send_message(message.chat.id, "✅Правильно: " + str(data[self.task[username] * 2 - 1])
                                  + "\n❌Неправильно:" + str(data[self.task[username] * 2]))
        except:
            self.bot.send_message(message.chat.id, "Для построения диаграммы необходимо хотя бы раз пройти тест")

    def static_eque_diagram(self, message, correct, errors):
        labels = ['Правильно', 'Неправильно']
        sizes = [correct, errors]
        colors = ['lightgreen', 'pink']
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.axis("equal")
        plt.savefig('plot.png')
        self.bot.send_photo(message.chat.id, open('plot.png', 'rb'))
        self.bot.send_message(message.chat.id, "✅Правильно: " + str(correct) + "\n❌Неправильно:" + str(errors))

    def all_static_eque_diagram(self, message):
        data = self.get_user_data(message)
        labels = ['Правильно', 'Неправильно']
        correct = 0
        error = 0

        try:
            for i in range(1, len(data), 2):
                correct += data[i]
                error += data[i + 1]
            sizes = [correct, error]
            colors = ['lightgreen', 'pink']
            fig1, ax1 = plt.subplots()
            ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')
            plt.savefig('plot.png')
            self.bot.send_photo(message.chat.id, open('plot.png', 'rb'))
            self.bot.send_message(message.chat.id, "✅Правильно: " + str(correct) + "\n❌Неправильно:" + str(error))

        except TypeError:
            self.bot.send_message(message.chat.id, "Для построения диаграммы необходимо хотя бы раз пройти тест")

    def start(self):
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            self.main_menu(message)
            self.bot.send_message(message.chat.id,
                                  "Добрый день, спасибо, что пользуетесь данным ботом."
                                  " Все задания взяты из открытого банка заданий ФИПИ и диагностических работ ЕГЭ."
                                  " Данный проект не является коммерческим.")

        @self.bot.message_handler(func=lambda m: True)
        def handle_message(message):
            self.user_interaction.handle_text_message(message)

        self.bot.polling()


if __name__ == '__main__':
    bot = EgeBot('your telegram API bot')
    bot.start()
