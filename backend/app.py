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
    #  retries = 5
    #   for attempt in range(retries):
    #       try:
    #            delete_chroma_collection()  # Attempt to delete the collection
    #           break  # Exit loop if successful
    #       except Exception as e:
    #           print(f"Attempt {attempt + 1}: {e}")
    #          time.sleep(1)  # Wait before retrying

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
    symbol = data.get("symbol", "").upper().strip()

    if not symbol:
        return jsonify({"error": "Please provide a valid stock symbol for sentiment analysis."}), 400

    try:
        # Fetch top 3 latest news articles
        latest_articles = newsapi.get_everything(q=symbol, language="en", sort_by="publishedAt", page_size=3)
        latest_news = [
            {"title": article["title"], "description": article.get("description", ""), "url": article["url"]}
            for article in latest_articles.get("articles", [])
        ]

        # Fetch top 3 most relevant news articles
        relevant_articles = newsapi.get_everything(q=symbol, language="en", sort_by="relevancy", page_size=3)
        relevant_news = [
            {"title": article["title"], "description": article.get("description", ""), "url": article["url"]}
            for article in relevant_articles.get("articles", [])
        ]

        # Combine and remove duplicates
        combined_news = {article["url"]: article for article in latest_news + relevant_news}.values()
        limited_news = list(combined_news)[:5]  # Limit to top 5 unique articles

        # Extract content for sentiment analysis
        news_texts = [f"{article['title']} {article['description']}" for article in limited_news]

        # Perform sentiment analysis
        sentiment = SentimentAnalysis(news_texts).sentiment_analysis()

        # Extract article URLs
        links = [article["url"] for article in limited_news]

        return jsonify(
            {
                "sentiments": sentiment,  # Sentiment results
                "links": links,  # News links
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route("/api/chatbot", methods=["POST", "OPTIONS"])
def api_chatbot():
    # Handle CORS preflight
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json(silent=True) or {}
    question = (data.get("message") or data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "Missing 'message' or 'question' in request body."}), 400

    try:
        result = query_rag(question)
        return jsonify({"response": result}), 200
    except Exception as e:
        logging.exception("Error in /api/chatbot")
        return jsonify({"error": "An error occurred while processing your query."}), 500




if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
