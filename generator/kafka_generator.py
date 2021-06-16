"""Main script for Kafka Message Generator."""
import argparse
import json
import logging
import os
import sys
import time

from kafka import KafkaProducer

import template_jinja as template
from common import (
    DEFAULT_WAIT_TIME_SEC,
    FAULTY_DEVICE_COUNT,
    create_device_list,
    create_drop_list,
    create_sample_data,
    drop_device_message,
)

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def main():
    """Create sample messages."""

    device_list = create_device_list()
    device_drop_list = create_drop_list(device_list, FAULTY_DEVICE_COUNT)
    device_drop_count = {}

    # Loop Forever
    while True:

        for device in device_list:
            # Get data
            data = create_sample_data(device)

            if drop_device_message(data, device_drop_list, device_drop_count):
                logging.info("dropping device message...")
            else:

                message = template.render_json(
                    data, TEMPLATE_PATH, TEMPLATE_SOURCE_MESSAGE
                )

                logging.info("Sending Event %s", message)
                PRODUCER.send(KAFKA_TOPIC, message)

        logging.info("waiting...")
        time.sleep(WAIT_TIME_SEC)


if __name__ == "__main__":
    logging.info("Starting script")

    parser = argparse.ArgumentParser(
        description="Kafka Data Generator.",
        add_help=True,
    )
    parser.add_argument(
        "--server",
        "-s",
        help="Kafka server",
    )
    parser.add_argument(
        "--username",
        "-u",
        help="Kafka username",
    )
    parser.add_argument(
        "--password",
        "-p",
        help="Kafka password",
    )
    parser.add_argument(
        "--topic",
        "-o",
        help="Kafka topic",
    )
    parser.add_argument(
        "--template_path",
        "-t",
        help="Template Path",
    )
    parser.add_argument(
        "--template_source_message",
        "-ts",
        help="Template to create the Source Message",
    )
    parser.add_argument(
        "--wait_time_seconds",
        "-w",
        type=int,
        help="Time in seconds to wait between sending messages.",
    )

    args = parser.parse_args()

    KAFKA_SERVER = args.server or os.environ.get("KAFKA_SERVER")
    KAFKA_USERNAME = args.username or os.environ.get("KAFKA_USERNAME")
    KAFKA_PASSWORD = args.password or os.environ.get("KAFKA_PASSWORD")
    KAFKA_TOPIC = args.topic or os.environ.get("KAFKA_TOPIC")
    TEMPLATE_PATH = args.template_path or os.environ.get("TEMPLATE_PATH")
    TEMPLATE_SOURCE_MESSAGE = args.template_source_message or os.environ.get(
        "TEMPLATE_SOURCE_MESSAGE"
    )
    WAIT_TIME_SEC = (
        args.wait_time_seconds or int(os.environ.get("WAIT_TIME_SEC"))
        if ("WAIT_TIME_SEC" in os.environ and os.environ.get("WAIT_TIME_SEC").isdigit())
        else DEFAULT_WAIT_TIME_SEC
    )

    if not KAFKA_SERVER:
        raise ValueError(
            "Kafka server is required." "Have you set the KAFKA_SERVER env variable?"
        )
    if not KAFKA_USERNAME:
        raise ValueError(
            "Kafka username is required."
            "Have you set the KAFKA_USERNAME env variable?"
        )
    if not KAFKA_PASSWORD:
        raise ValueError(
            "Kafka password is required."
            "Have you set the KAFKA_PASSWORD env variable?"
        )
    if not KAFKA_TOPIC:
        raise ValueError(
            "Kafka topic is required." "Have you set the KAFKA_TOPIC env variable?"
        )
    if not TEMPLATE_PATH:
        raise ValueError(
            "Template path is required." "Have you set the TEMPLATE_PATH env variable?"
        )

    if not TEMPLATE_SOURCE_MESSAGE:
        raise ValueError(
            "Template source message is required."
            "Have you set the TEMPLATE_SOURCE_MESSAGE env variable?"
        )

    PRODUCER = KafkaProducer(
        bootstrap_servers=KAFKA_SERVER,
        security_protocol="SASL_PLAINTEXT",
        sasl_mechanism="PLAIN",
        sasl_plain_username=KAFKA_USERNAME,
        sasl_plain_password=KAFKA_PASSWORD,
        api_version=(2, 8, 0),
        # value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    main()
