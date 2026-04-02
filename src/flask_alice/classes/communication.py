import json
import flask
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Union


def _dict_to_obj(data: Union[Dict, List, Any]) -> Any:
    """Рекурсивно преобразует словари и списки в объекты с доступом через точку."""
    if isinstance(data, dict):
        obj = SimpleNamespace()
        for key, value in data.items():
            setattr(obj, key, _dict_to_obj(value))
        return obj
    elif isinstance(data, list):
        return [_dict_to_obj(item) for item in data]
    else:
        return data


class Request:
    """
    Класс для парсинга входящего запроса от Яндекс Диалогов.
    Поддерживает данные в виде словаря, Flask-запроса или JSON-строки.
    Все поля становятся доступны как атрибуты, вложенные объекты также преобразуются.
    """

    def __init__(self, data: Union[Dict, flask.Request, str]):
        """
        Args:
            data: Входные данные запроса
        """
        if isinstance(data, flask.Request):
            raw_data = data.json()
        elif isinstance(data, str):
            raw_data = json.loads(data)
        else:
            raw_data = data

        obj = _dict_to_obj(raw_data)

        self.__dict__.update(obj.__dict__)

        self._raw = raw_data

    def __repr__(self) -> str:
        return f"<Request type={self.request.type if hasattr(self, 'request') else 'unknown'}>"

    def is_new_session(self) -> bool:
        """Возвращает True, если это первое сообщение в сессии."""
        return getattr(self.session, 'new', False)

    def get_command(self) -> str:
        """
        Возвращает нормализованную команду пользователя.
        Работает только для SimpleUtterance, иначе возвращает пустую строку.
        """
        if hasattr(self.request, 'command'):
            return self.request.command
        return ""

    def get_original_utterance(self) -> str:
        """Возвращает исходную фразу пользователя (если есть)."""
        if hasattr(self.request, 'original_utterance'):
            return self.request.original_utterance
        return ""

    def get_request_type(self) -> str:
        """Возвращает тип запроса (SimpleUtterance, ButtonPressed, Show.Pull)."""
        return getattr(self.request, 'type', '')

    def get_payload(self) -> Optional[Any]:
        """Возвращает payload из запроса (для кнопок или кастомных данных)."""
        return getattr(self.request, 'payload', None)

    def get_intents(self) -> Dict:
        """Возвращает словарь интентов (если есть)."""
        if hasattr(self.request, 'nlu') and hasattr(self.request.nlu, 'intents'):
            return self.request.nlu.intents.__dict__
        return {}

    def get_entities(self) -> List:
        """Возвращает список именованных сущностей."""
        if hasattr(self.request, 'nlu') and hasattr(self.request.nlu, 'entities'):
            return self.request.nlu.entities
        return []

    def get_tokens(self) -> List[str]:
        """Возвращает список токенов из запроса."""
        if hasattr(self.request, 'nlu') and hasattr(self.request.nlu, 'tokens'):
            return self.request.nlu.tokens
        return []

    def is_dangerous_context(self) -> bool:
        """Проверяет, помечен ли запрос как опасный (криминальный подтекст)."""
        if hasattr(self.request, 'markup') and hasattr(self.request.markup, 'dangerous_context'):
            return self.request.markup.dangerous_context
        return False

    def get_show_type(self) -> Optional[str]:
        """Возвращает тип шоу для запросов Show.Pull (например, 'MORNING')."""
        return getattr(self.request, 'show_type', None)

    def get_user_id(self) -> Optional[str]:
        """Возвращает идентификатор пользователя Яндекса (если авторизован)."""
        if hasattr(self.session, 'user') and hasattr(self.session.user, 'user_id'):
            return self.session.user.user_id
        return None

    def get_access_token(self) -> Optional[str]:
        """Возвращает OAuth-токен пользователя (если выполнена связка аккаунтов)."""
        if hasattr(self.session, 'user') and hasattr(self.session.user, 'access_token'):
            return self.session.user.access_token
        return None

    def get_application_id(self) -> Optional[str]:
        """Возвращает идентификатор экземпляра приложения."""
        if hasattr(self.session, 'application') and hasattr(self.session.application, 'application_id'):
            return self.session.application.application_id
        return None

    def get_session_state(self) -> Optional[Any]:
        """Возвращает состояние сессии (если сохранено)."""
        if hasattr(self.state, 'session'):
            return self.state.session
        return None

    def get_user_state(self) -> Optional[Any]:
        """Возвращает состояние пользователя (если сохранено)."""
        if hasattr(self.state, 'user'):
            return self.state.user
        return None

    def get_application_state(self) -> Optional[Any]:
        """Возвращает состояние приложения (если сохранено)."""
        if hasattr(self.state, 'application'):
            return self.state.application
        return None