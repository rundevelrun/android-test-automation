#!/usr/bin/env bash
# Appium 서버 시작 스크립트

HOST="127.0.0.1"
PORT="4723"
LOG_FILE="appium.log"

echo "Appium 서버 시작: http://$HOST:$PORT"
echo "로그: $LOG_FILE"
echo "종료: Ctrl+C"
echo ""

appium \
  --address "$HOST" \
  --port "$PORT" \
  --log "$LOG_FILE" \
  --log-level info \
  --relaxed-security \
  --allow-cors
