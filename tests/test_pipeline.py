"""
Unit tests for Day 6 Lab pipeline functions.
Tests normal execution, edge cases, and graceful degradation under network errors.
"""

import os
import sys

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import MagicMock, patch
import requests
from api.github import fetch_repos
from main import to_records, summarise, write_csv


def test_fetch_repos_success():
    mock_resp = MagicMock()
    mock_resp.json.return_value = [{"name": "repo1", "stargazers_count": 10}]
    mock_resp.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_resp):
        data = fetch_repos("testuser")
        assert data == [{"name": "repo1", "stargazers_count": 10}]


def test_fetch_repos_timeout():
    with patch("requests.get", side_effect=requests.exceptions.Timeout("Timed out")):
        data = fetch_repos("testuser")
        assert data is None


def test_fetch_repos_http_error():
    mock_resp = MagicMock()
    http_err = requests.exceptions.HTTPError(response=mock_resp)
    with patch("requests.get", side_effect=http_err):
        data = fetch_repos("testuser")
        assert data is None


def test_fetch_repos_connection_error():
    with patch("requests.get", side_effect=requests.exceptions.ConnectionError("Host not found")):
        data = fetch_repos("testuser")
        assert data is None


def test_to_records_graceful_missing_fields():
    raw_data = [
        # Normal record
        {
            "name": "full-repo",
            "stargazers_count": 100,
            "forks_count": 20,
            "language": "Python",
            "license": {"name": "MIT"},
            "open_issues_count": 2,
            "fork": False,
            "size": 500,
            "html_url": "https://github.com/test/full-repo",
            "updated_at": "2026-01-01T00:00:00Z",
        },
        # Record with missing/None fields (malformed / missing field bonus requirement)
        {
            "name": None,
            "stargazers_count": None,
            "forks_count": None,
            "language": None,
            "license": None,
            "open_issues_count": None,
            "fork": None,
            "size": None,
            "html_url": None,
            "updated_at": None,
        },
        # Malformed item (not a dict)
        "invalid_item",
    ]

    records = to_records(raw_data)
    assert len(records) == 2

    # Verify first record
    assert records[0]["name"] == "full-repo"
    assert records[0]["stars"] == 100
    assert records[0]["language"] == "Python"
    assert records[0]["license"] == "MIT"

    # Verify second record handled gracefully without crashing
    assert records[1]["name"] == "unnamed_repo"
    assert records[1]["stars"] == 0
    assert records[1]["language"] == "Unspecified"
    assert records[1]["license"] == "None"


def test_summarise():
    records = [
        {"name": "repoA", "stars": 100, "forks": 10, "language": "Python", "is_fork": False},
        {"name": "repoB", "stars": 50, "forks": 5, "language": "Python", "is_fork": True},
        {"name": "repoC", "stars": 150, "forks": 25, "language": "C", "is_fork": False},
        {"name": "repoD", "stars": 0, "forks": 0, "language": "Unspecified", "is_fork": False},
    ]

    summary = summarise(records)
    assert summary["total_repos"] == 4
    assert summary["total_stars"] == 300
    assert summary["total_forks"] == 40
    assert summary["average_stars"] == 75.0
    assert summary["top_repo_name"] == "repoC"
    assert summary["top_repo_stars"] == 150
    assert summary["original_repos"] == 3
    assert summary["forked_repos"] == 1
    assert summary["missing_language_count"] == 1

    # Check language breakdown
    lang_map = {l["language"]: l for l in summary["languages"]}
    assert lang_map["Python"]["repos"] == 2
    assert lang_map["Python"]["stars"] == 150
    assert lang_map["Python"]["percentage"] == 50.0
    assert lang_map["C"]["repos"] == 1
    assert lang_map["C"]["stars"] == 150
    assert lang_map["Unspecified"]["repos"] == 1


def test_write_csv(tmp_path):
    records = [
        {"name": "r1", "stars": 10, "language": "Python"},
        {"name": "r2", "stars": 20, "language": "C"},
    ]
    test_csv = os.path.join(tmp_path, "output.csv")
    result = write_csv(records, test_csv)
    assert result is True
    assert os.path.exists(test_csv)

    with open(test_csv, "r", encoding="utf-8") as f:
        lines = f.readlines()
    assert len(lines) == 3
    assert "name,stars,language" in lines[0]


if __name__ == "__main__":
    import tempfile
    test_fetch_repos_success()
    test_fetch_repos_timeout()
    test_fetch_repos_http_error()
    test_fetch_repos_connection_error()
    test_to_records_graceful_missing_fields()
    test_summarise()
    with tempfile.TemporaryDirectory() as td:
        test_write_csv(td)
    print("All pipeline unit tests passed successfully!")
