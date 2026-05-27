import discord
from discord.ext import commands
import asyncio
import os
import time

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

active_tasks = {}

@bot.event
async def on_ready():
    print(f"{bot.user} 로그인 완료!")

@bot.command()
async def ping(ctx):
    await ctx.send("pong!")

# !반복 2 30 물마셔
@bot.command()
async def 반복(ctx, hours: int, interval: int, *, message):

    user_id = ctx.author.id

    # 기존 반복 중지
    if user_id in active_tasks:
        active_tasks[user_id].cancel()

    duration = hours * 60 * 60  # 초로 변환
    interval_sec = interval * 60

    await ctx.send(
        f"{hours}시간 동안 {interval}분 간격 반복 시작!"
    )

    async def repeat_alarm():

        start_time = time.time()
        count = 0

        try:
            while True:

                # ✅ 수정된 부분 (시간 체크 먼저)
                if time.time() - start_time >= duration:
                    break

                await asyncio.sleep(interval_sec)

                count += 1
                await ctx.send(f"[{count}] {message}")

            await ctx.send("반복 종료!")

        except asyncio.CancelledError:
            await ctx.send("반복이 중지되었습니다.")

    task = bot.loop.create_task(repeat_alarm())
    active_tasks[user_id] = task

@bot.command()
async def 중지(ctx):

    user_id = ctx.author.id

    if user_id not in active_tasks:
        await ctx.send("실행 중인 반복 없음")
        return

    active_tasks[user_id].cancel()
    del active_tasks[user_id]

bot.run(TOKEN)
