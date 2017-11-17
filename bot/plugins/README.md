## Плагины
VKBot поддерживает плагины, написанные на python.  
Все встроенные команды реализованы через плагины. Для добавления плагина, его необходимо назвать его по образцу: `plugin_длинное_название.py`.  
Если плагин назван неправильно, он не будет загружен.  
При необходимости, можно заменить встроенный плагин на свой, указав такое же имя плагина (не путать с именем файла!)

### Базовый палгин
```
# coding:utf8


class Plugin(object):
    __doc__ = '''Плагин предназначен для ответа на команду.
    Для использования необходимо иметь уровень доступа {protection} или выше
    Ключевые слова: [{keywords}]
    Использование: {keyword} <текст>
    Пример: {keyword} привет'''

    name = 'plugin'
    keywords = (name, u'плагин')
    protection = 0
    argument_required = False

    def respond(self, msg, rsp, *args, **kwargs):
        # ваш код
        # ...
        rsp.text = u'Результат работы'

        return rsp
```

### Базовая структура плагина
Плагину необходимо иметь следующие элементы (в соответствующем порядке):
* основной класс с названием `Plugin`, к которому будет обращаться программа
* документацию
* переменную `name`, содержащую имя плагина
* переменную `keywords`, содержащую ключевые слова для вызова плагина
* переменную `protection`
* переменную `argument_required`, обозначающую, нужно ли передавать дополнительный аргумент для работы команды
* функцию `respond`

### Документация плагина
Класс плагина должен иметь переменную `__doc__`.  
Рекомендация по структуре строки документацию:  
1 строка: `Плагин предназначен для <предназначение>.`  
2 строка: `    Для использования необходимо иметь уровень доступа {protection} или выше`  
3 строка: `    Ключевые слова: [{keywords}]`  
4 строкк: `    Использование: {keyword} <использование>`  
5 строка: `    Пример: {keyword} <пример>`  

*Необходимо указать свои значения вместо объектов в угловых скобках `<>`

### Переменные плагина

#### name: str
Имя плагина.

#### keywords: tuple
Ключевые слова (str), при обнаружении которых будет вызван плагин.

#### protection: int
Если уровень доступа пользователь меньше (вызывается после функции _accept_request), команда не будет вызвана.

#### argument_required: bool
Если True и команде не передан дополнительный аргумент, функция `respond` не будет вызвана. (функция `_accept_request` вызывается)

#### disabled: bool
Если True, плагин не будет загружен. По умолчанию False.

### Функции плагина

#### _accept_request(self, msg, rsp, utils, *args, **kwargs): bool
Вызывается до функции respond, возвращаемое значение определяет, будет ли вызван данный плагин. Определена по умолчанию:
```
def _accept_request(self, msg, rsp, utils, *args, **kwargs):
    if msg.was_appeal and msg.args[0].lower() in self.keywords:
        return True

    return False
```

#### respond(self, msg, rsp, utils, *args, **kwargs): rsp
Принимает на вход объект сообщения msg, объект ответа rsp, объект класса дополнительных инструментов utils.
Возвращает полученный объект ответа rsp.

### Описание передаваемых объектов

#### msg
TODO

#### rsp
TODO

#### utils
TODO