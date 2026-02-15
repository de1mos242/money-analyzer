from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = ROOT / "BEADS_STATUS.md"


def load_issues() -> list[dict[str, object]]:
    proc = subprocess.run(
        ["bd", "list", "--json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


def sort_key(issue: dict[str, object]) -> tuple[int, str]:
    priority = int(str(issue.get("priority", 9)))
    issue_id = str(issue.get("id", ""))
    return (priority, issue_id)


def render_markdown(issues: list[dict[str, object]]) -> str:
    by_status: Counter[str] = Counter(str(i.get("status", "unknown")) for i in issues)
    by_type: Counter[str] = Counter(str(i.get("issue_type", "unknown")) for i in issues)

    open_items = sorted(
        [i for i in issues if str(i.get("status", "")) == "open"],
        key=sort_key,
    )
    done_items = sorted(
        [i for i in issues if str(i.get("status", "")) == "done"],
        key=sort_key,
    )

    latest_update = max(
        (
            datetime.fromisoformat(str(i.get("updated_at", "")).replace("Z", "+00:00"))
            for i in issues
            if i.get("updated_at")
        ),
        default=None,
    )
    latest_update_text = (
        latest_update.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        if latest_update
        else "n/a"
    )

    lines: list[str] = []
    lines.append("# Beads Task Status")
    lines.append("")
    lines.append(f"Last updated from Beads data: {latest_update_text}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total issues: {len(issues)}")
    lines.append(f"- Open: {by_status.get('open', 0)}")
    lines.append(f"- Done: {by_status.get('done', 0)}")
    lines.append(f"- In progress: {by_status.get('in_progress', 0)}")
    lines.append(f"- Epics: {by_type.get('epic', 0)}")
    lines.append(f"- Tasks: {by_type.get('task', 0)}")
    lines.append("")

    lines.append("## Open Items")
    lines.append("")
    lines.append("| ID | Priority | Type | Title |")
    lines.append("|---|---:|---|---|")
    for issue in open_items:
        lines.append(
            f"| {issue.get('id')} | P{issue.get('priority')} | {issue.get('issue_type')} | {issue.get('title')} |"
        )
    if not open_items:
        lines.append("| - | - | - | No open items |")
    lines.append("")

    lines.append("## Recently Done")
    lines.append("")
    lines.append("| ID | Priority | Type | Title |")
    lines.append("|---|---:|---|---|")
    for issue in done_items[:12]:
        lines.append(
            f"| {issue.get('id')} | P{issue.get('priority')} | {issue.get('issue_type')} | {issue.get('title')} |"
        )
    if not done_items:
        lines.append("| - | - | - | No done items yet |")
    lines.append("")

    lines.append("## Refresh")
    lines.append("")
    lines.append("```bash")
    lines.append("python3 scripts/export_beads_status.py")
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    issues = load_issues()
    OUTPUT_FILE.write_text(render_markdown(issues), encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
