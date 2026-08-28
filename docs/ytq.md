# ytq — find a video and queue it for overnight download

`ytq` searches YouTube and queues what you pick for the
[overnight download queue](download-queue.md). It asks yt-dlp for **metadata
only** (~0.1–0.5 MB, no media), shows every format with the size yt-dlp states
for it, and writes a queue item with that measured size as its spending cap.
The video itself downloads during the nightly window and appears in your video
download directory — on the phone that is Android's Downloads until you point
it somewhere else with `dlqd dest video <dir>`.

## Use

```
ytq                # search, or paste a URL, in the same field
ytq crust of rust  # straight to the results
ytq subs           # straight to your subscription feed
ytq <url>          # straight to the format list
ytq --now <url>    # open the format list ready to start it now
```

`ytq` is the command name once installed — see
[Installing](download-queue.md#installing-ytq-and-dlq). Uninstalled, it is
`python3 ~/ytq/ytq.py <url>`, and every `ytq` line below reads the
same way.

Four screens, and `q` or esc always goes back exactly one of them:

1. **Search** — type words to search for, paste a URL, or type `subs` for your
   subscription feed. It tells the three apart by looking, so there is one
   field rather than three. What each costs is printed underneath before you
   spend it.
2. **Results** — 20 hits (or the newest 30 from the feed) with the channel, the
   age and the length; ↑↓ to move, ←→ (or page up/down) to jump a screenful,
   enter to see the formats, `/` to search again with your words still there —
   or, on the feed, `r` to read it again. **It keeps your place**: queueing a
   video, backing out of the format list, `m` and `r` all put you back where
   you were rather than at the top.
3. **Format list** — pick with ↑↓; enter queues it for tonight, `n` starts it
   now. The cursor opens on whatever you chose last time.
4. **Confirm** — shows the size and the cap; `e` edits the priority number or
   file name if you care, `n` and `t` switch between now and tonight, enter
   commits.

Queueing takes you back to the results with a `✓` on the row — on the row you
were on, so finding three things to download is one search rather than three. A `✓` is also on anything
the queue *already* holds — queued, downloaded or given up on — so most repeats
are visible in the list before a single byte is spent asking about them.

## It will not queue the same video twice

Between the format list and the confirmation, a video that is already in the
queue or has already been downloaded gets a screen of its own:

```
 already downloaded
   downloaded 2026-08-11
   as 10-samsung-galaxy-z-flip8-review
   a  queue it again anyway
```

Any other key goes back. Nothing about it is a guess: an item records what it
is a download of (`# SOURCE: youtube:<video id>`), so the same video is
recognised however its URL was written — `youtu.be/x`, `watch?v=x`,
`watch?v=x&list=…` are one video, not three.

Items queued before that header existed have no id, so they are matched on
their name instead — the same title, which is usually but not always the same
video. The screen says which of the two it matched, because they are not
equally good evidence.

The check is in the one line every route to a queue item goes through, so it
covers the search, a pasted URL, `--now` and `--from-json` alike; `dlq` is the
same, keyed on the URL, with `dlq --again` for meaning it.

It prints something like:

```
queued 50-some-talk.py — 487 MiB (1080p mp4), cap 506 MiB
```

The download then runs on the next night(s) with allowance to spare, and the
finished file appears in the video download directory as `some-talk.mp4`.
`dlqd list` shows progress and `dlqd path some-talk` says where it went.

```
dlqd dest video ~/storage/movies   # change it for everything
ytq --dest ~/storage/dcim <url>    # or for this one only
```

## Searching

One search is a single request — about 0.1 MB, the same order as the metadata
extraction `ytq` already runs, so it is not asked about separately. Nothing is
downloaded until you pick a format and commit.

```
 search: crust of rust
 20 results  ·  ~ approx dates
 Crust of Rust: Lifetime Annotations
   Jon Gjengset · ~5y · 90m34s
 ✓ Rust Lifetimes Finally Explained
   Let's Get Rusty · ~2y · 26m01s
```

- **The age is approximate, and says so.** YouTube's search page gives a
  rounded phrase ("4 months ago"), not a date, so `ytq` shows `~4mo` rather
  than inventing a day. `<1d` is anything posted today; `?` means the answer
  came back with no date at all, which happens.
- The channel is the column that gets shortened when there is no room. The
  length and the age are never dropped — a 90-minute video and a 3-minute one
  are not the same choice.
- `✓` marks what this session has already queued.
- Getting the words wrong costs the search again, so `/` reopens the field with
  what you typed still in it; fixing a typo is an edit, not a retype. Repeating
  a search you have already run in this session is free.
- No paging. Asking for the next twenty re-fetches the first twenty to get
  there, so better words are always cheaper than a second page.

Searches go through your `~/.config/yt-dlp/config` like everything else, which
matters — see the bot-check section below.

## Your subscription feed

`subs` in the same field — or `ytq subs`, or `ytq --subs` — asks YouTube for the
newest 30 videos from the accounts you follow. It is the same results screen,
so a video out of the feed is picked, sized, marked and queued exactly as a
search hit is.

```
 subscriptions
 30 videos · just now · m 60 ~0.4MB
 Crust of Rust: Subtyping and Variance
   Jon Gjengset · ~3d · 90m34s
 ✓ Making a Case for Rust
   Some Channel · ~1w · 12m40s
```

- **`m` keeps your place.** The videos already on screen keep their positions
  when the list grows underneath them, so a deeper look carries on from where
  you were reading instead of starting again. ←→ jump a screenful, which is
  what 150 rows needs and what a phone's page keys are too buried to give.
- **`m` goes further back**, thirty at a time, up to 150. The line under the
  banner is the price of the next press before you press it — and it is the
  **total**, not the extra thirty, because YouTube's pages are sequential:
  there is no asking for videos 31–60 without walking 1–30 to reach them, so
  going deeper re-buys what is already on screen. Five presses is
  0.2 + 0.4 + 0.6 + 0.8 + 1.0 MB, so going deep is worth doing in one decision
  rather than five idle taps.
- **`m` switches itself off at the bottom of the feed.** If YouTube hands back
  fewer videos than were asked for, that is everything it has, and the line
  says `the whole feed` instead of a price. At 150 it says `at the cap`, which
  is the different sentence: there *is* more and ytq will not spend it. A
  deeper look that fails changes nothing — the count and the price go back to
  what is actually on screen.
- **The selected title scrolls when it does not fit.** Only the one under the
  cursor, slowly, and only when it is genuinely too long for the room; every
  other row keeps its `…` and stays still, because a list where every line
  slides is a list nothing can be read off. Moving the cursor starts the new
  title from its beginning. A screen with nothing to scroll still blocks on
  the keyboard and costs no wakeups at all.
- **It needs the stored cookie**, and it is the only screen here that does. The
  feed is a signed-in page; the jar is the same
  `~/.config/yt-dlp/cookies.txt` the bot-check section below is about, wired in
  by the `--cookies` line in `~/.config/yt-dlp/config`. `ytq` reads that config
  itself and refuses **before** spending anything if there is no cookie line,
  or the file it names is not there.
- **An empty feed is never reported as "nothing new."** YouTube answers a
  logged-out feed with no entries rather than with an error, so an empty answer
  means the cookies have expired. The screen says exactly that, and how old the
  jar is.
- **One page is about 0.2 MB.** Bounded on purpose: yt-dlp will follow every
  continuation YouTube offers, which for a few years of subscriptions is
  hundreds of pages on the mobile radio. `SUBS_RESULTS` in `ytq.py` is the
  first bound and `SUBS_MAX` is the last one; the 0.2 MB is an estimate by
  analogy with the search page and has not been measured on the vessel's link.
- **It is cached for the session**, so backing out of a video and into another
  costs nothing — and because it is, the header says how old what you are
  looking at is. `r` reads it again, which is another 0.2 MB.
- The dates are approximate exactly as the search's are, and `✓` marks what the
  queue already holds before anything is probed — which on a feed is worth more
  than on a search, because the feed shows you the same videos every day until
  you do something about them.
- `ytq --list --subs` prints the first page and writes nothing, for a pipe or
  an ssh session with no terminal. Going deeper is a TUI thing: it is a
  decision with a price on it, and a price belongs on a screen somebody is
  looking at.

## Reading the format list

```
  487 MiB   1080p mp4       137+140      avc1 + mp4a 129k, merged
  312 MiB~  1080p webm      248+251      vp9 + opus 141k, merged
   38 MiB   360p mp4        18           one file, avc1+mp4a
   10 MiB   audio 129k m4a  140          mp4a, no video
```

- `~` marks a size yt-dlp only estimates; the cap takes a 12% margin instead
  of 3% to cover it.
- `137+140` entries download video and audio separately and merge locally —
  the size shown is both together.
- Audio-only rows sort to the bottom.
- Formats yt-dlp states **no size** for are hidden: the queue needs a measured
  cap, not a guess. The header says how many, so a short list explains itself.
- **A list holding nothing but 360p says why.** If YouTube sent only the legacy
  progressive stream, that is the bot check and not a video that only exists in
  360p — the header says `bot check`, and the first time it happens in a
  session you get the whole explanation and the one command that diagnoses it.
  It is told apart from the case above by the *absence of adaptive streams*,
  not by the symptom: both end up as one 360p row, and they have different
  fixes.
- **The size is coloured by how many nights it will take** — green fits inside
  one window comfortably, amber is most of one, red spans several. Anything
  needing more than one night also says so in words (`(8 nights)`), because a
  terminal without colours must not be the one that loses the warning.

On a phone in portrait the format id and the codec detail drop off — they are
the two columns nobody chooses on — leaving the size, the label and the nights:

```
  4.48 GiB  2160p mp4 (8 nights)
   486 MiB  1080p60 mp4
   393 MiB~ 1080p webm
    10 MiB  audio 129k m4a
```

## Without the picker

```
ytq --list <url>            # print the table, write nothing
ytq --list --subs           # print the subscription feed, write nothing
ytq --from-json dump.json   # reuse a saved 'yt-dlp -J' dump —
                            # changing your mind costs no data
```

`--from-json` takes a saved search too — a `yt-dlp -J --flat-playlist
'ytsearch20:…'` dump opens on the results screen instead of the format list,
and `--list` prints those rows rather than formats. That is how the screens can
be worked on without spending anything.

## Downloading it now

Press `n` instead of enter on the format list, or pass `--now`. The confirm
screen changes its header to **download NOW — paid**, says the number in words
(`this spends 505 MiB of PAID data`), and starts as soon as you press enter.
`t` puts it back to *queue tonight — free* if you change your mind.

**That is ordinary mobile data, charged normally** — the window exists to spend
allowance that is about to expire, and this is outside it. Tonight is free;
now is not, which is why the two are spelled out rather than colour-coded.

It runs in the **background**, so choosing it does not end the session: the
screen goes back to the results with the download reporting itself along the
bottom, and you can carry on queueing. `x` stops it — what has downloaded stays
on disk and the item stays queued, so the nightly window carries on from where
you stopped. Leaving `ytq` leaves the download running.

Only one at a time: the queue takes an exclusive lock, so asking for a second
while one is going says so and leaves the second queued. It still writes the
queue item first either way, so it shows up in `dlqd list`, and
`dlqd path <name>` says where it landed.

## When YouTube says "Sign in to confirm you're not a bot"

Nothing to do with the video — YouTube is refusing the extraction. Two causes,
both handled in `~/.config/yt-dlp/config` rather than in `ytq`:

- **No JavaScript runtime.** YouTube's "n" challenge has to be solved or the
  formats are withheld. yt-dlp only enables `deno` by default and this device
  has `node`, hence `--js-runtimes node` in the config, plus the solver scripts
  from `pip install yt-dlp-ejs` (~53 KiB, one-off). Without both you get
  storyboards and nothing else.
- **The vessel's IP is rate-limited.** The watch page comes back HTTP 429, so
  there is no visitor data and so no PO token. Cookies from a logged-in session
  get past it — `~/.config/yt-dlp/cookies.txt`, wired in by the `--cookies` line
  in the config. Without them the same URL either fails outright or lists a
  fraction of the formats it really has (one 320p entry, on the video this was
  first debugged with, against thirty up to 960p60 with them).

  **Check the version first.** YouTube breaks yt-dlp faster than anything else
  here, and a stale copy produces exactly this symptom with a perfectly correct
  config — that is what happened on 2026-08-28, where 2026.7.4's authenticated
  default client had stopped working and the fix had been released nine days
  earlier. `ytq`'s own notice leads with the version and the right upgrade
  command for how it is installed; by hand it is:

  ```
  head -1 $(command -v yt-dlp)     # which python owns it
  uv tool list                     # or whether uv does
  ```

  A shebang under `uv/tools/` means `uv tool install yt-dlp --with yt-dlp-ejs
  --force` — **not** `uv tool upgrade`, which answers "Nothing to upgrade" and
  does nothing if the tool carries any version constraint. Anything else means
  `<that python> -m pip install -U yt-dlp`. Do not read the `(pip)` marker in
  `yt-dlp -v` as an answer: it says `(pip)` under a uv tool too.

  **Checking the other two halves takes one command, no URL and no data:**

  ```
  yt-dlp -v 2>&1 | grep -i 'js runtimes\|optional lib'
  ```

  ```
  [debug] Optional libraries: sqlite3-3.45.1, yt_dlp_ejs-0.8.0
  [debug] JS runtimes: node-22.22.2
  ```

  That is what working looks like. `JS runtimes: none` means the challenge
  cannot be solved; a missing `yt_dlp_ejs` means the solver scripts are not
  installed **for the yt-dlp that actually runs**. That last part is the trap:
  `ytq` is a `uv` tool whose venv declares no dependencies on purpose, so it
  falls back to the `yt-dlp` binary on `PATH` — and `yt-dlp-ejs` has to be
  installed alongside *that* one, not alongside `ytq`. `yt-dlp -v` reports for
  whichever it is, which is why the check is that rather than a `pip list`.

  Where to install it depends on where that yt-dlp came from — the same
  `-v` output says, on its version line: `(pip)` means
  `pip install yt-dlp-ejs` into the python owning `$(command -v yt-dlp)`, and
  a `uv tool` install takes `uv tool install yt-dlp --with yt-dlp-ejs`.

  The cookies expire. When the bot-check message comes back, re-export
  `cookies.txt` from the phone browser in Netscape format and overwrite that
  file — mode 600, and never in the repo: it holds live Google session tokens,
  and yt-dlp rewrites it in place as they refresh.

  The same jar is what the **subscription feed** signs in with, and it is the
  louder alarm of the two: a search with stale cookies still returns something,
  where the feed returns nothing at all. So an empty feed and a short format
  list are the same fault, and `ytq` says so on both screens rather than
  leaving "no new videos" to be believed.

## Notes

- One video at a time; playlist URLs are refused. A *search* naturally comes
  back as a list of them, which is a different thing and is what the results
  screen is.
- Which format you chose last is remembered, in the queue's own `config.json`
  beside the destinations, and only decides where the cursor opens. If the
  video does not offer it, the closest resolution wins; if it offers nothing
  close, you are back at the top of the list as before.
- A plain file URL (not a video page) belongs in `dlq` instead — it slices
  more precisely and skips the per-night metadata overhead.
- Large videos span nights. Each nightly firing re-runs yt-dlp (media URLs
  expire in hours, so they must be re-resolved) at ~0.1–0.5 MB per firing;
  that overhead is already inside the declared cap.
