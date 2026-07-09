import json
from confluent_kafka import Consumer,KafkaException

class KafkaEventConsumer:
    def __init__(self,bootstrap_servers: str = "localhost:9092"):
        self.consumer = Consumer({
            "bootstrap.servers":bootstrap_servers,
            "group.id": "uber-replica-consumer",
            "auto.offset.reset":"earliest"



        })

    def consume(self):
        topics= [
            "agents.requests",
            "agent.responses",
            "audit.logs"

        ]

        self.consumer.subscribe(topics)
        print(f"Listening to kafka topics: {topics})")

        try:
            while True:
                message = self.consumer.poll(timeout=1.0)

                if message is None:
                    continue
                if message.error():
                    raise KafkaException(message.error())
                event = json.loads(
                    message.value().decode("utf-8")

                )

                print("\nKafka event received")
                print(f"Topic:{message.topic()}")
                print(f"partition:{message.partition()}")
                print(f"offest:{message.offset()}")
                print(f"event:{event}")
        
        except KeyboardInterrupt:
            print("kafka Consumer Stopped ")


        finally:
            self.consumer.close()

if __name__ == "__main__":
    KafkaEventConsumer().consume()
    