import discord
from discord.ext import commands, tasks
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import os
import asyncio

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

SCHEDULE_FILE = "schedules.json"

KST = ZoneInfo("Asia/Seoul")

# 반복 작업 저장
active_repeat_tasks = {}

# 예약 로드
def load_schedules():

    if not os.path.exists(SCHEDULE_FILE):
        return []

    with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# 예약 저장
def save_schedules(data):

    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

schedules = load_schedules()

@bot.event
async def on_ready():

    print(f"{bot.user} 로그인 완료!")
    check_schedule.start()

# 관리자 권한 체크
def is_admin(ctx):

    return ctx.author.guild_permissions.administrator

# 핑
@bot.command()
async def ping(ctx):

    await ctx.send("pong!")

# 일반 예약
# !예약 19:00 메세지
@bot.command()
async def 예약(ctx, time_str, *, message):

    if not is_admin(ctx):
        await ctx.send("관리자만 사용할 수 있습니다.")
        return

    try:
        hour, minute = map(int, time_str.split(":"))

    except:
        await ctx.send("시간 형식: HH:MM")
        return

    schedule = {
        "type": "daily",
        "channel_id": ctx.channel.id,
        "hour": hour,
        "minute": minute,
        "message": message
    }

    schedules.append(schedule)
    save_schedules(schedules)

    await ctx.send(
        f"예약 완료!\n"
        f"매일 {hour:02d}:{minute:02d}"
    )

# 요일 예약
# !요일예약 월 19:00 회의 시작
@bot.command()
async def 요일예약(ctx, weekday, time_str, *, message):

    if not is_admin(ctx):
        await ctx.send("관리자만 사용할 수 있습니다.")
        return

    weekday_map = {
        "월": 0,
        "화": 1,
        "수": 2,
        "목": 3,
        "금": 4,
        "토": 5,
        "일": 6
    }

    if weekday not in weekday_map:
        await ctx.send("요일은 월~일 로 입력하세요.")
        return

    try:
        hour, minute = map(int, time_str.split(":"))

    except:
        await ctx.send("시간 형식: HH:MM")
        return

    schedule = {
        "type": "weekday",
        "weekday": weekday_map[weekday],
        "channel_id": ctx.channel.id,
        "hour": hour,
        "minute": minute,
        "message": message
    }

    schedules.append(schedule)
    save_schedules(schedules)

    await ctx.send(
        f"{weekday}요일 "
        f"{hour:02d}:{minute:02d} 예약 완료!"
    )

# 예약 목록
@bot.command()
async def 목록(ctx):

    if not schedules:
        await ctx.send("예약 없음")
        return

    text = ""

    for i, s in enumerate(schedules):

        if s["type"] == "daily":

            text += (
                f"[{i}] 매일 "
                f"{s['hour']:02d}:{s['minute']:02d} "
                f"- {s['message']}\n"
            )

        elif s["type"] == "weekday":

            days = ["월", "화", "수", "목", "금", "토", "일"]

            text += (
                f"[{i}] "
                f"{days[s['weekday']]}요일 "
                f"{s['hour']:02d}:{s['minute']:02d} "
                f"- {s['message']}\n"
            )

    await ctx.send(text)

# 예약 삭제
@bot.command()
async def 삭제(ctx, index: int):

    if not is_admin(ctx):
        await ctx.send("관리자만 사용할 수 있습니다.")
        return

    if index < 0 or index >= len(schedules):
        await ctx.send("없는 번호")
        return

    removed = schedules.pop(index)

    save_schedules(schedules)

    await ctx.send("삭제 완료!")

# 반복 알람
# !반복 2 30 물마셔
@bot.command()
async def 반복(ctx, hours: int, interval: int, *, message):

    total_minutes = hours * 60

    count = total_minutes // interval

    user_id = ctx.author.id

    await ctx.send(
        f"{hours}시간 동안 "
        f"{interval}분 간격 반복 시작!"
    )

    async def repeat_task():

        for i in range(count):

            await ctx.send(
                f"[{i+1}/{count}] {message}"
            )

            if i < count - 1:
                await asyncio.sleep(interval * 60)

        await ctx.send("반복 종료!")

    task = bot.loop.create_task(repeat_task())

    active_repeat_tasks[user_id] = task

# 반복 중지
@bot.command()
async def 중지(ctx):

    user_id = ctx.author.id

    if user_id not in active_repeat_tasks:
        await ctx.send("실행 중인 반복 없음")
        return

    active_repeat_tasks[user_id].cancel()

    del active_repeat_tasks[user_id]

    await ctx.send("반복 중지 완료!")

# DM 반복
# !DM반복 1 10 공부해
@bot.command()
async def DM반복(ctx, hours: int, interval: int, *, message):

    user = ctx.author

    total_minutes = hours * 60

    count = total_minutes // interval

    await ctx.send("DM 반복 시작!")

    async def dm_repeat():

        for i in range(count):

            await user.send(
                f"[{i+1}/{count}] {message}"
            )

            if i < count - 1:
                await asyncio.sleep(interval * 60)

        await user.send("DM 반복 종료!")

    bot.loop.create_task(dm_repeat())

# 예약 체크
@tasks.loop(minutes=1)
async def check_schedule():

    now = datetime.now(KST)

    for s in schedules:

        if (
            now.hour == s["hour"]
            and now.minute == s["minute"]
        ):

            if s["type"] == "daily":

                channel = bot.get_channel(s["channel_id"])

                if channel:
                    await channel.send(s["message"])

            elif s["type"] == "weekday":

                if now.weekday() == s["weekday"]:

                    channel = bot.get_channel(s["channel_id"])

                    if channel:
                        await channel.send(s["message"])

bot.run(TOKEN)
