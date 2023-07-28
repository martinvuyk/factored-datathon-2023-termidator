import asyncio
from azure.eventhub.aio import EventHubConsumerClient

EVENT_HUB_NAME = "factored_datathon_amazon_reviews_1"
CONSUMER_GROUP = "termidator"
EVENT_HUB_CONNECTION_STR = "Endpoint=sb://factored-datathon.servicebus.windows.net/;SharedAccessKeyName=datathon_group_1;SharedAccessKey=2GETvVt0FxyM0bo0Qau4inlmC/w3t4Uut+AEhAnAEgk=;EntityPath=factored_datathon_amazon_reviews_1"


async def on_event(partition_context, event):
    try:
        if previous != partition_context.partition_id:
            counter = 0
        else:
            counter += 1
    except UnboundLocalError:
        counter = 0
    print(f"downloading partition: {partition_context.partition_id}")
    json_object = event.body_as_str(encoding="UTF-8")
    with open(
        f"./stream/partition_{partition_context.partition_id}_{counter}.json",
        "w",
    ) as outfile:
        outfile.write(json_object)

    # Update the checkpoint so that the program doesn't read the events
    # that it has already read when you run it next time.
    previous = partition_context.partition_id
    await partition_context.update_checkpoint(event)


async def main():
    # Create a consumer client for the event hub.
    client = EventHubConsumerClient.from_connection_string(
        EVENT_HUB_CONNECTION_STR,
        consumer_group=CONSUMER_GROUP,
        eventhub_name=EVENT_HUB_NAME,
    )
    async with client:
        # Call the receive method. Read from the beginning of the
        # partition (starting_position: "-1")
        await client.receive(on_event=on_event, starting_position="-1")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # Run the main method.
    loop.run_until_complete(main())
