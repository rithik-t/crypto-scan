from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

def check_token_info(token_name):
    try:
        # Ensure the token name is in a valid format (e.g., lowercase, no spaces)
        token_name = token_name.strip().lower()
        if not token_name.isalnum():
            return {"status": "error", "message": "Invalid token name. Please enter a valid cryptocurrency token name."}

        url = f"https://api.coingecko.com/api/v3/coins/{token_name}"
        res = requests.get(url)
        data = res.json()

        if 'error' in data:
            return {"status": "not_found", "message": "Token not found in the database."}

        market_data = data.get("market_data", {})
        score = {
            "is_risky": False,
            "market_cap": market_data.get("market_cap", {}).get("usd", 0),
            "holders": "Not Available",
            "liquidity": "Not Available",
            "symbol": data.get("symbol", "")
        }

        # Simple flagging rule: if no market cap or it's very low
        if score["market_cap"] < 1000000:
            score["is_risky"] = True

        return {"status": "found", "result": score}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"API request failed: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check():
    token = request.form.get('token')
    if not token:
        return jsonify({"status": "error", "message": "Token name is required!"})

    result = check_token_info(token)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
