from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

JSONDict = Dict[str, Any]


def _ensure_dict(value: Any) -> JSONDict:
    if isinstance(value, dict):
        return value
    return {}


def _maybe_dict(value: Any) -> Optional[JSONDict]:
    return value if isinstance(value, dict) else None


def _deep_copy_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _deep_copy_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_deep_copy_json(v) for v in value]
    return value


@dataclass
class YandexMetaInterfaces:
    screen: Optional[JSONDict] = None
    account_linking: Optional[JSONDict] = None
    audio_player: Optional[JSONDict] = None
    extra: JSONDict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "YandexMetaInterfaces":
        data = data or {}
        known = {"screen", "account_linking", "audio_player"}
        return cls(
            screen=_maybe_dict(data.get("screen")),
            account_linking=_maybe_dict(data.get("account_linking")),
            audio_player=_maybe_dict(data.get("audio_player")),
            extra={k: _deep_copy_json(v) for k, v in data.items() if k not in known},
        )


@dataclass
class YandexMeta:
    locale: Optional[str] = None
    timezone: Optional[str] = None
    client_id: Optional[str] = None
    interfaces: Optional[YandexMetaInterfaces] = None
    extra: JSONDict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "YandexMeta":
        data = data or {}
        known = {"locale", "timezone", "client_id", "interfaces"}
        return cls(
            locale=data.get("locale"),
            timezone=data.get("timezone"),
            client_id=data.get("client_id"),
            interfaces=YandexMetaInterfaces.from_dict(data.get("interfaces"))
            if isinstance(data.get("interfaces"), dict)
            else None,
            extra={k: _deep_copy_json(v) for k, v in data.items() if k not in known},
        )


@dataclass
class YandexSessionUser:
    user_id: Optional[str] = None
    access_token: Optional[str] = None
    extra: JSONDict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "YandexSessionUser":
        data = data or {}
        known = {"user_id", "access_token"}
        return cls(
            user_id=data.get("user_id"),
            access_token=data.get("access_token"),
            extra={k: _deep_copy_json(v) for k, v in data.items() if k not in known},
        )


@dataclass
class YandexSessionApplication:
    application_id: Optional[str] = None
    extra: JSONDict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "YandexSessionApplication":
        data = data or {}
        known = {"application_id"}
        return cls(
            application_id=data.get("application_id"),
            extra={k: _deep_copy_json(v) for k, v in data.items() if k not in known},
        )


@dataclass
class YandexSession:
    message_id: Optional[int] = None
    session_id: Optional[str] = None
    skill_id: Optional[str] = None
    user_id: Optional[str] = None
    user: Optional[YandexSessionUser] = None
    application: Optional[YandexSessionApplication] = None
    new: Optional[bool] = None
    extra: JSONDict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "YandexSession":
        data = data or {}
        known = {
            "message_id",
            "session_id",
            "skill_id",
            "user_id",
            "user",
            "application",
            "new",
        }
        return cls(
            message_id=data.get("message_id"),
            session_id=data.get("session_id"),
            skill_id=data.get("skill_id"),
            user_id=data.get("user_id"),
            user=YandexSessionUser.from_dict(data.get("user")) if isinstance(data.get("user"), dict) else None,
            application=YandexSessionApplication.from_dict(data.get("application"))
            if isinstance(data.get("application"), dict)
            else None,
            new=data.get("new"),
            extra={k: _deep_copy_json(v) for k, v in data.items() if k not in known},
        )


@dataclass
class YandexState:
    session: Optional[JSONDict] = None
    user: Optional[JSONDict] = None
    application: Optional[JSONDict] = None
    extra: JSONDict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "YandexState":
        data = data or {}
        known = {"session", "user", "application"}
        return cls(
            session=_maybe_dict(data.get("session")),
            user=_maybe_dict(data.get("user")),
            application=_maybe_dict(data.get("application")),
            extra={k: _deep_copy_json(v) for k, v in data.items() if k not in known},
        )


@dataclass
class YandexNluTokens:
    start: int
    end: int

    @classmethod
    def from_dict(cls, data: Any) -> Optional["YandexNluTokens"]:
        if not isinstance(data, dict):
            return None
        if "start" not in data or "end" not in data:
            return None
        return cls(start=int(data["start"]), end=int(data["end"]))


@dataclass
class YandexNluEntity:
    tokens: Optional[YandexNluTokens] = None
    type: Optional[str] = None
    value: Any = None
    extra: JSONDict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "YandexNluEntity":
        data = data or {}
        known = {"tokens", "type", "value"}
        return cls(
            tokens=YandexNluTokens.from_dict(data.get("tokens")),
            type=data.get("type"),
            value=_deep_copy_json(data.get("value")),
            extra={k: _deep_copy_json(v) for k, v in data.items() if k not in known},
        )


@dataclass
class YandexNlu:
    tokens: List[str] = field(default_factory=list)
    entities: List[YandexNluEntity] = field(default_factory=list)
    intents: JSONDict = field(default_factory=dict)
    extra: JSONDict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "YandexNlu":
        data = data or {}
        known = {"tokens", "entities", "intents"}
        return cls(
            tokens=list(data.get("tokens") or []),
            entities=[
                YandexNluEntity.from_dict(item)
                for item in (data.get("entities") or [])
                if isinstance(item, dict)
            ],
            intents=_ensure_dict(data.get("intents")),
            extra={k: _deep_copy_json(v) for k, v in data.items() if k not in known},
        )


@dataclass
class YandexRequestMarkup:
    dangerous_context: Optional[bool] = None
    extra: JSONDict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "YandexRequestMarkup":
        data = data or {}
        known = {"dangerous_context"}
        return cls(
            dangerous_context=data.get("dangerous_context"),
            extra={k: _deep_copy_json(v) for k, v in data.items() if k not in known},
        )


@dataclass
class YandexRequestBody:
    type: Optional[str] = None
    command: Optional[str] = None
    original_utterance: Optional[str] = None
    payload: Optional[JSONDict] = None
    show_type: Optional[str] = None
    markup: Optional[YandexRequestMarkup] = None
    nlu: Optional[YandexNlu] = None
    extra: JSONDict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "YandexRequestBody":
        data = data or {}
        known = {
            "type",
            "command",
            "original_utterance",
            "payload",
            "show_type",
            "markup",
            "nlu",
        }
        return cls(
            type=data.get("type"),
            command=data.get("command"),
            original_utterance=data.get("original_utterance"),
            payload=_maybe_dict(data.get("payload")),
            show_type=data.get("show_type"),
            markup=YandexRequestMarkup.from_dict(data.get("markup")) if isinstance(data.get("markup"), dict) else None,
            nlu=YandexNlu.from_dict(data.get("nlu")) if isinstance(data.get("nlu"), dict) else None,
            extra={k: _deep_copy_json(v) for k, v in data.items() if k not in known},
        )

    @property
    def is_simple_utterance(self) -> bool:
        return self.type == "SimpleUtterance"

    @property
    def is_button_pressed(self) -> bool:
        return self.type == "ButtonPressed"

    @property
    def is_show_pull(self) -> bool:
        return self.type == "Show.Pull"


@dataclass
class AliceRequest:
    meta: Optional[YandexMeta] = None
    request: Optional[YandexRequestBody] = None
    session: Optional[YandexSession] = None
    state: Optional[YandexState] = None
    version: Optional[str] = None
    extra: JSONDict = field(default_factory=dict)
    raw: JSONDict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AliceRequest":
        if not isinstance(data, dict):
            raise TypeError("from_dict ожидает dict")

        # Show.Pull иногда приходит как {"body": {...}}
        root = data.get("body") if isinstance(data.get("body"), dict) else data

        known = {"meta", "request", "session", "state", "version"}
        return cls(
            meta=YandexMeta.from_dict(root.get("meta")) if isinstance(root.get("meta"), dict) else None,
            request=YandexRequestBody.from_dict(root.get("request")) if isinstance(root.get("request"), dict) else None,
            session=YandexSession.from_dict(root.get("session")) if isinstance(root.get("session"), dict) else None,
            state=YandexState.from_dict(root.get("state")) if isinstance(root.get("state"), dict) else None,
            version=root.get("version"),
            extra={k: _deep_copy_json(v) for k, v in root.items() if k not in known},
            raw=_deep_copy_json(data),
        )

    @classmethod
    def from_json(cls, data: str, encoding: str = "utf-8") -> "AliceRequest":
        if not isinstance(data, str):
            raise TypeError("from_json ожидает строку JSON")
        parsed = json.loads(data)
        if not isinstance(parsed, dict):
            raise ValueError("JSON должен содержать объект верхнего уровня")
        return cls.from_dict(parsed)

    @classmethod
    def from_flask_request(cls, flask_request: Any) -> "AliceRequest":
        """
        Поддерживает:
        - flask.request
        - werkzeug request
        - любой объект с get_json()
        - любой объект с data / get_data()
        """
        if hasattr(flask_request, "get_json"):
            try:
                parsed = flask_request.get_json(silent=True)
                if isinstance(parsed, dict):
                    return cls.from_dict(parsed)
            except Exception:
                pass

        raw_bytes = None

        if hasattr(flask_request, "get_data"):
            try:
                raw_bytes = flask_request.get_data()
            except Exception:
                raw_bytes = None

        if raw_bytes is None and hasattr(flask_request, "data"):
            raw_bytes = flask_request.data

        if raw_bytes is None:
            raise ValueError("Не удалось извлечь тело запроса из Flask request")

        if isinstance(raw_bytes, bytes):
            text = raw_bytes.decode("utf-8")
        else:
            text = str(raw_bytes)

        return cls.from_json(text)

    def to_dict(self) -> JSONDict:
        return _deep_copy_json(self.raw)

    @property
    def request_type(self) -> Optional[str]:
        return self.request.type if self.request else None

    @property
    def is_simple_utterance(self) -> bool:
        return bool(self.request and self.request.is_simple_utterance)

    @property
    def is_button_pressed(self) -> bool:
        return bool(self.request and self.request.is_button_pressed)

    @property
    def is_show_pull(self) -> bool:
        return bool(self.request and self.request.is_show_pull)

    @property
    def command(self) -> Optional[str]:
        return self.request.command if self.request else None

    @property
    def original_utterance(self) -> Optional[str]:
        return self.request.original_utterance if self.request else None

    @property
    def payload(self) -> Optional[JSONDict]:
        return self.request.payload if self.request else None

    @property
    def session_state(self) -> Optional[JSONDict]:
        return self.state.session if self.state else None

    @property
    def user_state(self) -> Optional[JSONDict]:
        return self.state.user if self.state else None

    @property
    def application_state(self) -> Optional[JSONDict]:
        return self.state.application if self.state else None

    @property
    def locale(self) -> Optional[str]:
        return self.meta.locale if self.meta else None

    @property
    def timezone(self) -> Optional[str]:
        return self.meta.timezone if self.meta else None

    @property
    def has_screen(self) -> bool:
        return bool(self.meta and self.meta.interfaces and self.meta.interfaces.screen is not None)

    @property
    def has_account_linking(self) -> bool:
        return bool(self.meta and self.meta.interfaces and self.meta.interfaces.account_linking is not None)

    @property
    def has_audio_player(self) -> bool:
        return bool(self.meta and self.meta.interfaces and self.meta.interfaces.audio_player is not None)

    def __repr__(self) -> str:
        return (
            "YandexDialogIncomingRequest("
            f"type={self.request_type!r}, "
            f"locale={self.locale!r}, "
            f"session_id={self.session.session_id if self.session else None!r}, "
            f"new={self.session.new if self.session else None!r})"
        )


def _clean_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Удаляет None из словаря рекурсивно."""
    result = {}
    for key, value in data.items():
        if value is None:
            continue
        if isinstance(value, dict):
            value = _clean_dict(value)
        elif isinstance(value, list):
            value = [
                _clean_dict(item) if isinstance(item, dict) else item
                for item in value
                if item is not None
            ]
        result[key] = value
    return result


@dataclass
class YandexButton:
    title: str
    payload: Optional[JSONDict] = None
    url: Optional[str] = None
    hide: bool = False

    def to_dict(self) -> JSONDict:
        data = {
            "title": self.title,
            "payload": self.payload if self.payload is not None else {},
            "url": self.url,
            "hide": self.hide,
        }
        return _clean_dict(data)


@dataclass
class YandexCardButton:
    text: str
    url: Optional[str] = None
    payload: Optional[JSONDict] = None

    def to_dict(self) -> JSONDict:
        data = {
            "text": self.text,
            "url": self.url,
            "payload": self.payload if self.payload is not None else {},
        }
        return _clean_dict(data)


@dataclass
class YandexBigImageCard:
    image_id: str
    title: str
    description: Optional[str] = None
    button: Optional[YandexCardButton] = None
    type: str = field(init=False, default="BigImage")

    def to_dict(self) -> JSONDict:
        data = {
            "type": self.type,
            "image_id": self.image_id,
            "title": self.title,
            "description": self.description,
            "button": self.button.to_dict() if self.button else None,
        }
        return _clean_dict(data)


@dataclass
class YandexImageItem:
    image_id: str
    title: str
    description: Optional[str] = None
    button: Optional[YandexCardButton] = None

    def to_dict(self) -> JSONDict:
        data = {
            "image_id": self.image_id,
            "title": self.title,
            "description": self.description,
            "button": self.button.to_dict() if self.button else None,
        }
        return _clean_dict(data)


@dataclass
class YandexItemsListCard:
    items: List[YandexImageItem]
    header_text: Optional[str] = None
    footer_text: Optional[str] = None
    footer_button: Optional[YandexCardButton] = None
    type: str = field(init=False, default="ItemsList")

    def to_dict(self) -> JSONDict:
        data = {
            "type": self.type,
            "header": {"text": self.header_text} if self.header_text else None,
            "items": [item.to_dict() for item in self.items],
            "footer": (
                {
                    "text": self.footer_text,
                    "button": self.footer_button.to_dict() if self.footer_button else None,
                }
                if self.footer_text or self.footer_button
                else None
            ),
        }
        return _clean_dict(data)


@dataclass
class YandexImageGalleryCard:
    items: List[YandexImageItem]
    type: str = field(init=False, default="ImageGallery")

    def to_dict(self) -> JSONDict:
        data = {
            "type": self.type,
            "items": [item.to_dict() for item in self.items],
        }
        return _clean_dict(data)


@dataclass
class YandexShowItemMeta:
    content_id: str
    publication_date: str
    title: Optional[str] = None
    title_tts: Optional[str] = None
    expiration_date: Optional[str] = None

    def to_dict(self) -> JSONDict:
        data = {
            "content_id": self.content_id,
            "title": self.title,
            "title_tts": self.title_tts,
            "publication_date": self.publication_date,
            "expiration_date": self.expiration_date,
        }
        return _clean_dict(data)


class AliceResponse:
    """
    Универсальный builder для ответов Яндекс.Диалогов.
    """

    PROTOCOL_VERSION = "1.0"

    def __init__(
            self,
            text: str = "",
            tts: str = "",
            end_session: bool = False,
    ) -> None:
        if tts == '':
            tts = text

        self.text = text
        self.tts = tts
        self.end_session = end_session

        self.buttons: List[YandexButton] = []
        self.card: Optional[Union[YandexBigImageCard, YandexItemsListCard, YandexImageGalleryCard, JSONDict]] = None

        self.session_state: Optional[JSONDict] = None
        self.user_state_update: Optional[JSONDict] = None
        self.application_state: Optional[JSONDict] = None

        self.analytics_events: List[JSONDict] = []

        self.directives: JSONDict = {}
        self.show_item_meta: Optional[YandexShowItemMeta] = None

    def set_text(self, text: str) -> "AliceResponse":
        self.text = text
        return self

    def set_tts(self, tts: str) -> "AliceResponse":
        self.tts = tts
        return self

    def set_end_session(self, value: bool) -> "AliceResponse":
        self.end_session = value
        return self

    def add_button(
            self,
            title: str,
            payload: Optional[JSONDict] = None,
            url: Optional[str] = None,
            hide: bool = False,
    ) -> "AliceResponse":
        self.buttons.append(YandexButton(title=title, payload=payload, url=url, hide=hide))
        return self

    def clear_buttons(self) -> "AliceResponse":
        self.buttons = []
        return self

    def set_big_image(
            self,
            image_id: str,
            title: str,
            description: Optional[str] = None,
            button_text: Optional[str] = None,
            button_url: Optional[str] = None,
            button_payload: Optional[JSONDict] = None,
    ) -> "AliceResponse":
        button = None
        if button_text is not None:
            button = YandexCardButton(text=button_text, url=button_url, payload=button_payload)
        self.card = YandexBigImageCard(
            image_id=image_id,
            title=title,
            description=description,
            button=button,
        )
        return self

    def set_items_list(
            self,
            items: List[Dict[str, Any]],
            header_text: Optional[str] = None,
            footer_text: Optional[str] = None,
            footer_button_text: Optional[str] = None,
            footer_button_url: Optional[str] = None,
            footer_button_payload: Optional[JSONDict] = None,
    ) -> "AliceResponse":
        parsed_items: List[YandexImageItem] = []
        for item in items:
            button = item.get("button")
            parsed_button = None
            if isinstance(button, dict):
                parsed_button = YandexCardButton(
                    text=button.get("text", ""),
                    url=button.get("url"),
                    payload=button.get("payload"),
                )
            parsed_items.append(
                YandexImageItem(
                    image_id=item["image_id"],
                    title=item["title"],
                    description=item.get("description"),
                    button=parsed_button,
                )
            )

        footer_button = None
        if footer_button_text is not None:
            footer_button = YandexCardButton(
                text=footer_button_text,
                url=footer_button_url,
                payload=footer_button_payload,
            )

        self.card = YandexItemsListCard(
            items=parsed_items,
            header_text=header_text,
            footer_text=footer_text,
            footer_button=footer_button,
        )
        return self

    def set_image_gallery(self, items: List[Dict[str, Any]]) -> "AliceResponse":
        parsed_items: List[YandexImageItem] = []
        for item in items:
            button = item.get("button")
            parsed_button = None
            if isinstance(button, dict):
                parsed_button = YandexCardButton(
                    text=button.get("text", ""),
                    url=button.get("url"),
                    payload=button.get("payload"),
                )
            parsed_items.append(
                YandexImageItem(
                    image_id=item["image_id"],
                    title=item["title"],
                    description=item.get("description"),
                    button=parsed_button,
                )
            )

        self.card = YandexImageGalleryCard(items=parsed_items)
        return self

    def set_card_raw(self, card: JSONDict) -> "AliceResponse":
        """
        Позволяет передать любую карточку как есть.
        Полезно для расширений или нестандартных сценариев.
        """
        self.card = card
        return self

    def set_session_state(self, value: JSONDict) -> "AliceResponse":
        self.session_state = value
        return self

    def set_user_state_update(self, value: JSONDict) -> "AliceResponse":
        self.user_state_update = value
        return self

    def set_application_state(self, value: JSONDict) -> "AliceResponse":
        self.application_state = value
        return self

    def add_analytics_event(
            self,
            name: str,
            value: Optional[JSONDict] = None,
    ) -> "AliceResponse":
        event: JSONDict = {"name": name}
        if value is not None:
            event["value"] = value
        self.analytics_events.append(event)
        return self

    def clear_analytics(self) -> "AliceResponse":
        self.analytics_events = []
        return self

    def start_account_linking(self) -> "AliceResponse":
        self.directives["start_account_linking"] = {}
        return self

    def set_directive_raw(self, name: str, value: Any = None) -> "AliceResponse":
        self.directives[name] = {} if value is None else value
        return self

    def set_show_item_meta(
            self,
            content_id: str,
            publication_date: str,
            title: Optional[str] = None,
            title_tts: Optional[str] = None,
            expiration_date: Optional[str] = None,
    ) -> "AliceResponse":
        self.show_item_meta = YandexShowItemMeta(
            content_id=content_id,
            publication_date=publication_date,
            title=title,
            title_tts=title_tts,
            expiration_date=expiration_date,
        )
        return self

    def to_dict(self) -> JSONDict:
        response: JSONDict = {
            "text": self.text,
            "tts": self.tts,
            "end_session": self.end_session,
        }

        if self.card is not None:
            if hasattr(self.card, "to_dict"):
                response["card"] = self.card.to_dict()
            else:
                response["card"] = self.card

        if self.buttons:
            response["buttons"] = [button.to_dict() for button in self.buttons]

        if self.directives:
            response["directives"] = self.directives

        if self.show_item_meta is not None:
            response["show_item_meta"] = self.show_item_meta.to_dict()

        payload: JSONDict = {
            "response": _clean_dict(response),
            "version": self.PROTOCOL_VERSION,
        }

        if self.session_state is not None:
            payload["session_state"] = self.session_state
        if self.user_state_update is not None:
            payload["user_state_update"] = self.user_state_update
        if self.application_state is not None:
            payload["application_state"] = self.application_state
        if self.analytics_events:
            payload["analytics"] = {"events": self.analytics_events}

        return _clean_dict(payload)

    def to_json(self, ensure_ascii: bool = False, indent: Optional[int] = None) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)

    def to_flask_response(self, status_code: int = 200):
        """
        Возвращает Flask Response с JSON-телом.
        """
        from flask import Response

        return Response(
            self.to_json(ensure_ascii=False),
            status=status_code,
            mimetype="application/json; charset=utf-8",
        )

    @classmethod
    def simple(cls, text: str, tts: Optional[str] = None, end_session: bool = False) -> "AliceResponse":
        return cls(text=text, tts=tts or text, end_session=end_session)