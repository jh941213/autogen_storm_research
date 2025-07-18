#!/usr/bin/env python3
"""
인터랙티브 STORM Research Assistant 테스트 클라이언트
사용자 피드백 시나리오를 자동으로 테스트합니다.
"""

import asyncio
import json
import websockets
import aiohttp
from datetime import datetime
import time

class InteractiveTestClient:
    def __init__(self, base_url="http://localhost:8002"):
        self.base_url = base_url
        self.ws_url = base_url.replace("http", "ws")
        self.session_id = f"test_session_{int(time.time())}"
        self.websocket = None
        
    async def connect(self):
        """WebSocket 연결"""
        try:
            uri = f"{self.ws_url}/ws/{self.session_id}"
            print(f"🔗 WebSocket 연결 시도: {uri}")
            self.websocket = await websockets.connect(uri)
            print("✅ WebSocket 연결 성공!")
            return True
        except Exception as e:
            print(f"❌ WebSocket 연결 실패: {e}")
            return False
    
    async def send_message(self, message_type, data):
        """메시지 전송"""
        if not self.websocket:
            print("❌ WebSocket 연결이 없습니다")
            return
        
        message = {
            "type": message_type,
            "data": data
        }
        
        print(f"📤 메시지 전송: {message}")
        await self.websocket.send(json.dumps(message))
    
    async def receive_messages(self):
        """메시지 수신 (백그라운드 태스크)"""
        if not self.websocket:
            return
        
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await self.handle_message(data)
        except websockets.exceptions.ConnectionClosed:
            print("🔌 WebSocket 연결이 종료되었습니다")
        except Exception as e:
            print(f"❌ 메시지 수신 오류: {e}")
    
    async def handle_message(self, data):
        """수신된 메시지 처리"""
        msg_type = data.get("type")
        msg_data = data.get("data", {})
        
        print(f"📥 수신된 메시지: {msg_type}")
        print(f"    데이터: {msg_data}")
        
        if msg_type == "progress":
            print(f"📊 진행 상황: {msg_data.get('message', '')}")
            
        elif msg_type == "analyst_count_request":
            print(f"👥 분석가 수 요청: {msg_data}")
            # 시나리오: 5명의 분석가 선택
            await asyncio.sleep(2)  # 사용자 사고 시간 시뮬레이션
            await self.send_message("analyst_count", {"count": 5})
            print("✅ 분석가 수 응답: 5명")
            
        elif msg_type == "report_approval_request":
            print(f"📋 보고서 승인 요청:")
            preview = msg_data.get("preview", {})
            print(f"    버전: {preview.get('version', 'N/A')}")
            print(f"    서론 미리보기: {preview.get('introduction_preview', 'N/A')[:100]}...")
            print(f"    본문 미리보기: {preview.get('main_content_preview', 'N/A')[:100]}...")
            print(f"    결론 미리보기: {preview.get('conclusion_preview', 'N/A')[:100]}...")
            print(f"    전체 길이: {preview.get('total_length', 'N/A')}자")
            
            # 시나리오: 첫 번째 보고서는 피드백으로 재작성 요청
            await asyncio.sleep(3)  # 사용자 검토 시간 시뮬레이션
            
            version = preview.get('version', 1)
            if version == 1:
                print("🔄 시나리오: 첫 번째 보고서 - 피드백 재작성 요청")
                feedback = "AI 기술의 윤리적 문제와 개인정보보호 측면을 더 강조해주세요. 특히 데이터 편향성과 알고리즘 투명성에 대한 내용을 추가하고, 규제 현황도 포함해주세요."
                await self.send_message("report_approval", {
                    "action": "rewrite",
                    "rewrite_type": "feedback",
                    "feedback": feedback
                })
                print(f"✅ 피드백 전송: {feedback}")
                
            elif version == 2:
                print("✅ 시나리오: 두 번째 보고서 - 승인")
                await self.send_message("report_approval", {
                    "action": "approve"
                })
                print("✅ 보고서 승인 완료")
            
        elif msg_type == "result":
            print("🎉 최종 결과 수신!")
            print(f"    주제: {msg_data.get('topic', 'N/A')}")
            print(f"    분석가 수: {len(msg_data.get('analysts', []))}")
            print(f"    인터뷰 수: {msg_data.get('interview_count', 'N/A')}")
            print(f"    완료 시간: {msg_data.get('completed_at', 'N/A')}")
            
            # 결과 저장
            filename = f"test_result_{self.session_id}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(msg_data.get('final_report', ''))
            print(f"📄 결과 저장: {filename}")
            
        elif msg_type == "error":
            print(f"❌ 오류 발생: {msg_data.get('error', 'Unknown error')}")
    
    async def start_research(self, topic="AI의 미래와 윤리적 도전"):
        """연구 시작"""
        url = f"{self.base_url}/research/interactive/{self.session_id}"
        
        payload = {
            "topic": topic,
            "max_analysts": 3,
            "max_interview_turns": 3,
            "parallel_interviews": True,
            "model_provider": "azure_openai"
        }
        
        print(f"🚀 연구 시작 요청: {url}")
        print(f"    주제: {topic}")
        print(f"    페이로드: {payload}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ 연구 시작 성공: {result}")
                        return True
                    else:
                        error_text = await response.text()
                        print(f"❌ 연구 시작 실패: {response.status} - {error_text}")
                        return False
        except Exception as e:
            print(f"❌ 연구 시작 오류: {e}")
            return False
    
    async def run_test_scenario(self):
        """전체 테스트 시나리오 실행"""
        print("🌟 STORM Research Assistant 인터랙티브 테스트 시작")
        print("="*60)
        
        # 1. WebSocket 연결
        if not await self.connect():
            return False
        
        # 2. 메시지 수신 백그라운드 태스크 시작
        receive_task = asyncio.create_task(self.receive_messages())
        
        # 3. 연구 시작
        await asyncio.sleep(1)  # 연결 안정화 대기
        success = await self.start_research()
        
        if not success:
            receive_task.cancel()
            return False
        
        # 4. 테스트 완료 대기 (최대 10분)
        try:
            await asyncio.wait_for(receive_task, timeout=600)
        except asyncio.TimeoutError:
            print("⏰ 테스트 타임아웃 (10분)")
            receive_task.cancel()
        except Exception as e:
            print(f"❌ 테스트 오류: {e}")
            receive_task.cancel()
        
        # 5. 연결 종료
        if self.websocket:
            await self.websocket.close()
        
        print("🏁 테스트 완료")
        return True
    
    async def close(self):
        """연결 종료"""
        if self.websocket:
            await self.websocket.close()

async def main():
    """메인 테스트 함수"""
    client = InteractiveTestClient()
    
    print("🧪 인터랙티브 피드백 시나리오 테스트")
    print("="*60)
    print("시나리오:")
    print("1. 분석가 수 요청 → 5명 선택")
    print("2. 첫 번째 보고서 → 윤리/개인정보 측면 강화 피드백")
    print("3. 두 번째 보고서 → 승인")
    print("="*60)
    
    try:
        await client.run_test_scenario()
    except KeyboardInterrupt:
        print("\n🛑 사용자가 테스트를 중단했습니다")
    except Exception as e:
        print(f"❌ 테스트 실행 오류: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())