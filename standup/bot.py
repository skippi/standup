"""Module for hosting bot related functionality."""

# pylint: disable=missing-function-docstring

import asyncio
from datetime import datetime, timezone
from typing import List, Optional

import discord
from discord.ext import commands
from standup.post import message_is_formatted
from standup.persist import Post, Room, RoomRole


BOT = commands.Bot(command_prefix=commands.when_mentioned)


@BOT.event
async def on_command_completion(ctx: commands.Context) -> None:
    await ctx.message.add_reaction("✅")


@BOT.event
async def on_command_error(ctx: commands.Context, exception: Exception) -> None:
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
async def on_message(msg: discord.Message) -> None:
    await BOT.process_commands(msg)

    messaged_room = Room.select().where(Room.channel_id == msg.channel.id).first()
    if not messaged_room:
        return

    if not message_is_formatted(msg.content):
        await msg.delete()

        dm_help = (
            "Your posted standup is incorrectly formatted:\n"
            f"```{msg.content}```"
            "Please format your standup correctly, here is a template example: ```\n"
            "Yesterday I: [...]\n"
            "Today I will: [...]\n"
            "Potential hard problems: [...]\n"
            "```"
        )

        await msg.author.send(dm_help)
        return

    new_post = Post.create(
        room=messaged_room,
        user_id=msg.author.id,
        timestamp=datetime.now(tz=timezone.utc),
        message_id=msg.id,
    )

    await _post_setup_roles(new_post)


@BOT.event
async def on_raw_message_delete(event: discord.RawMessageDeleteEvent) -> None:
    posts_to_delete = (
        Post.select(Post, Room).join(Room).where(Post.message_id == event.message_id)
    )
    if len(posts_to_delete) == 0:
        return

    for post in posts_to_delete:
        await _post_cleanup_roles(post)

    Post.delete().where(Post.id.in_([p.id for p in posts_to_delete])).execute()


async def _post_setup_roles(post: Post) -> None:
    roles_to_add = _room_fetch_roles(post.room)
    member = _post_fetch_member(post)
    if not member:
        return

    await member.add_roles(*roles_to_add)


@BOT.event
async def on_member_update(before: discord.Member, after: discord.Member) -> None:
    removed_roles = set(before.roles) - set(after.roles)
    invalidated_posts = (
        Post.select(Post, Room)
        .join(Room)
        .join(RoomRole, on=(RoomRole.room == Post.room))
        .where(
            ~(Post.is_expired(datetime.now(tz=timezone.utc)))
            & (Post.user_id == after.id)
            & RoomRole.role_id.in_([r.id for r in removed_roles])
        )
    )
    for post in invalidated_posts:
        await _post_cleanup_roles(post)

        try:
            await BOT.http.delete_message(post.room.channel_id, post.message_id)
        except discord.NotFound:
            pass

    Post.delete().where(Post.id.in_([p.id for p in invalidated_posts])).execute()


@BOT.event
async def on_member_join(member: discord.Member) -> None:
    active_posts = (
        Post.select()
        .join(Room)
        .where(
            ~(Post.is_expired(datetime.now(tz=timezone.utc)))
            & (Post.user_id == member.id)
        )
    )

    for post in active_posts:
        await _post_setup_roles(post)


@BOT.group(name="rooms")
async def rooms_group(ctx: commands.Context) -> None:
    """Manage standup rooms."""

    if not ctx.invoked_subcommand:
        await ctx.send_help(rooms_group)


@rooms_group.command(name="add")
@commands.has_permissions(administrator=True)
async def rooms_add(ctx: commands.Context, channel_id: int) -> None:
    """Declares a discord channel as a standup room."""

    conflicting_room = Room.select().where(Room.channel_id == channel_id).first()
    if conflicting_room:
        await ctx.send(f"```Failed: channel '{channel_id}' already is a room.```")
        raise commands.CommandError()

    Room.create(channel_id=channel_id)


@rooms_group.command(name="remove")
@commands.has_permissions(administrator=True)
async def rooms_remove(_, channel_id: int) -> None:
    """Removes a discord channel from the list of functional standup rooms."""

    Room.delete().where(Room.channel_id == channel_id).execute()


@rooms_group.command(name="list")
@commands.has_permissions(administrator=True)
async def rooms_list(ctx: commands.Context) -> None:
    """Lists all created standup rooms along with their assigned roles."""

    rooms = Room.select()
    formatted = (r.format_for_listing() for r in rooms)
    numbered = (f"{i}: {string}" for i, string in enumerate(formatted, 1))
    joined = "\n".join(numbered)

    await ctx.send(f"```\n{joined}```")


@rooms_group.command(name="config")
@commands.has_permissions(administrator=True)
async def rooms_config(ctx: commands.Context, room: int, key: str, value: str) -> None:
    """
    Configures a standup room's key-value properties.

    Keys:
    - 'roles': Accepts a comma separated list of role IDs. Use empty quotes to
      specify an empty list.
    - 'cooldown': Accepts an integer value representing seconds. (default: 3600)
    """

    target_room = Room.select().where(Room.channel_id == room).first()
    if not target_room:
        ctx.send(f"```\nFailed: room '{room}' does not exist.```")
        raise commands.CommandError()

    if key == "roles":
        snowflakes = _parse_snowflake_csv(value)
        target_room.update_roles(snowflakes)
    elif key == "cooldown":
        Room.update(cooldown=int(value)).where(Room.channel_id == room).execute()


def _parse_snowflake_csv(string: str) -> List[int]:
    return [int(s) for s in string.split(",") if s]


GITHUB_URL = "https://www.github.com/skippi/standup"


@BOT.command(aliases=["about"])
async def info(ctx: commands.Context) -> None:
    """Displays information about the standup bot."""

    embed = discord.Embed()
    embed.colour = discord.Colour(0x43B581)
    embed.description = (
        'A discord bot for conducting daily stand-ups in "The Programming Hangout".'
    )
    embed.set_author(name="Info", url=GITHUB_URL, icon_url=str(BOT.user.avatar_url))
    embed.set_thumbnail(url=str(BOT.user.avatar_url))
    embed.add_field(name="GitHub", value=f"[skippi/standup]({GITHUB_URL})")
    embed.add_field(
        name="Framework", value="[discord.py](https://github.com/Rapptz/discord.py)"
    )

    await ctx.send(embed=embed)


async def _prune_expired_posts_task() -> None:
    await BOT.wait_until_ready()

    while not BOT.is_closed():
        await asyncio.sleep(60)

        expired_posts = (
            Post.select()
            .join(Room)
            .where(Post.is_expired(datetime.now(tz=timezone.utc)))
        )
        if len(expired_posts) == 0:
            continue

        for post in expired_posts:
            await _post_cleanup_roles(post)

        Post.delete().where(Post.id.in_([p.id for p in expired_posts])).execute()


async def _post_cleanup_roles(post: Post) -> None:
    roles_to_remove = _room_fetch_roles(post.room)
    member = _post_fetch_member(post)
    if not member:
        return

    await member.remove_roles(*roles_to_remove)


def _room_fetch_roles(room: Room) -> List[discord.Role]:
    query = RoomRole.select().where(RoomRole.room == room)
    role_ids = [room_role.role_id for room_role in query]

    guild = BOT.get_channel(room.channel_id).guild
    return [r for r in guild.roles if r.id in role_ids]


def _post_fetch_member(post: Post) -> Optional[discord.Member]:
    guild = BOT.get_channel(post.room.channel_id).guild
    return guild.get_member(post.user_id)


BOT.loop.create_task(_prune_expired_posts_task())
