#!/bin/bash

API_KEY="mown32.2reesssFFDSfsby"
BASE_URL="http://localhost:8000"

URL="$1"

if [ -z "$URL" ]; then
  echo "Usage: ./download.sh <YouTube URL>"
  exit 1
fi

# ----------------------------------------
# ダウンロード開始
# ----------------------------------------
JOB_RESPONSE=$(curl -sS -X POST \
  --get "$BASE_URL/download/start" \
  --data-urlencode "url=$URL" \
  -H "x-api-key: $API_KEY")

JOB_ID=$(echo "$JOB_RESPONSE" | jq -r '.job_id')

if [ -z "$JOB_ID" ] || [ "$JOB_ID" == "null" ]; then
  echo "Failed to start job."
  echo "Response: $JOB_RESPONSE"
  exit 1
fi

echo "Job started: $JOB_ID"

# ----------------------------------------
# 完了まで待機
# ----------------------------------------
while true; do

  STATUS_JSON=$(curl -sS \
    "$BASE_URL/download/status/$JOB_ID" \
    -H "x-api-key: $API_KEY")

  STATUS=$(echo "$STATUS_JSON" | jq -r '.status')
  PROGRESS=$(echo "$STATUS_JSON" | jq -r '.progress')

  echo "Status: $STATUS | Progress: $PROGRESS"

  if [ "$STATUS" == "success" ]; then
    break

  elif [ "$STATUS" == "error" ]; then
    echo "Error:"
    echo "$STATUS_JSON" | jq -r '.error'
    exit 1
  fi

  sleep 3
done

# ----------------------------------------
# ファイル名取得
# ----------------------------------------
FILENAME=$(echo "$STATUS_JSON" | jq -r '.filename')

if [ -z "$FILENAME" ] || [ "$FILENAME" == "null" ]; then
  echo "Failed to get filename."
  exit 1
fi

echo "Filename: $FILENAME"

# ----------------------------------------
# 一時ファイルにダウンロード
# ----------------------------------------
TEMP_FILE="${FILENAME}.download"

echo "Downloading video..."

if ! curl -L \
  --fail-with-body \
  --show-error \
  -H "x-api-key: $API_KEY" \
  "$BASE_URL/download/result/$JOB_ID" \
  -o "$TEMP_FILE"; then

  echo
  echo "Download failed."

  if [ -f "$TEMP_FILE" ]; then
    echo "Temporary file size:"
    ls -lh "$TEMP_FILE"
    rm -f "$TEMP_FILE"
  fi

  exit 1
fi

# ----------------------------------------
# ファイルサイズ確認
# ----------------------------------------
if [ ! -s "$TEMP_FILE" ]; then
  echo "Download failed: downloaded file is empty."
  rm -f "$TEMP_FILE"
  exit 1
fi

# ----------------------------------------
# 正式なファイル名に変更
# ----------------------------------------
mv "$TEMP_FILE" "$FILENAME"

echo
echo "Download complete!"
echo "Saved as: $FILENAME"
echo "File size:"
ls -lh "$FILENAME"
