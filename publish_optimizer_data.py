#!/usr/bin/env python3
"""Publish an atomic account-data snapshot to the optimizer-data branch."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

BRANCH = "optimizer-data"
SNAPSHOT_FILES = (
    "swgoh_972824625.json", "c3po.json", "data.json", "localization.json",
    "roster.csv", "ships.csv", "mods.csv", "mod_profiles.json",
)
ROLES = {
    "swgoh_972824625.json": "raw Comlink player export",
    "c3po.json": "C3PO inventory export",
    "data.json": "normalized current game data",
    "localization.json": "current ENG_US localization",
    "roster.csv": "derived character roster",
    "ships.csv": "derived ship roster",
    "mods.csv": "derived complete mod inventory",
    "mod_profiles.json": "shared SWGOH.GG mod profiles",
}

def run(command: list[str], *, cwd: Path | None = None) -> str:
    result = subprocess.run(command, cwd=cwd, check=True, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return result.stdout.strip()

def git_blob_sha(data: bytes) -> str:
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()

def csv_rows(path: Path) -> int:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    return len(rows)

def validate_source(root: Path, names: tuple[str, ...]) -> dict:
    for name in names:
        path = root / name
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"Brak wymaganego pliku snapshotu: {name}")
    json_names = {"swgoh_972824625.json", "c3po.json", "data.json",
                  "localization.json", "mod_profiles.json"}
    parsed = {}
    for name in names:
        if name in json_names:
            parsed[name] = json.loads((root / name).read_text(encoding="utf-8"))
    if "swgoh_972824625.json" in parsed and not parsed["swgoh_972824625.json"].get("rosterUnit"):
        raise RuntimeError("Player export nie zawiera rosterUnit.")
    if "c3po.json" in parsed:
        ally = str(parsed["c3po.json"].get("allyCode", "")).replace("-", "")
        if ally != "972824625":
            raise RuntimeError("c3po.json nie dotyczy konta 972824625.")
    if "data.json" in parsed:
        game = parsed["data.json"]
        for key in ("units", "equipment", "recipe"):
            if not game.get(key):
                raise RuntimeError(f"data.json nie zawiera {key}.")
    if "mod_profiles.json" in parsed and not parsed["mod_profiles.json"].get("profiles"):
        raise RuntimeError("mod_profiles.json nie zawiera profili.")
    for name in ("roster.csv", "ships.csv", "mods.csv"):
        if name in names and csv_rows(root / name) < 1:
            raise RuntimeError(f"{name} nie zawiera rekordów.")
    return parsed

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profiles-only", action="store_true")
    args = parser.parse_args()
    root = Path.cwd()
    names = ("mod_profiles.json",) if args.profiles_only else SNAPSHOT_FILES
    parsed = validate_source(root, names)
    repository = os.environ.get("GITHUB_REPOSITORY", "vhontebh-arch/swgoh")
    source_branch = os.environ.get("GITHUB_REF_NAME", "main")
    source_commit = run(["git", "rev-parse", "HEAD"], cwd=root)
    published_at = datetime.now(timezone.utc).isoformat()
    run(["git", "fetch", "origin", BRANCH], cwd=root)
    temporary = Path(tempfile.mkdtemp(prefix="optimizer-data-worktree-"))
    temporary.rmdir()
    try:
        run(["git", "worktree", "add", "--detach", str(temporary), f"origin/{BRANCH}"], cwd=root)
        manifest_path = temporary / "data_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        records = manifest.setdefault("files", {})
        for name in names:
            shutil.copy2(root / name, temporary / name)
            content = (temporary / name).read_bytes()
            old = records.get(name, {})
            records[name] = {
                "role": old.get("role", ROLES.get(name, name)),
                "bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
                "git_blob_sha": git_blob_sha(content),
                "source_branch": source_branch,
                "source_commit": source_commit,
            }
        if args.profiles_only:
            manifest["profiles_published_at"] = published_at
            manifest["profiles_source_commit"] = source_commit
        else:
            player = parsed["swgoh_972824625.json"]
            c3po = parsed["c3po.json"]
            manifest["snapshot"] = {
                "published_at": published_at,
                "producer_repository": repository,
                "producer_branch": source_branch,
                "producer_commit": source_commit,
                "c3po_source_commit": os.environ.get("C3PO_SOURCE_COMMIT", ""),
                "player_roster_units": len(player.get("rosterUnit", [])),
                "character_rows": csv_rows(root / "roster.csv"),
                "ship_rows": csv_rows(root / "ships.csv"),
                "mod_rows": csv_rows(root / "mods.csv"),
                "c3po_unequipped_mods": len(c3po.get("inventory", {}).get("unequippedMod", [])),
            }
        manifest["schema_version"] = 1
        manifest["dataset"] = f"{repository} canonical optimizer data"
        manifest["account_ally_code"] = "972824625"
        manifest["policy"] = {
            **manifest.get("policy", {}),
            "single_source_of_truth": BRANCH,
            "atomic_snapshot": "Account raw exports and all derived account files are published together from one update run.",
            "recent_changes": "Differences between exports taken minutes apart can be legitimate; all consumers use one immutable published commit.",
            "profile_freshness_days": 5,
            "consumers": "All active optimizer versions fetch and hash-verify files from this branch. Local copies are temporary runtime inputs.",
        }
        manifest["files"] = records
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        run(["git", "config", "user.name", "github-actions[bot]"], cwd=temporary)
        run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], cwd=temporary)
        run(["git", "add", *names, "data_manifest.json"], cwd=temporary)
        run(["git", "commit", "-m", "Publish canonical SWGOH optimizer data"], cwd=temporary)
        new_commit = run(["git", "rev-parse", "HEAD"], cwd=temporary)
        run(["git", "push", "origin", f"HEAD:refs/heads/{BRANCH}"], cwd=temporary)
        print(f"Published {len(names)} files to {BRANCH}@{new_commit}")
        print(f"Snapshot timestamp: {published_at}")
        for name in names:
            print(f"- {name}: {records[name]['git_blob_sha']}")
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(temporary)],
                       cwd=root, check=False)
        shutil.rmtree(temporary, ignore_errors=True)

if __name__ == "__main__":
    main()
