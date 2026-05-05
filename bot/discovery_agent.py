import asyncio, aiohttp
from bot.clob_client import ClobClient
async def main():
      async with aiohttp.ClientSession() as session:
                clob = ClobClient(session)
                markets = await clob.get_markets()
                print(f"Scanned {len(markets)} markets")
        if __name__ == "__main__": asyncio.run(main())
