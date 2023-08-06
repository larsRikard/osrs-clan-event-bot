import json
import random

from discord.ext import commands


class Event(commands.Cog):
    message_id = None
    random_events = None

    @commands.group(name="event", invoke_without_command=True)
    async def event(self, ctx):
        """Event commands"""
        subcommands = [
            f"{command.name} | {', '.join(command.aliases)}"
            for command in self.event.commands
        ]
        subcommands_list = "\n".join([f"• {subcommand}" for subcommand in subcommands])
        await ctx.send(f"Available sub-commands:\n```{subcommands_list}```")

    @event.group(name="vote", invoke_without_command=True)
    async def vote(self, ctx):
        """Vote for an event"""
        subcommands = [
            f"{command.name} | {', '.join(command.aliases)}"
            for command in self.vote.commands
        ]
        subcommands_list = "\n".join([f"• {subcommand}" for subcommand in subcommands])
        await ctx.send(f"Available sub-commands:\n```{subcommands_list}```")

    @vote.command(name="start", aliases=["begin", "create", "new"])
    @commands.has_permissions(administrator=True)
    async def vote_event(self, ctx):
        """Pick 4 random events from the event list"""
        if self.message_id is not None:
            await ctx.message.channel.send("There is already an ongoing event vote.")
            return

        data = read_event_json()
        self.random_events = random.sample(data, k=4)

        event_message = "**Randomly picked events:**\n\n" + "\n".join(
            [f"{event['emoji']} {event['name']}" for event in self.random_events]
        )

        sent_message = await ctx.message.channel.send(event_message)
        self.message_id = sent_message.id

        for event in self.random_events:
            await sent_message.add_reaction(event["emoji"])

        def check(reaction_msg):
            return (
                reaction_msg.author == ctx.client.user
                and reaction_msg.id == sent_message.id
            )

        await ctx.client.wait_for("message", timeout=10.0, check=check)

    @vote.command(name="close", aliases=["end", "finish", "stop"])
    @commands.has_permissions(administrator=True)
    async def close_vote(self, ctx):
        if not self.message_id:
            await ctx.message.channel.send(
                "Please start a vote for an event first using `!event vote start`."
            )
            return
        try:
            sent_message = await ctx.message.channel.fetch_message(self.message_id)
        except ctx.discord.NotFound:
            await ctx.message.channel.send("Referenced message not found.")
            return

        reactions = sent_message.reactions

        most_voted_event = max(reactions, key=lambda reaction: reaction.count)
        selected_event = None

        for event in self.random_events:
            if event["emoji"] == most_voted_event.emoji:
                selected_event = event
                break

        if selected_event:
            await ctx.message.channel.send(
                f"The most voted event is: {selected_event['name']}!"
            )

            self.message_id = None
            self.random_events = None

            await sent_message.delete()
        else:
            await ctx.message.channel.send("No event was voted on or event not found.")

    @event.command(name="add", aliases=["create", "new"])
    @commands.has_permissions(administrator=True)
    async def add_event(self, ctx, emoji, *args):
        """Adds an event to the event list"""
        name = " ".join(args)
        data = read_event_json()

        for event in data:
            if event["name"] == name:
                await ctx.send(f"Event '{name}' already exists.")
                return
            if event["emoji"] == emoji:
                await ctx.send(f"Event with emoji {emoji} already exists.")
                return

        data.append({"name": name, "emoji": emoji})
        write_event_json(data)
        await ctx.send(f"Added event '{name}' with emoji {emoji} to the event list.")

    @event.command(name="remove", aliases=["delete"])
    @commands.has_permissions(administrator=True)
    async def remove_event(self, ctx, entry):
        """Removes an event from the event list by name or emoji"""
        data = read_event_json()
        for event in data:
            if event["name"] == entry:
                data.remove(event)
                write_event_json(data)
                await ctx.send(
                    f"Removed event '{event['name']} {event['emoji']}' from the event list."
                )
                return
            if event["emoji"] == entry:
                data.remove(event)
                write_event_json(data)
                await ctx.send(
                    f"Removed event '{event['name']} {event['emoji']}' from the event list."
                )
                return
        await ctx.send(f"Event {entry} not found in the event list.")

    @event.command(name="list", aliases=["show", "view", "all"])
    async def list_events(self, ctx):
        """Lists all events"""
        data = read_event_json()
        message = ""
        for event in data:
            message += f"{event['name']} {event['emoji']}\n"
        await ctx.send(message)


def write_event_json(data):
    with open("../assets/events.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def read_event_json():
    with open("../assets/events.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


async def setup(bot):
    await bot.add_cog(Event())
