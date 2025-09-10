import os
from openai import OpenAI
from dotenv import load_dotenv
from config import Config

# 매번 인스턴스 생성하지 않게 하기!
class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def get_gpt_response(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": """너는 반려동물 건강 상담 챗봇이야. 
                     출력 규칙:
                    - 들여쓰기(indent 2칸)를 사용해.
                    - 항목은 줄바꿈 후 보기 좋게 정리해.
                    - 불필요한 말 없이 깔끔하게 보여줘.
                    """},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"❌ GPT 호출 중 오류 발생: {str(e)}"

# 전역 인스턴스 (싱글톤)
_openai_service = None

def get_openai_service():
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service

# 호환성을 위한 전역 함수
def get_gpt_response(prompt: str) -> str:
    service = get_openai_service()
    return service.get_gpt_response(prompt)
