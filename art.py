from flask import Flask, request, jsonify, render_template
import requests
import os  # Для использования переменных окружения

app = Flask(__name__)

# Функция получения данных
def get_wb_goods(api_key, limit=10, offset=0, filter_nm_id=None):
    url = "https://discounts-prices-api.wildberries.ru/api/v2/list/goods/filter"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    params = {
        "limit": limit,
        "offset": offset
    }
    if filter_nm_id:
        params["filterNmID"] = filter_nm_id

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if data and 'data' in data and 'listGoods' in data['data']:
            return data['data']['listGoods']
        else:
            return "Данные не найдены"
    except requests.exceptions.RequestException as e:
        return f"Ошибка запроса: {e}"

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# API для обработки запроса
@app.route('/get_goods', methods=['POST'])
def get_goods():
    api_key = request.form.get('api_key')
    article = request.form.get('article')

    try:
        article = int(article)
        specific_goods = get_wb_goods(api_key, filter_nm_id=article)
        if isinstance(specific_goods, list) and specific_goods:
            for good in specific_goods:
                if good.get('nmID') == article:
                    return jsonify({
                        "price": good['sizes'][0].get('price', 'Цена не указана'),
                        "discounted_price": good['sizes'][0].get('discountedPrice', 'Цена со скидкой не указана')
                    })
        return jsonify({"error": "Товар не найден"})
    except ValueError:
        return jsonify({"error": "Некорректный артикул"})

# Для запуска на хостинге
if __name__ == "__main__":
    # Указываем host="0.0.0.0" и порт, чтобы Flask слушал на всех интерфейсах
    port = int(os.environ.get("PORT", 8080))  # Берём порт из переменной окружения (по умолчанию 8080)
    app.run(host="0.0.0.0", port=port)
