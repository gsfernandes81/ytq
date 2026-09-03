#!/bin/bash
# The checks: the pytest suite, one runner, one copy.
#
#     .githooks/checks.sh        run everything
#     make check                 the same thing
#
# The pre-push hook runs this and refuses the push on a failure — a push is a
# deploy here: the phone pulls it and the nightly runner runs what landed.
#
# Offline: no network, no scheduler. Needs the sibling checkouts (dlq — and
# zwana-quota, which dlq's runner imports — beside this one or under ~),
# because the modules import across them the same way a real run does. The
# suite points EXPIRE_HOME at a throwaway queue root of its own, so running
# this never touches the real queue.
#
# The front ends lay out to the terminal and check every line fits it down to
# 32 columns, so these fail on a long checkout path — that is the path, not a
# regression: run them from a shallow clone (~/ytq is what they are built for).
#
# An empty collection is a failure, not a pass. pytest exits 5 when it finds
# no tests at all, and that is exactly what a suite deleted, renamed out of
# discovery or broken at import looks like — a green gate that ran nothing.
# It was passed while the suite was being rebuilt (2026-09-02); it is not now.
set -u

cd "$(git rev-parse --show-toplevel)" || exit 1

if [ -d .venv ] && command -v uv >/dev/null 2>&1; then
    uv run pytest -q
else
    python3 -m pytest -q
fi
rc=$?

if [ "$rc" -eq 5 ]; then
    echo "checks: pytest collected no tests at all — that is the failure." >&2
fi
exit $rc
