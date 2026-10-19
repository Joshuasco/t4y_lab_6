"""
GitHub API Client Module for Day 6 Lab: Fetch, Parse, Transform.
Provides fetch functionality with proper query params, timeouts,
and specific error handling as required by the lab specification.
"""

import requests

BASE_URL = "https://api.github.com/users/torvalds/repos"


def fetch_repos(username="torvalds", per_page=100):
    """
    Call the GitHub API to fetch public repositories for a given user.
    Returns parsed JSON (list of repository dicts), or None if something went wrong.
    """
    url = f"https://api.github.com/users/{username}/repos"
    params = {"per_page": per_page}
    headers = {"User-Agent": "tech4youth-lab6-fetcher"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print("The request timed out.")
        return None
    except requests.exceptions.HTTPError as err:
        print(f"The API rejected the request: {err}")
        return None
    except requests.exceptions.RequestException as err:
        print(f"Could not reach the service: {err}")
        return None

    return response.json()


def request_repo(username="torvalds", per_page=100):
    """
    Backward-compatible alias for fetch_repos that returns the parsed JSON.
    """
    return fetch_repos(username=username, per_page=per_page)