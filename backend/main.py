from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google_play_scraper import Sort, reviews
from google_play_scraper.exceptions import NotFoundError
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

from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()

@app.post("/analyze-reviews")
async def analyze_reviews(request: AppNameRequest):
    app_id = request.appName

    loop = asyncio.get_running_loop()

    # Fetch reviews. google_play_scraper does blocking network I/O, so it runs in the thread pool;
    # called directly it froze the event loop (every other request) for the whole fetch.
    try:
        result, _ = await loop.run_in_executor(
            executor,
            lambda: reviews(app_id, lang='en', country='us', sort=Sort.NEWEST, count=100),
        )
    except NotFoundError:
        # A mistyped package name is the caller's error, not a server fault.
        raise HTTPException(status_code=404, detail=f"No app found with id {app_id!r}")
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail=f"Could not fetch reviews for {app_id!r}: {exc}"
        ) from exc

    review_texts = [r['content'] for r in result if r.get('content')]

    # True Async function
    async def analyze(text):
        # The model accepts at most 512 tokens and Play Store reviews can run to 4000 characters;
        # without truncation one long review raised inside the pipeline and failed the whole request.
        return await loop.run_in_executor(
            executor, lambda: sentiment_pipeline(text, truncation=True, max_length=512)
        )

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
