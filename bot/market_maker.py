class MarketMaker:
      def __init__(self, clob, risk, session): self.clob, self.risk, self.session = clob, risk, session
            async def quote(self, token_id, size): return {"status": "quoted", "token_id": token_id, "size": size}
