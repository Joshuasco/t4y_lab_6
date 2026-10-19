"""
Day 6 Lab: Fetch, Parse, Transform
Fetches public repositories from the GitHub API, parses and transforms the data,
computes non-trivial aggregations (stars, language breakdown, rankings),
handles missing/malformed fields gracefully, and exports the records to CSV.
"""

import csv
import sys
from api.github import fetch_repos as api_fetch_repos


# Function 1: fetch_*
def fetch_repos(username="torvalds", per_page=100):
    """
    Calls the GitHub API to fetch repositories for a user.
    Returns parsed JSON data (list of dictionaries) or None if something went wrong.
    """
    return api_fetch_repos(username=username, per_page=per_page)


# Function 2: to_records
def to_records(data):
    """
    Turns the raw API response into a clean list of dictionaries, one per repository.
    Handles missing or malformed fields gracefully.
    """
    if not isinstance(data, list):
        print("Invalid data format: expected a list of repositories.")
        return []

    records = []
    for item in data:
        if not isinstance(item, dict):
            continue

        # Safely extract and normalize fields
        name = item.get("name") or "unnamed_repo"
        stars = int(item.get("stargazers_count") or 0)
        forks = int(item.get("forks_count") or 0)

        # Handle missing or None language gracefully (bonus requirement)
        raw_lang = item.get("language")
        language = str(raw_lang).strip() if raw_lang else "Unspecified"

        # Handle nested or missing license safely
        license_obj = item.get("license")
        if isinstance(license_obj, dict):
            license_name = license_obj.get("name") or "Unspecified"
        elif isinstance(license_obj, str):
            license_name = license_obj
        else:
            license_name = "None"

        open_issues = int(item.get("open_issues_count") or 0)
        is_fork = bool(item.get("fork", False))
        size_kb = int(item.get("size") or 0)
        html_url = item.get("html_url") or ""
        updated_at = item.get("updated_at") or "Unknown"

        records.append({
            "name": name,
            "stars": stars,
            "forks": forks,
            "language": language,
            "license": license_name,
            "open_issues": open_issues,
            "is_fork": is_fork,
            "size_kb": size_kb,
            "html_url": html_url,
            "updated_at": updated_at,
        })

    return records


# Function 3: summarise
def summarise(records):
    """
    Reduces repository records to key summary metrics that are not
    directly visible in the raw JSON response.
    Returns a dictionary of calculated metrics.
    """
    if not records:
        return {}

    total_repos = len(records)
    total_stars = sum(r["stars"] for r in records)
    total_forks = sum(r["forks"] for r in records)
    average_stars = round(total_stars / total_repos, 2) if total_repos > 0 else 0.0

    # Find the top starred repository
    top_repo = max(records, key=lambda r: r["stars"], default=None)

    # Language breakdown: count of repos, total stars, and percentage
    lang_stats = {}
    missing_lang_count = 0
    fork_count = 0

    for r in records:
        lang = r["language"]
        if lang == "Unspecified":
            missing_lang_count += 1

        if r["is_fork"]:
            fork_count += 1

        if lang not in lang_stats:
            lang_stats[lang] = {"repo_count": 0, "total_stars": 0}
        lang_stats[lang]["repo_count"] += 1
        lang_stats[lang]["total_stars"] += r["stars"]

    # Rank languages by number of repositories descending
    ranked_languages = sorted(
        [
            {
                "language": lang,
                "repos": stats["repo_count"],
                "stars": stats["total_stars"],
                "percentage": round((stats["repo_count"] / total_repos) * 100, 1),
            }
            for lang, stats in lang_stats.items()
        ],
        key=lambda x: (x["repos"], x["stars"]),
        reverse=True,
    )

    return {
        "total_repos": total_repos,
        "total_stars": total_stars,
        "total_forks": total_forks,
        "average_stars": average_stars,
        "top_repo_name": top_repo["name"] if top_repo else "N/A",
        "top_repo_stars": top_repo["stars"] if top_repo else 0,
        "original_repos": total_repos - fork_count,
        "forked_repos": fork_count,
        "missing_language_count": missing_lang_count,
        "languages": ranked_languages,
    }


# Function 4: write_*
def write_csv(records, path="torvalds_repos.csv"):
    """
    Writes the list of records to a CSV file.
    Uses newline='' to prevent blank lines across operating systems.
    Returns True if written successfully, False otherwise.
    """
    if not records:
        print("No records to write.")
        return False

    fieldnames = list(records[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Wrote {len(records)} rows to {path}")
    return True


# Function 5: main
def main():
    """
    Orchestrates the workflow: calls fetch, parse, transform, summarise,
    and output in order, handling failures at each step.
    """
    print("Fetching repositories for user 'torvalds' from GitHub API...")
    data = fetch_repos(username="torvalds", per_page=100)

    # Specific error handling check
    if data is None:
        print("Error: Could not retrieve repository data. Aborting.")
        sys.exit(1)

    print(f"Successfully retrieved raw data. Parsing into structured records...")
    records = to_records(data)
    if not records:
        print("Error: No valid records parsed from response. Aborting.")
        sys.exit(1)

    print(f"Parsed {len(records)} repository records.")

    # Compute something non-trivial from the records
    summary = summarise(records)

    print("\n" + "=" * 55)
    print("               GITHUB REPOSITORY SUMMARY            ")
    print("=" * 55)
    print(f"Total Repositories  : {summary['total_repos']}")
    print(f"Total Stars         : {summary['total_stars']:,}")
    print(f"Total Forks         : {summary['total_forks']:,}")
    print(f"Average Stars/Repo  : {summary['average_stars']:,}")
    print(f"Top Repository      : {summary['top_repo_name']} ({summary['top_repo_stars']:,} stars)")
    print(f"Original Repos      : {summary['original_repos']} (Forks: {summary['forked_repos']})")
    print(f"Unspecified Langs   : {summary['missing_language_count']}")
    print("-" * 55)
    print("Language Breakdown:")
    print(f"  {'Language':<16} {'Repos':<8} {'Stars':<12} {'Share (%)':<10}")
    print("  " + "-" * 48)
    for lang in summary["languages"]:
        print(f"  {lang['language']:<16} {lang['repos']:<8} {lang['stars']:<12,} {lang['percentage']:<10.1f}")
    print("=" * 55 + "\n")

    # Persist the output
    output_filename = "torvalds_repos.csv"
    success = write_csv(records, output_filename)
    if not success:
        print("Failed to save records to CSV.")
        sys.exit(1)

    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()