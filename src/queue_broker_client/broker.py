import functools
import pika, sys, os
from pika.adapters.blocking_connection import BlockingChannel
import json
import threading



class Broker:
    connection: pika.BlockingConnection
    channel: BlockingChannel
    queues = {}

    def __init__(self,url):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=url))
        self.channel = self.connection.channel()


    def from_queue(self, name):
        '''read from a queue using function'''
        def wrapper(funct):
            self.queues[name] = funct
            return funct
        return wrapper

    def to_queue(self, name):
        '''send output of function to a queue'''
        def decorator(funct):
            @functools.wraps(funct)
            def wrapper(*args, **kwargs):
                data = funct(*args, **kwargs)
                self.channel.basic_publish(exchange='', routing_key=name, body=json.dump(data))
            return wrapper
        return decorator

    @staticmethod
    def deserialise(klass):
        def decorator(funct):
            @functools.wraps(funct)
            def wrapper(*args, **kwargs):
                body = args[3]
                deserialise_body = klass(json.loads(body))
                #args[3] = deserialise_body
                args = (args[1],args[2],args[3],deserialise_body)
                return funct(*args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def _serialize(obj):
        return obj.__dict__

    @staticmethod
    def serialise():
        def decorator(funct):
            @functools.wraps(funct)
            def wrapper(*args, **kwargs):
                response = funct(*args, **kwargs)
                response_json = json.dumps(response.__dict__, default = Broker._serialize)
                return response_json
            return wrapper
        return decorator
 
    def send(self, queue, message):
        '''Send a message to a queue'''
        if isinstance(message, str) == False:
            message = json.dumps(message.__dict__, default = Broker._serialize)
        print(message)
        self.channel.queue_declare(queue=queue) # ensure the queue exists
        print("Sending")
        self.channel.basic_publish(exchange='', routing_key=queue, body=message)
        method_frame, header_frame, body = self.channel.basic_get(queue)
        print(body)

    def read(self, queue):
        '''Read latest message from a queue, will return a string if there is a message
        in the queue or None if there are no messages queued'''
        data = None
        self.channel.queue_declare(queue=queue) # ensure the queue exists
        method_frame, header_frame, body = self.channel.basic_get(queue)
        if method_frame:
            data = body
            data = json.loads(data.decode("utf-8"))
            self.channel.basic_ack(method_frame.delivery_tag) # acknowledge that the message was received
        return data

    def create_all(self):
        for queue in self.queues.keys():
            self.channel.queue_declare(queue=queue)
            self.channel.basic_consume(queue=queue, on_message_callback=self.queues[queue], auto_ack=True)
        self.channel.start_consuming()

    def run(self):
        #waiting for messages 
        print("Waiting for messages")
        self.channel.start_consuming()
