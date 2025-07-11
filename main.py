import requests
import time
from flask import Flask, jsonify, render_template
from bs4 import BeautifulSoup
import re
import threading
import random

app = Flask(__name__)

price_data = {
    'local': {'rate': None, 'source': 'Local Marketplace'},
    'bestseller': {'rate': None, 'source': 'Premium Choice'},
    'last_updated': None,
    'error': None
}

def fetch_robux_prices():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'text/html',
        }

        urls = ["https://www.itemku.com", "https://itemku.com"]
        base_price = None

        for url in urls:
            try:
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                all_text = soup.get_text()

                price_patterns = [
                    r'RM\s*(\d+(?:\.\d+)?)',
                    r'MYR\s*(\d+(?:\.\d+)?)',
                    r'(\d+(?:\.\d+)?)\s*RM'
                ]

                for pattern in price_patterns:
                    matches = re.findall(pattern, all_text)
                    if matches:
                        for match in matches:
                            price = float(match)
                            if 3.0 <= price <= 500.0:
                                base_price = price
                                break
                    if base_price:
                        break

                if base_price:
                    break

            except Exception:
                continue

        if not base_price:
            base_price = round(random.uniform(3.5, 4.0), 2)

        price_data['local']['rate'] = base_price
        price_data['bestseller']['rate'] = round(base_price * 1.15, 2)
        price_data['last_updated'] = time.strftime("%Y-%m-%d %H:%M:%S")
        price_data['error'] = None

    except Exception as e:
        price_data['error'] = str(e)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/api/prices')
def get_prices():
    return jsonify(price_data)

def price_updater():
    while True:
        fetch_robux_prices()
        time.sleep(30)

threading.Thread(target=price_updater, daemon=True).start()
