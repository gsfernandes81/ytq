# ytq — search and queue videos for the overnight download queue

A four-screen curses app for the phone: search (or paste a URL, or open the
subscription feed), results, formats, confirm. What it queues downloads
overnight through [`dlq`](../dlq), the expiring-quota download queue, on
allowance that would otherwise be wiped at midnight. `docs/ytq.md` is the
user guide.

It runs on the phone under Termux, where **every byte is metered**: the app
says what a request will cost before the key that spends it, and the one
request it makes unasked is the search itself.

## The three checkouts

This repo split out of a monorepo on 2026-08-28. `ytq.py` writes queue items
into the **dlq** checkout (`~/dlq`, or `$EXPIRE_HOME`) — the queue root every
path is anchored to, deliberately never this file's own directory — and its
confirm screens quote portal figures through `expire_runner` there.
`ytdl_item.py` stays here because the items ytq writes download through it;
they reach `expire_dl` in the dlq checkout the same way. Sibling resolution
is: env override first, then a clone beside this repo, then `~/<name>`.

Install (optional — `python3 ~/ytq/ytq.py` works as-is):

```
uv tool install --offline --editable ~/ytq
ln -s ~/ytq/completions/ytq.fish ~/.config/fish/completions/
```

## Checks

`make test` (pytest) or `make check` — the same self-tests;
`.githooks/checks.sh` is the one copy and the pre-push hook
(`git config core.hooksPath .githooks`) refuses a push that fails them.
They need the sibling checkouts present, and a shallow clone path — the
screens check their own widths down to 32 columns.
