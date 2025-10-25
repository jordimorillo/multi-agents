#!/usr/bin/env bash
set -euo pipefail

# linear-move.sh
# Usage: ./linear-move.sh ISSUE_ID STATE_ID
# Requires LINEAR_API_KEY environment variable set to a personal API key with project access.

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 ISSUE_ID STATE_ID" >&2
  exit 2
fi

ISSUE_ID="$1"
STATE_ID="$2"

if [ -z "${LINEAR_API_KEY:-}" ]; then
  echo "Please set LINEAR_API_KEY environment variable." >&2
  exit 3
fi

payload=$(cat <<-JSON
{"query":"mutation issueUpdate($id: String!, $input: IssueUpdateInput!) { issueUpdate(id: $id, input: $input) { success } }","variables":{"id":"$ISSUE_ID","input":{"stateId":"$STATE_ID"}}}
JSON
)

curl -s -X POST "https://api.linear.app/graphql" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${LINEAR_API_KEY}" \
  -d "$payload" | jq -r '.data.issueUpdate.success'
