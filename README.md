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
uv tool install --editable ~/ytq
ln -s ~/ytq/completions/ytq.fish ~/.config/fish/completions/
```

## Checks

`make dev` (`uv sync`, once, networked) puts the locked pytest, hypothesis and
pyte into `.venv`; then `make test` or `make check` — both are
`.githooks/checks.sh`, the one copy of what runs (pytest through `.venv` when
there is one, plain `python3 -m pytest` otherwise), and the pre-push hook
(`git config core.hooksPath .githooks`) refuses a push that fails it.

The suite is under `tests/`. It is offline and hermetic: it builds a throwaway
queue root in a temp directory and points `EXPIRE_HOME` and `$HOME` at it, so
running the checks never touches the real queue. It does need the sibling
checkouts present — it imports across them the way a real run does — and a
shallow clone path, because the screens check their own widths down to 32
columns and a deep worktree is itself the width they cannot fit. The curses
screens are driven for real, under a pty with `pyte` reading them back; the
ones that would spend data are not driven at all.

```
make test                 # the suite (a few seconds)
uv run pytest -q -m "not tui"   # without the pty-driven screen tests
make mutants              # the slower question below
```

`make mutants` runs [poodle](https://pypi.org/project/poodle/) over `ytq.py`
and `ytdl_item.py`: it changes one operator or literal at a time and re-runs
the tests, and reports the mutants that **survived** — the lines no test was
actually asserting anything about. It is a **ratchet, not a gate**: some
mutants are equivalent to the code they replace and can never be killed, so it
is deliberately outside `make test` and outside the pre-push hook, and the
score is there to notice a suite going backwards rather than to be 100%. It
lives in its own `mutants` dependency group, so `uv sync` does not install it.
It currently kills 53.3% of 3133 mutants and takes about an hour; `CLAUDE.md`
explains what the survivors are and which of them are worth a test.
