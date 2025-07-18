#!/usr/bin/env python3
"""
WebSocket 연결 테스트 스크립트
"""

import asyncio
import websockets
import json

async def test_websocket():
    session_id = "test_session_123"
    ws_url = f"ws://localhost:8002/ws/{session_id}"
    
    try:
        print(f"Connecting to WebSocket: {ws_url}")
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # 테스트 메시지 전송
            test_message = {
                "type": "analyst_count",
                "data": {"count": 3}
            }
            
            await websocket.send(json.dumps(test_message))
            print("✅ Message sent successfully!")
            
            # 응답 대기 (타임아웃 포함)
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"✅ Response received: {response}")
            except asyncio.TimeoutError:
                print("⏰ No response received within timeout (this is expected)")
                
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_websocket())