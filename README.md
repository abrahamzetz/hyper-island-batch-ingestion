# Batch Ingestion Demo

A 60-line Python script that pulls JSON from a public API and saves it to
disk. That's batch ingestion. Everything else (Fivetran, ADF, Airflow) is
a more sophisticated version of this same idea.

## Setup

```bash
git clone <REPO_URL>
cd batch-ingestion-demo
pip install requests
```

That's the whole setup. One dependency.

## Run it

```bash
python ingest.py
```

You should see:

```
→ Fetching from citibike...
✓ Saved data/citibike_2026-05-09T14-37.json
  size: 1195.7 KB
  records: 2406
```

Look in the `data/` folder. There's a JSON file there now.

## Run it again

```bash
python ingest.py
```

Now look in `data/` again. What changed?

If you ran it within the same minute, the file got *overwritten* — same
filename, new contents. If a minute passed, you got a *new* file
alongside the old one.

That difference matters. It's the difference between:

- **Idempotent** runs (same input → same output, safe to retry)
- **Snapshotting** (every run produces a new artifact, history accumulates)

The script picks one based on how often the source updates. Citibike
updates every ~10 seconds, so we use minute-level filenames — every
minute is a meaningful new snapshot.

## What's in the file?

Open it. It's pretty.

```bash
# macOS / Linux
python -m json.tool data/citibike_*.json | head -40

# or just open it in your editor
```

You'll see ~2400 NYC Citibike stations, each with how many bikes are
docked, how many empty slots there are, station ID, and timestamps.

## Things to try

1. **Run it 5 times in a row.** How many files do you have?
2. **Wait 2 minutes, run it again.** How many now?
3. **Disconnect from wifi, run it.** What error do you get? Where in the
   script does the error come from?
4. **Read the script.** It's ~60 lines. You can read it in 3 minutes.
   Find the line that handles "what if the API returns an error?" Find
   the line that prevents the script from hanging forever.

## What this script doesn't do (yet)

- **No state.** It doesn't remember the last time it ran. Every run
  pulls everything available right now. That's a "full snapshot" —
  simple, but expensive at scale.
- **No retries.** If the API is briefly down, the script crashes. Real
  ingestion code retries with backoff.
- **No deduplication.** If two runs happen in the same minute, the
  second overwrites the first. Real ingestion writes to durable storage
  with primary keys.
- **No schedule.** It runs when *you* run it. To run it every day at
  9am UTC automatically, see `.github/workflows/ingest.yml`.

You'll see Fivetran handle most of these things automatically in the
next part of the session. The point of writing this script first is so
you understand what Fivetran is doing for you.

## Try the GitHub Actions workflow (optional)

`.github/workflows/ingest.yml` runs this script automatically every day
at 9am UTC and commits the resulting JSON file back to the repo.

To activate it: fork this repo, enable Actions, and you're done. Files
will start appearing in `data/` daily, committed by GitHub itself.

This is the simplest possible "managed" batch pipeline — your code, your
schedule, no infrastructure. Good for hobby projects and small
internal tools. Not what most companies use in production, but a great
mental model for what every ingestion tool is doing under the hood.
