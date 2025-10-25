#!/usr/bin/env bash
set -euo pipefail

# ensure-tests-for-changes.sh
# Simple heuristic: for each changed source file check presence of a related test file.
# Exits 0 if tests exist for all changed source files, otherwise exits 1.

BASE_REF="${GITHUB_BASE_REF:-}" 
if [ -n "$BASE_REF" ]; then
  git fetch origin "$BASE_REF" --depth=1 || true
  CHANGED_FILES=$(git diff --name-only "origin/$BASE_REF"...HEAD || git diff --name-only "$BASE_REF"...HEAD)
else
  # fallback: compare with main if available, else last commit
  if git rev-parse --verify origin/main >/dev/null 2>&1; then
    git fetch origin main --depth=1 || true
    CHANGED_FILES=$(git diff --name-only origin/main...HEAD)
  else
    CHANGED_FILES=$(git diff --name-only HEAD~1 HEAD || true)
  fi
fi

if [ -z "$CHANGED_FILES" ]; then
  echo "No changed files detected."
  exit 0
fi

echo "Changed files:" >&2
echo "$CHANGED_FILES" >&2

MISSING_TESTS=()

is_test_file() {
  local f="$1"
  case "$f" in
    *test*|*spec*) return 0;;
    tests/*) return 0;;
    *) return 1;;
  esac
}

for file in $CHANGED_FILES; do
  # skip docs, config, workflows
  case "$file" in
    *.md|.github/*|.gitignore|LICENSE|README*|setup*|SETUP.md) continue;;
  esac

  if is_test_file "$file"; then
    continue
  fi

  # consider source code extensions
  case "$file" in
    *.js|*.ts|*.jsx|*.tsx|*.py|*.go|*.java|*.rb|*.php)
      ;;
    *)
      # not a source file we enforce tests for
      continue
      ;;
  esac

  # heuristics: sibling test file, tests/ path, __tests__ or *.spec.*
  dir=$(dirname "$file")
  base=$(basename "$file")
  test_candidates=("$dir/test_$base" "$dir/${base%.js}.spec.js" "$dir/${base%.js}.test.js" "tests/$base" "tests/${base}" "$dir/__tests__/${base}" "$dir/${base%.py}_test.py" "tests/${base%.py}_test.py")

  found=false
  for t in "${test_candidates[@]}"; do
    if [ -f "$t" ]; then
      found=true
      break
    fi
  done

  if ! $found; then
    MISSING_TESTS+=("$file")
  fi
done

if [ ${#MISSING_TESTS[@]} -ne 0 ]; then
  echo "The following changed source files are missing tests:" >&2
  for f in "${MISSING_TESTS[@]}"; do
    echo " - $f" >&2
  done
  echo "Failing due to missing tests (project policy: require_tests=true)." >&2
  exit 1
fi

echo "All changed source files have corresponding tests (heuristic)."
exit 0
