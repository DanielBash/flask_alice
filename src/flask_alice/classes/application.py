import re
import typing

import flask
from flask import Flask, Blueprint
from .communication import Request


def _handler_type(condition_method):
    def registration_method(self, *args, **kwargs):
        def decorator(user_func):
            def condition(request):
                return condition_method(self, request, *args, **kwargs)

            handler = Handler(user_func, condition)
            self.handlers.append(handler)
            return user_func

        return decorator

    return registration_method

class Dialogs:
    """Основной класс Яндекс.Диалогов.

    Этот класс осуществляет валидацию запросов, управление сессиями
    и форматирование ответов для Яндекс.Диалогов.

    Attributes:
        app (Flask): Экземпляр приложения Flask.
    """
    def __init__(self, flask_app: Flask, webhook_url: str = '/') -> None:
        """
        Attributes:
            flask_app (Flask): Экземпляр приложения Flask.
            webhook_url (str): Путь вебхука, принимающего POST-запросы от сервера Яндекса.
        """
        self.app = flask_app
        self.webhook_url = webhook_url
        self.handlers = []

        self._setup()

    def _setup(self) -> None:
        """
        Функция инициализации класса.
        Вызывает все методы, начинающиеся с _setup_
        """

        for i in dir(self):
            if i.startswith('_setup_'):
                getattr(self, i)()

    def _setup_paths(self):
        """
        Создаёт все необходимые пути приложения.
        """
        bp = Blueprint('alice', __name__)

        @bp.route(self.webhook_url, methods=['POST'])
        def webhook():
            return self._handle_request()

        self.app.register_blueprint(bp)

    def _handle_request(self) -> flask.Response:
        """Ищет обработчик запроса"""
        req = Request(flask.request)

        handler = self._find_handler(req)

        response_data = handler(req)

        return flask.jsonify(response_data)

    def _find_handler(self, request: Request) -> typing.Callable:
        for handler in self.handlers:
            if handler.validate(request):
                return handler

    @_handler_type
    def on_text(self, request, text, regex: bool = False, flags: int = 0):
        command = request.get_command()

        if regex:
            return re.fullmatch(text, command, flags) is not None
        else:
            return command == text


class Handler:
    def __init__(self, func, condition):
        self.handler_func: typing.Callable = func
        self.condition: typing.Callable = condition

    def validate(self, request):
        return self.condition(request)

    def __call__(self, request):
        return self.handler_func(request)
