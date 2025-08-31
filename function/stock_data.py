import json
from datetime import datetime, timedelta
from pandas.tseries.offsets import BDay
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
    result = get_stock_info(stock_code=stock_code)['prdy_ctrt'] + "%"
    if result[0] != '-':
        result = "+" + result
    return result

def get_today_price_yield(stock_code: str):
    result = get_stock_info(stock_code=stock_code)
    current_price = result['stck_prpr']
    yield_data = result['prdy_ctrt'] + "%"
    if yield_data[0] != '-':
        yield_data = "+" + yield_data
    return current_price, yield_data

def get_industry(stock_code: str):
    result = get_stock_info(stock_code=stock_code)
    return result['bstp_kor_isnm']

def get_business_day(date: str = datetime.now().strftime("%Y%m%d")):
    _date = datetime.strptime(date, "%Y%m%d")
    if _date.weekday() > 4:
        return (_date - BDay(1)).strftime("%Y%m%d")
    return _date.strftime("%Y%m%d")

if __name__ == "__main__":
    #get_today_price_yield("005930")
    #get_today_price_yield("069500")

    print(get_business_day())

