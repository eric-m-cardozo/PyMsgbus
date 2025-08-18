# Copyright 2025 Eric Hermosis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You can obtain a copy of the License at:
# 
#     http://www.apache.org/licenses/LICENSE-2.0
#
# This software is distributed "AS IS," without warranties or conditions.
# See the License for specific terms.  

from typing import Any
from pymsgbus.subscriber import Subscriber

class Publisher:
    """
    A **publisher** is a component that sends messages to one or more **subscribers**. Unlike a **producer**
    It's the **publisher**'s responsibility to route the messages to the corresponding **subscribers**.
    
    Methods:
        register: Registers one or more **subscribers** to the **publisher**.
        publish: Publishes a message to one or more **subscribers** based on the topic. 

    Example:
        ```python	
        from pymsgbus import Depends
        from pymsgbus import Subscriber
        from pymsgbus import Publisher

        subscriber = Subscriber()
        metricsdb = []

        def metrics():
            return metricsdb

        @subscriber.subscribe('loss', 'accuracy')
        def store_metric(metric, metrics: list = Depends(metrics)):
            metrics.append(metric)

        @subscriber.subscribe('accuracy')
        def on_accuracy_to_high(metric):
            if metric > 0.99:
                raise StopIteration
            
        publisher = Publisher()
        publisher.register(subscriber)

        publisher.publish(0.1, 'loss')
        publisher.publish(0.9, 'accuracy')
        assert metricsdb == [0.1, 0.9]

        try:
            publisher.publish(1.0, 'accuracy')
        except StopIteration:
            print("Early stopping") 
        ```
    """
    def __init__(self) -> None:
        self.subscribers = list[Subscriber]()

    def publish(self, message: Any, topic: str) -> None:
        """
        Publishes a message to one or more **subscribers** based on the topic.

        Args:
            message (Any): The message to publish.
            topic (str): The topic to publish the message to.
        """
        for subscriber in self.subscribers:
            subscriber.receive(message, topic)

    def register(self, *subscribers: Subscriber) -> None:
        """
        Registers one or more **subscribers** to the **publisher**.
        """
        for subscriber in subscribers:
            self.subscribers.append(subscriber)