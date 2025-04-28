"use client";

import { useState } from "react";
import axios from "axios";

export default function Home() {
  const [appName, setAppName] = useState("");
  const [averageSentiment, setAverageSentiment] = useState<number | null>(null);
  const [reviewCount, setReviewCount] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAnalyze = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.post("http://127.0.0.1:8000/analyze-reviews", {
        appName,
      });
      setAverageSentiment(response.data.average_sentiment_score);
      setReviewCount(response.data.number_of_reviews_analyzed);
    } catch (err: any) {
      console.error(err);
      setError("Failed to fetch sentiment analysis.");
    }
    setLoading(false);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8">
      <h1 className="text-3xl font-bold mb-6">Google Play Review Sentiment Analyzer</h1>

      <input
        type="text"
        value={appName}
        onChange={(e) => setAppName(e.target.value)}
        placeholder="Enter App Package Name"
        className="border p-2 rounded mb-4 w-80"
      />

      <button
        onClick={handleAnalyze}
        className="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600 transition"
      >
        Analyze
      </button>

      {loading && <p className="mt-4">Analyzing...</p>}

      {error && <p className="mt-4 text-red-500">{error}</p>}

      {averageSentiment !== null && reviewCount !== null && (
        <div className="mt-6">
          <p className="text-lg">Average Sentiment Score: <strong>{averageSentiment.toFixed(2)}</strong></p>
          <p className="text-lg">Number of Reviews Analyzed: <strong>{reviewCount}</strong></p>
        </div>
      )}
    </div>
  );
}
