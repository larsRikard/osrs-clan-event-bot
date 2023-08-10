import json
import random

import tabulate
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

        # Find the maximum number of votes
        max_votes = max(reactions, key=lambda reaction: reaction.count).count

        # Find all events with the maximum number of votes
        selected_events = [
            event
            for event in self.random_events
            if any(
                reaction.count == max_votes
                for reaction in reactions
                if reaction.emoji == event["emoji"]
            )
        ]

        if selected_events:
            # Create a table to display vote results
            table_data = [["Event", "Votes"]]
            for event in self.random_events:
                vote_count = sum(
                    reaction.count
                    for reaction in reactions
                    if reaction.emoji == event["emoji"]
                )
                table_data.append([event["name"], vote_count - 1])

            vote_results_table = tabulate.tabulate(
                table_data, headers="firstrow", tablefmt="fancy_grid"
            )
            await ctx.message.channel.send(
                f"Vote Results:\n```\n{vote_results_table}\n```"
            )

            if len(selected_events) == 1:
                winner = selected_events[0]
                vote_count = max_votes - 1
                await ctx.message.channel.send(
                    f"The most voted event is: **{winner['name']}** with {vote_count} vote{'s' if vote_count != 1 else ''}! {winner['emoji']}"
                )
            else:
                event_names = ", ".join(
                    f"**{event['name']}** {event['emoji']}"
                    for event in selected_events[:-1]
                )
                event_names += f", and **{selected_events[-1]['name']}** {selected_events[-1]['emoji']}"
                vote_count = max_votes - 1
                await ctx.message.channel.send(
                    f"The most voted events are: {event_names} with {vote_count} vote{'s' if vote_count != 1 else ''} each!"
                )

            self.message_id = None
            self.random_events = None

            await sent_message.delete()
        else:
            await ctx.message.channel.send("No event was voted on or events not found.")

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
