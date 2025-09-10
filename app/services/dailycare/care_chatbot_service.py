# -----------------------------
# care_chatbot_service.py 수정본
# -----------------------------
from dotenv import load_dotenv
import json
from app.services.pet import PetService
from app.services.dailycare.healthcare_service import HealthCareService
from app.services.dailycare.medicalcare_service import MedicalCareService
from app.services.dailycare.openAI_service import get_gpt_response
from app.services.dailycare.vectorstore_service import VectorStoreService
from flask import current_app as app
from langchain_core.documents import Document
load_dotenv()
print(VectorStoreService)

class CareChatbotService:
    # 벡터 스토어 인스턴스를 클래스 변수로 관리 (싱글톤)
    _vector_store = None

    ATTRIBUTE_MAP = {
        "health": {"weight_kg": ["몸무게", "체중"], "food": ["음식", "사료"], "water": ["물", "음수"], "excrement_status": ["배변"], "walk_time_minutes": ["산책"]},
        "allergy": {"allergen": ["알러지"], "symptoms": ["증상"], "severity": ["심각도"], "allergy_type": ["알러지 유형"]},
        "disease": {"disease_name": ["질병"], "diagnosis_date": ["진단일"], "doctor_name": ["의사"], "hospital_name": ["병원명"], "medical_cost": ["병원비"], "symptoms": ["증상"], "treatment_details": ["치료"]},
        "medication": {"medication_name": ["약"], "dosage": ["용량"], "purpose": ["목적"], "side_effects_notes": ["부작용"], "hospital_name": ["병원명"], "frequency": ["주기"]},
        "surgery": {"surgery_type": ["수술"], "surgery_name": ["수술명"], "surgery_date": ["수술일"], "hospital_name": ["병원명"], "recovery_status": ["회복상태"], "doctor_name": ["의사"]},
        "vaccination": {"vaccine_name": ["백신"], "vaccination_date": ["접종일"], "next_vaccination_date": ["다음 접종"], "side_effects": ["부작용"], "manufacturer": ["제조회사"], "lot_number": ["로트번호"]},
    }

    # -----------------------------
    # 벡터 스토어 관리
    # -----------------------------
   # care_chatbot_service.py에서 VectorStoreService 호출 직후 예시
    @classmethod
    def get_vector_store(cls) -> VectorStoreService:
        """벡터 스토어 인스턴스를 안전하게 가져오거나 생성"""
        if cls._vector_store is None:
            try:
                print("벡터 스토어 초기화 시작...")
                cls._vector_store = VectorStoreService()
                print("VectorStoreService 객체 생성:", cls._vector_store)
                
                # 벡터 DB 초기화
                store = cls._vector_store.initialize_vector_db()
                print("벡터 DB 초기화 완료:", store)
                
                # store가 제대로 설정되었는지 확인
                if store is None:
                    print("경고: 벡터 DB 초기화가 None을 반환했습니다.")
                    cls._vector_store.store = None
                else:
                    cls._vector_store.store = store
                    print(f"벡터 스토어 설정 완료. 문서 수: {cls._get_document_count(store)}")
                    
            except Exception as e:
                print(f"벡터 스토어 초기화 중 오류 발생: {e}")
                import traceback
                print(f"상세 오류 정보: {traceback.format_exc()}")
                # 초기화 실패 시 None으로 설정하여 다음에 다시 시도할 수 있도록 함
                cls._vector_store = None
                return None
        else:
            print("이미 초기화된 벡터 스토어 사용")
            
        return cls._vector_store

    @classmethod
    def _get_document_count(cls, store) -> int:
        """벡터 스토어의 문서 수를 안전하게 가져오기"""
        try:
            if hasattr(store, '_collection') and store._collection:
                return store._collection.count()
            elif hasattr(store, 'similarity_search'):
                # 간단한 테스트 검색으로 스토어가 작동하는지 확인
                test_results = store.similarity_search("test", k=1)
                return len(test_results) if test_results else 0
        except Exception as e:
            print(f"문서 수 확인 중 오류: {e}")
        return 0


   
    # def search_knowledge_base(query: str, k: int = 5) -> str:
    #     """벡터 스토어에서 관련 문서 검색"""
    #     try:
    #         # 입력 검증
    #         if not query or not query.strip():
    #             print("검색어가 비어있습니다.")
    #             return ""
            
    #         vector_store = CareChatbotService.get_vector_store()
    #         if not vector_store:
    #             print("벡터 스토어 서비스를 가져올 수 없습니다.")
    #             return ""
            
    #         # store 속성 존재 여부 확인
    #         if not hasattr(vector_store, 'store') or vector_store.store is None:
    #             print("벡터 스토어가 초기화되지 않았습니다.")
    #             return ""

    #         # similarity_search 실행 및 안전한 처리
    #         search_results = None
    #         try:
    #             search_results = vector_store.store.similarity_search(query, k=k)
    #         except Exception as search_error:
    #             print(f"검색 실행 중 오류 발생: {search_error}")
    #             return ""
            
    #         # 검색 결과 검증
    #         if not search_results:
    #             print("검색 결과가 없습니다.")
    #             return ""
            
    #         if not isinstance(search_results, list):
    #             print(f"예상치 못한 검색 결과 타입: {type(search_results)}")
    #             return ""

    #         knowledge_context = []
            
    #         for i, doc in enumerate(search_results):
    #             try:
    #                 # Document 객체 검증
    #                 if not doc:
    #                     print(f"인덱스 {i}의 문서가 None입니다.")
    #                     continue
                    
    #                 if not isinstance(doc, Document):
    #                     print(f"인덱스 {i}의 객체가 Document가 아닙니다: {type(doc)}")
    #                     continue

    #                 # page_content 안전하게 추출
    #                 content = ""
    #                 if hasattr(doc, 'page_content') and doc.page_content:
    #                     content = str(doc.page_content).strip()
                    
    #                 if not content:
    #                     print(f"인덱스 {i}의 문서 내용이 비어있습니다.")
    #                     continue

    #                 print(f'content {i+1}: {content[:100]}...')  # 처음 100자만 출력

    #                 # metadata 안전하게 추출
    #                 metadata = {}
    #                 if hasattr(doc, 'metadata') and isinstance(doc.metadata, dict):
    #                     metadata = doc.metadata

    #                 # source 정보 구성
    #                 source_info = ""
    #                 source_candidates = ['source_file', 'file_path', 'data_type']
                    
    #                 for candidate in source_candidates:
    #                     if metadata.get(candidate):
    #                         source_info = f"[출처: {metadata[candidate]}]"
    #                         break
                    
    #                 if not source_info:
    #                     source_info = "[출처: 알 수 없음]"

    #                 # 컨텍스트에 추가
    #                 formatted_content = f"참고자료 {i+1} {source_info}:\n{content}\n"
    #                 knowledge_context.append(formatted_content)

    #             except Exception as doc_error:
    #                 print(f"문서 {i} 처리 중 오류 발생: {doc_error}")
    #                 continue

    #         # 최종 결과 반환
    #         if not knowledge_context:
    #             print("처리 가능한 검색 결과가 없습니다.")
    #             return ""
            
    #         result = "\n".join(knowledge_context)
    #         print(f"총 {len(knowledge_context)}개의 참고자료를 찾았습니다.")
            
    #         return result

    #     except Exception as e:
    #         print(f"지식 베이스 검색 중 예상치 못한 오류 발생: {e}")
    #         import traceback
    #         print(f"상세 오류 정보: {traceback.format_exc()}")
    #         return ""
    @staticmethod
    def search_knowledge_base(query: str, k: int = 5, search_type: str = "hybrid") -> str:
        """
        지식 베이스에서 관련 문서 검색
        search_type: "vector", "keyword", "hybrid"
        """
        try:
            if not query or not query.strip():
                print("검색어가 비어있습니다.")
                return ""

            vector_store = CareChatbotService.get_vector_store()
            if not vector_store:
                print("벡터 스토어 서비스를 가져올 수 없습니다.")
                return ""

            if not hasattr(vector_store, "store") or vector_store.store is None:
                print("벡터 스토어가 초기화되지 않았습니다.")
                return ""

            # 검색 타입에 따라 다른 검색 방법 사용
            try:
                print(f"실행할 검색 타입: {search_type}")
                
                if search_type == "vector":
                    search_results = vector_store.store.similarity_search(query, k=k)
                    print(f"벡터 검색 완료")
                elif search_type == "keyword":
                    keyword_results = vector_store.keyword_search(query, k=k)
                    search_results = [doc for doc, _ in keyword_results]
                    print(f"키워드 검색 완료")
                    # 키워드 검색 점수 출력
                    for i, (doc, score) in enumerate(keyword_results[:5]):
                        print(f"키워드 점수 {i+1}: {score:.2f} - {doc.page_content[:100]}...")
                elif search_type == "hybrid":
                    search_results = vector_store.hybrid_search(query, k=k)
                    print(f"하이브리드 검색 완료")
                else:
                    print(f"지원하지 않는 검색 타입: {search_type}")
                    search_results = vector_store.store.similarity_search(query, k=k)
                    
                print(f"최종 검색 결과 수: {len(search_results) if search_results else 0}")
                
                # 검색된 문서들의 메타데이터 출력
                if search_results:
                    print("\n검색된 문서들:")
                    for i, doc in enumerate(search_results[:5]):  # 상위 5개만 출력
                        source = "알 수 없음"
                        if hasattr(doc, 'metadata') and doc.metadata:
                            for key in ["source_file", "file_path", "data_type"]:
                                if key in doc.metadata and doc.metadata[key]:
                                    source = doc.metadata[key]
                                    break
                        print(f"{i+1}. 출처: {source}")
                        print(f"   내용: {doc.page_content[:150]}...")
                        print()
                
            except Exception as search_error:
                print(f"검색 실행 중 오류 발생: {search_error}")
                import traceback
                print(f"상세 오류: {traceback.format_exc()}")
                # 실패 시 기본 벡터 검색으로 폴백
                try:
                    search_results = vector_store.store.similarity_search(query, k=k)
                    print("기본 벡터 검색으로 폴백 완료")
                except:
                    return ""

            if not search_results or not isinstance(search_results, list):
                print("검색 결과가 없습니다 또는 예상치 못한 타입입니다.")
                return ""

            knowledge_context = []

            for i, doc in enumerate(search_results):
                if not doc or not hasattr(doc, "page_content"):
                    continue

                content = str(doc.page_content).strip()
                if not content:
                    continue

                # metadata 안전 처리
                metadata_dict = {}
                if hasattr(doc, "metadata"):
                    if isinstance(doc.metadata, dict):
                        metadata_dict = doc.metadata
                    else:
                        try:
                            metadata_dict = json.loads(doc.metadata)
                        except:
                            metadata_dict = {}

                # 출처 추출
                source_info = "[출처: 알 수 없음]"
                for key in ["source_file", "file_path", "data_type"]:
                    if key in metadata_dict and metadata_dict[key]:
                        source_info = f"[출처: {metadata_dict[key]}]"
                        break

                formatted_content = f"참고자료 {i+1} {source_info}:\n{content}\n"
                knowledge_context.append(formatted_content)
                # 더 자세한 미리보기 제거 (위에서 이미 출력함)

            if not knowledge_context:
                print("처리 가능한 검색 결과가 없습니다.")
                return ""

            print(f"총 {len(knowledge_context)}개의 참고자료를 찾았습니다.")
            return "\n".join(knowledge_context)

        except Exception as e:
            print(f"지식 베이스 검색 중 예상치 못한 오류 발생: {e}")
            import traceback
            print(traceback.format_exc())
            return ""

    # -----------------------------
    # 반려동물 기록 관련
    # -----------------------------
    @staticmethod
    def get_pet_records(pet_id: int):
        return {
            'pet': PetService.get_pet(pet_id),
            'health': HealthCareService.get_health_records_by_pet(pet_id),
            'allergy': MedicalCareService.get_allergy_pet(pet_id),
            'disease': MedicalCareService.get_disease_pet(pet_id),
            'medication': MedicalCareService.get_medications_by_pet(pet_id),
            'surgery': MedicalCareService.get_surgery_pet(pet_id),
            'vaccination': MedicalCareService.get_vaccination_pet(pet_id),
        }

    @staticmethod
    def summarize_record_list(records, record_type: str, limit: int = 3) -> list:
        if not records:
            return []
        attr_map = CareChatbotService.ATTRIBUTE_MAP.get(record_type, {})
        summaries = []
        for r in records[:limit]:
            parts = []
            for attr in attr_map.keys():
                val = getattr(r, attr, None)
                if val:
                    parts.append(f"{attr}: {val}")
            summaries.append(" | ".join(parts))
        return summaries

    @staticmethod
    def summarize_pet_records(records: dict) -> str:
        pet = records.get("pet", {})
        return f"""
        반려동물: {pet.get('pet_name', '-') } ({pet.get('species_name', '-') } - {pet.get('breed_name', '-') })
        나이/성별: {pet.get('pet_age', '-') }살, {pet.get('pet_gender', '-') } / 중성화: {"O" if pet.get('is_neutered') else "X"}

        최근 건강 기록: {CareChatbotService.summarize_record_list(records.get('health', []), 'health')}
        알러지: {CareChatbotService.summarize_record_list(records.get('allergy', []), 'allergy')}
        질병: {CareChatbotService.summarize_record_list(records.get('disease', []), 'disease')}
        복용 중인 약: {CareChatbotService.summarize_record_list(records.get('medication', []), 'medication')}
        수술 내역: {CareChatbotService.summarize_record_list(records.get('surgery', []), 'surgery')}
        예방접종 내역: {CareChatbotService.summarize_record_list(records.get('vaccination', []), 'vaccination')}
        """

    @staticmethod
    def build_enhanced_prompt(user_input: str, records_summary: str, knowledge_context: str) -> str:
        return f"""
        너는 전문적인 반려동물 건강 상담 챗봇이야.
        아래 정보들을 참고해서 정확하고 도움이 되는 답변을 해줘.

        == 반려동물 기록 ==
        {records_summary}

        == 전문 지식 자료 ==
        {knowledge_context}

        == 사용자 질문 ==
        {user_input}
        """

    @staticmethod
    def chatbot_with_records(user_input: str, pet_id: int, user_id: int, 
                           use_vector_search: bool = True, search_type: str = "hybrid") -> str:
        """
        반려동물 기록과 지식 베이스를 활용한 챗봇 응답
        search_type: "vector", "keyword", "hybrid" 중 선택
        """
        with app.app_context():
            records = CareChatbotService.get_pet_records(pet_id)
            records_summary = CareChatbotService.summarize_pet_records(records)

            if use_vector_search:
                print(f"\n=== 검색 시작 ===")
                print(f"검색어: {user_input}")
                print(f"검색 타입: {search_type}")
                print(f"검색할 문서 수: 10")
                
                knowledge_context = CareChatbotService.search_knowledge_base(
                    user_input, k=10, search_type=search_type
                )
                
                print(f"\n=== 검색 결과 ===")
                if knowledge_context:
                    print(f"검색된 문서 내용 길이: {len(knowledge_context)} 글자")
                    print("검색된 내용 미리보기:")
                    print(knowledge_context[:500] + "..." if len(knowledge_context) > 500 else knowledge_context)
                else:
                    print("검색된 문서가 없습니다.")
                
                prompt = CareChatbotService.build_enhanced_prompt(user_input, records_summary, knowledge_context)
                
                print(f"\n=== 최종 프롬프트 ===")
                print("프롬프트 길이:", len(prompt), "글자")
                print("프롬프트 내용:")
                print(prompt)
                print("=" * 50)
                
            else:
                prompt = f"사용자 질문: {user_input}\n\n반려동물 기록:\n{records_summary}"

            prompt = CareChatbotService.pretty_format(prompt)
            return get_gpt_response(prompt)

    @staticmethod
    def pretty_format(text: str) -> str:
        lines = text.split("\n")
        return "\n".join("  " + line.strip() for line in lines if line.strip())

# -----------------------------
# 테스트용 실행 코드
# -----------------------------
if __name__ == "__main__":
    from flask import Flask
    from app.models import db

    # 1. Flask 앱 생성
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mypetsvoice.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        pet_id = 1
        user_id = 1
        user_input = "강아지가 브루셀라병에 대해 알려줘."

        response = CareChatbotService.chatbot_with_records(
            user_input=user_input,
            pet_id=pet_id,
            user_id=user_id,
            use_vector_search=True,
            search_type="hybrid"  # 하이브리드 검색 사용
        )

        print("\n=== 챗봇 응답 ===\n")
        print(response)
