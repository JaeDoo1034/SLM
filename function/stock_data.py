import json
from datetime import datetime, timedelta
from server import (
    inquery_stock_price,
    inquery_balance,
    order_stock,
    inquery_order_list,
    inquery_order_detail,
    inquery_stock_info,
    inquery_stock_history,
    inquery_stock_ask,
    order_overseas_stock,
    inquery_overseas_stock_price
)

class StockData():
    stock_code = ''

    def __init__(self, stock_code):
        self.stock_code = stock_code

    async def get_today_yield(self):
        # AAPL 현재가 조회
        result = await inquery_overseas_stock_price(
            symbol="AAPL",
            market="NASD"
        )
        print("\nOverseas Stock Price Response:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        return '금일 ' + self.stock_code + '의 수익률은 5%입니다.'