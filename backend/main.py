from fastapi import FastAPI
from pydantic import BaseModel
from google_play_scraper import Sort, reviews
from transformers import pipeline
import asyncio

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Load Sentiment Analysis Model
sentiment_pipeline = pipeline("sentiment-analysis")

class AppNameRequest(BaseModel):
    appName: str

import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()

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

    # True Async function
    async def analyze(text):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, sentiment_pipeline, text)

    tasks = [analyze(text) for text in review_texts]
    sentiments = await asyncio.gather(*tasks)

    # Calculate average sentiment score
    score_mapping = {'POSITIVE': 1, 'NEGATIVE': 0}
    scores = [score_mapping[s[0]['label']] for s in sentiments]
    avg_score = sum(scores) / len(scores) if scores else 0

    return {
        "average_sentiment_score": avg_score,
        "number_of_reviews_analyzed": len(scores)
    }
