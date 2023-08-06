import datetime
import os
import random

import discord
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

TOKEN = os.getenv('DISCORD_TOKEN')

# Define the intents your bot requires
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.content.startswith('!pick_event'):
        event_list, other_events = read_event_list()
        if not event_list:
            await message.channel.send("The event list is empty. Add some events to 'eventList.txt'.")
            return

        primary_events = [event for event in event_list if event not in other_events]
        if not primary_events:
            await message.channel.send("There are no primary events available.")
            return

        primary_picks = random.sample(primary_events, 4)
        if "Other" in primary_picks:
            primary_picks.remove("Other")
            primary_picks.extend(random.sample(other_events, 1))

        #response = "Randomly picked primary events:\n" + "\n".join(primary_picks)
        next_sunday = datetime.date.today() + datetime.timedelta(days=(6 - datetime.date.today().weekday()) % 7)
        
        response = "!poll title:Stem på event til " + next_sunday.strftime("%d.%m.%Y") + f" answer1:{primary_picks[0]} answer2:{primary_picks[1]} answer3:{primary_picks[2]} answer4:{primary_picks[3]}"

        await message.channel.send(response)

def read_event_list():
    try:
        with open("eventList.txt", "r") as file:
            events = file.read().strip().splitlines()
        
        primary_events = []
        other_events = []
        is_other_category = False

        for event in events:
            if event.startswith('\t'):  # Event is in the "Other:" category
                is_other_category = True
                other_events.append(event.strip())
            else:
                if is_other_category:  # Exiting "Other:" category
                    is_other_category = False
                primary_events.append(event.strip())

        return primary_events, other_events
    except FileNotFoundError:
        return [], []

client.run(TOKEN)
