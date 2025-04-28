# 📱 Google Play Store Review Sentiment Analyzer

A fullstack application that fetches latest reviews of any Android app from Play Store and predicts overall sentiment.

---

## 🚀 Tech Stack

- **Backend**: FastAPI, HuggingFace Transformers, google-play-scraper
- **Frontend**: Next.js (TypeScript), Tailwind CSS
- **Model Used**: `distilbert-base-uncased-finetuned-sst-2-english` (via Huggingface)

---

## 🛠 Features

- Input Android App Package Name (e.g., `com.instagram.android`)
- Fetch 100 latest reviews directly
- Perform real-time Sentiment Analysis
- Display:
  - Average Sentiment Score
  - Number of Reviews Analyzed

---

## 🌐 Setup Instructions

### Backend

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

Backend will run at: http://127.0.0.1:8000/docs

---

### frontend

```bash
cd frontend
npm install
npm run dev

---

Frontend will run at: http://localhost:3000
