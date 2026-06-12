import json
from confluent_kafka import Producer


class KafkaEventProducer:
    """
    Kafka producer for publishing agent and ride events.
    """

    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.producer = Producer({
            "bootstrap.servers": bootstrap_servers,
            "client.id": "uber-replica-api"
        })

    def _delivery_report(self, error, message):
        if error is not None:
            print(f"Kafka delivery failed: {error}")
            return

        print(
            f"Kafka event delivered to "
            f"{message.topic()} partition {message.partition()}"
        )

    def publish(self, topic: str, event_type: str, payload: dict) -> None:
        event = {
            "event_type": event_type,
            "payload": payload
        }

        self.producer.produce(
            topic=topic,
            value=json.dumps(event).encode("utf-8"),
            callback=self._delivery_report
        )

        self.producer.poll(0)

    def flush(self) -> None:
        self.producer.flush()