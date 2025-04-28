from fastapi import FastAPI
from pydantic import BaseModel
from google_play_scraper import Sort, reviews
from transformers import pipeline
import asyncio

app = FastAPI()

# Load Sentiment Analysis Model
sentiment_pipeline = pipeline("sentiment-analysis")

class AppNameRequest(BaseModel):
    appName: str

@app.post("/analyze-reviews")
async def analyze_reviews(request: AppNameRequest):
    app_id = request.appName

    # Fetch reviews
    result, _ = reviews(
        app_id,
        lang='en',
        country='us',
        sort=Sort.NEWEST,
        count=100,
    )

    review_texts = [r['content'] for r in result if r.get('content')]

    # Analyze sentiments asynchronously
    async def analyze(text):
        return sentiment_pipeline(text)[0]

    tasks = [analyze(text) for text in review_texts]
    sentiments = await asyncio.gather(*tasks)

    # Calculate average sentiment score
    score_mapping = {'POSITIVE': 1, 'NEGATIVE': 0}
    scores = [score_mapping[s['label']] for s in sentiments]
    avg_score = sum(scores) / len(scores) if scores else 0

    return {
        "average_sentiment_score": avg_score,
        "number_of_reviews_analyzed": len(scores)
    }
