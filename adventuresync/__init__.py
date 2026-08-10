# -*- coding: utf-8 -*-
from redbot.core.bot import Red

from .adventuresync import AdventureSync


async def setup(bot: Red) -> None:
    await bot.add_cog(AdventureSync(bot))
