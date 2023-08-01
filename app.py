from flask import Flask, request, render_template
from portfolio import Portfolio
from scraper import Scraper
from request_cache import RequestCache
from fund_factory import FundFactory
from stock_factory import StockFactory
from fund import Fund
from concurrent.futures import ThreadPoolExecutor
from flask_cors import CORS
from flask import jsonify


app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        symbols = request.form.get('symbols').split(',')
        shares_list = request.form.get('shares').split(',')
        shares = [int(share) for share in shares_list]

        portfolio = Portfolio()
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

        holdings = portfolio.holdings_table()
        return jsonify(holdings=holdings)

    return render_template('index.html')

def process_holding(holding, request_cache, portfolio):
    if isinstance(holding, Fund):
        holding.set_holdings_values()
        with ThreadPoolExecutor() as executor:
            executor.map(lambda sub_holding: process_holding(sub_holding, request_cache, portfolio), holding.holdings)
    else:
        portfolio.add_holding(holding)

if __name__ == "__main__":
    app.run(debug=True)
