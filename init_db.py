import asyncio

import models
from database import engine, base

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)

asyncio.run(init_db())