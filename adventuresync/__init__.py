# -*- coding: utf-8 -*-
from .adventuresync import AdventureSync


async def setup(bot) -> None:
    cog = AdventureSync(bot)
    bot.add_cog(cog)
