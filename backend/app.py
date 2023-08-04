from concurrent.futures import ThreadPoolExecutor

from flask import Flask, request, jsonify, session, abort
from flask_cors import CORS
from flask_session import Session

from fund import Fund
from fund_factory import FundFactory
from portfolio import Portfolio
from request_cache import RequestCache
from scraper import Scraper
from stock_factory import StockFactory

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# Check Flask-Session docs for different types of sessions
# Here, we'll use filesystem-based sessions
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

portfolio = Portfolio()


@app.route('/receive', methods=['POST'])
def receive_data():
    try:
        symbols = request.form.get('symbols')
        shares_list = request.form.get('shares')

        if not symbols or not shares_list:
            abort(400, description="Missing symbols or shares parameters")

        symbols = symbols.split(',')
        shares_list = shares_list.split(',')
        shares = [int(share) for share in shares_list]

        # Store symbols and shares in session
        session['symbols'] = symbols
        session['shares'] = shares

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

    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        abort(500, description="An error occurred while processing your request")


@app.route('/return', methods=['GET'])
def return_data():
    # Retrieve symbols and shares from session
    symbols = session.get('symbols')
    shares = session.get('shares')

    if not symbols or not shares:
        abort(400, description="No data in session")

    # Rest of the code...

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
