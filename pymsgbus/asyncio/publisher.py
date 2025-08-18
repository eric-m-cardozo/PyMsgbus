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
from asyncio import gather
from pymsgbus.subscriber import Subscriber

class Publisher:
    """
    A **publisher** is a component that sends messages to one or more **subscribers**. Unlike a **producer**,
    it's the **publisher**'s responsibility to route the messages to the corresponding **subscribers**.
    
    Methods:
        register: Registers one or more **subscribers** to the **publisher**.
        publish: Asynchronously publishes a message to all **subscribers** subscribed to the topic. 
    """
    def __init__(self) -> None:
        self.subscribers = list[Subscriber]()

    async def publish(self, message: Any, topic: str) -> None:
        """
        Asynchronously publishes a message to all subscribers based on the topic.

        Args:
            message (Any): The message to publish.
            topic (str): The topic to publish the message to.
        """ 
        await gather(*(subscriber.receive(message, topic) for subscriber in self.subscribers))

    def register(self, *subscribers: Subscriber) -> None:
        """
        Registers one or more **subscribers** to the **publisher**.
        """
        self.subscribers.extend(subscribers)
