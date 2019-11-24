from discord.ext import commands
from . import persist


BOT = commands.Bot(command_prefix=commands.when_mentioned)


@BOT.event
async def on_command_completion(ctx: commands.Context):
    await ctx.message.add_reaction("✅")


@BOT.event
async def on_command_error(ctx: commands.Context, exception):
    await ctx.message.add_reaction("❌")

    if isinstance(exception, commands.MissingPermissions):
        ctx.send(f"Failed: missing permissions `{', '.join(exception.missing_perms)}`")


@BOT.group(name="channels")
async def channels_group(ctx: commands.Context):
    if not ctx.invoked_subcommand:
        await ctx.send_help(channels_group)


@channels_group.command(name="add")
@commands.has_permissions(administrator=True)
async def channels_add(_, channel_id: int):
    channels = persist.load_channels()
    channels.add(channel_id)
    persist.save_channels(channels)


@channels_group.command(name="remove")
@commands.has_permissions(administrator=True)
async def channels_remove(_, channel_id: int):
    channels = persist.load_channels()
    channels.remove(channel_id)
    persist.save_channels(channels)


@channels_group.command(name="list")
@commands.has_permissions(administrator=True)
async def channels_list(ctx: commands.Context):
    channels_str = "\n".join(map(str, persist.load_channels()))
    await ctx.send(f"```\n{channels_str}```")
