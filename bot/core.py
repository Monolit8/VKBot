# -*- coding: utf-8 -*-


import time
import re
import math
import random

from threading import Thread

from utils import PATH, DATA_PATH, load_custom_commands,\
save_custom_commands, load_blacklist, save_blacklist

import vkrequests as vkr

__version__ = '0.0.7'
AUTHOR_VK_ID = 180850898
__author__ = 'Eugene Ershov - https://vk.com/id%d' % AUTHOR_VK_ID

__help__ = u'''
Версия: {v}

Я умею:
*Говорить то, что вы попросите
(/say ... |/скажи ... )
*Производить математические операции
(/calculate ... |/посчитай ... ) =
*Проверять, простое ли число
(/prime ... |/простое ... ) %
*Определять достоверность информации
(/chance ... |/инфа ... )
*Выбирать участника беседы
(/who ... |/кто ... )
*Учить ответы
(/learn command:response |/выучи команда:ответ ) +
*Забывать ответы
(/forgot command:response |/забудь команда:ответ ) -
*Вызывать помощь
(/help |/помощь ) ?


Автор: {author}

В конце моих сообщений ставится знак верхней кавычки
'''.format(\
    v = __version__, author = __author__
)


class Bot():
    def blacklist(self, cmd, blacklist):
        if not cmd.out:
            return u'Отказано в доступе', blacklist
        if len(cmd.words) == 1:
            chat_id = cmd.msg_from[0] if cmd.msg_from[0] else cmd.msg_from[1]
            if cmd.from_chat:
                chat_id += 2000000000
            chat_id = str(chat_id)
            if chat_id in blacklist:
                return u'Данный id уже находится в чёрном списке', blacklist
            else:
                blacklist.append(chat_id)
                save_blacklist(blacklist)
                return u'id {} добавлен в чёрный список'.format(chat_id), blacklist
        else:
            if cmd.words[1] == '-':
                if len(cmd.words) == 2:
                    chat_id = cmd.msg_from[0] if cmd.msg_from[0] else cmd.msg_from[1]
                else:
                    if re.match('^\d+$', cmd.words[2]):
                        chat_id = cmd.words[2]
                    else:
                        return u'Неправильно указан id', blacklist
                if cmd.from_chat and chat_id < 2000000000:
                    chat_id = int(chat_id)
                    chat_id += 2000000000
                chat_id = str(chat_id)
                if chat_id not in blacklist:
                    return u'В чёрном списке нет данного id', blacklist
                else:
                    blacklist.remove(chat_id)
                    save_blacklist(blacklist)
                    return u'id {} удалён из чёрного спика'.format(chat_id), blacklist
            else:
                if re.match('\d+', cmd.words[1]):
                    chat_id = cmd.words[1]
                    chat_id = str(chat_id)
                    if chat_id in blacklist:
                        return u'Данный id уже находится в чёрном списке', blacklist
                    else:
                        blacklist.append(chat_id)
                        save_blacklist(blacklist)
                    return u'id {} добавлен в чёрный список'.format(chat_id), blacklist
                else:
                    return u'Неправильно указан id', blacklist

    def help(self):
        return __help__

    def say(self, cmd):
        words = cmd.words
        argument_required = self._is_argument_missing(words)
        if argument_required:
            return argument_required

        del words[0]
        text = ' '.join(words)
        return text

    def calculate(self, cmd):
        words = cmd.words
        argument_required = self._is_argument_missing(words)
        if argument_required:
            return argument_required

        if words[0].startswith('='):
            words[0] = words[0][1:]
        else:
            del words[0]
        words = ''.join(words).lower()
        if not re.match(u'[^\d+\-*/:().,^√πe]', words) or re.match('(sqrt\(.+\))|(pi)', words):
            words = ' ' + words + ' '
            words = re.sub(u'(sqrt)|√', 'math.sqrt', words)
            words = re.sub(u'(pi)|π', 'math.pi', words)
            words = re.sub('\^', '**', words)
            words = re.sub(',', '.', words)
            words = re.sub(u':|÷', '/', words)
            while True:
                if '/' in words:
                    index = re.search('[^.\d]\d+[^.\de]', words)
                    if index:
                        index = index.end() - 1
                        words = words[:index] + '.' + words[index:]
                    else:
                        break
                else:
                    break
            try:
                result = str(eval(words))
            except SyntaxError:
                result = u'Ошибка [0]'
            except NameError:
                result = u'Ошибка [1]'
            except AttributeError:
                result = u'Ошибка [2]'
            except TypeError:
                result = u'Ошибка [3]'
            except ZeroDivisionError:
                result = u'Деление на 0'
            except OverflowError:
                result = u'Слишком большой результат'
        else:
            result = u'Не математическая операция'
        return result

    def prime(self, cmd):
        words = cmd.words
        argument_required = self._is_argument_missing(words)
        if argument_required:
            return argument_required

        del words[0]
        input_number = ''.join(words)
        if re.match('^\d+$', input_number) and len(input_number)<=5:
            input_number = int(input_number)
            luc_number = 0
            last_luc_number = 0
            for i in range(input_number):
                if luc_number == 0:
                    luc_number = 1
                elif luc_number == 1:
                    last_luc_number = luc_number
                    luc_number = 3
                else:
                    luc_number, last_luc_number = last_luc_number + luc_number, luc_number
                            
            if input_number != 0:
                is_prime = True if (luc_number - 1) % input_number == 0 else False
                result = u'Является простым числом' if is_prime else u'Не является простым числом'
            else:
                result = u'0 не является простым числом'
        else:
            result = u'Дано неверное или слишком большое значение'
        return result

    def chance(self, cmd):
        argument_required = self._is_argument_missing(cmd.words)
        if argument_required:
            return argument_required

        return u'Вероятность ' + str(random.randrange(102)) + '%'

    def who(self, cmd):
        argument_required = self._is_argument_missing(cmd.words)
        if argument_required:
            return argument_required

        if not cmd.from_chat:
            return u'Данная команда работает только в беседе'
        elif len(cmd.chat_users) < 2:
            return u'Для корректной работы команды в беседе должно находиться больше одного человека'
        else:
            user_id = random.choice(cmd.chat_users)
            user_name, error = vkr.get_user_name(user_id=user_id, name_case='acc')
            if user_name:
                return u'Я выбираю [id{0}|{1}]'.format(str(user_id), user_name)

    def learn(self, cmd, custom_commands, protect=True):
        if protect:
            if not cmd.out:
                return custom_commands, u'Отказано в доступе'

        response_text = u'Команда выучена.\nТеперь на «{}» я буду отвечать «{}»'
        words = cmd.words
        argument_required = self._is_argument_missing(words)

        del words[0]
        text = ' '.join(words)
        text = text.split(':')
        command = text[0]
        response = ':'.join(text[1:])

        if argument_required:
            response_text = argument_required
        elif len(text) <2 or not (command and response):
            response_text = u'Неправильный синтаксис команды' 
        elif command.lower() in custom_commands.keys() and response\
                in custom_commands[command.lower()]:
            response_text = u'Я уже знаю такой ответ'
        elif command in custom_commands.keys():
            custom_commands[command.lower()].append(response)
            response_text = response_text.format(command.lower(), response)
        else:
            custom_commands[command.lower()] = [response]
            response_text = response_text.format(command.lower(), response)

        save_custom_commands(custom_commands)
        return custom_commands, response_text

    def forgot(self, cmd, custom_commands, protect=True):
        if protect:
            if not cmd.out:
                return custom_commands, u'Отказано в доступе'

        response_text = u'Команда забыта'
        words = cmd.words
        argument_required = self._is_argument_missing(words)
        if argument_required:
            return custom_commands, argument_required        

        del words[0]
        text = ' '.join(words)
        if ':' in text:
            text = text.split(':')
            command = text[0]
            response = ':'.join(text[1:])
        else:
            command = text
            response = ''

        if command and response:
            if not command in custom_commands.keys():
                response = ''
            elif len(custom_commands[command.lower()]) < 2:
                response = ''
            elif response not in custom_commands[command.lower()]:
                response_text = u'В команде «{}» нет ключа «{}»'.format(
                                custom_commands[command.lower()], response
                                )
            else:
                custom_commands[command.lower()].remove(response)
                response_text = u'Ключ для команды забыт'

        if not response and not custom_commands.pop(command.lower(), None):
            response_text = u'Я не знаю такой команды ({})'.format(command)
        
        save_custom_commands(custom_commands)
        return custom_commands, response_text

    def custom_command(self, cmd, custom_commands):
        response_text, attachments = '', []
        if custom_commands and cmd.joined_text.lower() in custom_commands.keys():
            response = random.choice(custom_commands[cmd.joined_text.lower()])

            if response.startswith('self='):
                command = '_' + response[5:]
                if command.lower() in custom_commands.keys():
                    response = custom_commands[command.lower()]
                    response = random.choice(response)
                else:
                    response = u'Ошибка. Нет указанного ключа'

            if response.startswith('attach='):
                attachments = response[7:]
                if re.match('.*/((photo)|(video)|(audio)|(doc)|(wall)|(market))(\d+_\d+(_\d+)?)$', attachments):
                    attachments = attachments.split('/')[-1] # URGLY # FIXME
                else:
                    response_text = u'Не могу показать вложение. Неправильная ссылка'
            else:
                response_text = response
        return response_text, attachments

    def activate_bot(self, cmd, activated):
        if activated:
            return u'Бот уже активирован', True
        elif cmd.from_chat and cmd.chat_user == AUTHOR_VK_ID:
            return u'Активация прошла успешно', True
        else:
            return u'Отказано в доступе', False

    def deactivate_bot(self, cmd, activated):
        if cmd.from_chat and cmd.chat_user == AUTHOR_VK_ID:
            return u'Деактивация прошла успешно', False
        elif activated:
            return u'Отказано в доступе', True
        else:
            return u'Отказано в доступе', False

    def _is_argument_missing(self, words):
        if len(words) == 1:
            return u'Команду необходимо использовать с аргументом'
        else:
            return False


class Command():
    def __init__(self, SELF_ID):
        self.SELF_ID = SELF_ID
        self.text = ''
        self.words = ['']
        self.is_command = False
        self.mark_msg = True
        self.joined_text = ''
        self.from_user = False
        self.from_chat = False
        self.from_group = False
        self.msg_from = None, None
        self.chat_user = None
        self.chat_users = []
        self.out = False

    def load(self, message):
        self.__init__(self.SELF_ID) # refresh params

        self.text = message['body']

        if self.text:
            self.words = self.text.split(' ')

        if self.words[0].startswith('/'):
            self.words[0] = self.words[0][1:]
            self.is_command = True
            if self.words[0].startswith('/'):
                self.words[0] = self.words[0][1:]
                self.mark_msg = False

        self.joined_text = ' '.join(self.words)
        if 'chat_id' in message.keys():
            self.from_chat = True
        elif int(message['user_id']) < 1:
            self.from_group = True
            self.mark_msg = False
        else:
            self.from_user = True

        if self.from_chat:
            self.msg_from = message['chat_id'], None
            self.chat_user = message['user_id']
            self.forward_msg = message['id']
            self.chat_users = message['chat_active']
        else:
            self.msg_from = None, message['user_id']
            self.forward_msg = None

        if self.msg_from[1] == self.SELF_ID:
            self.out = 1
        else:
            self.out = message['out']
        

class LongPollSession(Bot):
    def __init__(self):
        self.activated = False
        self.authorized = False
        self.update_processing = None
        self.run_bot = False
        self.running = False
        self.runtime_error = None
        self.reply_count = 0
        self.custom_commands = None
        self.use_custom_commands = False
        self.protect_custom_commands = True

    def authorization(self, login= '', password= '', token='', key='', logout=False, token_path=''):
        if not token_path:
            token_path = DATA_PATH + 'token.txt'
        authorized = False
        error = None
        if logout:
            open(token_path, 'w').close()
            self.authorized = False
            return authorized, error

        if not (login and password):
            if token:
                response, error = vkr.log_in(token=token)
                if response and not error:
                    authorized = True
            else:
                try:
                    with open(token_path, 'r') as token_file:
                        lines = token_file.readlines()
                        if lines:
                            token = lines[0][:-1]
                except:
                    token = None
                    open(token_path, 'w').close()

                if token:
                    response, error = vkr.log_in(token=token)
                    if response and not error:
                        authorized = True
                        if error:
                            if 'invalid access_token' in error:
                                open(token_path, 'w').close()
        else:
            new_token, error = vkr.log_in(login=login, password=password, key=key)
            if new_token and not error:
                with open(token_path, 'w') as token_file:
                    token_file.write('{}\n{}'.format(\
                        new_token, 'НИКОМУ НЕ ПОКАЗЫВАЙТЕ СОДЕРЖИМОЕ ЭТОГО ФАЙЛА'
                        )
                    )
                authorized = True
            elif self.authorized:
                return authorized, error

        self.authorized = authorized
        return authorized, error

    def _process_updates(self):
        try:
            if not self.authorized: raise Exception('Not authorized')               

            self.black_list = load_blacklist()

            SELF_ID = vkr.get_self_id()[0]
            command = Command(SELF_ID)

            mlpd = vkr.get_message_long_poll_data()[0]
            last_response_text = ''
            response_text = ''
            custom_response = ''
            attachments = []
            self.runtime_error = None
            self.running = True

            print('@LAUNCHED')
            while self.run_bot:
                updates, error = vkr.get_message_updates(ts=mlpd['ts'],pts=mlpd['pts'])
                
                if updates:
                    history = updates[0]
                    mlpd['pts'] = updates[1]
                    messages = updates[2]
                elif 'connection' in error:
                    error = None
                    time.sleep(1)
                    continue
                else:
                    raise Exception(error)

                response_str = str(updates)
                # if u'emoji' in messages.keys():
                #     print(response_str)
                # else:
                #     print(response_str.decode('unicode-escape').encode('utf8'))

                for message in messages['items']:
                    command.load(message)
                    if not command.text or command.text == last_response_text:
                        continue

                    blacklisted = False
                    if command.is_command and re.match(u'^blacklist$', command.words[0].lower()):
                        response_text, self.black_list = self.blacklist(command, self.black_list)
                    elif command.msg_from[0] and str(command.msg_from[0] + 2000000000) in self.black_list:
                        blacklisted = True
                    elif str(command.msg_from[1]) in self.black_list:
                        blacklisted = True

                    if command.is_command and not blacklisted:
                        if re.match(u'(^help)|(^помощь)|(^info)|(^инфо)|(^информация)|^\?$',\
                            command.words[0].lower()):
                            response_text = self.help()

                        elif re.match(u'(^скажи)|(^say)$', command.words[0].lower()):
                            response_text = self.say(command)

                        elif re.match(u'(^посчитай)|(^calculate)|^=$', command.words[0].lower()):
                            response_text = self.calculate(command)    

                        elif re.match(u'(^простое)|(^prime)|%$', command.words[0].lower()):
                            response_text = self.prime(command)

                        elif re.match(u'(^инфа)|(^chance)$', command.words[0].lower()):
                            response_text = self.chance(command)

                        elif re.match(u'(^кто)|(^who)$', command.words[0].lower()):
                            response_text = self.who(command)

                        elif re.match(u'(^выучи)|(^learn)|\+$', command.words[0].lower()):
                            self.custom_commands, response_text = self.learn(
                                command,
                                self.custom_commands,
                                protect=self.protect_custom_commands
                                )

                        elif re.match(u'(^забудь)|(^forgot)|\-$', command.words[0].lower()):
                            self.custom_commands, response_text = self.forgot(
                                command,
                                self.custom_commands,
                                protect=self.protect_custom_commands
                                )
                            
                        elif re.match(u'(^stop)|(^выйти)|(^exit)|(^стоп)|(^terminate)|(^завершить)|(^close)|^!$',\
                             command.words[0].lower()):
                            response_text = self._stop_bot_from_message(command)

                        elif command.words[0].lower() == 'activate':
                            response_text, self.activated = self.activate_bot(command, self.activated)

                        elif command.words[0].lower() == 'deactivate':
                            response_text, self.activated = self.deactivate_bot(command, self.activated)

                        elif command.words[0].lower() == 'raise':
                            response_text = self._raise_debug_exception(command)

                        else:
                            response_text = u'Неизвестная команда. Вы можете использовать /help для получения списка команд.'
                            if self.use_custom_commands:
                                custom_response, attachments = self.custom_command(
                                                                    command,
                                                                    self.custom_commands
                                                                    )

                    elif self.use_custom_commands and self.custom_commands is not None and not blacklisted:
                        custom_response, attachments = self.custom_command(
                            command,
                            self.custom_commands
                            )

                    if custom_response:
                            response_text = custom_response

                    if not (response_text or attachments):
                        continue

                    if not self.activated:
                        response_text +=\
                            u'\n\nБот не активирован. По вопросам активации просьба обратиться к автору: %s' % __author__

                    if command.mark_msg:
                        response_text += "'"

                    chat_id, user_id = command.msg_from
                    message_to_resend = command.forward_msg

                    msg_id, error = vkr.send_message(
                                        text = response_text,
                                        uid = user_id,
                                        gid = chat_id,
                                        forward = message_to_resend,
                                        attachments = attachments
                                        )
                    if error:
                        raise Exception(error)

                    last_response_text = response_text
                    response_text = ''
                    attachments = []
                    self.reply_count += 1
            time.sleep(1)
        except:
            if not 'traceback' in globals():
                import traceback
            tb = traceback.format_exc()
            try:
                self.runtime_error = tb.decode('unicode-escape')
            except UnicodeDecodeError:
                self.runtime_error = tb
            self.run_bot = False

        self.running = False
        self.reply_count = 0
        print('@STOPPED')

    def launch_bot(self):
        self.run_bot = True

        self.update_processing = Thread(target=self._process_updates)
        self.update_processing.start()

        while not self.running:
            time.sleep(0.1)
            if self.runtime_error:
                raise Exception(self.runtime_error)
        return True

    def stop_bot(self):
        self.run_bot = False

        while self.running: continue
        self.update_processing = None
        return True, self.activated

    def load_params(self,
                    activated=False,
                    use_custom_commands=False,
                    protect_custom_commands=True):
        if use_custom_commands:
            self.custom_commands = load_custom_commands()

        self.activated = activated
        self.use_custom_commands = use_custom_commands
        self.protect_custom_commands = protect_custom_commands

    def _stop_bot_from_message(self, command):
        if command.out:
            self.run_bot = False
            return u'Завершаю работу'
        else:
            return u'Отказано в доступе'

    def _raise_debug_exception(self, command):
        if command.out:
            words = command.words
            del words[0]
            if not words:
                exception_text = 'Default exception text'
            else:
                exception_text = ' '.join(words)
            raise Exception(exception_text)
        else:
            return u'Отказано в доступе'


if __name__ == '__main__':
    session = LongPollSession()
    DATA_PATH = PATH + DATA_PATH
    while not session.authorized:
        response, error = session.authorization()
        if not response:
            LOGIN = raw_input('login:')
            PASSWORD = raw_input('password:')
            response, error = session.authorization(login=LOGIN, password=PASSWORD)

        if error and 'code is needed' in error:
            key = raw_input('key:')
            response, error = session.authorization(login=LOGIN, password=PASSWORD, key=key)

    print('\tУспешная авторизация\n')
    session.start_bot()