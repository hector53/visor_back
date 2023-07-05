import requests

symbols_news = ['CBOT:ZS1!', 'CME:ES1!', 'NYMEX:CL1!']

news = []

headers = {
    'Origin': 'https://www.tradingview.com', "Accept-Encoding": "gzip, deflate, br", 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

for symbol in symbols_news:
    url = f'https://news-headlines.tradingview.com/headlines/?category=futures&lang=en&symbol={symbol}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        filtered_news = [item for item in response.json() if any(
            s in symbols_news for s in [s['symbol'] for s in item.get('relatedSymbols', [])])]
        news += filtered_news

# Eliminamos las noticias duplicadas
unique_news = []
for item in news:
    if item not in unique_news:
        unique_news.append(item)

# Ordenamos las noticias por timestamp en orden descendente (noticias más recientes primero)
unique_news.sort(key=lambda x: x['published'], reverse=True)

print("news", len(unique_news))
