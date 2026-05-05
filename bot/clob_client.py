import hmac, hashlib, time, aiohttp
from bot.config import CLOB_BASE, POLY_API_KEY, POLY_API_SECRET, POLY_API_PASS
class ClobClient:
      def __init__(self, session): self._s = session
            async def get_markets(self, limit=20):
                      async with self._s.get(f"{CLOB_BASE}/markets", params={"limit": limit, "active": "true"}) as r:
                                    return (await r.json()).get("data", [])
                            async def get_book(self, token_id):
                                      async with self._s.get(f"{CLOB_BASE}/book", params={"token_id": token_id}) as r: return await r.json()
