from confluent_kafka import Consumer

def run_consumer():
    consumer = Consumer({
        """
        """
    })

    consumer.subscribe(["agents.eveents"])

    print("kafka consumer started. Listening to topic: agent.events")

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                print("consumer error:", msg.error())
                continue
            print("received event:")
            print(msg.value().decode("utf-8"))
            print("-"*80)


    except KeyboardInterrupt:
        print("Consumer stopped.")
    
    finally:
        consumer.close()



if __name__ == "__main__":
    run_consumer()

