from flask import Flask, Blueprint


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

    def _handle_request(self) -> None:
        """
        Обрабатывает запрос пользователя и передаёт его в нужную функцию.
        """
        pass