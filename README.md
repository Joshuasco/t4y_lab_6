# GitHub Repositories: Fetch, Parse, Transform

Fetches public repository data for a GitHub user, parses and transforms the JSON records, and computes aggregate metrics including total stars, language distribution, and repository rankings.

Calls the [GitHub REST Repositories API](https://docs.github.com/en/rest/repos/repos#list-repositories-for-a-user).

How to run it: pip install requests, then python main.py

One thing I would improve with more time: Add pagination handling using the `Link` header to fetch and aggregate repositories across multiple pages.
