# -*- coding: utf-8 -*-
import logging
from typing import Optional

import discord
from redbot.core import commands
from redbot.core.i18n import Translator, cog_i18n

_ = Translator("AdventureSync", __file__)

log = logging.getLogger("red.cogs.adventuresync")

# guild_id -> {display name, the #adventure channel to post cross-server
# notices into, and the invite link people should use to find that server}
LINKED_GUILDS = {
    312367941578653696: {  # OJ
        "name": "OJ",
        "channel_id": 589503429173444619,
        "invite": "https://discord.gg/oj",
    },
    420336618260529169: {  # OJF
        "name": "OJF",
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

        Adventure's own dispatch_adventure() does:
            self.bot.dispatch("adventure", session)
        so what actually lands here as `ctx` is a GameSession, not a real
        commands.Context - see game_session.py. It duck-types fine for
        .guild / .channel / .message (those are plain attributes on
        GameSession), which is the same trick AdventureAlert relies on.
        It does NOT have an embed_color() method though, since that's a
        method Red only puts on real Context objects - calling
        `ctx.embed_color()` directly here raises AttributeError. The real
        Context Adventure used to build the session is available at
        `session.ctx`, so that's what we call embed_color() on instead.
        """
        session = ctx  # this is actually a GameSession - renamed for clarity
        guild: Optional[discord.Guild] = getattr(session, "guild", None)
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

        message = getattr(session, "message", None)
        jump_url = message.jump_url if message is not None else None
        if jump_url is None:
            return

        source_info = LINKED_GUILDS[guild.id]

        try:
            colour = await session.embed_color()
        except AttributeError:
            colour = await session.ctx.embed_color()

        embed = discord.Embed(
            description=_(
                "Feeling adventurous? A group over on **{guild}** just set off on an "
                "adventure of their own. Come join [their adventure]({jump_url})!\n{jump_url}"
            ).format(guild=source_info["name"], jump_url=jump_url),
            colour=colour,
        )
        embed.add_field(
            name=_("Link to the Server"),
            value=f"[{source_info['name']}]({source_info['invite']})",
            inline=False,
        )
        await target_channel.send(embed=embed)
