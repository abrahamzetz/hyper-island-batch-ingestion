# Batch Ingestion Demo

Two short Python scripts that pull JSON from a public API and save it to
disk. That's batch ingestion. Everything else (Fivetran, ADF, Airflow)
is a more sophisticated version of this same idea.

The repo has two examples, each demonstrating a different pattern:

- **`citibike.py`** — open public API, no auth, **per-minute snapshots**
- **`fingrid.py`** — authenticated API, **daily idempotent files** with backfill

Each script is under 30 lines.

## Setup

```bash
uv sync
```

That installs Python and `requests` from `pyproject.toml`. One dependency.

(If you don't use uv: `pip install requests` works too — Python 3.10+.)

## Run citibike.py

```bash
uv run citibike.py
```

You should see:

```
Saved data/citibike_2026-05-09T14-37.json
```

Look in `data/`. There's a JSON file there now — ~2400 NYC Citibike
stations, each with how many bikes are docked, empty slots, station ID,
and timestamps.

### Run it again

If you ran it within the same minute, the file got *overwritten* — same
filename, new contents. If a minute passed, you got a *new* file
alongside the old one.

That's because the filename uses minute-level granularity. Citibike
updates every ~10 seconds, so a new snapshot every minute is meaningful.

## Run fingrid.py (authenticated example)

This one needs an API key. Register at [data.fingrid.fi](https://data.fingrid.fi)
(free), then:

```bash
export FINGRID_API_KEY=your_key_here
uv run fingrid.py
```

You should see:

```
Saved data/fingrid_2026-05-02.json
```

Two things to notice in the script:

1. **The auth header.** Fingrid wants the key in an `x-api-key` header,
   passed via `requests.get(..., headers=...)`. Different APIs use
   different header names (`Authorization: Bearer ...`, `x-api-key`, ...)
   — read the docs for whichever API you're hitting.
2. **The filename uses a date, not a timestamp.** Fingrid 358 is hourly
   data published in batches — so each run produces one file per day.
   Re-running with the same `DAYS_AGO` overwrites the same file. That's
   **idempotency**: safe to retry, deterministic output.

### Backfill

Want yesterday? `DAYS_AGO = 1`. Want last week? Run with `DAYS_AGO = 1`,
then `2`, then `3`, etc. The filename derives from the day being fetched,
not from when you ran the script — so you can backfill a year and the
files land on the right dates.

This is how every real backfill works under the hood.

## Two patterns, one idea

| | `citibike.py` | `fingrid.py` |
| --- | --- | --- |
| Auth | none | `x-api-key` header |
| Source updates | every ~10 seconds | hourly, with publication lag |
| Filename | per-minute timestamp | per-day date |
| Re-running | snapshots accumulate | idempotent overwrite |
| Backfill | n/a | change `DAYS_AGO` |

Both scripts do the same shape of work — `GET → JSON → file` — but the
filename strategy is what makes them safe to schedule.

## Things to try

1. **Run `citibike.py` 5 times in a row.** How many files do you have?
2. **Wait 2 minutes, run it again.** How many now?
3. **Disconnect from wifi, run `citibike.py`.** What error do you get?
   Where in the script does the error come from?
4. **Read each script.** Both are under 30 lines. Find the line that
   parses JSON, the line that creates the folder, the line that authenticates.
5. **Run `fingrid.py` with `DAYS_AGO = 0`.** Does it return any data?
   Why or why not? (Hint: publication lag.)
6. **Look at the `pagination` block** in any `fingrid_*.json`. Is
   `nextPage` `null`? If yes, you got everything. If not, the script
   silently truncated — real ingestion would loop until `nextPage` is
   gone.

## What these scripts don't do (yet)

- **No state.** They don't remember the last time they ran. Every run
  pulls everything in the requested window.
- **No retries.** If the API is briefly down, the script crashes. Real
  ingestion code retries with backoff.
- **No pagination loop.** `fingrid.py` requests `pageSize=20000` and
  hopes the response fits. Real ingestion follows `nextPage` until done.
- **No deduplication beyond filenames.** Real ingestion writes to
  durable storage with primary keys.
- **No schedule.** The scripts run when *you* run them.
