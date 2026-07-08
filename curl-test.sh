#!/usr/bin/env bash
# Tests the timeline_post API endpoints:
#   1. POST a random timeline post
#      e.g. curl -X POST http://localhost:5001/api/timeline_post -d "name=Ronard" -d "email=ronard@example.com" -d "content=Hello world"
#   2. GET all posts and verify the new post is there
#      e.g. curl http://localhost:5001/api/timeline_post
#   3. DELETE the test post and verify it's gone
#      e.g. curl -X DELETE http://localhost:5001/api/timeline_post/1
#
# Usage: ./curl-test.sh [base_url]   (default: http://localhost:5001)

set -euo pipefail

BASE_URL="${1:-http://localhost:5001}"
ENDPOINT="$BASE_URL/api/timeline_post"

RAND=$RANDOM
NAME="TestUser$RAND"
EMAIL="testuser$RAND@example.com"
CONTENT="Test post content $RAND"

echo "==> POST: creating test timeline post (name=$NAME)"
POST_RESPONSE=$(curl -sf -X POST "$ENDPOINT" \
  -d "name=$NAME" \
  -d "email=$EMAIL" \
  -d "content=$CONTENT")
echo "$POST_RESPONSE" | python3 -m json.tool

POST_ID=$(echo "$POST_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "==> Created post with id=$POST_ID"

echo "==> GET: verifying the post appears in the timeline"
GET_RESPONSE=$(curl -sf "$ENDPOINT")
if echo "$GET_RESPONSE" | python3 -c "
import sys, json
posts = json.load(sys.stdin)['timeline_posts']
sys.exit(0 if any(p['id'] == $POST_ID and p['content'] == '$CONTENT' for p in posts) else 1)
"; then
    echo "PASS: post $POST_ID found in GET response"
else
    echo "FAIL: post $POST_ID not found in GET response"
    exit 1
fi

echo "==> DELETE: cleaning up test post $POST_ID"
curl -sf -X DELETE "$ENDPOINT/$POST_ID" | python3 -m json.tool

echo "==> GET: verifying the post was deleted"
GET_RESPONSE=$(curl -sf "$ENDPOINT")
if echo "$GET_RESPONSE" | python3 -c "
import sys, json
posts = json.load(sys.stdin)['timeline_posts']
sys.exit(1 if any(p['id'] == $POST_ID for p in posts) else 0)
"; then
    echo "PASS: post $POST_ID no longer in GET response"
else
    echo "FAIL: post $POST_ID still present after DELETE"
    exit 1
fi

echo "All tests passed."
