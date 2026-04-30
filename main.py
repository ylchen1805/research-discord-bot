import json
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

CONFIG = "config.json"


# load_configs
def load_configs():
    if os.path.exists(CONFIG):
        with open(CONFIG, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}


# save configs
def save_configs(data):
    with open(CONFIG, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("Config saved")


configs = load_configs()  # load configs

# load Environment
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise RuntimeError("Environment variable 'DISCORD_TOKEN' is not set")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)


@bot.command()
@commands.has_permissions(administrator=True)
async def papers(ctx: commands.Context):
    if ctx.guild is None:
        print("Guild not found")
        return
    guild_id = str(ctx.guild.id)
    if guild_id not in configs:
        configs[guild_id] = {}

    configs[guild_id]["paper_channel"] = ctx.channel.id
    save_configs(configs)

    await ctx.send("論文頻道設定成功")


@bot.command()
@commands.has_permissions(administrator=True)
async def leave(ctx: commands.Context):
    if ctx.guild is None:
        print("Guild not found")
        return
    guild_id = str(ctx.guild.id)
    if guild_id not in configs:
        await ctx.send("未被設定過，不做任何改變")
        return

    for k, v in configs[guild_id].items():
        if v == ctx.channel.id:
            configs[guild_id][k] = ""

    save_configs(configs)
    await ctx.send("88")


@bot.command()
async def channels(ctx: commands.Context):
    if ctx.guild is None:
        print("Guild not found")
        return
    guild_id = str(ctx.guild.id)
    if guild_id not in configs:
        await ctx.send("沒有已設定的頻道")
        return

    for k, v in configs[guild_id].items():
        channel = "未被設定過" if v == "" else v
        await ctx.send(f"{k} id : {channel}")


@bot.command()
async def ping(ctx):
    print(f"{ctx.author.name} called /ping in {ctx.channel}")
    await ctx.send("pong")


bot.run(TOKEN)
