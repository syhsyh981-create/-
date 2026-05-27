import discord
from discord.ext import commands
import asyncio
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 실행 중인 반복 저장
active_tasks = {}

@bot.event
async def on_ready():
    print(f"{bot.user} 로그인 완료!")

# 테스트
@bot.command()
async def ping(ctx):
    await ctx.send("pong!")

# 반복 알람
# !반복 2 30 물마셔
@bot.command()
async def 반복(ctx, hours: int, interval: int, *, message):

    user_id = ctx.author.id

    # 기존 반복 중지
    if user_id in active_tasks:
        active_tasks[user_id].cancel()

    total_minutes = hours * 60
    repeat_count = total_minutes // interval

    await ctx.send(
        f"{hours}시간 동안 "
        f"{interval}분 간격 반복 시작!"
    )

    async def repeat_alarm():

        try:

            for i in range(repeat_count):

                await ctx.send(
                    f"[{i+1}/{repeat_count}] {message}"
                )

                if i < repeat_count - 1:
                    await asyncio.sleep(interval * 60)

            await ctx.send("반복 종료!")

        except asyncio.CancelledError:
            await ctx.send("반복이 중지되었습니다.")

    task = bot.loop.create_task(repeat_alarm())

    active_tasks[user_id] = task

# 반복 중지
@bot.command()
async def 중지(ctx):

    user_id = ctx.author.id

    if user_id not in active_tasks:
        await ctx.send("실행 중인 반복 없음")
        return

    active_tasks[user_id].cancel()

    del active_tasks[user_id]

bot.run(TOKEN)
