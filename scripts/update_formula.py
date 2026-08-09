#!/usr/bin/env python3
"""Update the atomgit-cli Formula from the latest stable AtomGit release."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import tarfile
import tempfile
from typing import Final
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


RELEASE_API: Final = (
    "https://api.atomgit.com/api/v5/repos/"
    "hust-open-atom-club/atomgit-cli/releases/latest"
)
DOWNLOAD_ROOT: Final = (
    "https://atomgit.com/hust-open-atom-club/atomgit-cli/releases/download"
)
ASSETS: Final = (
    "ag_darwin_arm64.tar.gz",
    "ag_darwin_amd64.tar.gz",
    "ag_linux_arm64.tar.gz",
    "ag_linux_amd64.tar.gz",
)
VERSION_RE: Final = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
FORMULA_VERSION_RE: Final = re.compile(r'^(\s*version ")([^"]+)("\s*)$', re.MULTILINE)
SHA256_RE: Final = re.compile(r"^[0-9a-f]{64}$")
USER_AGENT: Final = "homebrew-tap-atomgit-cli-updater/1.0"


class UpdateError(RuntimeError):
    """Raised when release metadata or artifacts are unsafe to apply."""


def request_bytes(url: str) -> bytes:
    request = Request(
        url,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
    )
    try:
        with urlopen(request, timeout=60) as response:
            return response.read()
    except (HTTPError, URLError, TimeoutError) as error:
        raise UpdateError(f"failed to download {url}: {error}") from error


def latest_version(api_url: str) -> tuple[str, tuple[int, int, int]]:
    try:
        release = json.loads(request_bytes(api_url))
    except json.JSONDecodeError as error:
        raise UpdateError("latest release API returned invalid JSON") from error

    tag = release.get("tag_name") if isinstance(release, dict) else None
    if not isinstance(tag, str) or (match := VERSION_RE.fullmatch(tag)) is None:
        raise UpdateError(f"unexpected latest release tag: {tag!r}")

    return tag, tuple(int(part) for part in match.groups())


def current_version(formula: str) -> tuple[str, tuple[int, int, int]]:
    matches = list(FORMULA_VERSION_RE.finditer(formula))
    if len(matches) != 1:
        raise UpdateError(f"expected one Formula version, found {len(matches)}")

    version = matches[0].group(2)
    match = VERSION_RE.fullmatch(f"v{version}")
    if match is None:
        raise UpdateError(f"unexpected Formula version: {version!r}")

    return version, tuple(int(part) for part in match.groups())


def download_and_hash(tag: str, asset: str) -> str:
    url = f"{DOWNLOAD_ROOT}/{tag}/{asset}"
    digest = hashlib.sha256()

    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=120) as response, tempfile.NamedTemporaryFile() as archive:
            while chunk := response.read(1024 * 1024):
                digest.update(chunk)
                archive.write(chunk)
            archive.flush()

            try:
                with tarfile.open(archive.name, mode="r:gz") as tar:
                    if not any(PurePosixPath(member.name).name == "ag" for member in tar):
                        raise UpdateError(f"{asset} does not contain the ag executable")
            except tarfile.TarError as error:
                raise UpdateError(f"{asset} is not a valid tar.gz archive") from error
    except (HTTPError, URLError, TimeoutError) as error:
        raise UpdateError(f"failed to download {url}: {error}") from error

    checksum = digest.hexdigest()
    if SHA256_RE.fullmatch(checksum) is None:
        raise UpdateError(f"failed to calculate SHA-256 for {asset}")
    return checksum


def replace_once(
    text: str, pattern: re.Pattern[str], replacement: str, label: str
) -> str:
    updated, count = pattern.subn(replacement, text)
    if count != 1:
        raise UpdateError(f"expected one {label}, found {count}")
    return updated


def update_formula(formula: str, version: str, checksums: dict[str, str]) -> str:
    formula = replace_once(
        formula,
        FORMULA_VERSION_RE,
        rf'\g<1>{version}\g<3>',
        "Formula version declaration",
    )

    for asset, checksum in checksums.items():
        url_pattern = re.compile(
            rf"(releases/download/)v[^/]+(/{re.escape(asset)})"
        )
        formula = replace_once(
            formula,
            url_pattern,
            rf"\g<1>v{version}\g<2>",
            f"URL for {asset}",
        )

        checksum_pattern = re.compile(
            rf'(url "[^"]+/{re.escape(asset)}"\n\s*sha256 ")[0-9a-f]{{64}}(")'
        )
        formula = replace_once(
            formula,
            checksum_pattern,
            rf"\g<1>{checksum}\g<2>",
            f"SHA-256 for {asset}",
        )

    return formula


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
    parser.add_argument("--api-url", default=RELEASE_API)
    args = parser.parse_args()

    formula = args.formula.read_text(encoding="utf-8")
    old_version, old_version_parts = current_version(formula)
    tag, new_version_parts = latest_version(args.api_url)
    new_version = tag.removeprefix("v")

    if new_version_parts < old_version_parts:
        raise UpdateError(
            f"refusing to downgrade Formula from {old_version} to {new_version}"
        )
    if new_version_parts == old_version_parts:
        print(f"atomgit-cli {old_version} is already current")
        return 0

    checksums = {asset: download_and_hash(tag, asset) for asset in ASSETS}
    updated = update_formula(formula, new_version, checksums)
    write_atomically(args.formula, updated)
    print(f"updated atomgit-cli Formula from {old_version} to {new_version}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UpdateError) as error:
        raise SystemExit(f"error: {error}") from error
