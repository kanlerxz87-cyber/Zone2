"""One definition of "is this flag still open", shared by every surface that counts them.

Why this module exists
----------------------
Three surfaces publish a flag count, and for most of this project they disagreed:

* `pages/flags.html` used `len(rows)` — literally every flag in the register — and announced
  "28 open items" (F-31).
* `summary.html` used `f.get("status", "open") == "open"` — which counts the 23 flags that carry no
  `status` field at all, including 11 whose owner is already `done` (F-29, session `ba8b2d38`).
* `flagged.html` typed the number by hand and let it rot at "26 flags (F-01 … F-26)" (F-26, F-28).

Two different sessions fixed two of those three surfaces in two different ways in the same hour, which
is how "28 open" and "25 open" ended up on one site. The predicate now lives in one module and both
generators import it, so the numbers cannot diverge again.

The rule
--------
A flag is **open** when it has not been recorded as resolved. It is recorded as resolved either by
`status: "closed"` or by `owner: "done"`. A flag that carries an explicit `status` is judged by that
field; a flag with no `status` field is judged by its owner.
"""

from __future__ import annotations

from typing import Any


def is_open(flag: dict[str, Any]) -> bool:
    """True when this flag still needs the owner's action."""
    status = flag.get("status")
    if status is not None:
        return status != "closed"
    return flag.get("owner") != "done"


def open_count(flags: list[dict[str, Any]]) -> int:
    return sum(1 for f in flags if is_open(f))
