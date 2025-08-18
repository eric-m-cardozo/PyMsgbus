# Copyright 2025 Eric Hermosis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You can obtain a copy of the License at:
# 
#     http://www.apache.org/licenses/LICENSE-2.0
#
# This software is distributed "AS IS," without warranties or conditions.
# See the License for specific terms.

from asyncio import to_thread
from re import sub
from typing import Any
from collections.abc import Callable
from pymsgbus.depends import inject, Provider
from pymsgbus.depends import Depends as Depends
from inspect import iscoroutinefunction

class Service:
    """
    A **service** is the technical authority for a business capability. And it is the exclusive
    owner of a certain subset of the business data.  It centralizes and organizes domain
    operations, enforces business rules, and coordinates workflows. 

    The `Service` serves as an entry point for the service layer and provides a simple way to
    build stateless logic for executing domain operations.

    A **service** should be modeled with **ubiquitous language**. This means that the names of handler
    functions should reflect the domain operations that the service is responsible for. Keep
    this in mind when naming the functions that will be registered as handlers, since the `Service`
    class provides a method to call the handlers by their registered name. This is useful for example 
    when building REST APIs with Command Query Segregation (CQS) and you want to invoke a handler based
    on the action they perfom (aka. The handler's name).

    A naming generator can be provided to the `Service` constructor in order to customize the function names
    to the ubiquitous language of the domain. The default generator transforms the function name from snake_case
    to kebab-case.

    Methods: 
        handler:
            Decorator for registering a function as a handler.

        execute:
            Executes the handler associated with a given action.
    """
    def __init__(
        self,
        provider: Provider | None = None,
        *,
        generator: Callable[[str], str] = lambda name: sub(r'_', '-', name)
    ):
        self.handlers = dict[str, Callable[..., Any]]()
        self.generator = generator
        self.provider = provider or Provider()

    @property
    def dependency_overrides(self) -> dict:
        """
        Returns:
            dict: A dictionary of the dependency overrides.
        """
        return self.provider.dependency_overrides

    def override(self, dependency: Callable, implementation: Callable):
        """
        Overrides a dependency with a new implementation.
        """
        self.dependency_overrides[dependency] = implementation

    def handler(self, wrapped: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorator to register a function as a handler, injecting dependencies.

        Args:
            wrapped: The handler function.

        Returns:
            The wrapped and injected handler.
        """
        injected = inject(self.provider)(wrapped)
        self.handlers[self.generator(wrapped.__name__)] = injected
        return injected

    async def execute(self, action: str, *args: Any, **kwargs: dict[str, Any]) -> Any:
        """
        Asynchronously executes the handler registered under the given action.

        Automatically awaits if the handler is a coroutine function.

        Args:
            action: The handler name to invoke.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Raises:
            KeyError: If no handler is registered under the action.

        Returns:
            The result of the handler, awaited if needed.
        """
        handler = self.handlers.get(action)
        if not handler:
            raise KeyError(f'Handler not found for action: {action}')
        
        if iscoroutinefunction(handler):
            return await handler(*args, **kwargs)
        return await to_thread(handler, *args, **kwargs)