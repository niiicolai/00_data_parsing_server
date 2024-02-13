from flask import Flask, request
import json
import pandas as pd
import yaml
import requests
from requests.exceptions import HTTPError

app = Flask(__name__)

def fetch_data():
    text = None
    error = None
    try:
        url = request.args.get('url')
        response = requests.get(url)
        response.raise_for_status()
    except HTTPError as http_err:
        error = f'HTTP error occurred: {http_err}'
    except Exception as err:
        error = f'Other error occurred: {err}'
    else:
        text = response.text
    
    return { "text": text, "error": error }

def handle_response(data, parse_method):
    if data["error"]:
        return data["error"], 500
    else:
        if not data["text"]:
            return "File at URL is empty", 500
        else:
            return parse_method(data["text"])

@app.route("/csv.json")
def parse_csv():
    return pd.read_csv(request.args.get('url'), sep=(request.args.get('sep') or ',')).to_json()

@app.route("/json.json")
def parse_json():
    return handle_response(fetch_data(), lambda text: json.loads(text))

@app.route("/xml.json")
def parse_xml():
    return handle_response(fetch_data(), lambda text: pd.read_xml(text).to_json())

@app.route("/yaml.json")
def parse_yaml():
    return handle_response(fetch_data(), lambda text: json.dumps(yaml.safe_load(text)))
    
@app.route("/text.json")
def parse_text():
    return handle_response(fetch_data(), lambda text: json.dumps(text))

if __name__ == "__main__":
    app.run(debug=True)
