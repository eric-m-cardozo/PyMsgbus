# PyMsgbus 

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

pymsgbus is a lightweight, extensible Python message bus framework designed to simplify event-driven and message-driven architectures using **services, producers, consumers, publishers, and subscribers** with dependency injection support. It offers synchronous and asynchronous support for handling messages/events with automatic dependency resolution.

---

## Features

- **Event-driven communication** via Producers and Consumers  
- **Topic-based messaging** with Publishers and Subscribers  
- **Dependency injection** via `Depends` decorator and provider overrides  
- Support for **sync and async** message handling  
- Flexible message routing with automatic handler registration  
- Uses **ubiquitous language** concepts for clear event modeling  
- Supports **generic and union** event types  
- Designed for **domain-driven design (DDD)** and microservices architecture  

---

## Installation

```bash
pip install pymsgbus
```

--- 

## Quickstart
### User Registration with Notifications and Persistence example

Let's create a simple event-driven registration system for users. First, we define a basic `User` entity and some related events.

```python
from dataclasses import dataclass
from pymsgbus import event 
 
@dataclass
class User:
    id: int
    name: str

@event
class Created[T]:  # Generics are supported.
    entity: T

@event
class UpdatedUser:
    entity: User

@event
class RegistrationDone:
    text: str
``` 

#### Declaring Dependencies and Writing Handlers

Next, declare dependencies and write handlers for these events. You can implement them inline or use dependency injection to provide the actual implementations later.

A **Consumer** handles events, while a Subscriber handles messages. Consumers are smart—they determine which events to handle based on type hints. You can group multiple event types for a single consumer using unions, allowing one handler to process several event types. Multiple consumers can handle the same event type as well.

Messages passed to a **Subscriber** are routed via topics. Subscribers can listen to multiple topics, and multiple subscribers can subscribe to the same topic.

```python 
from pymsgbus import Depends
from pymsgbus import Consumer, Subscriber

consumer = Consumer()
subscriber = Subscriber() 
 
def getdb() -> dict:  # Database dependency, to be overridden later
    raise NotImplementedError

def getnfs() -> list:  # Notifications dependency, to be overridden later
    raise NotImplementedError

@consumer.handler
def handle_put(event: Created[User] | UpdatedUser, db: dict = Depends(getdb)):
    db[event.entity.id] = event.entity.name

@consumer.handler
def handle_registered(event: Created[User]):
    consumer.consume(RegistrationDone(f"User {event.entity.id} registered."))

@subscriber.subscribe('notifications')
def handle_notification(msg: RegistrationDone, nfs: list = Depends(getnfs)):
    nfs.append(msg.text)

@consumer.handler
def forward_to_subscriber(event: RegistrationDone):
    subscriber.receive(event, 'notifications')
```

#### Producing events.

Now, write code that produces the events you defined. These can be simple functions or part of a Service. Services also support dependency injection and can be invoked directly or by name.

```python
from pymsgbus import Service
from pymsgbus import Depends

def register(name: str):
    user = User(id=1, name=name)
    consumer.consume(Created(user))

service = Service()

def somedep():
    return "I'm a dependency"

@service.handler
def update(id: int, name: str, dep: str = Depends(somedep)):
    user = User(id=id, name=name)
    consumer.consume(UpdatedUser(user))
    print(dep) #"I'm a dependency"
```

#### Overriding Dependencies and Running the Logic

Finally, override the dependencies with actual infrastructure—in this case, simple Python objects. Then execute your logic; all events and messages will be dispatched and handled by the registered components.

```python

db = {}
nfs = []

def getrealdb():
    return db

def getrealnfs():
    yield nfs #Generators with cleanup supported. 

consumer.override(getdb, getrealdb)
subscriber.override(getnfs, getrealnfs)

register('Alice')
update(1, 'Alice Updated') #or service.execute('update', 1, 'Alice Updated')

assert db[1] == 'Alice Updated'
print(db)
assert nfs == ["User 1 registered."]
print(nfs)
```

#### Late Binding with Producers and Publishers

Consumers and subscribers can also be late-bound using a Producer (for consumers) and a Publisher (for subscribers). Define these alongside your services.

```python
from pymsgbus import Service
from pymsgbus import Depends
from pymsgbus import Producer, Publisher 

service = Service()
producer = Producer()
publisher = Publisher()


def register(name: str):
    user = User(id=1, name=name)
    producer.dispatch(Created(user))

def somedep():
    return "I'm a dependency"

@service.handler
def update(id: int, name: str, dep: str = Depends(somedep)):
    user = User(id=id, name=name)
    producer.dispatch(UpdatedUser(user))
    publisher.publish("Update performed", 'some-topic')
```

Then, bind them at runtime like this:

```python
producer.register(consumer)
publisher.register(subscriber)

...

register('Alice')
update(1, 'Alice Updated')  # Or: service.execute('update', 1, 'Alice Updated')
```

#### Async support

All core components (e.g., `Consumer`, `Service`, `Producer`, etc.) have asynchronous counterparts 
available in the `pymsgbus.asyncio` subpackage. Use `async` and `await` to integrate them into an 
asynchronous workflow.

```python
from pymsgbus.asyncio import Service
from pymsgbus.asyncio import Depends
from pymsgbus.asyncio import Producer, Publisher

service = Service()
producer = Producer()
publisher = Publisher()

async def register(name: str):
    user = User(id=1, name=name)
    await producer.dispatch(Created(user))

async def somedep():
    return "I'm a dependency" 

@service.handler
async def update(id: int, name: str, dep: str = Depends(somedep)):
    user = User(id=id, name=name)
    await producer.dispatch(UpdatedUser(user))
    await publisher.publish("Update performed", 'some-topic')

...

async def main():
    await register('Alice')
    await update(1, 'Alice Updated')  # Or: await service.execute('update', 1, 'Alice Updated')
```

## API Summary

### Producer

- `register(*consumers)`: Register consumers to send events to.
- `dispatch(event)`: Dispatch an event to registered consumers.

### Consumer

- `handler(func)`: Decorator to register an event handler.
- `consume(event)`: Method to consume an event.
- `override(dep, impl)`: Override a dependency.

### Publisher

- `register(*subscribers)`: Register subscribers.
- `publish(message, topic)`: Method to publish a message to subscribers.

### Subscriber

- `subscribe(*topics)`: Decorator to register handlers for topics.
- `receive(message, topic)`: Method to receive messages for a topic.
- `override(dep, impl)`: Override dependencies.

---


## License

This project is licensed under the Apache License, Version 2.0 — see the [LICENSE](LICENSE) file for details.

© 2025 Eric Hermosis. All rights reserved.

---

## Contributing

Contributions are welcome! Please open issues or pull requests for bugs, features, or enhancements.

---
