import discord
from discord.ext import commands
from discord.ext import tasks
from datetime import datetime
import os

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} 로그인 완료!")
    scheduled_message.start()

@bot.command()
async def ping(ctx):
    await ctx.send("pong!")

@tasks.loop(minutes=1)
async def scheduled_message():
    now = datetime.now()

    if now.hour == 9 and now.minute == 0:
        channel = bot.get_channel(CHANNEL_ID)

        if channel:
            await channel.send("자동 반복 메시지입니다!")

bot.run(TOKEN)
