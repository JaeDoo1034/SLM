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


def get_stock_info(stock_code: str):
    result = call_sync(inquery_stock_price, stock_code)
    print("\nStock Info Response:")
    # print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\n({stock_code}):")
    print(f"sector: {result['bstp_kor_isnm']}")
    print(f"Current price: {result['stck_prpr']}")
    print(f"Change: {result['prdy_vrss']} ({result['prdy_ctrt']}%)")
    print(f"Volume: {result['acml_vol']}")
    print(f"Trading value: {result['acml_tr_pbmn']}")
    return result

def get_today_yield(stock_code: str):
    result = get_stock_info(stock_code=stock_code)
    return result['prdy_ctrt']

def get_industry(stock_code: str):
    result = get_stock_info(stock_code=stock_code)
    return result['bstp_kor_isnm']

if __name__ == "__main__":
    get_today_yield("005930")
    get_today_yield("069500")
