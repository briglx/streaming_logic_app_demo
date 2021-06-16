#!/usr/bin/python
"""Main script for Eventhub Message Generator."""
import argparse
import asyncio
import logging
import os
import signal
import sys

from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient

import template_jinja as template
from generator import (
    DEFAULT_WAIT_TIME_SEC,
    FAULTY_DEVICE_COUNT,
    create_device_list,
    create_drop_list,
    create_sample_data,
    drop_device_message,
)

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


async def run():
    """Create sample messages."""
    async with PRODUCER:

        device_list = create_device_list()
        device_drop_list = create_drop_list(device_list, FAULTY_DEVICE_COUNT)
        device_drop_count = {}

        # Loop Forever
        while True:

            # Create a batch.
            event_data_batch = await PRODUCER.create_batch()

            for device in device_list:

                # Get data
                data = create_sample_data(device)

                if drop_device_message(data, device_drop_list, device_drop_count):
                    logging.info("dropping device message...")
                else:

                    message = template.render_json(
                        data, TEMPLATE_PATH, TEMPLATE_SOURCE_MESSAGE
                    )

                    # Add event to the batch.
                    logging.info("Sending Event %s", message)
                    event_data_batch.add(EventData(message))

            # Send the batch of events to the event hub.
            await PRODUCER.send_batch(event_data_batch)

            logging.info("waiting...")
            await asyncio.sleep(WAIT_TIME_SEC)


if __name__ == "__main__":
    logging.info("Starting script")

    parser = argparse.ArgumentParser(
        description="Eventhub Data Generator.",
        add_help=True,
    )
    parser.add_argument(
        "--connection_string",
        "-c",
        help="Eventhubs Connection String",
    )
    parser.add_argument(
        "--eventhubs_name",
        "-n",
        help="EventHubs Name",
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

    CONNECTION_STRING = args.connection_string or os.environ.get(
        "EVENT_HUB_CONNECTION_STRING"
    )
    EVENT_HUB_NAME = args.eventhubs_name or os.environ.get("EVENT_HUB_NAME")
    TEMPLATE_PATH = args.template_path or os.environ.get("TEMPLATE_PATH")
    TEMPLATE_SOURCE_MESSAGE = args.template_source_message or os.environ.get(
        "TEMPLATE_SOURCE_MESSAGE"
    )
    WAIT_TIME_SEC = (
        args.wait_time_seconds or int(os.environ.get("WAIT_TIME_SEC"))
        if (os.environ.get("WAIT_TIME_SEC").isdigit())
        else DEFAULT_WAIT_TIME_SEC
    )

    if not CONNECTION_STRING:
        raise ValueError(
            "Event hub connection string is required."
            "Have you set the EVENT_HUB_CONNECTION_STRING env variable?"
        )

    if not EVENT_HUB_NAME:
        raise ValueError(
            "Event hub name is required."
            "Have you set the EVENT_HUB_NAME env variable?"
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

    # This restores the default Ctrl+C signal handler, which just kills the process
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Create a producer client to send messages to the event hub.
    # Specify a connection string to your event hubs namespace and
    # the event hub name.
    PRODUCER = EventHubProducerClient.from_connection_string(
        conn_str=CONNECTION_STRING, eventhub_name=EVENT_HUB_NAME
    )

    # Start Message Generator
    loop = asyncio.get_event_loop()
    loop.create_task(run())
    loop.run_forever()
