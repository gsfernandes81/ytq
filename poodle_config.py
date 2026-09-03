"""How `make mutants` runs poodle over this repo.

Mutation testing is the suite's own check: poodle changes one operator, literal
or comparison at a time and re-runs the tests, and a mutant that *survives* is
a line no test was actually asserting anything about. It is a ratchet and never
a gate — some mutants are equivalent (the same behaviour spelled differently)
and can never be killed — so `make mutants` is deliberately outside `make test`
and `make check`, which the pre-push hook runs.

Three things here are load-bearing:

* ``source_folders = ["."]``. The modules sit at the repo root, not under
  ``src/``, which is poodle's default and would find nothing.
* ``file_copy_filters``. poodle copies the working tree per worker into
  ``.poodle-temp``; without this it drags in ``.venv``, ``.git`` and the
  ``.hypothesis`` cache, which is most of a gigabyte per worker.
* ``YTQ_TEST_DLQ``. That copy has no sibling checkout beside it, and
  ``tests/conftest.py`` needs the real dlq to build the throwaway queue root
  out of. Set from this file's own location, which is the real one.

The curses event loops in ``ytq.py`` are fenced with ``# nomut: start`` /
``# nomut: end``: a mutant inside one does not fail a test, it hangs a terminal
until the timeout below kills it, and a whole test-suite timeout per mutant is
what turns a twenty-minute run into an overnight one. What those loops do is
checked under a pty instead (``tests/test_screens.py``), which is also why the
mutation run skips them — the pty tests are most of the suite's wall clock and
none of the code they cover is mutated.
"""

import os
from pathlib import Path

HERE = Path(__file__).resolve().parent

os.environ.setdefault("YTQ_TEST_DLQ", str(HERE.parent / "dlq"))

source_folders = ["."]

#: The two modules this repo owns. dlq's are copied into the throwaway root by
#: the suite and are that repo's to mutate.
only_files = ["ytq.py", "ytdl_item.py"]

file_filters = ["test_*.py", "*_test.py", "poodle_config.py", "conftest.py"]

file_copy_filters = [
    # The bytecode of the two modules being mutated must never be copied — a
    # stale .pyc beside a mutant would be a mutant that was never run. Every
    # other module's is worth carrying: compiling the test files from scratch
    # is nearly half of each run, and there are three thousand runs.
    "__pycache__/ytq.*",
    "__pycache__/ytdl_item.*",
    ".git/**",
    ".venv/**",
    ".pytest_cache/**",
    ".ruff_cache/**",
    ".hypothesis/**",
    ".poodle-temp/**",
    "queue/**",
    "work/**",
    "out/**",
    "*.log",
]

#: The suite is a couple of seconds; a mutant that turns a bound into a longer
#: loop needs room to finish rather than being reported as a timeout, and a
#: phone is slower than anything this was measured on.
min_timeout = 60
timeout_multiplier = 10

#: One worker per core. The runs are short and mostly CPU.
max_workers = 4

#: Two things make this run in half an hour rather than five hours. The pty
#: tests are excluded — the code they drive is fenced out of mutation anyway,
#: and they are most of the suite's wall clock. And the hypothesis profile
#: turns **shrinking off**: under mutation nearly every run has a failing
#: property test, shrinking one takes seconds, and poodle only needs to know
#: that the suite noticed rather than a minimal example of what it noticed.
runner_opts = {
    "command_line": (
        "python -m pytest -x -q -p no:cacheprovider -m 'not tui' "
        "--hypothesis-profile=mutants"
    )
}
