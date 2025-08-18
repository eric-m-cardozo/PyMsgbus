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
from pymsgbus.consumer import Consumer

class Producer:
    """
    A producer is responsible for producing the **events** that will be consumed by **consumers**. 
    You can implement a producer implementing the `register` method to register consumers, and 
    some delivery mechanism to deliver the events to them.

    Methods:
        register: Registers a consumer to the producer.
        dispatch: Dispatches an event to all registered consumers.

    Example:
        ```python	  
        from pymsgbus import event

        #creates some events.
        
        @event
        class ModelTrained:
            model: Callable
            metrics: Sequence

        @event
        class ModelEvaluated:
            model: Callable
            metrics: Sequence
        ...

        #Define a consumer.
        from pymsgbus import Consumer, event
        from pymsgbus import Publisher #Not necessary, just to show how to couple stuff.  
    
        consumer = Consumer()
        publisher = Publisher()

        @consumer.handler
        def on_model_iterated(event: ModelTrained | ModelEvaluated):
            for metric in event.metrics:
                publisher.publish(metric, metric['name'])
        ...

        #Late bind the consumer now.    
        producer.register(consumer)
        producer.dispatch(ModelTrained(model, [{'name': 'loss', 'value': 0.1}, {'name': 'accuracy', 'value': 0.9}]))
        producer.dispatch(ModelEvaluated(model, [{'name': 'loss', 'value': 0.1}, {'name': 'accuracy', 'value': 0.9}]))
        ```
    """
    def __init__(self):
        self.consumers = list[Consumer]() 

    def register(self, *consumers: Consumer):
        """
        Registers a sequence of consumers to the producer. The producer will dispatch events to all registered
        consumers.
        """
        for consumer in consumers:
            self.consumers.append(consumer)

    def dispatch(self, event: Any):
        """
        Dispatches an event to all registered consumers. The event will be consumed by the consumers that have
        registered handlers for the event type.

        Args:
            event (Any): The event to dispatch.
        """
        for consumer in self.consumers:
            consumer.consume(event)