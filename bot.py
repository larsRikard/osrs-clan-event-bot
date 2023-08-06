import os
import json
import random
import re

import discord
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

TOKEN = os.getenv('DISCORD_TOKEN')

# Define the intents your bot requires
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

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

        # Check if "Other" is in primary_picks and replace it
        if "Other" in primary_picks:
            primary_picks.remove("Other")
            primary_picks.extend(random.sample(other_events, 1))

        response = "**Randomly picked primary events:**\n\n" + "\n".join(primary_picks)

        # Send the poll message
        poll_message = await message.channel.send(response)

        # Add reactions to the poll message
        emojis = [event[-1] for event in primary_picks]
        for emoji in emojis:
            print(emoji)
            print(len(emoji))
            await poll_message.add_reaction(emoji)
        """ await poll_message.add_reaction("⚱️") """
            

@client.event
async def on_reaction_add(reaction, user):
    if not user.bot and reaction.message.content.startswith("Randomly picked primary events:"):
        # Parse the poll message and extract the events
        events = reaction.message.content.split('\n')[1:]
        events = [event.split(':')[-1].strip() for event in events]

        # Get the corresponding emoji
        emoji_reaction = reaction.emoji
        print(emoji_reaction)

        # Check if the emoji is present in the events
        for index, event in enumerate(events):
            emoji_pattern = r'[^a-zA-Z0-9 ]'
            event_emoji = re.sub(emoji_pattern, '', event[-1])
            if emoji_reaction == event_emoji:
                # Increment the vote count for the event
                event_votes = int(re.findall(r'\d+', event)[0]) + 1
                events[index] = event.replace(f":{event_votes - 1}:", f":{event_votes}:")

        # Create the updated poll message
        updated_message = "Randomly picked primary events:\n" + "\n".join(events)

        # Edit the poll message with updated votes
        await reaction.message.edit(content=updated_message)

def read_event_list():
    try:
        with open("eventList.txt", "r", encoding="utf-8") as file:
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
