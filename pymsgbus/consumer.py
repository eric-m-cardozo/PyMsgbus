# Copyright 2025 Eric M. Cardozo (Eric Hermosis)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You can obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# This software is distributed "AS IS," without warranties or conditions.
# See the License for specific terms.

from re import sub
from inspect import signature
from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import Union
from typing import get_args
from typing import get_origin

from pymsgbus.depends import Depends as Depends
from pymsgbus.depends import Provider
from pymsgbus.depends import inject
 
def event(cls: type):
    """
    A decorator to define an Event message.

    Args:
        cls (type): The occurrence of something that happened represented by a class.

    Returns:
        type: A slotted dataclass representing the event.
    """
    return dataclass(slots=True)(cls)


class Consumer:
    """
    A **consumer** is a component that listens for and reacts to ocurrences in a **bounded context**.
    """

    def __init__(
        self,
        provider: Provider | None = None,
        *,
        generator: Callable[[str], str] = lambda name: sub(r"(?<!^)(?=[A-Z])", "-", name).lower(),
    ):
        self.handlers = dict[str, list[Callable[[Any], None]]]()
        self.types = dict[str, Any]()
        self.generator = generator
        self.provider = provider or Provider()

    @property
    def dependency_overrides(self) -> dict:
        """
        Returns the dependency overrides for the consumer.

        Returns:
            dict: A dictionary of the dependency map.
        """
        return self.provider.dependency_overrides

    def override(self, dependency: Callable, implementation: Callable):
        """
        Overrides a dependency with an implementation.

        Args:
            dependency (Callable): The dependency function to override.
            implementation (Callable): The implementation.
        """
        self.dependency_overrides[dependency] = implementation

    def register(self, annotation: Any, handler: Callable[..., None]) -> Callable[..., None]:
        """
        Registers an event type and its corresponding handler function.

        Generic aliases are normalized to their origin type and union types
        are recursively expanded so the handler is registered for each event.

        Args:
            annotation (Any): The event annotation to be registered.
            handler (Callable[..., None]): The handler function.

        Returns:
            Callable[..., None]: The injected handler.
        """
        origin = get_origin(annotation)

        if origin is Union:
            for argument in get_args(annotation):
                self.register(argument, handler)
            return handler

        if origin is not None:
            return self.register(origin, handler)

        key = self.generator(annotation.__name__)
        self.types[key] = annotation

        injected = inject(self.provider)(handler)
        self.handlers.setdefault(key, []).append(injected)
        return injected

    def handler(self, wrapped: Callable[..., None]) -> Callable[..., None]:
        """
        Decorator for registering a handler function.
        """
        function_signature = signature(wrapped)
        parameter = next(iter(function_signature.parameters.values()))
        return self.register(parameter.annotation, wrapped)

    def consume(self, event: Any):
        """
        Consumes an event by invoking its registered handler functions.

        Args:
            event (Any): The message to consume.
        """
        key = self.generator(event.__class__.__name__)

        for handler in self.handlers.get(key, []):
            handler(event)