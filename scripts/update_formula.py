#!/usr/bin/env python3
"""Pin the atomgit-cli Formula to the latest AtomGit main commit."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Final
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_ROOT: Final = (
    "https://api.atomgit.com/api/v5/repos/"
    "hust-open-atom-club/atomgit-cli"
)
RELEASE_API: Final = f"{API_ROOT}/releases/latest"
COMMIT_API: Final = f"{API_ROOT}/commits/main"
RELEASE_VERSION_RE: Final = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
SNAPSHOT_VERSION_RE: Final = re.compile(
    r"^(\d+)\.(\d+)\.(\d+)-0\.(\d{14})-([0-9a-f]{12})$"
)
FORMULA_VERSION_RE: Final = re.compile(
    r'^(\s*version ")([^"]+)("\s*)$', re.MULTILINE
)
FORMULA_REVISION_RE: Final = re.compile(
    r'^(\s*revision: ")[0-9a-f]{40}("\s*)$', re.MULTILINE
)
COMMIT_RE: Final = re.compile(r"^[0-9a-f]{40}$")
USER_AGENT: Final = "homebrew-tap-atomgit-cli-updater/2.0"


class UpdateError(RuntimeError):
    """Raised when upstream metadata is unsafe to apply."""


def request_json(url: str) -> object:
    request = Request(
        url,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
    )
    try:
        with urlopen(request, timeout=60) as response:
            return json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise UpdateError(f"failed to read JSON from {url}: {error}") from error


def latest_release_version(url: str) -> tuple[int, int, int]:
    release = request_json(url)
    tag = release.get("tag_name") if isinstance(release, dict) else None
    if not isinstance(tag, str) or (match := RELEASE_VERSION_RE.fullmatch(tag)) is None:
        raise UpdateError(f"unexpected latest release tag: {tag!r}")
    return tuple(int(part) for part in match.groups())


def latest_main_commit(url: str) -> tuple[str, datetime]:
    commit = request_json(url)
    if not isinstance(commit, dict):
        raise UpdateError("latest main commit API returned a non-object")

    sha = commit.get("sha")
    commit_data = commit.get("commit")
    committer = commit_data.get("committer") if isinstance(commit_data, dict) else None
    committed_at = committer.get("date") if isinstance(committer, dict) else None

    if not isinstance(sha, str) or COMMIT_RE.fullmatch(sha) is None:
        raise UpdateError(f"unexpected main commit SHA: {sha!r}")
    if not isinstance(committed_at, str):
        raise UpdateError(f"unexpected main commit date: {committed_at!r}")

    try:
        timestamp = datetime.fromisoformat(committed_at.replace("Z", "+00:00"))
    except ValueError as error:
        raise UpdateError(f"unexpected main commit date: {committed_at!r}") from error
    if timestamp.tzinfo is None:
        raise UpdateError(f"main commit date has no timezone: {committed_at!r}")
    return sha, timestamp.astimezone(timezone.utc)


def snapshot_version(
    release: tuple[int, int, int], commit: str, committed_at: datetime
) -> str:
    major, minor, patch = release
    timestamp = committed_at.astimezone(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"{major}.{minor}.{patch + 1}-0.{timestamp}-{commit[:12]}"


def current_snapshot(formula: str) -> tuple[str, str, datetime]:
    version_matches = list(FORMULA_VERSION_RE.finditer(formula))
    revision_matches = list(FORMULA_REVISION_RE.finditer(formula))
    if len(version_matches) != 1:
        raise UpdateError(f"expected one Formula version, found {len(version_matches)}")
    if len(revision_matches) != 1:
        raise UpdateError(
            f"expected one Formula Git revision, found {len(revision_matches)}"
        )

    version = version_matches[0].group(2)
    revision_line = revision_matches[0].group(0)
    revision_match = re.search(r"[0-9a-f]{40}", revision_line)
    if revision_match is None:
        raise UpdateError("Formula Git revision is malformed")
    revision = revision_match.group(0)

    match = SNAPSHOT_VERSION_RE.fullmatch(version)
    if match is None:
        raise UpdateError(f"unexpected Formula snapshot version: {version!r}")
    if match.group(5) != revision[:12]:
        raise UpdateError("Formula version and Git revision do not match")

    timestamp = datetime.strptime(match.group(4), "%Y%m%d%H%M%S").replace(
        tzinfo=timezone.utc
    )
    return version, revision, timestamp


def replace_once(
    text: str, pattern: re.Pattern[str], replacement: str, label: str
) -> str:
    updated, count = pattern.subn(replacement, text)
    if count != 1:
        raise UpdateError(f"expected one {label}, found {count}")
    return updated


def update_formula(formula: str, version: str, revision: str) -> str:
    formula = replace_once(
        formula,
        FORMULA_VERSION_RE,
        rf'\g<1>{version}\g<3>',
        "Formula version declaration",
    )
    return replace_once(
        formula,
        FORMULA_REVISION_RE,
        rf'\g<1>{revision}\g<2>',
        "Formula Git revision",
    )


def write_atomically(path: Path, content: str) -> None:
    mode = path.stat().st_mode
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)
    os.chmod(temporary_path, mode)
    os.replace(temporary_path, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--formula", type=Path, default=Path("Formula/atomgit-cli.rb")
    )
    parser.add_argument("--release-api-url", default=RELEASE_API)
    parser.add_argument("--commit-api-url", default=COMMIT_API)
    args = parser.parse_args()

    formula = args.formula.read_text(encoding="utf-8")
    old_version, old_revision, old_timestamp = current_snapshot(formula)
    release = latest_release_version(args.release_api_url)
    revision, committed_at = latest_main_commit(args.commit_api_url)
    new_version = snapshot_version(release, revision, committed_at)

    if revision == old_revision and new_version == old_version:
        print(f"atomgit-cli {old_version} already tracks {old_revision[:12]}")
        return 0
    if committed_at < old_timestamp:
        raise UpdateError(
            f"refusing to move Formula from {old_revision[:12]} "
            f"back to {revision[:12]}"
        )

    updated = update_formula(formula, new_version, revision)
    write_atomically(args.formula, updated)
    print(
        f"updated atomgit-cli from {old_revision[:12]} to {revision[:12]} "
        f"({new_version})"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UpdateError) as error:
        raise SystemExit(f"error: {error}") from error
