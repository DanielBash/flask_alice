"""Модуль для обработки запросов Яндекс.Диалогов во Flask.

Предоставляет основные классы расширения Flask и утилиты
для интеграции Яндекс.Диалогов с приложениями Flask.

Пример:
    from flask_alice import Alice
    app = Flask(__name__)
    alice = Dialogs(app, listener='/post')

Автор: DanielBash
"""

from .classes.communication import AliceRequest, AliceResponse
from .classes.application import Dialogs