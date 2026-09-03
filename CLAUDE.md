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
  `--playlist-end` is the whole cost argument (a test must pin `subs_argv`
  beside the search's); **↓ at the last row goes further back and every look
  re-buys the listing** (2026-08-28: the down arrow is the only key that asks
  — the `m` alias it took over from is gone; `feed_cost` is the total, never
  the increment, and `feed_meta` puts it on screen before the key is pressed);
  fewer rows back than asked for is the end of the feed, told apart from
  `SUBS_MAX` in words; the depth commits only on a fetch that came back
  (`subs_want` vs `subs_asked`).
- **The cookie is asked about before anything is spent** — `cookie_state`
  reads yt-dlp's own config with `shlex`, and refuses on a missing
  `--cookies` line or a jar not on disk. **An empty feed is never reported as
  "nothing new"** — YouTube answers a logged-out feed with no entries, and
  `empty_feed_advice` says what that means and how old the jar is; a test
  must pin that it does.
- **A format list holding nothing but 360p says why** — `withheld` reads the
  RAW formats, deliberately not `choices()`'s output, scoped to
  `ADAPTIVE_ALWAYS` because the claim is only true of YouTube. Said twice on
  purpose: a full notice once a session and `withheld_note` on every list it
  applies to, measured at three widths, no `⚠` (ambiguous-width).
- **The results screen hands its place back** — `results` takes and returns
  `(cursor, top)`, keyed by query, and `viewport` is what makes a restored
  place safe on a list that grew, shrank or was resized, and it wants a test
  driving a spread of restores. `←`/`→` alias page up/down and are in neither hint set — no room
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
- **`p` on the confirm screen is dlq's listing, not a copy of it**
  (2026-09-02). The video does not exist yet, so `expire_ui.pick_place` holds a
  phantom row and gives back a **position**; ytq writes the item last exactly
  as it always did and then asks `expire_ui.place` to put it there, so the
  numbering rule, the cut line and the refusal all stay on dlq's side and
  nothing is renamed before the file exists. **`expire_ui` is imported inside
  the key handler and never at module top** — it binds `ytq._addstr` while it
  loads, and at ytq's top that name is 1800 lines away: expire_ui imports
  expire_sched, which imports this half-built module back, so the screen would
  die at the import rather than at the key. `item_name` is the one spelling of
  the name `write_item` makes, because a picker handed a second f-string is
  holding a file nobody writes. A number typed with `e` and a place picked with
  `p` are exclusive and the row shows the one in force; `n` drops the place,
  because what starts now runs from the file under the name it was written
  with. A refused move is a receipt line, never a traceback and never a retry.
- **`next_number` caps at `MAX_PRIORITY`** — the runner sorts file names, so
  a third digit puts an item at the front, not the back.
- **Downloading now spawns a detached `dlq now`** (by path under the queue
  root: `HERE / "expire_sched.py"`), so ytq stays open and the download
  outlives the screen.
- **`Choice.kind` decides an item's destination** — never the file extension
  (at queue time there is no file); `ytq.dest_for` is the one place, `--dest`
  wins over both.
- **The format list's columns carry the codec family; the selected row says
  it exactly** (2026-08-28) — `Choice.codecs` keeps yt-dlp's full strings
  (`_exact_codec`, beside `_codec` which truncates for the columns) and the
  formats screen draws them for the cursor row alone on the line above the
  hints. `c` there copies the page URL through `to_clipboard`
  (termux-clipboard-set; its answer flashes on the same line), and the fetch
  wait is `spinner_while`'s box over the calling screen, never a page of its
  own — nothing erases, so the results stay visible behind it.

- **A flick scrolls; only a keypress spends** (2026-08-28). The results and
  formats screens take wheel events — what Termux turns a touch drag into —
  via `enable_touch_scroll` (wheels only: a tap must never press a key, and
  some keys here spend data) and `read_wheel`/`wheel_step`, which dlq's
  screen imports rather than re-spelling. The wheel deliberately does NOT
  trigger the feed's deeper look at the bottom: ↓ is a decision, a flick is
  momentum. And the deeper look completes the ↓ that asked for it —
  `bumped_place` steps the cursor onto the first new row once the longer
  listing lands.
- **A run with no stop time must never be formatted with `int()`**
  (2026-08-28, and it had been broken since long before the split). `dlq
  now` and `run-now --blind` both set `EXPIRE_STOP_EPOCH=0` on purpose —
  they are deliberately outside the window — and `expire_dl.Env.deadline`
  spells that `+inf`. Every *comparison* against it is right; the banner's
  `int(deadline - time.time())` was not, and `int(inf)` raises. So `n` on a
  video died before a byte moved, in the line that says what it is about to
  do, leaving `unhandled error: OverflowError` in a log nobody opens — while
  file downloads through `expire_dl` worked, because that module only ever
  compares. `time_left()` is the one place that phrase is built now, and it
  says "no stop time" in words.

## Checks

`make test` (pytest) = `make check` (`.githooks/checks.sh`, the one copy; the
pre-push hook runs it). Offline: nothing reaches YouTube or the portal. Needs
the sibling checkouts, and a shallow clone path — a deep worktree is itself
the width the screens cannot fit. `make mutants` is the separate, slower
question below, and is deliberately not part of either.

`tests/conftest.py` is the hermetic half and the only place that knows the
environment. `ytq` anchors `HERE`/`QUEUE`/`DONE`/`FAILED` at **import time**,
so the pointing has to happen before the first `import ytq` anywhere: it
builds a throwaway queue root in a temp directory, **copies** dlq's modules
into it (copies and not symlinks — `expire_runner` anchors its own root on
`Path(__file__).resolve().parent`, and a symlink resolves back to the real
checkout and its `config.json`), and points `EXPIRE_HOME`, `ZWANA_HOME` and
`$HOME` at temp directories. `$YTQ_TEST_DLQ` overrides where the real dlq is
found, which is what lets the mutation runner work in a copied tree with no
sibling beside it. An autouse fixture empties the root between tests.

The eight files, and what each is for:

- `test_item_bytes.py` — the metering. The merge case above all: a rename is
  not new bytes, two names for one stream are one high-water mark, the freeze
  holds the *last* figure, and a property says the count can never go down
  however the files move about.
- `test_item_firing.py` — one firing: the resuming argv, `time_left` on an
  endless deadline, which file was produced and where it goes, and the whole
  decision table (a slice too small to extract in, no time left, already
  delivered, finished, exit 0 with nothing to show, the zero-firing strikes).
  The poll loop runs on a **fake clock** (`Clock`) and a fake child, so the
  budget stop, the deadline stop and the postprocessing lift are deterministic
  and instant.
- `test_asking.py` — what is asked for and what is said before asking:
  `--flat-playlist`, `--playlist-end`, the four ways `ask` fails, the feed's
  price being the total, `next_page`'s two different sentences, the cookie
  states, and the ages that mark themselves approximate.
- `test_formats.py` — what is offered and at what cap: unsized formats hidden
  and counted, storyboards dropped, merges paired by container family, the
  3%/12% margin, `withheld` scoped to YouTube and never conflated with
  `choices`'s `unsized`, and where the cursor opens.
- `test_queue_items.py` — the one door. The item the runner has to be able to
  read (asked of `expire_runner.parse_item`), the duplicate refusal keyed on
  id and the weaker fallback on name, two-digit names, and the picker's
  write-then-place path with `expire_ui.place` stubbed — the stub checks the
  file is on disk *before* dlq is asked to move it.
- `test_layout.py` — the widths, 32 columns up, as properties: every hint set
  in its stated room, every row inside the terminal, `viewport` always handing
  back a place the screen draws, `message_body` never growing past its own way
  out, and the marquee filling its room exactly.
- `test_cli.py` — the paths with no terminal: the flag combinations that are
  refused, `--list --from-json` printing and writing nothing, the feed
  refusing without a cookie, and the receipts printed after curses is gone.
- `test_screens.py` — the curses screens under a pty, read back with `pyte`.
  Marked `tui`. Structure only — which screen is up, that a row for a video
  exists, that the hint line still names a way out — never whole-line
  literals. Arrows go as `\x1bOA`/`\x1bOB` because keypad mode is on. It
  drives what costs nothing: the entry field, the cookie refusal, a listing
  and a format list from a saved dump, the confirmation, and the whole road
  from a dump to a written item. **The idle-screen property is here**: a
  screen of short titles emits zero bytes over two seconds and one with a
  title too long for its room does not.

Two helpers deleted with the old self-tests are back as tests rather than as
code: the shebang question (`test_the_runner_admits_what_ytq_writes` expects
exactly one objection off Termux, where the item's interpreter is not on disk)
and the json leak (`null`/`true`/`false` are valid Python *names*, so an item
holding one compiles and fails only on the night it was queued for).

### Mutation testing — `make mutants`

`uv run --group mutants poodle` (an optional group: a plain `uv sync` does not
install it). It changes one operator, literal or comparison at a time and
re-runs the suite; a mutant that **survives** is a line nothing was actually
asserting anything about. The score is a **ratchet, not a gate** — some
mutants cannot be killed by any test worth having, so 100% is not a target and
`--fail_under 50` is there to catch a suite going backwards. `poodle_config.py`
carries the reasons for every setting; the two that matter are
`source_folders = ["."]` (the modules are at the root, not under `src/`) and
the copy filters (poodle copies the tree per worker — and carries every
module's bytecode but the two being mutated, which halves the run).

**3133 mutants, 53.3% killed** (2026-09-03, ~65 minutes on four cores). Read
the survivor list with that number in mind: the four groups below are most of
it, and none of them is a behaviour nobody pinned — they are behaviour pinned
somewhere this run cannot see, or wording and constants that only a brittle
test could hold down. What is left over is where the next test goes.

- **the screens** (~535). `duplicate_screen`, `entry`, `message`, `app`,
  `pick`, `confirm`, `results` and the printing paths are covered by
  `test_screens.py` and `test_cli.py`, but the mutation command excludes the
  `tui` mark for runtime, so nothing in the run is there to kill them.
- **prose** (427 String mutants). poodle rewrites `"queued"` as
  `"XXqueuedXX"`, which every `in` assertion still passes. Killing those needs
  exact-equality assertions on wording, which is the brittleness this suite is
  written to avoid.
- **numbers read through their own constant** (a large share of 450). A test
  that asks `cost_band(NIGHT_BYTES)` moves with a mutated `NIGHT_BYTES`;
  pinning it would mean writing the byte count out by hand in the test.
- **equivalent** — e.g. `ceiling = max(budget // 2, budget - guard)`, whose
  first arm is unreachable while `MIN_USEFUL_SLICE` is eight times
  `GUARD_FLOOR`, and `state.pop("zero_firings", None)` whose default is never
  returned.

The curses event loops in `ytq.py` are fenced with `# nomut: start` /
`# nomut: end`, and that is the only thing in the code that exists for the
mutation run: a mutant inside one does not fail a test, it hangs a terminal
until the timeout kills it. Those loops are checked under a pty instead, which
is also why the mutation command skips the `tui` mark — that code is not
mutated and those tests are most of the suite's wall clock.

**A surviving mutant is a question, not a failure.** Read it: either it names
a behaviour nobody pinned, and the answer is a test, or it is equivalent, and
the answer is to say so.
