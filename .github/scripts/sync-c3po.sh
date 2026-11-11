#!/usr/bin/env bash
set -euo pipefail

REPOSITORY="${GITHUB_REPOSITORY:-vhontebh-arch/swgoh}"
SOURCE_COMMIT="${C3PO_SOURCE_COMMIT:-}"

if [[ -z "$SOURCE_COMMIT" ]]; then
  SOURCE_COMMIT="$(git ls-remote origin refs/heads/main | awk 'NR == 1 { print $1 }')"
fi

if [[ ! "$SOURCE_COMMIT" =~ ^[0-9a-f]{40}$ ]]; then
  echo "ERROR: nie udało się ustalić poprawnego commita źródłowego main: $SOURCE_COMMIT" >&2
  exit 1
fi

SOURCE_URL="https://raw.githubusercontent.com/$REPOSITORY/$SOURCE_COMMIT/c3po.json"
curl --fail --silent --show-error --location --retry 3 --retry-delay 2 \
  "$SOURCE_URL" --output c3po.json

test -s c3po.json

python - <<'PY'
import json
from pathlib import Path

data = json.loads(Path("c3po.json").read_text(encoding="utf-8"))
if str(data.get("allyCode", "")).replace("-", "") != "972824625":
    raise SystemExit("ERROR: c3po.json nie dotyczy oczekiwanego konta.")
mods = data.get("inventory", {}).get("unequippedMod")
if not isinstance(mods, list):
    raise SystemExit("ERROR: c3po.json nie zawiera inventory.unequippedMod jako listy.")
print("C3PO unequipped mods:", len(mods))
PY

BLOB_SHA="$(git hash-object c3po.json)"
SHA256="$(sha256sum c3po.json | awk '{ print $1 }')"
MOD_COUNT="$(python -c 'import json; print(len(json.load(open("c3po.json", encoding="utf-8"))["inventory"]["unequippedMod"]))')"

echo "Canonical C3PO source: main@$SOURCE_COMMIT"
echo "Git blob SHA: $BLOB_SHA"
echo "SHA-256: $SHA256"
echo "Unequipped mods: $MOD_COUNT"

if [[ -n "${GITHUB_ENV:-}" ]]; then
  {
    echo "C3PO_SOURCE_COMMIT=$SOURCE_COMMIT"
    echo "C3PO_BLOB_SHA=$BLOB_SHA"
    echo "C3PO_SHA256=$SHA256"
  } >> "$GITHUB_ENV"
fi

if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
  {
    echo "## Canonical C-3PO snapshot"
    echo "- Source: `main@$SOURCE_COMMIT`"
    echo "- Git blob SHA: `$BLOB_SHA`"
    echo "- SHA-256: `$SHA256`"
    echo "- Unequipped mods: **$MOD_COUNT**"
  } >> "$GITHUB_STEP_SUMMARY"
fi
