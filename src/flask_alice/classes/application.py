import inspect
import re
import typing
import flask
from flask import Flask, Blueprint
from .communication import AliceRequest, AliceResponse
import re
import ngram


def pass_if_need(func, req):
    sig = inspect.signature(func)
    params = sig.parameters

    if len(params) > 0:
        return func(req)
    else:
        return func()


def normalize(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

def are_similar(user_input, candidates):
    user_input = normalize(user_input)
    
    scores = [
        ngram.NGram.compare(user_input, normalize(c))
        for c in candidates
    ]
    return max(scores) if scores else 0.0


class Handler:
    def __init__(self, func, condition):
        self.handler_func: typing.Callable[[AliceRequest], AliceResponse] = func
        self.condition: typing.Callable[[AliceRequest], bool] = condition

    def validate(self, request: AliceRequest) -> bool:
        return self.condition(request)

    def __call__(self, request: AliceRequest) -> AliceResponse:
        return pass_if_need(self.handler_func, request)


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
            typing.Callable[[AliceRequest], AliceResponse]] = None

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
        req = AliceRequest.from_flask_request(flask.request)

        self.app.logger.info("Incoming request: %s", req.command)

        handler = self._find_handler(req)

        if handler is None:
            if self.not_found_handler is not None:
                response_data = pass_if_need(self.not_found_handler, req)
            else:
                response_data = AliceResponse(text="Привет!", tts="Привет!")
        else:
            response_data = pass_if_need(handler, req)

        self.app.logger.info("Response: %s", response_data)
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
            return re.sub(r'[^\w\s]', '', s).strip()

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
    ) -> bool | typing.Callable:

        return request.session.new
    
    @_handler_type
    def on_ngram(
            self,
            request: AliceRequest,
            synonims: list,
            threshold: float = 0.75,
    ) -> bool | typing.Callable:
        return are_similar(request.command, synonims)
    
    @_handler_type
    def on_exact(
            self,
            request: AliceRequest,
            text: str,
    ) -> bool | typing.Callable:

        return request.original_utterance == text