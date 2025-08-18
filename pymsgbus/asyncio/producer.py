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

from typing import Any
from dataclasses import dataclass
from asyncio import gather
from pymsgbus.asyncio import Consumer

class Producer:
    """
    A producer is responsible for producing the **events** that will be consumed by **consumers**.
    This async version supports awaiting consumer event handling.

    Methods:
        register: Registers a consumer to the producer.
        dispatch: Asynchronously dispatches an event to all registered consumers.
    """
    def __init__(self):
        self.consumers: list[Consumer] = []

    def register(self, *consumers: Consumer):
        """
        Registers a sequence of consumers to the producer. The producer will dispatch events to all registered
        consumers.
        """
        self.consumers.extend(consumers)

    async def dispatch(self, event: Any):
        """
        Asynchronously dispatches an event to all registered consumers. The event will be consumed by the consumers
        that have registered handlers for the event type.

        Args:
            event (Any): The event to dispatch.
        """
        await gather(*(consumer.consume(event) for consumer in self.consumers))
 