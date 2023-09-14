from concurrent.futures import ThreadPoolExecutor

from flask import Flask, request, jsonify
from flask_cors import CORS

from fund import Fund
from fund_factory import FundFactory
from portfolio import Portfolio
from request_cache import RequestCache
from scraper import Scraper
from stock_factory import StockFactory

app = Flask(__name__)
CORS(app)


@app.route('/data', methods=['POST'])
def receive_and_return_data():
    portfolio = Portfolio()
    request_data = request.json
    request_portfolio = request_data['portfolio']

    request_cache = RequestCache()

    symbols = [item['symbol'] for item in request_portfolio]
    shares = [int(item['shares']) for item in request_portfolio]

    with ThreadPoolExecutor() as executor:
        data_list = list(executor.map(lambda symbol: Scraper(symbol, request_cache).get_data(), symbols))

    for data, share in zip(data_list, shares):
        if data["is_fund"]:
            fund = FundFactory.create(data, request_cache)
            fund.shares = share
            process_holding(fund, request_cache, portfolio)
        else:
            stock = StockFactory.create(data)
            stock.shares = share
            portfolio.add_holding(stock)

    holdings = portfolio.holdings_table()
    return jsonify(holdings=holdings), 200



def process_holding(holding, request_cache, portfolio):
    if isinstance(holding, Fund):
        holding.set_holdings_values()
        with ThreadPoolExecutor() as executor:
            executor.map(lambda sub_holding: process_holding(sub_holding, request_cache, portfolio), holding.holdings)
    else:
        portfolio.add_holding(holding)


if __name__ == '__main__':
    app.run()
