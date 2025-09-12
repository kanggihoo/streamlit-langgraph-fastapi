# Agent Service Toolkit Makefile
.PHONY: help run-servers stop-servers install dev run-ec2-servers git-pull

# 기본 도움말
help:
	@echo "Available commands:"
	@echo "  make run-servers      - Start both FastAPI server and Streamlit app in iTerm vertical split"
	@echo "  make stop-servers     - Stop all running servers and close iTerm window"
	@echo "  make install          - Install dependencies"
	@echo "  make dev              - Run in development mode"
	@echo "  make run-ec2-servers  - Start servers on EC2 (FastAPI + Streamlit with venv activation)"
	@echo "  make git-pull         - Pull latest code from GitHub on EC2"

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

# EC2에서 서버 실행 (가상환경 활성화 후 순차 실행)
run-ec2-servers: stop-ec2-servers
	@echo "🚀 Starting servers on EC2..."
	@echo "📁 Activating virtual environment and moving to project directory..."
	@cd /home/ec2-user/SW-project && \
	. ./.venv/bin/activate && \
	echo "✅ Virtual environment activated and moved to project directory" && \
	echo "🔧 Starting FastAPI server..." && \
	uv run python3 src/run_server.py & \
	echo "⏳ Waiting 2 seconds before starting Streamlit server..." && \
	sleep 2 && \
	echo "🎨 Starting Streamlit server..." && \
	uv run streamlit run src/streamlit_app.py
	@echo "✅ Both servers started on EC2"


# ==============================================================================
# 🛑 포트 정리: 8001, 8501 포트를 사용하는 모든 프로세스를 종료합니다.
# `make stop-servers`
# ==============================================================================
stop-ec2-servers:
	@echo "🛑 Checking for and stopping existing servers..."
	@lsof -t -i:8001 | xargs --no-run-if-empty kill -9
	@lsof -t -i:8501 | xargs --no-run-if-empty kill -9
	@echo "✅ Ports 8001 and 8501 are clear."

# EC2에서 GitHub에서 최신 코드 가져오기

git-pull:
	@echo "📥 Pulling latest code from GitHub on EC2..."
	@cd /home/ec2-user/SW-project && \
	. ./.venv/bin/activate && \
	echo "✅ Virtual environment activated and moved to project directory" && \
	git pull origin && \
	echo "✅ Code updated from GitHub"