# GitHub Public Repositories Fetch & Transform

A Python script that fetches public repositories for a GitHub user, transforms the deeply nested and varied records, computes repository metrics (total stars, language breakdown, forks, and rankings) that cannot be seen directly in the raw response, and exports the clean records to CSV.

API: GitHub REST API ([GitHub Repositories API Documentation](https://docs.github.com/en/rest/repos/repos#list-repositories-for-a-user))

How to run it:
```bash
pip install requests
python main.py
```

One thing I would improve with more time: Add automatic pagination handling across multiple pages (`Link` header) and asynchronous batch fetching to retrieve full historical commit and contributor statistics.
