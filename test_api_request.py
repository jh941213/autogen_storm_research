#!/usr/bin/env python3
"""
API 요청 테스트 스크립트
"""

import asyncio
import websockets
import json
import requests
import time

async def test_interactive_research():
    session_id = f"test_session_{int(time.time())}"
    
    # 1. WebSocket 연결 먼저 설정
    ws_url = f"ws://localhost:8002/ws/{session_id}"
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print(f"✅ WebSocket connected: {ws_url}")
            
            # 2. API 요청 보내기
            api_url = f"http://localhost:8002/research/interactive/{session_id}"
            payload = {
                "topic": "AI의 미래",
                "max_analysts": 2,
                "max_interview_turns": 2, 
                "parallel_interviews": True,
                "model_provider": "azure_openai"
            }
            
            print(f"Sending API request to: {api_url}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(api_url, json=payload)
            
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("✅ API request successful!")
                
                # WebSocket 메시지 수신 대기
                try:
                    while True:
                        message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        print(f"📨 WebSocket message: {message}")
                except asyncio.TimeoutError:
                    print("⏰ No more messages received")
            else:
                print(f"❌ API request failed: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_interactive_research())