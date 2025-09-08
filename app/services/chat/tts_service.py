import os
import base64
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import openai
from app.models.tts import TTSSettings, TTSVoice
from app.models.pet import Pet

logger = logging.getLogger(__name__)

class TTSProvider(ABC):
    """TTS 제공업체 인터페이스"""
    
    @abstractmethod
    def generate_speech(self, text: str, settings: TTSSettings) -> bytes:
        """음성 생성"""
        pass
    
    @abstractmethod
    def get_available_voices(self) -> Dict[str, Any]:
        """사용 가능한 음성 목록 반환"""
        pass

class OpenAITTSProvider(TTSProvider):
    """OpenAI TTS 제공업체"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # OpenAI TTS 음성 목록
        self.voices = {
            'alloy': '자연스러운 중성 목소리',
            'echo': '남성적인 목소리',
            'fable': '영국식 남성 목소리',
            'onyx': '깊고 차분한 남성 목소리',
            'nova': '활기찬 여성 목소리',
            'shimmer': '부드러운 여성 목소리'
        }
    
    def generate_speech(self, text: str, settings: TTSSettings) -> bytes:
        """OpenAI TTS API를 사용하여 음성 생성"""
        try:
            # OpenAI TTS 파라미터 설정
            voice = settings.voice_id or 'nova'
            speed = max(0.25, min(4.0, settings.speed or 1.0))  # OpenAI 허용 범위
            
            logger.info(f"OpenAI TTS 요청 - 음성: {voice}, 속도: {speed}, 텍스트 길이: {len(text)}")
            
            response = self.client.audio.speech.create(
                model="tts-1",  # 또는 "tts-1-hd" (고품질)
                voice=voice,
                input=text,
                speed=speed,
                response_format="mp3"
            )
            
            audio_data = response.content
            logger.info(f"OpenAI TTS 성공 - 오디오 크기: {len(audio_data)} bytes")
            return audio_data
            
        except Exception as e:
            logger.error(f"OpenAI TTS 생성 실패: {str(e)}")
            raise Exception(f"OpenAI TTS 오류: {str(e)}")
    
    def get_available_voices(self) -> Dict[str, Any]:
        """OpenAI 사용 가능한 음성 목록"""
        return {
            'korean_female': {
                'nova': '활기찬 여성 목소리',
                'shimmer': '부드러운 여성 목소리'
            },
            'korean_male': {
                'echo': '남성적인 목소리',
                'onyx': '깊고 차분한 남성 목소리',
                'fable': '영국식 남성 목소리'
            },
            'international': {
                'alloy': '자연스러운 중성 목소리'
            }
        }


class TTSService:
    """TTS 서비스 메인 클래스"""
    
    def __init__(self):
        self.providers = {
            'openai': OpenAITTSProvider()
        }
        
        # 기본 제공업체 설정
        self.default_provider = os.getenv('DEFAULT_TTS_PROVIDER', 'openai')
        
        logger.info(f"TTS 서비스 초기화 - 기본 제공업체: {self.default_provider}")
    
    def validate_voice_for_provider(self, provider: str, voice_id: str) -> str:
        """제공업체에 맞는 음성인지 검증하고 필요시 기본값 반환"""
        if provider not in self.providers:
            return 'nova'  # 기본 OpenAI 음성
            
        provider_instance = self.providers[provider]
        available_voices = provider_instance.get_available_voices()
        
        # 모든 카테고리에서 음성 ID 검색
        for category_voices in available_voices.values():
            if voice_id in category_voices:
                return voice_id
        
        # 호환되지 않는 음성인 경우 OpenAI 기본값 반환
        return 'nova'

    def generate_speech_for_pet(self, pet_id: str, text: str) -> Dict[str, Any]:
        """반려동물용 음성 생성"""
        try:
            # TTS 설정 조회
            settings = TTSSettings.get_by_pet_id(pet_id)
            
            if not settings:
                # 기본 설정 생성
                settings = TTSSettings.create_default_settings(pet_id, self.default_provider)
                logger.info(f"반려동물 {pet_id}에 대한 기본 TTS 설정 생성")
            
            # 제공업체와 음성 호환성 검증 및 자동 수정
            validated_voice = self.validate_voice_for_provider(settings.provider, settings.voice_id)
            if validated_voice != settings.voice_id:
                logger.warning(f"음성 불일치 수정: {settings.provider} 제공업체에서 {settings.voice_id} -> {validated_voice}")
                settings.update_settings(voice_id=validated_voice)
                settings.voice_id = validated_voice  # 메모리상 즉시 반영
            
            # TTS가 비활성화된 경우
            if not settings.is_enabled:
                return {
                    'success': False,
                    'error': 'TTS가 비활성화되어 있습니다.',
                    'audio': None
                }
            
            # 제공업체별 음성 생성
            provider = self.providers.get(settings.provider)
            if not provider:
                logger.error(f"지원하지 않는 TTS 제공업체: {settings.provider}")
                return {
                    'success': False,
                    'error': f'지원하지 않는 TTS 제공업체: {settings.provider}',
                    'audio': None
                }
            
            # 텍스트 길이 제한
            if len(text) > 4000:  # TTS API 제한
                text = text[:4000] + "..."
                logger.warning(f"텍스트가 너무 길어 자동 잘림: {len(text)}자")
            
            # 음성 생성
            audio_data = provider.generate_speech(text, settings)
            
            # Base64 인코딩
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            return {
                'success': True,
                'audio': audio_base64,
                'provider': settings.provider,
                'voice_id': settings.voice_id,
                'text_length': len(text)
            }
            
        except Exception as e:
            logger.error(f"TTS 생성 중 오류 (pet_id: {pet_id}): {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'audio': None
            }
    
    def get_pet_tts_settings(self, pet_id: str) -> Dict[str, Any]:
        """반려동물의 TTS 설정 조회"""
        try:
            settings = TTSSettings.get_by_pet_id(pet_id)
            
            if not settings:
                # 기본 설정 생성
                settings = TTSSettings.create_default_settings(pet_id, self.default_provider)
            
            # 펫 이름도 함께 조회
            from app.models.pet import Pet
            from app.models import db
            pet = db.session.query(Pet).filter(Pet.pet_id == pet_id).first()
            
            settings_dict = settings.to_dict()
            settings_dict['pet_name'] = pet.pet_name if pet else None
            
            return {
                'success': True,
                'settings': settings_dict
            }
            
        except Exception as e:
            logger.error(f"TTS 설정 조회 중 오류 (pet_id: {pet_id}): {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'settings': None
            }
    
    def update_pet_tts_settings(self, pet_id: str, **kwargs) -> Dict[str, Any]:
        """반려동물의 TTS 설정 업데이트"""
        try:
            settings = TTSSettings.get_by_pet_id(pet_id)
            
            if not settings:
                settings = TTSSettings.create_default_settings(pet_id, self.default_provider)
            
            # 설정 업데이트
            settings.update_settings(**kwargs)
            
            return {
                'success': True,
                'settings': settings.to_dict()
            }
            
        except Exception as e:
            logger.error(f"TTS 설정 업데이트 중 오류 (pet_id: {pet_id}): {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'settings': None
            }
    
    def get_available_voices(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """사용 가능한 음성 목록 조회"""
        try:
            if provider and provider in self.providers:
                return {
                    'success': True,
                    'voices': self.providers[provider].get_available_voices()
                }
            
            # 모든 제공업체의 음성 목록 병합
            all_voices = {}
            for prov_name, prov_instance in self.providers.items():
                try:
                    voices = prov_instance.get_available_voices()
                    for category, voice_list in voices.items():
                        if category not in all_voices:
                            all_voices[category] = {}
                        all_voices[category].update(voice_list)
                except Exception as e:
                    logger.warning(f"{prov_name} 제공업체 음성 목록 로드 실패: {str(e)}")
            
            return {
                'success': True,
                'voices': all_voices
            }
            
        except Exception as e:
            logger.error(f"음성 목록 조회 중 오류: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'voices': {}
            }

# TTS 서비스 싱글톤 인스턴스
tts_service = TTSService()