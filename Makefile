# Agent Service Toolkit Makefile
.PHONY: help run-servers stop-servers install dev

# 기본 도움말
help:
	@echo "Available commands:"
	@echo "  make run-servers  - Start both FastAPI server and Streamlit app in iTerm vertical split"
	@echo "  make stop-servers - Stop all running servers and close iTerm window"
	@echo "  make install      - Install dependencies"
	@echo "  make dev          - Run in development mode"

# 서버 실행 (FastAPI + Streamlit) - iTerm vertical 분할에서
run-servers:
	@echo "🚀 Starting servers in iTerm vertical split..."
	@./scripts/run_servers.sh

# 서버 중지 및 iTerm 창 닫기
stop-servers:
	@echo "🛑 Stopping servers..."
	@pkill -f "uv run python3 src/run_service.py" || true
	@pkill -f "streamlit run src/streamlit_app.py" || true
	@pkill -f "streamlit" || true
	@echo "✅ Servers stopped"
	@echo "🪟 Closing iTerm window..."
	@if [ -f "/tmp/agent_service_window_id.txt" ]; then \
		WINDOW_ID=$$(cat /tmp/agent_service_window_id.txt); \
		osascript -e "tell application \"iTerm\" to close window id $$WINDOW_ID" || true; \
		rm -f /tmp/agent_service_window_id.txt; \
	else \
		osascript -e 'tell application "iTerm" to close every window' || true; \
	fi
	@echo "✅ iTerm window closed"

# 의존성 설치
install:
	@echo "📦 Installing dependencies..."
	@uv sync

# 개발 모드 (의존성 설치 후 서버 실행)
dev: install run-servers
