import json
import re
from http import HTTPStatus, HTTPMethod
from json.decoder import JSONDecodeError
import hashlib

import uvicorn

from constants import REGULAR_URL
from db import DataBase
from throttlings import Throttling
from typings import Scope, Receive, Send


class ShortLinksHandler:
    """Сервис по созданию коротких ссылок.

    Attributes:
        db (DataBase): объект базы данных.
        throttling (Throttling): объект троттлинга запросов.
        response_start (str): тип старта ответа.
        response_body (str): тип тела ответа.
    """

    db = DataBase()
    throttling = Throttling()
    response_start = "http.response.start"
    response_body = "http.response.body"

    async def _page_404(self, send: Send) -> None:
        """Ответ при отсутсвии страницы.

        send (Send): канал исходящих сообщений сервера.
        """
        await send(
            {
                "type": self.response_start,
                "status": HTTPStatus.NOT_FOUND,
            }
        )
        await send(
            {
                "type": self.response_body,
            }
        )

    async def _method_not_allowed(self, send: Send) -> None:
        """Ответ при запрещённом методе.

        send (Send): канал исходящих сообщений сервера.
        """
        await send(
            {
                "type": self.response_start,
                "status": HTTPStatus.METHOD_NOT_ALLOWED,
            }
        )
        await send(
            {
                "type": self.response_body,
            }
        )

    async def _too_many_requests(self, send: Send) -> None:
        """Ответ при временной блокировки пользователя.

        send (Send): канал исходящих сообщений сервера.
        """
        await send(
            {
                "type": self.response_start,
                "status": HTTPStatus.TOO_MANY_REQUESTS,
            }
        )
        await send(
            {
                "type": self.response_body,
            }
        )

    async def _response_error(
        self,
        errors: dict[str, str],
        send: Send,
    ) -> None:
        """Ответ сервера при ошибке.

        Args:
            errors (dict[str, str]): ошибки.
            send (Send): канал исходящих сообщений сервера.
        """
        body = json.dumps(errors).encode("utf-8")
        await send(
            {
                "type": self.response_start,
                "status": HTTPStatus.BAD_REQUEST,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode()),
                ],
            }
        )
        await send(
            {
                "type": self.response_body,
                "body": body,
            }
        )

    async def _response_create_short_link(
        self,
        scope: Scope,
        short_link: str,
        send: Send,
    ) -> None:
        """Ответ сервера при создании короткой ссылки.

        Args:
            scope (Scope): данные по входящему соединению сервера.
            short_link (str): короткая ссылка.
            send (Send): канал исходящих сообщений сервера.
        """
        headers = dict(scope["headers"])
        short_link = f'{scope['scheme']}://{headers[b'host'].decode()}/{short_link}'
        body = json.dumps({"short_link": short_link}).encode("utf-8")
        await send(
            {
                "type": self.response_start,
                "status": HTTPStatus.CREATED,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode()),
                ],
            }
        )
        await send(
            {
                "type": self.response_body,
                "body": body,
            }
        )

    async def _redirect_to_original_url(
        self,
        original_url: str,
        send: Send,
    ) -> None:
        """Редирект на оригинальную ссылку.

        Args:
            original_url (str): оригинальная ссылка.
            send (Send): канал исходящих сообщений сервера.
        """
        await send(
            {
                "type": self.response_start,
                "status": HTTPStatus.FOUND,
                "headers": [
                    (b"location", original_url.encode()),
                ],
            }
        )
        await send(
            {
                "type": self.response_body,
            }
        )

    def _get_short_link(self, url: str) -> tuple[str, bool]:
        """Отдаёт короткую ссылку.

        Args:
            url (str): оригинальная ссылка.

        Returns:
            tuple[str, bool]: короткая ссылка, флаг создания.
        """
        short_link = self.db._get_short_link(url)
        if short_link:
            return short_link, False
        hash_bytes = hashlib.md5(url.encode("utf-8")).digest()
        return hash_bytes.hex(), True

    def _get_original_url(self, scope: Scope) -> str | None:
        """Отдаёт оригинальную ссылку.

        Args:
            scope (Scope): данные по входящему соединению сервера.

        Returns:
            str | None: оригинальная ссылка.
        """
        return self.db.get_original_url(scope["path"].strip("/"))

    def _create_short_link(self, data: dict) -> str:
        """Создание короткой ссылки.

        Args:
            data (dict): данные из POST-запроса.

        Returns:
            str: короткая ссылка.
        """
        url = data["url"]
        short_link, is_create = self._get_short_link(url)
        if not is_create:
            return short_link
        self.db.save_short_link(url, short_link)
        return short_link

    async def _get_body(self, receive: Receive) -> bytes:
        """Возвращает тело запроса.

        Args:
            receive(Receive): канал входящих сообщений сервера.

        Returns:
            bytes: тело запроса.
        """
        body = b""

        while True:
            message = await receive()
            body += message.get("body", b"")
            if message.get("more_body", False):
                continue
            break
        return body

    async def _validate_post_data_short_link(self, receive: Receive) -> dict:
        """Валидирует данные POST-запроса создания короткой ссылки.

        Args:
            receive(Receive): канал входящих сообщений сервера.

        Returns:
            dict: данные POST-запроса.
        """
        post_data = json.loads(await self._get_body(receive))
        url = post_data.get("url")
        pattern = re.compile(REGULAR_URL)
        if not url:
            raise ValueError({"url": "Обязательное поле."})
        elif not isinstance(url, str):
            raise ValueError({"url": "Поле должно быть тип строкой."})
        elif not re.match(pattern, url):
            raise ValueError({"url": "Поле должно быть ссылкой."})
        return post_data

    async def _view_create_short_link(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        """View создания короткой ссылки.

        Args:
            scope (Scope): данные по входящему соединению сервера.
            receive(Receive): канал входящих сообщений сервера.
            send (Send): канал исходящих сообщений сервера.
        """
        data = await self._validate_post_data_short_link(receive)
        short_link = self._create_short_link(data)
        await self._response_create_short_link(scope, short_link, send)

    async def _view_redirect_by_short_link(
        self,
        scope: Scope,
        send: Send,
    ) -> None:
        """View редиректа по короткой ссылке.

        Args:
            scope (Scope): данные по входящему соединению сервера.
            send (Send): канал исходящих сообщений сервера.
        """
        is_blocked = self.throttling.refresh_history(scope["client"][0])
        if is_blocked:
            await self._too_many_requests(send)
            return
        original_url = self._get_original_url(scope)
        if original_url:
            await self._redirect_to_original_url(original_url, send)
        else:
            await self._page_404(send)

    async def _router(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        """Маршрутизация запросов.

        Args:
            scope (Scope): данные по входящему соединению сервера.
            receive(Receive): канал входящих сообщений сервера.
            send (Send): канал исходящих сообщений сервера.
        """
        match (scope["path"], scope["method"]):
            case ("/short-link" | "/short-link/", HTTPMethod.POST):
                await self._view_create_short_link(scope, receive, send)
            case ("/short-link" | "/short-link/", _):
                await self._method_not_allowed(send)
            case (_, HTTPMethod.GET):
                await self._view_redirect_by_short_link(scope, send)
            case _:
                await self._method_not_allowed(send)

    async def _handler(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        """Обработчик запросов.

        Args:
            scope (Scope): данные по входящему соединению сервера.
            receive(Receive): канал входящих сообщений сервера.
            send (Send): канал исходящих сообщений сервера.
        """
        try:
            await self._router(scope, receive, send)
        except JSONDecodeError:
            await self._response_error(
                {"non_field": "Не валидная структура JSON."},
                send,
            )
        except ValueError as e:
            await self._response_error(e.args[0], send)

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        """
        Args:
            scope (Scope): данные по входящему соединению сервера.
            receive(Receive): канал входящих сообщений сервера.
            send (Send): канал исходящих сообщений сервера.
        """
        assert scope["type"] == "http"
        await self._handler(scope, receive, send)


app = ShortLinksHandler()

if __name__ == "__main__":
    uvicorn.run(app)
