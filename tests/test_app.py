"""Offline checks: the LLM is mocked, so these need no key, model or network."""
import json
import os
from pathlib import Path

os.environ["LLM_PROVIDER"] = "ollama"
ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import main  # noqa: E402
from agents.base_agent import BaseAgent  # noqa: E402

SAMPLE = ROOT / "resumes" / "sample_resume.pdf"


@pytest.fixture
def client():
    return TestClient(main.app)


def test_pages_render(client):
    assert client.get("/").status_code == 200
    assert client.get("/recruiter").status_code == 200


def test_candidates_endpoint(client):
    response = client.get("/api/recruiter/candidates")
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_no_key_is_committed_in_config():
    from config import Config

    assert Config.NEBIUS_API_KEY == os.getenv("NEBIUS_API_KEY", "")


class NoSearch:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def text(self, query, max_results=5):
        return []


def test_candidate_pipeline_on_the_sample_resume(client, monkeypatch):
    monkeypatch.setattr(BaseAgent, "_query_llm", lambda self, prompt: json.dumps({"ok": True}))
    monkeypatch.setattr("duckduckgo_search.DDGS", NoSearch)
    with SAMPLE.open("rb") as resume:
        response = client.post(
            "/api/candidate/analyze",
            files={"file": ("sample_resume.pdf", resume, "application/pdf")},
        )
    assert response.status_code == 200
    assert response.json().get("status") == "success", response.json()
