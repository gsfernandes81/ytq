# ytq — working notes for Claude

The YouTube search-and-queue front end for the `dlq` overnight download
queue. Split out of the `or3` monorepo's `termux/expire/` on 2026-08-28. It
runs on the phone, where **the mobile radio is metered** — every design
decision below is about not spending twice, and about a 40-column portrait
terminal.

`ytq.py` anchors every queue path to the **dlq checkout** (`ytq._root`:
`$EXPIRE_HOME`, a clone beside this repo, then `~/dlq`), never to its own
`__file__` — an installed copy queuing next to itself is a nightly job firing
faithfully onto an empty queue. `ytdl_item.py` lives here (the items ytq
writes download through it) and reaches `expire_dl` in the dlq checkout the
same way; a written item spells **both** directories into its own
`sys.path.insert` lines, resolved at write time.

Decisions that travel with this code:

- **`ytq` is a four-screen curses app**: search, results, formats, confirm.
  The search is one flat `ytsearch` request — the only place it spends data
  unasked — with `--extractor-args youtubetab:approximate_date`, which is why
  every age it prints is marked `~`.
- **The entry field's third answer is `subs`, the subscription feed** —
  `looks_like_feed` is asked *before* `looks_like_url` because the feed's URL
  passes that test too. It is not a fifth screen: `results()` draws both.
  `--playlist-end` is the whole cost argument (`subs_argv`'s self-test pins it
  beside the search's); **`m` goes further back and every press re-buys the
  listing** (`feed_cost` is the total, never the increment, and `feed_meta`
  puts it on screen before the key is pressed); fewer rows back than asked for
  is the end of the feed, told apart from `SUBS_MAX` in words; the depth
  commits only on a fetch that came back (`subs_want` vs `subs_asked`).
- **The cookie is asked about before anything is spent** — `cookie_state`
  reads yt-dlp's own config with `shlex`, and refuses on a missing
  `--cookies` line or a jar not on disk. **An empty feed is never reported as
  "nothing new"** — YouTube answers a logged-out feed with no entries, and
  `empty_feed_advice` says what that means and how old the jar is; a check
  pins that it does.
- **A format list holding nothing but 360p says why** — `withheld` reads the
  RAW formats, deliberately not `choices()`'s output, scoped to
  `ADAPTIVE_ALWAYS` because the claim is only true of YouTube. Said twice on
  purpose: a full notice once a session and `withheld_note` on every list it
  applies to, measured at three widths, no `⚠` (ambiguous-width).
- **The results screen hands its place back** — `results` takes and returns
  `(cursor, top)`, keyed by query, and `viewport` is what makes a restored
  place safe on a list that grew, shrank or was resized; a check drives seven
  restores. `←`/`→` alias page up/down and are in neither hint set — no room
  at 38 columns; `docs/ytq.md` carries them.
- **The selected title scrolls; nothing else does, and an idle screen still
  blocks.** `marquee` holds at the start of each lap; `title_room` is the one
  place that decides both drawing and waking, and a screen of short titles
  emits **zero** bytes over three idle seconds — the property the loop was
  written for.
- **`message()` may never lose its own way out** — `message_body` is pure and
  bounded, says what it dropped, and every notice is measured against 40x24
  whole. `wrapped()` sets `break_on_hyphens=False` because a path broken
  across two lines is a path retyped wrong.
- **Two hint sets** — `HINTS` at 38 columns and `TIGHT_HINTS` at 30 — because
  a hint clipped at the floor is usually the way out that got clipped.
- **`ytq.write_item` is the one door and refuses duplicates**
  (`ytq.Duplicate`), keyed on extractor and id rather than URL; the search,
  a pasted URL, `--now`, `--from-json` and `dlq` all end there. The
  results list marks what the queue already holds — before the probe is
  spent.
- **`next_number` caps at `MAX_PRIORITY`** — the runner sorts file names, so
  a third digit puts an item at the front, not the back.
- **Downloading now spawns a detached `dlq now`** (by path under the queue
  root: `HERE / "expire_sched.py"`), so ytq stays open and the download
  outlives the screen.
- **`Choice.kind` decides an item's destination** — never the file extension
  (at queue time there is no file); `ytq.dest_for` is the one place, `--dest`
  wins over both.

## Checks

`make test` (pytest) = `make check` (`.githooks/checks.sh`, the one copy; the
pre-push hook runs it). Offline: nothing reaches YouTube or the portal. Needs
the sibling checkouts, and a shallow clone path — both screens check every
line fits the terminal down to 32 columns, so a deep worktree is itself the
width they cannot fit.
