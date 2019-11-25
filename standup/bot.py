import asyncio
import re
from datetime import datetime, timedelta

import discord
from discord.ext import commands
from . import persist


STANDUP_REGEX = (
    r"^Yesterday I:[\s\S]+\nToday I will:[\s\S]+\nPotential hard problems:[\s\S]+$"
)
STANDUP_DM_HELP = """Please format your standup correctly, here is a template example: ```
Yesterday I: [...]
Today I will: [...]
Potential hard problems: [...]
```\n
"""
BOT = commands.Bot(command_prefix=commands.when_mentioned)


@BOT.event
async def on_command_completion(ctx: commands.Context):
    await ctx.message.add_reaction("✅")


@BOT.event
async def on_command_error(ctx: commands.Context, exception):
    await ctx.message.add_reaction("❌")

    if isinstance(exception, commands.MissingPermissions):
        await ctx.send(
            f"Failed: missing permissions `{', '.join(exception.missing_perms)}`"
        )
    else:
        await ctx.send(f"```\n{exception}```")


@BOT.event
async def on_message(msg: discord.Message):
    await BOT.process_commands(msg)

    rooms = persist.load_rooms()
    related_rooms = [r for r in rooms if r.channel_id == msg.channel.id]
    if not related_rooms:
        return

    if not re.match(STANDUP_REGEX, msg.content):
        await msg.delete()
        await msg.author.send(STANDUP_DM_HELP)
        return

    posts = persist.load_posts()
    posts.append(
        persist.Post(
            channel_id=msg.channel.id,
            user_id=msg.author.id,
            roles=set(),
            timestamp=datetime.now(),
        )
    )
    persist.save_posts(posts)


@BOT.group()
async def rooms(ctx: commands.Context):
    if not ctx.invoked_subcommand:
        await ctx.send_help(rooms)


@rooms.command(name="add")
@commands.has_permissions(administrator=True)
async def rooms_add(ctx: commands.Context, channel_id: int):
    rooms = persist.load_rooms()
    conflicting_rooms = [r for r in rooms if r.channel_id == channel_id]
    if conflicting_rooms:
        await ctx.send(f"Failed: channel `{channel_id}` already is a room.")
        raise commands.CommandError()

    rooms.append(persist.Room(channel_id=channel_id, roles=set()))
    persist.save_rooms(rooms)


@rooms.command(name="remove")
@commands.has_permissions(administrator=True)
async def rooms_remove(_, channel_id: int):
    rooms = persist.load_rooms()
    new_rooms = [r for r in rooms if r.channel_id != channel_id]
    persist.save_rooms(new_rooms)


@rooms.command(name="list")
@commands.has_permissions(administrator=True)
async def rooms_list(ctx: commands.Context):
    rooms = persist.load_rooms()
    rooms_formatted = [
        f"{index}: {r.channel_id} | Roles: {str(r.roles) if r.roles else '{}'}"
        for index, r in enumerate(rooms, 1)
    ]
    joined = "\n".join(rooms_formatted)

    await ctx.send(f"```\n{joined}```")


async def prune_expired_posts_task():
    await BOT.wait_until_ready()

    while not BOT.is_closed:
        await asyncio.sleep(60)

        posts = persist.load_posts()
        expired_posts = (
            p for p in posts if datetime.now() - p.timestamp >= timedelta(hours=24)
        )
        if not expired_posts:
            continue

        for post in expired_posts:
            channel = BOT.get_channel(post.channel_id)
            member = channel.guild.get_member(post.user_id)
            await member.remove_roles(*post.roles)

        remaining_posts = (
            p for p in posts if datetime.now() - p.timestamp < timedelta(hours=24)
        )
        persist.save_posts(remaining_posts)


BOT.loop.create_task(prune_expired_posts_task())
