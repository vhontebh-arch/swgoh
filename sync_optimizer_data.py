#!/usr/bin/env python3
"""Fetch one immutable optimizer-data snapshot and verify every Git blob hash."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

DEFAULT_REPOSITORY = "vhontebh-arch/swgoh"
DEFAULT_BRANCH = "optimizer-data"
REQUIRED_FILES = (
    "swgoh_972824625.json", "c3po.json", "data.json", "localization.json",
    "roster.csv", "ships.csv", "mods.csv", "mod_profiles.json",
)

def git_blob_sha(data: bytes) -> str:
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()

def fetch_bytes(url: str) -> bytes:
    headers = {"User-Agent": "Vhonte-SWGOH-Optimizer-Data/1.0"}
    token = os.environ.get("GITHUB_TOKEN")
    if token and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {token}"
        headers["Accept"] = "application/vnd.github+json"
    with urlopen(Request(url, headers=headers), timeout=60) as response:
        return response.read()

def snapshot_commit(repository: str, branch: str) -> str:
    url = f"https://api.github.com/repos/{repository}/branches/{branch}"
    payload = json.loads(fetch_bytes(url))
    commit = payload.get("commit", {}).get("sha")
    if not isinstance(commit, str) or len(commit) != 40:
        raise RuntimeError(f"Nie udało się ustalić commita gałęzi {branch}.")
    return commit

def load_snapshot(repository: str, branch: str, requested: list[str] | None = None):
    commit = snapshot_commit(repository, branch)
    base = f"https://raw.githubusercontent.com/{repository}/{commit}"
    manifest = json.loads(fetch_bytes(f"{base}/data_manifest.json"))
    entries = manifest.get("files")
    if not isinstance(entries, dict):
        raise RuntimeError("Manifest nie zawiera prawidłowej sekcji files.")
    names = list(requested) if requested else list(REQUIRED_FILES)
    if not requested:
        missing = sorted(set(REQUIRED_FILES) - set(entries))
        if missing:
            raise RuntimeError("Snapshot nie jest kompletny; brakuje w manifeście: " + ", ".join(missing))
    downloaded = {}
    for name in names:
        record = entries.get(name)
        if not isinstance(record, dict):
            raise RuntimeError(f"{name}: brak wpisu w data_manifest.json.")
        expected = record.get("git_blob_sha") or record.get("blob_sha")
        if not isinstance(expected, str) or len(expected) != 40:
            raise RuntimeError(f"{name}: manifest nie zawiera poprawnego Git blob SHA.")
        content = fetch_bytes(f"{base}/{name}")
        actual = git_blob_sha(content)
        if actual != expected:
            raise RuntimeError(f"{name}: niezgodny hash snapshotu (manifest {expected}, pobrano {actual}).")
        downloaded[name] = content
    return commit, manifest, downloaded

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", DEFAULT_REPOSITORY))
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    parser.add_argument("--files", nargs="+", help="Pobierz tylko wskazane pliki.")
    parser.add_argument("--output-dir", default=".")
    args = parser.parse_args()
    commit, manifest, files = load_snapshot(args.repository, args.branch, args.files)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        destination = output / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(destination.name + ".snapshot-tmp")
        temporary.write_bytes(content)
        temporary.replace(destination)
    print(f"Canonical data branch: {args.branch}")
    print(f"Snapshot commit: {commit}")
    print(f"Files synchronized and hash-verified: {len(files)}")
    for name, content in files.items():
        print(f"- {name}: {len(content)} bytes; git-blob={git_blob_sha(content)}")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as stream:
            stream.write("## Canonical optimizer data\n")
            stream.write(f"- Branch: {args.branch}\n")
            stream.write(f"- Snapshot commit: {commit}\n")
            stream.write(f"- Files hash-verified: {len(files)}\n")

if __name__ == "__main__":
    main()
