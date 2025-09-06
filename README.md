# Stock News Sentiment Analysis Platform
![DALL·E-2024-10-30-22 57](ss.png)
![sap_stocks](https://github.com/user-attachments/assets/dc342b2e-c589-4f2a-bf9a-b87e8245daa5)
![sap_stock2](https://github.com/user-attachments/assets/810bb33c-d115-41d0-92f5-1fb67005f675)

This platform provides real-time sentiment analysis on stock-related news. It fetches news from over 60 different sources and performs sentiment classification. Additionally, it integrates an AI chatbot that allows users to query the fetched news using a Retrieval-Augmented Generation (RAG) model.

## Features
- **Real-Time Data Fetching:** 
  - Scrapes news from over 60+ websites using Selenium for web scraping.
  - Extracts and parses relevant news using Llama 3.2 LLM.

  
- **Sentiment Analysis:** 
  - Utilizes the finBERT text classification model to classify news as "positive," "negative," or "neutral."

- **AI Chatbot for News Querying:**
  - Implements a RAG-based AI chatbot using Langchain and ChromaDB.
  - Utilizes the Gemini-1.5-Flash LLM as the base model for natural language querying of news articles.

## Technology Stack

- **Selenium:** Used for web scraping to fetch real-time news data from various websites.
- **Langchain:** Framework for building the RAG-based AI chatbot.
- **ChromaDB:** Vector database used for efficient semantic search and document retrieval.
- **Ollama API & Gemini API Platform:** For handling and deploying LLM models like Gemini-1.5-Flash for chatbot functionality.
- **Llama 3.2 LLM:** Used to parse HTML responses and extract relevant news articles.
- **finBERT:** Specialized model for sentiment analysis in financial texts, classifying news as positive, negative, or neutral.

## Installation (Without Docker)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/stock-news-sentiment-analysis-platform.git
   cd stock-news-sentiment-analysis-platform
   ```

2. **Set up a virtual environment (optional but recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API keys/Model Manifests:**
   - You need to set up environment variables or configuration files for the following APIs:
     - **Gemini API** (for querying news)
     - **Ollama Instance** (for Llama 3.2 LLM)
     - **finBERT** (for sentiment classification)

5. **Run the application:**
   ```bash
   python main.py
   ```
# Using Docker

The platform is containerized using Docker for easy setup and deployment. Here's how to run the platform with Docker:

## Prerequisites

Ensure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

---

## Steps to Build and Run

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/stock-news-sentiment-analysis-platform.git
cd stock-news-sentiment-analysis-platform
```

### 2. Set Up Environment Variables
  Create a .env file in the root directory and add the required API keys:
```bash
NEWS_API_KEY=your_news_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. Build and Start the Docker Containers
  Run the following commands to build and start the services:
```bash
docker-compose up --build
```
This will:
- Build the backend and frontend services.
- Start the Flask backend on http://localhost:5000.
- Start the ReactJS frontend on http://localhost:3000

### 4. 4. Access the Platform
  Open your browser and navigate to:
- Frontend: http://localhost:3000
- Backend (API): http://localhost:5000

## Usage

### 1. **Fetching and Analyzing Stock News**
   The platform scrapes real-time stock news and performs sentiment analysis using finBERT. The classified news is stored in a database for querying and further analysis.

### 2. **Querying News with AI Chatbot**
   The platform includes a chatbot interface where users can query the news using natural language. The chatbot uses Langchain's RAG model with ChromaDB and the Gemini-1.5-Flash LLM to deliver contextual answers based on the news.

   Example queries:
   - "What is the latest news about Tesla?"
   - "Show me positive news on Apple stock."

## Project Structure

- `backend/app.py`: Contains Flask backend server.
- `backend/bot.py`: Code for RAG Pipeline.
- `backend/sentiment_analysis.py`: Inference on finBERT text classification model.
- `backend/web_scrape.py`:Contain data fetching pipeline to scrape latest news and save to scraped_news.json.
- `frontend/`:Reactjs library for frontend .

## Future Improvements

- Add more advanced NLP models for better parsing of financial data.
- Expand sentiment classification to handle more nuanced market sentiments like "bullish" and "bearish."
- Integrate with more news sources for broader coverage.

## Contributing

Feel free to contribute by opening issues or submitting pull requests!
