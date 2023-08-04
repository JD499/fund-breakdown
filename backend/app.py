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
CORS(app)  # This will enable CORS for all routes

portfolio = Portfolio()


@app.route('/receive', methods=['POST'])
def receive_data():
    symbols = request.form.get('symbols').split(',')
    shares_list = request.form.get('shares').split(',')
    shares = [int(share) for share in shares_list]

    request_cache = RequestCache()

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

    return jsonify({'message': 'Data received successfully'}), 200


@app.route('/return', methods=['GET'])
def return_data():
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
    app.run(debug=True)
