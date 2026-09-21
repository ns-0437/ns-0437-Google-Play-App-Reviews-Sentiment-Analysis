"""Fixtures for the API tests.

The real endpoint needs a ~250 MB sentiment model and live Play Store access, so the two heavy
dependencies (`transformers`, `google_play_scraper`) are replaced with small stand-ins that are
installed in sys.modules before `main` is imported. That keeps the suite fast, offline and
runnable with just fastapi, httpx and pytest.
"""
import pathlib
import sys
import threading
import types

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

state = types.SimpleNamespace()


def _reset_state():
    state.reviews_result = []
    state.reviews_error = None
    state.reviews_thread = None
    state.pipeline_kwargs = []


def _install_stubs():
    class NotFoundError(Exception):
        pass

    exceptions = types.ModuleType("google_play_scraper.exceptions")
    exceptions.NotFoundError = NotFoundError

    scraper = types.ModuleType("google_play_scraper")
    scraper.Sort = types.SimpleNamespace(NEWEST="newest")
    scraper.exceptions = exceptions

    def reviews(app_id, **kwargs):
        state.reviews_thread = threading.current_thread()
        if state.reviews_error is not None:
            raise state.reviews_error
        return list(state.reviews_result), None

    scraper.reviews = reviews

    transformers = types.ModuleType("transformers")

    def pipeline(task):
        def run(text, **kwargs):
            state.pipeline_kwargs.append(kwargs)
            label = "POSITIVE" if "good" in text else "NEGATIVE"
            return [{"label": label, "score": 0.99}]

        return run

    transformers.pipeline = pipeline

    sys.modules["google_play_scraper"] = scraper
    sys.modules["google_play_scraper.exceptions"] = exceptions
    sys.modules["transformers"] = transformers


_reset_state()
_install_stubs()

from fastapi.testclient import TestClient  # noqa: E402

import main  # noqa: E402


@pytest.fixture
def api_state():
    _reset_state()
    return state


@pytest.fixture
def client():
    return TestClient(main.app)
