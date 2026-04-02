import re
import typing

import flask
from flask import Flask, Blueprint

from .communication import YandexDialogIncomingRequest, YandexDialogResponse


class Handler:
    def __init__(self, func, condition):
        self.handler_func: typing.Callable[[YandexDialogIncomingRequest], YandexDialogResponse] = func
        self.condition: typing.Callable[[YandexDialogIncomingRequest], bool] = condition

    def validate(self, request: YandexDialogIncomingRequest) -> bool:
        return self.condition(request)

    def __call__(self, request: YandexDialogIncomingRequest) -> YandexDialogResponse:
        return self.handler_func(request)


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
    """Основной класс Яндекс.Диалогов."""

    def __init__(self, flask_app: Flask, webhook_url: str = "/") -> None:
        self.app = flask_app
        self.webhook_url = webhook_url
        self.handlers: list[Handler] = []
        self.not_found_handler: typing.Optional[
            typing.Callable[[YandexDialogIncomingRequest], YandexDialogResponse]] = None

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

    def _handle_request(self) -> flask.Response:
        req = YandexDialogIncomingRequest.from_flask_request(flask.request)

        self.app.logger.info("Incoming request: %s", req.command)

        handler = self._find_handler(req)

        if handler is None:
            if self.not_found_handler is not None:
                response_data = self.not_found_handler(req)
            else:
                response_data = YandexDialogResponse(text="Привет!", tts="Привет!")
        else:
            response_data = handler(req)

        self.app.logger.info("Response: %s", response_data)
        return response_data.to_flask_response()

    def _find_handler(self, request: YandexDialogIncomingRequest) -> typing.Optional[typing.Callable]:
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
            request: YandexDialogIncomingRequest,
            text: str,
            regex: bool = False,
            flags: int = 0,
    ) -> bool:
        command = request.command or ""

        if regex:
            return re.fullmatch(text, command, flags) is not None
        return command == text
