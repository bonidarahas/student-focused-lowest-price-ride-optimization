import json
from datetime import datetime
from confluent_kafka import Producer


class KafkaEventProducer:
    """
    Real Kafka producer for publishing agent events.
    """
    def __init__(self, bootstrap_servers:str ="localhost:9892"):
        self.topic="agent.events"

        self.producer =Producer({
            "bootstrap.servers": bootstrap_servers
        })

    def publish_event(self,event_type:str,payload:dict):
        event = {
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.now().isoformat(timespec="seconds")
        }
        self.producer.producce(
            topic=self.topic,
            value = json.dumps(event).encode("utf-8")

        )
        self.producer.flush()
                    