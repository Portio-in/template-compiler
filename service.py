from dotenv import load_dotenv
import os
from compiler import TemplateCompiler
import pika
import json

load_dotenv()

# Create a callback function
def callback(ch, method, properties, body):
    try:
        json_body = json.loads(body)
        domain_name = json_body["domain_name"]
        template_code = json_body["template_code"]
        compiler = TemplateCompiler(template_code, domain_name)
        compiler.configAWS(os.environ.get("AWS_ACCESS_KEY_ID"), os.environ.get("AWS_ACCESS_KEY_SECRET"))
        compiler.run()
        compiler.storeTemplateToS3(os.environ.get("AWS_BUCKET_NAME"))
        compiler.purgeCache()
    except Exception as e:
        print(e)
        pass
    ch.basic_ack(delivery_tag=method.delivery_tag)



def start_consumer():
    # Create connection
    connection = pika.BlockingConnection(pika.URLParameters(os.environ.get("AMQP_URI")))
    channel = connection.channel()
    # Create queue
    channel.queue_declare(queue=os.environ.get("QUEUE_NAME"), durable=True)
    # Listen to the queue and 
    # call the callback function on receiving a message
    channel.basic_consume(queue=os.environ.get("QUEUE_NAME"), on_message_callback=callback, auto_ack=False)
    # Start consuming
    channel.start_consuming()

if __name__ == '__main__':
    start_consumer()