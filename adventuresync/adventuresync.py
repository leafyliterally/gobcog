# -*- coding: utf-8 -*-
import logging

import discord
from redbot.core import commands
from redbot.core.i18n import Translator, cog_i18n

_ = Translator("AdventureSync", __file__)

log = logging.getLogger("red.cogs.adventuresync")

# guild_id -> {the #adventure channel to post cross-server notices into,
# and the invite link people should use to find that server}. Display names
# aren't hardcoded here - we always pull the live guild.name at dispatch time.
LINKED_GUILDS = {
    312367941578653696: {  # OJ
        "channel_id": 589503429173444619,
        "invite": "https://discord.gg/oj",
    },
    420336618260529169: {  # OJF
        "channel_id": 688831526141558837,
        "invite": "https://discord.gg/ojg",
    },
}


@cog_i18n(_)
class AdventureSync(commands.Cog):
    """Cross-posts adventure spawns between the OJ and OJF servers.

    Whenever an adventure starts in one linked server's #adventure channel,
    a heads-up embed is dropped in the other linked server's #adventure
    channel so both communities can join each other's runs.
    """

    __version__ = "1.0.0"
    __author__ = ["Leafy"]

    def __init__(self, bot):
        self.bot = bot

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\n\nCog Version: {self.__version__}"

    async def red_delete_data_for_user(self, **kwargs) -> None:
        # This cog doesn't store any user data, nothing to delete.
        return

    @commands.Cog.listener()
    async def on_adventure(self, ctx: commands.Context) -> None:
        """Fires once per adventure spawn.

        On this branch (discord.py 1.7, pre-GameSession Adventure),
        dispatch_adventure() is just:
            self.bot.dispatch("adventure", ctx)
        called at the very top of _simple() - before challenge, attribute,
        or easy_mode are even rolled, and before the adventure embed itself
        is sent. So two things are different from the master-branch version
        of this cog:

        1. `ctx` here is a real, plain commands.Context - there's no
           GameSession standing in for it, so `ctx.embed_color()` just
           works directly. No AttributeError fallback needed.
        2. There's no monster/attribute/challenge data yet (nothing has
           been rolled at dispatch time), and no adventure message has been
           sent yet either - so there's no monster name to show and no
           message to build a jump_url from. We link to the #adventure
           channel itself instead of a specific message.
        """
        guild = ctx.guild
        if guild is None or guild.id not in LINKED_GUILDS:
            return

        other_guild_id = next(gid for gid in LINKED_GUILDS if gid != guild.id)
        target_info = LINKED_GUILDS[other_guild_id]

        target_channel = self.bot.get_channel(target_info["channel_id"])
        if target_channel is None:
            try:
                target_channel = await self.bot.fetch_channel(target_info["channel_id"])
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                log.warning("AdventureSync: couldn't reach channel %s", target_info["channel_id"])
                return

        source_info = LINKED_GUILDS[guild.id]
        colour = await ctx.embed_color()

        # No specific adventure message exists yet at dispatch time on this
        # branch, so this links to the #adventure channel itself rather than
        # a jump_url for a message that hasn't been sent.
        url = f"https://discord.com/channels/{guild.id}/{ctx.channel.id}"

        embed = discord.Embed(
            description=_(
                "Feeling adventurous? A group in **{guild}** just kicked off an adventure "
                "of their own. Come join [their adventure]({url}) at {url}"
            ).format(guild=guild.name, url=url),
            colour=colour,
        )
        embed.add_field(
            name=_("Link to the Server"),
            value=f"[{guild.name}]({source_info['invite']})",
            inline=False,
        )

        await target_channel.send(embed=embed)
