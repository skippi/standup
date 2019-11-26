"""Module for hosting bot related functionality."""

# pylint: disable=missing-function-docstring

import asyncio
from datetime import datetime, timedelta

import discord
from discord.ext import commands
from standup.post import message_is_formatted
from standup.persist import Post, Room


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
            f"```\nFailed: missing permissions `{', '.join(exception.missing_perms)}`.```"
        )
    else:
        exception_str = str(exception)
        if not exception_str:
            return

        await ctx.send(f"```\n{exception_str}```")


@BOT.event
async def on_message(msg: discord.Message):
    await BOT.process_commands(msg)

    related_room = Room.select().where(Room.channel_id == msg.channel.id).first()
    if not related_room:
        return

    if not message_is_formatted(msg.content):
        await msg.delete()
        await msg.author.send(STANDUP_DM_HELP)
        return

    member = msg.guild.get_member(msg.author.id)
    roles_to_add = [msg.guild.get_role(id) for id in related_room.role_ids]
    await member.add_roles(*roles_to_add)

    Post.create(
        channel_id=msg.channel.id,
        user_id=msg.author.id,
        role_ids=related_room.role_ids,
        timestamp=datetime.now(),
    )


@BOT.group(name="rooms")
async def rooms_group(ctx: commands.Context):
    if not ctx.invoked_subcommand:
        await ctx.send_help(rooms_group)


@rooms_group.command(name="add")
@commands.has_permissions(administrator=True)
async def rooms_add(ctx: commands.Context, channel_id: int):
    conflicting_room = Room.select().where(Room.channel_id == channel_id).first()
    if conflicting_room:
        await ctx.send(f"```Failed: channel '{channel_id}' already is a room.```")
        raise commands.CommandError()

    Room.create(channel_id=channel_id, role_ids=set())


@rooms_group.command(name="remove")
@commands.has_permissions(administrator=True)
async def rooms_remove(_, channel_id: int):
    Room.delete().where(Room.channel_id == channel_id).execute()


@rooms_group.command(name="list")
@commands.has_permissions(administrator=True)
async def rooms_list(ctx: commands.Context):
    rooms = Room.select()
    rooms_formatted = [
        f"{index}: {r.channel_id} | Roles: {str(r.role_ids) if r.role_ids else '{}'}"
        for index, r in enumerate(rooms, 1)
    ]
    joined = "\n".join(rooms_formatted)

    await ctx.send(f"```\n{joined}```")


@rooms_group.command(name="config")
@commands.has_permissions(administrator=True)
async def rooms_config(ctx: commands.Context, room: int, key: str, value: str):
    target_room = Room.select().where(Room.channel_id == room).first()
    if not target_room:
        ctx.send(f"```\nFailed: room '{room}' does not exist.```")
        raise commands.CommandError()

    if key == "roles":
        role_ids = [int(s) for s in value.split(",")]
        filtered = [id for id in role_ids if ctx.guild.get_role(id)]

        (
            Room.update({Room.role_ids: Room.role_ids.db_value(set(filtered))})
            .where(Room.channel_id == room)
            .execute()
        )


async def prune_expired_posts_task():
    await BOT.wait_until_ready()

    while not BOT.is_closed():
        await asyncio.sleep(60)

        expired_posts = Post.select().where(
            Post.timestamp < (datetime.now() - timedelta(hours=24))
        )
        if len(expired_posts) == 0:
            continue

        for post in expired_posts:
            channel = BOT.get_channel(post.channel_id)
            guild = channel.guild
            member = guild.get_member(post.user_id)
            roles_to_remove = [guild.get_role(id) for id in post.role_ids]
            await member.remove_roles(*roles_to_remove)

            post.delete_instance()


BOT.loop.create_task(prune_expired_posts_task())
