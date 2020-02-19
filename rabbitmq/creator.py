"""
Description:
Author: Alvin yx
Action      Date        Content
------------------------------------
Create      2019-
"""

import pika

credentials = pika.PlainCredentials('admin', '123456')
connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.1.120', 5672, '/', credentials))  # 连接
# channel = connection.channel()  # 频道
# connection = pika.BlockingConnection(pika.ConnectionParameters('172.18.2.253'))
channel = connection.channel()

# 声明queue
channel.queue_declare(queue='laowang')

# n RabbitMQ a message can never be sent directly to the queue, it always needs to go through an exchange.
channel.basic_publish(exchange='', routing_key='laowang', body="Hello Lao Wang!")
print(" [x] Sent 'Hello World!'")

# close connection
connection.close()
