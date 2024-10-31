import typing

type Scope = typing.MutableMapping[str, typing.Any]
type Message = typing.MutableMapping[str, typing.Any]

type Receive = typing.Callable[[], typing.Awaitable[Message]]
type Send = typing.Callable[[Message], typing.Awaitable[None]]
