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


def test_unknown_app_id_is_a_404_not_a_500(client, api_state):
    from google_play_scraper.exceptions import NotFoundError

    api_state.reviews_error = NotFoundError("app not found")
    response = client.post("/analyze-reviews", json={"appName": "com.does.not.exist"})
    assert response.status_code == 404
    assert "com.does.not.exist" in response.json()["detail"]


def test_scraper_failure_is_a_502_with_a_message(client, api_state):
    api_state.reviews_error = RuntimeError("play store unreachable")
    response = client.post("/analyze-reviews", json={"appName": "com.example.app"})
    assert response.status_code == 502
    assert "play store unreachable" in response.json()["detail"]


def test_reviews_are_truncated_to_the_model_limit(client, api_state):
    """distilbert-sst2 accepts 512 tokens; a longer review raises unless truncation is on."""
    api_state.reviews_result = [{"content": "good " * 2000}]
    assert client.post("/analyze-reviews", json={"appName": "com.example.app"}).status_code == 200
    assert api_state.pipeline_kwargs == [{"truncation": True, "max_length": 512}]


def test_cors_does_not_allow_credentials_for_arbitrary_origins(client):
    """allow_credentials=True together with a wildcard origin makes Starlette reflect whatever
    Origin the caller sends as a credentialed, trusted origin."""
    response = client.options(
        "/analyze-reviews",
        headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"},
    )
    assert "access-control-allow-credentials" not in response.headers
