# -*- coding: utf-8 -*-
import logging
from typing import Optional

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


class _RelaySession:
    """Duck-typed stand-in for a GameSession, aimed at the linked guild.

    Used only when AdventureSync redispatches an adventure into the other
    guild's own event stream (see AdventureSync._relay_adventure below).
    Only carries the handful of attributes anything listening for these
    events actually reads - the same set dispatch_adventure() in
    adventure.py exposes on the real session: .guild, .channel, .message,
    .ctx, plus the boss/miniboss/transcended/ascended/immortal/possessed/
    easy_mode flags used to decide which sub-events to fire.

    `.guild` and `.channel` point at the *linked* guild/channel rather than
    where the adventure actually spawned - that's the whole point, so that
    a cog like AdventureAlert installed on the linked guild reacts as if the
    adventure had spawned there. `.ctx` is carried over from the source
    session as-is; there's no real Context for the linked guild to hand out
    (nothing was actually invoked there), so anything that falls back to
    `.ctx.embed_color()` will get the *source* guild's colour, not the
    target's - a minor, unavoidable cosmetic tradeoff.
    """

    def __init__(self, source, guild: discord.Guild, channel: discord.abc.Messageable, message: discord.Message):
        self._adventuresync_relay = True
        self.guild = guild
        self.channel = channel
        self.message = message
        self.ctx = getattr(source, "ctx", None)
        self.easy_mode = getattr(source, "easy_mode", False)
        self.boss = getattr(source, "boss", False)
        self.miniboss = getattr(source, "miniboss", False)
        self.transcended = getattr(source, "transcended", False)
        self.ascended = getattr(source, "ascended", False)
        self.immortal = getattr(source, "immortal", False)
        self.possessed = getattr(source, "possessed", False)


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

        if getattr(session, "_adventuresync_relay", False):
            # This is a _RelaySession we dispatched ourselves further down -
            # ignore it here, otherwise the two linked guilds would keep
            # redispatching "adventure" back and forth at each other forever.
            return

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

        monster_name = None
        if getattr(session, "easy_mode", False):
            attribute = getattr(session, "attribute", "") or ""
            challenge = getattr(session, "challenge", None)
            if challenge:
                monster_name = _("a{attribute} {challenge}").format(attribute=attribute, challenge=challenge)

        if monster_name:
            description = _(
                "Feeling adventurous? A group in **{guild}** just kicked off an adventure "
                "of their own against **{monster}**. Come join [their adventure]({jump_url}) "
                "at {jump_url}"
            ).format(guild=guild.name, monster=monster_name, jump_url=jump_url)
        else:
            description = _(
                "Feeling adventurous? A group in **{guild}** just kicked off an adventure "
                "of their own. Come join [their adventure]({jump_url}) at {jump_url}"
            ).format(guild=guild.name, jump_url=jump_url)

        embed = discord.Embed(description=description, colour=colour)
        embed.add_field(
            name=_("Link to the Server"),
            value=f"[{guild.name}]({source_info['invite']})",
            inline=False,
        )

        if getattr(session, "easy_mode", False):
            monster = getattr(session, "monster", None)
            if monster and monster.get("image"):
                embed.set_thumbnail(url=monster["image"])

        relay_message = await target_channel.send(embed=embed)

        target_guild = self.bot.get_guild(other_guild_id)
        if target_guild is not None:
            self._relay_adventure(session, target_guild, target_channel, relay_message)

    def _relay_adventure(
        self,
        session,
        guild: discord.Guild,
        channel: discord.abc.Messageable,
        message: discord.Message,
    ) -> None:
        """Redispatch the adventure into the linked guild's own event stream.

        Mirrors dispatch_adventure() in adventure.py: builds a duck-typed
        stand-in for the session (see _RelaySession above) pointed at the
        linked guild instead of the guild the adventure actually spawned in,
        then fires the same "adventure"/"adventure_boss"/"adventure_miniboss"/
        etc. events so any other cog listening in that guild - AdventureAlert,
        or another AdventureSync-style cog - reacts exactly as if the
        adventure had spawned there.

        dispatch_adventure() only fires "adventure" `if not was_exposed`,
        since it can be called a second time for the same session once a
        boss/miniboss gets revealed mid-adventure. That guard doesn't apply
        here - the linked guild has never seen this session before, so
        "adventure" always fires once. The sub-events still only fire when
        `session.easy_mode`, matching the same easy_mode gate this cog
        already uses to decide whether the monster is known yet at all.
        """
        relay = _RelaySession(session, guild=guild, channel=channel, message=message)
        self.bot.dispatch("adventure", relay)
        if relay.easy_mode:
            if relay.boss:
                self.bot.dispatch("adventure_boss", relay)
            elif relay.miniboss:
                self.bot.dispatch("adventure_miniboss", relay)

            if relay.transcended:
                self.bot.dispatch("adventure_transcended", relay)
            elif relay.ascended:
                self.bot.dispatch("adventure_ascended", relay)

            if relay.immortal:
                self.bot.dispatch("adventure_immortal", relay)
            elif relay.possessed:
                self.bot.dispatch("adventure_possessed", relay)
