import os
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@bot.command()
async def ping(ctx):
    """Check the bot's latency."""
    await ctx.send(f"Pong! Latency: {round(bot.latency * 1000)}ms")


@bot.event
async def on_ready():
    await load_extension("event")
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, name="!help")
    )
    print(f"Logged in as {bot.user}")


async def load_extension(extension):
    try:
        await bot.load_extension(extension)
    except Exception as e:
        print(f"Failed to load extension {extension}", e)


if __name__ == "__main__":
    bot.run(os.getenv("TOKEN"))
