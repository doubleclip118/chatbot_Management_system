#!/bin/bash
# FastAPI 서버를 안전하게 재시작하는 스크립트

# FastAPI 서버 프로세스 종료
pkill -f "remake:app"
# 잠시 기다림 (예: 5초)
sleep 5

# FastAPI 서버 재시작
nohup sudo systemctl start remake.service
