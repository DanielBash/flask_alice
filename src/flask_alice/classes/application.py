import inspect
import re
import typing
from typing import Any, List, Optional
import flask
import ngram
from flask import Flask, Blueprint

from .communication import AliceRequest, AliceResponse


def pass_if_need(func, req):
    sig = inspect.signature(func)
    params = sig.parameters

    if len(params) > 0:
        return func(req)
    else:
        return func()


def normalize(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()


def are_similar(user_input, candidates):
    user_input = normalize(user_input)

    scores = [ngram.NGram.compare(user_input, normalize(c)) for c in candidates]
    return max(scores) if scores else 0.0


class Handler:
    def __init__(self, func, order: int = 0):
        self.handler_func: typing.Callable[[AliceRequest], AliceResponse] = func
        self.conditions: List[List[typing.Callable]] = [[]]
        self.order = order
        self.name = func.__name__

    def validate(self, request: AliceRequest) -> bool:
        for or_case in self.conditions:
            is_true = 1
            for condition in or_case:
                is_true = min(int(condition(request)), is_true)
            if is_true:
                return True
        return False

    def add_condition(self, func):
        self.conditions[-1].append(func)

    def add_or(self):
        self.conditions.append([])

    def __call__(self, request: AliceRequest) -> AliceResponse:
        return pass_if_need(self.handler_func, request)


def _handler_type(condition_method):
    def registration_method(self, *args, order: int = 0, **kwargs):
        def decorator(user_func):
            def condition(request):
                return condition_method(self, request, *args, **kwargs)

            func_name = user_func.__name__
            handler = self.find_handler(func_name)

            if not handler:
                handler = Handler(user_func, order=order)
                self.handlers.append(handler)

            handler.add_condition(condition)

            self.handlers.sort(key=lambda h: h.order)

            return user_func

        return decorator

    return registration_method


class Dialogs:
    """Основной класс Яндекс.Диалогов."""

    def __init__(self, flask_app: Flask, webhook_url: str = "/") -> None:
        self.app = flask_app
        self.webhook_url = webhook_url
        self.handlers: list[Handler] = []
        self.not_found_handler: typing.Optional[
            typing.Callable[[AliceRequest], AliceResponse]
        ] = None

        self._setup()

    def _setup(self) -> None:
        for name in dir(self):
            if name.startswith("_setup_"):
                getattr(self, name)()

    def _setup_paths(self) -> None:
        bp = Blueprint("alice", __name__)

        @bp.route(self.webhook_url, methods=["POST"])
        def webhook():
            return self._handle_request()

        self.app.register_blueprint(bp)

    def find_handler(self, handler_name):
        for handler in self.handlers:
            if handler.name == handler_name:
                return handler
        return None

    def _handle_request(self) -> flask.Response:
        req = AliceRequest.from_flask_request(flask.request)

        self.app.logger.info(f"YandexRequest: {req.command}")

        handler = self._find_handler(req)

        if handler is None:
            if self.not_found_handler is not None:
                response_data = pass_if_need(self.not_found_handler, req)
            else:
                response_data = AliceResponse(text="Ваш запрос мне непонятен.")
        else:
            response_data = pass_if_need(handler, req)

        return response_data.to_flask_response()

    def _find_handler(self, request: AliceRequest) -> typing.Optional[typing.Callable]:
        for handler in self.handlers:
            if handler.validate(request):
                return handler
        return None

    def on_not_found(self):
        def decorator(user_func):
            self.not_found_handler = user_func
            return user_func

        return decorator

    @_handler_type
    def on_text(
        self,
        request: AliceRequest,
        text: str | list[str],
        regex: bool = False,
        flags: int = 0,
        remove_symbols: bool = True,
    ) -> bool | typing.Callable:
        command = request.command or ""

        def normalize(s: str) -> str:
            if not remove_symbols:
                return s
            s = s.lower()
            return re.sub(r"[^\w\s]", "", s).strip()

        command_norm = normalize(command)

        texts = text if isinstance(text, list) else [text]

        for t in texts:
            if regex:
                if re.fullmatch(t, command, flags):
                    return True
            else:
                if command_norm == normalize(t):
                    return True

        return False

    @_handler_type
    def on_new_session(
        self,
        request: AliceRequest,
    ) -> Any:

        return request.session.new

    @_handler_type
    def on_ngram(
        self,
        request: AliceRequest,
        synonyms: list,
        threshold: float = 0.5,
    ) -> bool | typing.Callable:
        return are_similar(request.command, synonyms) >= threshold

    @_handler_type
    def on_exact(
        self,
        request: AliceRequest,
        text: str,
    ) -> bool | typing.Callable:

        return request.original_utterance == text

    @_handler_type
    def on_condition(
        self,
        request: AliceRequest,
        condition: str,
    ) -> bool | typing.Callable:

        return eval(condition)
