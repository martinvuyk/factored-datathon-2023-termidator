import asyncio
from azure.eventhub.aio import EventHubConsumerClient

EVENT_HUB_NAME = "factored-datathon"
CONSUMER_GROUP = "termidator"
EVENT_HUB_CONNECTION_STR = "Endpoint=sb://factored-datathon.servicebus.windows.net/;SharedAccessKeyName=datathon_listener;SharedAccessKey=sJJnyi8GGTBAa55jY89kacoT6hXAzWx2B+AEhCPEKYE=;EntityPath=factored_datathon_amazon_review_1"


async def on_event(partition_context, event):
    json_object = event.body_as_str(encoding="UTF-8")
    print((f"{json_object}"))
    with open(f"./stream/{partition_context.partition_id}.json", "w") as outfile:
        outfile.write(json_object)

    # Update the checkpoint so that the program doesn't read the events
    # that it has already read when you run it next time.
    await partition_context.update_checkpoint(event)


async def main():
    # Create a consumer client for the event hub.
    client = EventHubConsumerClient.from_connection_string(
        EVENT_HUB_CONNECTION_STR,
        consumer_group=CONSUMER_GROUP,
        eventhub_name=EVENT_HUB_NAME,
        logging_enable=True,
    )
    async with client:
        # Call the receive method. Read from the beginning of the
        # partition (starting_position: "-1")
        await client.receive(on_event=on_event, starting_position="-1")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # Run the main method.
    loop.run_until_complete(main())
