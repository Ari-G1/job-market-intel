"""
Replays postings.jsonl into Kafka topic jobs.raw.

This is a batch source replayed through Kafka to exercise the streaming
ingestion path. In production the producer is replaced by a live API poller
and nothing downstream changes. It is not a real-time job feed.
"""
import sys
import time
from kafka import KafkaProducer

BOOTSTRAP = "localhost:9092"
TOPIC = "jobs.raw"
JSONL_IN = "data/raw/postings.jsonl"

BATCH = 500          # messages between sleeps
SLEEP_SECONDS = 0.1  # pacing, so Spark sees several micro-batches


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None

    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP,
        value_serializer=lambda v: v.encode("utf-8"),  # see note 1
        linger_ms=50,
        batch_size=65536,
    )

    sent = 0
    with open(JSONL_IN, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue

            producer.send(TOPIC, value=line)
            sent += 1

            if sent % BATCH == 0:
                time.sleep(SLEEP_SECONDS)
                print(f"sent {sent:,}", flush=True)

            if limit is not None and sent >= limit:
                break

    producer.flush()   # see note 2
    producer.close()
    print(f"done. sent {sent:,} messages to {TOPIC}")


if __name__ == "__main__":
    main()