#-*- coding: utf-8 -*-
#qpy:kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.utils import platform
from kivy.clock import Clock

from bot_core import LongPollSession


Builder.load_string('''
#:import FadeTransition kivy.uix.screenmanager.FadeTransition
<Root>:
    id: rootscr
    transition: FadeTransition()
''')


class ChatBot(App):
    def __init__(self, *args, **kwargs):
        super(ChatBot, self).__init__(*args, **kwargs)
        self.root = Root()
    
    def on_stop(self):
        while not session.stop_bot(): continue

    def build(self):
        self.root.add_widget(HomeScreen(config=self.config))
        self.root.add_widget(LoginScreen())
        
        activation_status = self.config.getdefault('General', 'bot_activated', 0)
        global session
        session = LongPollSession(activated=activation_status)

        if not session.authorization():
            self.show_auth_form()

        return self.root

    def show_auth_form(self):
        self.root.current = 'login_screen'

    def show_home_form(self):
        self.root.current = 'home_screen'

    def on_pause(self):
        return True
        
    def build_config(self, config):
        config.setdefaults('General', {'show_bot_activity': 0, "bot_activated": 0})

    def build_settings(self, settings):
        settings.add_json_panel("Настройки бота", self.config, data=
            '''[
                {"type": "bool",
                "title": "Отображать состояние бота в статусе (WIP)",
                "section": "General",
                "key": "show_bot_activity",
                "values": [1, 0]
                },
                {"type": "bool",
                "title": "Бот активирован",
                "section": "General",
                "key": "bot_activated",
                "values": [1, 0],
                "disabled": 0
                }
            ]'''
        )

class LoginScreen(Screen):
    def log_in(self):
        login = self.ids.login.text
        password = self.ids.pass_input.text

        if login and password:
            if session.authorization(login=login, password=password):
                self.parent.current = 'home_screen'
                self.ids.pass_input.text = ''

        self.ids.login.text = ''


class HomeScreen(Screen):
    def __init__(self, *args, **kwargs):
        super(HomeScreen, self).__init__(*args, **kwargs)
        self.bot_check_event = Clock.schedule_interval(self.check_if_bot_active, 1)
        self.config = kwargs['config']
        
    def on_main_btn_press(self):
        run_bot_text = 'Запустить бота'
        stop_bot_text = 'Остановить бота'

        if self.ids.button.text == run_bot_text:
            config = ChatBot.get_running_app().config
            activation_status = config.getdefault('General', 'bot_activated', 0)
            while not session.start_bot(activated=activation_status): continue
            self.ids.button.text = stop_bot_text
            self.bot_check_event()
        else:
            self.bot_check_event.cancel()
            while not session.stop_bot(): continue
            self.ids.button.text = run_bot_text

        #self.update_answers_count()

    def update_answers_count(self):
        self.ids.answers_count_lb.text = 'Ответов: {}'.format(session.reply_count)

    def logout(self):
        session.authorization(logout=True)
        self.parent.current = 'login_screen'

    def crack_pentagon(self):
        return '(В разработке)'
    
    def check_if_bot_active(self, _):
        if not session.running:
            self.ids.button.text = 'Запустить бота'
            self.bot_check_event.cancel()

class Root(ScreenManager):
    pass

if __name__ == '__main__':
    ChatBot().run()