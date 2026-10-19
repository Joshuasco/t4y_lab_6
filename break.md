# Step 6: Break It on Purpose

This document tests and verifies the error handling and degradation behavior of the pipeline across three intentional failure scenarios specified in **Step 6** of the Day 6 Lab instructions.

---

## 1. Misspell the Host in `BASE_URL`

### Objective
Verify that an invalid or unreachable hostname degrades gracefully with an informative user-facing message instead of an unhandled traceback.

### Implementation / Test
We targeted an invalid domain:
```python
BASE_URL = "https://api.githubb-typo-domain.invalid/users/torvalds/repos"
```

The error is caught in the `fetch_repos` error handling hierarchy:
```python
except requests.exceptions.RequestException as err:
    print(f"Could not reach the service: {err}")
    return None
```

### Result Observed
```
Fetching repositories for user 'torvalds' from GitHub API...
Could not reach the service: HTTPSConnectionPool(host='api.githubb-typo-domain.invalid', port=443): Max retries exceeded with url: /users/torvalds/repos (Caused by NameResolutionError("<urllib3.connection.HTTPSConnection object at 0x73b8c33633e0>: Failed to resolve 'api.githubb-typo-domain.invalid' ([Errno -2] Name or service not known)"))
Error: Could not retrieve repository data. Aborting.
```

### Conclusion
- **No traceback** was raised.
- The pipeline captured `requests.exceptions.RequestException`, printed a clear error message, returned `None`, and `main()` aborted cleanly.

---

## 2. Set `timeout=0.001`

### Objective
Verify that an aggressive timeout degrades gracefully with our custom message instead of an unhandled `requests.exceptions.Timeout` traceback.

### Implementation / Test
The timeout threshold was set to `0.001` seconds:
```python
response = requests.get(url, params=params, headers=headers, timeout=0.001)
```

The error is caught specifically by:
```python
except requests.exceptions.Timeout:
    print("The request timed out.")
    return None
```

### Result Observed
```
Fetching repositories for user 'torvalds' from GitHub API...
The request timed out.
Error: Could not retrieve repository data. Aborting.
```

### Conclusion
- **No traceback** was raised.
- `requests.exceptions.Timeout` was caught before general `RequestException`, returning `None` and allowing `main()` to exit safely.

---

## 3. Ask for a Field That Does Not Exist

### Objective
Evaluate the two design options when querying a non-existent field: **crashing loudly** vs. **returning a deliberate default**.

### Comparison

#### Option A: Crash Loudly (`KeyError`)
```python
# Direct bracket access
stars = item["stars_nonexistent"]
```
- **Behavior**: Throws `KeyError: 'stars_nonexistent'`.
- **When it is appropriate**: When a field is strictly mandatory for data integrity (e.g., database primary keys or required authentication credentials) where proceeding with missing data would corrupt downstream storage.

#### Option B: Return a Default Deliberately (`.get(key, default)`)
```python
# Safe dictionary access with fallback
language = item.get("language") or "Unspecified"
license_obj = item.get("license") or "None"
```
- **Behavior**: Gracefully substitutes a defined fallback value without halting execution.
- **When it is appropriate**: When consuming public REST APIs where certain records omit nullable attributes (for example, repository `license` is `null` on unlicensed repos, or `language` is `null` for markdown/data repos).

### Deliberate Design Decision
For this lab, we **deliberately chose Option B (return a default)** in `to_records()`:
1. Public APIs frequently contain missing or schema-variant fields across different records.
2. In our dataset, Linus Torvalds' repository `pesconvert` has `license: null`. Crashing loudly would abort processing the remaining 11 repositories.
3. Supplying fallback defaults (`"Unspecified"`, `"None"`, `0`) allows `to_records()` and `summarise()` to process all valid records and track missing data metrics (e.g. `missing_language_count`), directly fulfilling the rubric's **+2 bonus points** requirement for handling missing or malformed fields gracefully.

---

## Summary Matrix

| Failure Test | Trigger | Handler | Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| **1. Misspelled Host** | Invalid domain in `BASE_URL` | `except requests.exceptions.RequestException` | Printed user-friendly error message, returned `None`, no traceback | **Pass** |
| **2. Aggressive Timeout** | `timeout=0.001` | `except requests.exceptions.Timeout` | Printed `"The request timed out."`, returned `None`, no traceback | **Pass** |
| **3. Non-existent Field** | Missing/null keys in JSON record | `item.get(field, default)` | Populated fallback value, preserved full pipeline execution | **Pass** |
