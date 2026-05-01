#!/usr/bin/env bash
ulimit -n 65536

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 포트 5000 강제 종료
PIDS=$(lsof -ti:5000 2>/dev/null)
if [ -n "$PIDS" ]; then
    echo "[llm-lite] 기존 프로세스 종료 중..."
    kill -9 $PIDS 2>/dev/null || true
    sleep 2
fi

source "$DIR/x64/gemma3N_E4B/pynq_env/bin/activate"
cd "$DIR/x64/gemma3N_E4B"

python gui_app.py &
BACKEND_PID=$!

echo "[llm-lite] 모델 로딩 중... 잠시 기다려주세요."

# Flask가 실제로 올라왔는지 확인 (최대 120초)
for i in $(seq 1 120); do
    # 백엔드 프로세스가 죽었으면 바로 에러 처리
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "[llm-lite] 오류: 백엔드 프로세스가 종료됨"
        exit 1
    fi
    curl -sf http://127.0.0.1:5000/api/health >/dev/null 2>&1 && break
    sleep 1
done

if ! curl -sf http://127.0.0.1:5000/api/health >/dev/null 2>&1; then
    echo "[llm-lite] 오류: 백엔드 응답 없음"
    kill -9 $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo "[llm-lite] 네이티브 GUI 실행 중..."
"$DIR/native/build/llm-lite-native"

kill -9 $BACKEND_PID 2>/dev/null || true
