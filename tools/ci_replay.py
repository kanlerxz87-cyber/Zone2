#!/usr/bin/env python3
"""Replay every `run:` step of .github/workflows/pages.yml locally, in order.

A tiny parser rather than PyYAML: the workflow's steps are a regular
`- name: ...` / `run: ...` shape, and the sandbox has no YAML package. Only the
`build` job is replayed; `deploy` needs the Pages API.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WF = (REPO / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")


def check_workflow_health() -> None:
    for idx, line in enumerate(WF.splitlines(), 1):
        if re.match(r"^(<<<<<<<|=======|>>>>>>>)", line):
            raise SystemExit(
                f"ERROR: .github/workflows/pages.yml contains unresolved conflict marker at line {idx}: {line}"
            )


def steps() -> list[tuple[str, str]]:
    check_workflow_health()
    out: list[tuple[str, str]] = []
    lines = WF.splitlines()
    i = 0
    name = None
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^\s*- name: (.+)$", line)
        if m:
            name = m.group(1).strip()
            i += 1
            continue
        m = re.match(r"^(\s*)run: (\S.*)$", line)
        if m:
            indent, inline = len(m.group(1)), m.group(2).strip()
            if inline in ("|", "|-", ">", ">-", "|+", ">+"):
                body: list[str] = []
                i += 1
                while i < len(lines):
                    nxt = lines[i]
                    if nxt.strip() and (len(nxt) - len(nxt.lstrip())) <= indent:
                        break
                    body.append(nxt[indent + 2 :] if len(nxt) > indent else "")
                    i += 1
                out.append((name or f"step {len(out) + 1}", "\n".join(body)))
                continue
            out.append((name or f"step {len(out) + 1}", inline))
            i += 1
            continue
        i += 1
    return out


def main() -> int:
    only = sys.argv[1] if len(sys.argv) > 1 else None
    failed = []
    all_steps = steps()
    ran = 0
    for n, (name, body) in enumerate(all_steps, 1):
        if only and only.lower() not in name.lower():
            continue
        ran += 1
        print(f"\n=== [{n}/{len(all_steps)}] {name} ===", flush=True)
        r = subprocess.run(["bash", "-c", body], cwd=str(REPO))
        if r.returncode != 0:
            failed.append(name)
            print(f"!!! FAILED: {name}")
            break
    print("\n" + "=" * 60)
    if failed:
        print(f"CI REPLAY FAILED at: {failed[0]}")
        return 1
    print(f"CI REPLAY PASSED — {ran} steps")
    return 0


if __name__ == "__main__":
    sys.exit(main())
