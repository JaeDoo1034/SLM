import json
from datetime import datetime, timedelta
from slm_mcp.mcp_server import (
    call_sync,
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


def get_today_yield(stock_code):
    # AAPL 현재가 조회
    result = call_sync(inquery_stock_price, stock_code)
    print("\nStock Info Response:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    return result['prdy_ctrt']