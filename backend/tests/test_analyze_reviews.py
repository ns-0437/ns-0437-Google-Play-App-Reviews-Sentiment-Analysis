def test_scores_the_share_of_positive_reviews(client, api_state):
    api_state.reviews_result = [{"content": "good app"}, {"content": "bad app"}, {"content": None}]
    response = client.post("/analyze-reviews", json={"appName": "com.example.app"})
    assert response.status_code == 200
    assert response.json() == {"average_sentiment_score": 0.5, "number_of_reviews_analyzed": 2}


def test_scraper_runs_in_the_thread_pool_not_on_the_event_loop(client, api_state):
    """google_play_scraper does blocking network I/O; called directly from the async endpoint it
    froze the event loop, and with it every other request, for the whole fetch."""
    api_state.reviews_result = [{"content": "good app"}]
    assert client.post("/analyze-reviews", json={"appName": "com.example.app"}).status_code == 200
    assert api_state.reviews_thread is not None
    assert api_state.reviews_thread.name.startswith("ThreadPoolExecutor")
