import csv
import os
from flask import Flask, request, jsonify
import yfinance as yf
from flask_cors import CORS
from sentiment_analysis import SentimentAnalysis
from newsapi import NewsApiClient  # Import News API Client
import logging
from bot import query_rag
from chromadb import PersistentClient
import time

app = Flask(__name__)
CORS(app)

COLLECTION_NAME = "stock_news"

newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))


@app.route("/query", methods=["POST"])
def query():
    data = request.json
    question = data.get("question")

    try:
        result = query_rag(question)
        return jsonify({"response": result})
    except Exception as e:
        logging.error(f"Error processing query: {e}")
        return jsonify({"error": "An error occurred while processing your query."}), 500


@app.route("/api/stock", methods=["GET"])
def stock():
    symbol = request.args.get("symbol", default="AAPL", type=str).upper().strip()

    # Check if symbol is provided
    if not symbol:
        return jsonify({"error": "Please provide a valid stock symbol."}), 400

    ticker = yf.Ticker(symbol)

    try:
        quote = ticker.info
        print(quote)

        if "regularMarketOpen" in quote:
            current_price = quote["regularMarketOpen"]
            return jsonify(
                {
                    "symbol": symbol,
                    "currentPrice": current_price,
                    "longName": quote.get("longName", "N/A"),
                    "error": None,
                }
            ), 200
        else:
            return jsonify(
                {"error": "Stock not found or no current price available"}
            ), 404
    except Exception as e:
        print("Error fetching data:", e)
        return jsonify({"error": str(e)}), 500


def delete_chroma_collection():
    try:
        chroma_client = PersistentClient(path="chroma_stock")
        chroma_client.delete_collection(COLLECTION_NAME)
        print(f"Collection {COLLECTION_NAME} deleted successfully.")
    except Exception as e:
        raise Exception(f"Unable to delete collection: {e}")


@app.route("/stock_data/<symbol>")
def stock_data(symbol):
    # Attempt to delete the Chroma database with retry logic
    # retries = 5
    # for attempt in range(retries):
    #     try:
    #         delete_chroma_collection()  # Attempt to delete the collection
    #         break  # Exit loop if successful
    #     except Exception as e:
    #         print(f"Attempt {attempt + 1}: {e}")
    #         time.sleep(1)  # Wait before retrying

    # Fetch stock data
    stock = yf.Ticker(symbol)
    data = stock.history(period="1mo")

    if data.empty:
        return jsonify({"error": "No data found for the symbol provided."})

    prices = data["Close"].to_dict()
    labels = list(prices.keys())
    values = list(prices.values())

    return jsonify({"labels": labels, "values": values})


@app.route("/api/sentiments", methods=["POST"])
def sentiment():
    data = request.json
    symbol = data.get("symbol")

    # Validate symbol
    if not symbol:
        return jsonify(
            {"error": "Please provide a valid stock symbol for sentiment analysis."}
        ), 400

    try:
        # Fetch news articles using NewsAPI, only for the provided symbol
        articles = newsapi.get_everything(q=symbol, language="en", sort_by="relevancy")
        news = [
            {"title": article["title"], "description": article["description"]}
            for article in articles["articles"]
        ]

        with open("backend\\news_file.csv", "w", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter="|")
            writer.writerow(["link", "content"])
            for article in news:
                writer.writerow([article["title"], article["description"]])

        # Extract titles and descriptions for sentiment analysis
        all_parsed_results = [
            item["title"] + " " + (item["description"] or "") for item in news
        ]

        if not all_parsed_results:
            return jsonify({"error": "No data found for sentiment analysis"}), 404

        # Perform sentiment analysis on the fetched news
        sentiment = SentimentAnalysis(all_parsed_results).sentiment_analysis()
        print(sentiment)

        # Collect the links of articles
        links = [article["url"] for article in articles["articles"]]

        return jsonify(
            {
                "sentiments": sentiment[0:5],
                "links": links[0:5],
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/chatbot", methods=["POST"])
def chatbot():
    data = request.json
    question = data.get("question")

    if not question:
        return jsonify({"error": "Please provide a question."}), 400

    response = query_rag(question)

    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=True)
