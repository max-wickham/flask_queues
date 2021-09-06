# Queue Broker Client
This is a tool for easily consuming from queues and sending messages to queues.

# Usage
## Setup
Use the following code to set up a connection to the queue broker
```
broker = Broker("url)
from queue_consumers import * # import any consumers here
broker.create_all()
```
## Create a Queue Consumer
To create a consumer use the following code
```
@from("queue_name")
def consume(body):
    return
```
The body will be the queue message in teh form of a python dictionarry
To send a return object to another queue use the "to" decorator
```
@from("from_queue_name")
@to("to_queue_name")
def consume(body):
    return {"message":"test"}
```
## Serialisation and Deserialisation
Rerceving messages and outgoing messages can be serialised and deserialised using this code
```
@from("from_queue_name")
@to("to_queue_name")
@deserialise(ClassName)
@serialise()
def consume(class_instance : ClassName):
    return Response()
```
The class passed to the deserialiser must have a constructor that accepts a dictionary, recommended that a pydantic class is used.

## Sending messages
Messages can be sent using the following code
```
broker.send("queue_name",message)
```
The messsage can be an object or a dictionary