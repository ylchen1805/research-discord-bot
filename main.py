import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise RuntimeError("Environment variable 'DISCORD_TOKEN' is not set")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)


@bot.command()
async def ping(ctx):
    print(f"{ctx.author.name} called /ping in {ctx.channel}")
    await ctx.send("pong")


bot.run(TOKEN)
