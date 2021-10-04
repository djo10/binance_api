from datetime import datetime

from fastapi import FastAPI, Response
from fastapi_utils.tasks import repeat_every

from .apihandler import get_24h, get_order_book, get_symbols

app = FastAPI()


session = {
    "symbol_spreads": {}  # symbol: [spread, delta]
}


@app.get("/metrics")
def home():
    output = ""
    for s, l in session["symbol_spreads"].items():
        output += """symbol_prices{symbol="%s",type="spread"} %s\n""" % (s, l[0])
        output += """symbol_prices{symbol="%s",type="spread_delta"} %s\n""" % (s, l[1])
    return Response(content=output, media_type="application/text")


@app.on_event("startup")
@repeat_every(seconds=10, wait_first=True)
def get_spreads_tick():
    dt = datetime.now()
    print(dt)
    previous_spreads = session["symbol_spreads"]
    new_spreads = get_spreads(previous_spreads.keys())
    deltas = {symbol: [new_spread, abs(new_spread - previous_spreads[symbol][0])]
              for symbol, new_spread in new_spreads.items()}

    for s, l in deltas.items():
        print("%s spread: %s, delta: %s" % (s, l[0], l[1]))

    session["symbol_spreads"] = deltas


def get_spreads(symbols):
    def get_spread(symbol):
        info = get_24h({"symbol": symbol})
        return float(info["askPrice"]) - float(info["bidPrice"])
    return {s: get_spread(s) for s in symbols}


@app.on_event("startup")
@app.get("/results")
async def get_results(volume_asset="BTC", trade_asset="USDT", count=5):

    tick_24h = get_24h()

    symbols_info = get_symbols()
    symbols_dict = {s["symbol"]: s for s in symbols_info}

    volume_symbols = [s for s in tick_24h if symbols_dict[s["symbol"]]["quoteAsset"] == volume_asset]
    volume = [[s["symbol"], float(s["volume"]) + float(s["quoteVolume"])] for s in volume_symbols]
    top_by_volume = sorted(volume, key=lambda x: x[1], reverse=True)[:count]
    top_by_volume_symbols = [v[0] for v in top_by_volume]
    print("Top symbols by volume (volume + quoteVolume): %s" % ", ".join(top_by_volume_symbols))

    trade_symbols = [s for s in tick_24h if symbols_dict[s["symbol"]]["quoteAsset"] == trade_asset]
    top_by_trade = sorted(trade_symbols, key=lambda x: x["count"], reverse=True)[:count]
    top_by_trade_symbols = [v["symbol"] for v in top_by_trade]
    print("Top symbols by trade count: %s" % ", ".join(top_by_trade_symbols))

    order_book_totals = {}
    for s in top_by_volume_symbols:
        order_book = get_order_book({"symbol": s, "limit": 500})
        bids_total = sum([float(b[0]) * float(b[1]) for b in order_book["bids"][:200]])
        asks_total = sum([float(b[0]) * float(b[1]) for b in order_book["asks"][:200]])
        order_book_totals[s] = {"bids_total": str(bids_total), "asks_total": str(asks_total)}

    print("Order book totals, latest 200: %s" % order_book_totals)

    symbol_spreads = {symbol: [spread, spread] for symbol, spread in get_spreads(top_by_trade_symbols).items()}
    session["symbol_spreads"] = symbol_spreads
    print("Symbols price spread: %s" % ", ".join(["%s: %s" % (s, l[0]) for s, l in symbol_spreads.items()]))

    return {
        "top_5_volume": top_by_volume_symbols,
        "top_5_trade_count": top_by_trade_symbols,
        "total_bids_asks_value": order_book_totals,
        "price_spread": {s: l[0] for s, l in symbol_spreads.items()}
    }
