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
from config import Config
import os


# LangSmith 설정
if Config.LANGCHAIN_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true" if Config.LANGSMITH_TRACING else "false"
    os.environ["LANGCHAIN_API_KEY"] = Config.LANGCHAIN_API_KEY
    if Config.LANGSMITH_PROJECT:
        os.environ["LANGCHAIN_PROJECT"] = Config.LANGSMITH_PROJECT
    os.environ["LANGCHAIN_ENDPOINT"] = Config.LANGSMITH_ENDPOINT


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
                
                # 멀티 콜렉션 벡터 DB 초기화
                stores = cls._vector_store.initialize_vector_db()
                print("멀티 콜렉션 벡터 DB 초기화 완료:", stores)
                
                # stores 확인
                if not stores or not any(stores.values()):
                    print("경고: 모든 콜렉션 초기화가 실패했습니다.")
                else:
                    for collection_type, store in stores.items():
                        if store:
                            count = cls._get_document_count(store)
                            print(f"{collection_type} 콜렉션 설정 완료. 문서 수: {count}")
                        else:
                            print(f"{collection_type} 콜렉션 초기화 실패")
                    
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

    @staticmethod 
    def _create_enhanced_query(query: str, pet_records: dict = None) -> str:
        """
        반려동물 정보를 포함한 향상된 검색 쿼리 생성
        """
        if not pet_records:
            return query
            
        pet_info = pet_records.get("pet", {})
        
        # 반려동물 기본 정보 추출
        pet_context_parts = []
        
        # 동물 종류와 품종
        if pet_info.get('species_name'):
            pet_context_parts.append(pet_info['species_name'])
        if pet_info.get('breed_name'):
            pet_context_parts.append(pet_info['breed_name'])
            
        # 나이와 성별
        if pet_info.get('pet_age'):
            pet_context_parts.append(f"{pet_info['pet_age']}살")
        if pet_info.get('pet_gender'):
            pet_context_parts.append(pet_info['pet_gender'])
            
        # 중성화 여부
        if pet_info.get('is_neutered') is not None:
            pet_context_parts.append("중성화됨" if pet_info['is_neutered'] else "중성화안됨")
            
        # 최근 건강 정보 추가
        health_records = pet_records.get("health", [])
        if health_records:
            latest_health = health_records[0] # 가장 최근 기록
            if hasattr(latest_health, 'weight_kg') and latest_health.weight_kg:
                pet_context_parts.append(f"{latest_health.weight_kg}kg")
        
        # 알러지 정보
        allergies = pet_records.get("allergy", [])
        if allergies:
            allergy_names = []
            for allergy in allergies[:2]:  # 최대 2개까지
                if hasattr(allergy, 'allergen') and allergy.allergen:
                    allergy_names.append(allergy.allergen)
            if allergy_names:
                pet_context_parts.append(f"알러지: {', '.join(allergy_names)}")
        
        # 질병 정보  
        diseases = pet_records.get("disease", [])
        if diseases:
            disease_names = []
            for disease in diseases[:2]:  # 최대 2개까지
                if hasattr(disease, 'disease_name') and disease.disease_name:
                    disease_names.append(disease.disease_name)
            if disease_names:
                pet_context_parts.append(f"질병력: {', '.join(disease_names)}")
        
        # 복용 중인 약물
        medications = pet_records.get("medication", [])
        if medications:
            med_names = []
            for med in medications[:2]:  # 최대 2개까지
                if hasattr(med, 'medication_name') and med.medication_name:
                    med_names.append(med.medication_name)
            if med_names:
                pet_context_parts.append(f"복용약물: {', '.join(med_names)}")
        
        # 향상된 쿼리 생성
        if pet_context_parts:
            pet_context = " ".join(pet_context_parts)
            enhanced_query = f"{query} {pet_context}"
        else:
            enhanced_query = query
            
        return enhanced_query

    @staticmethod
    def _create_metadata_filter(pet_records: dict = None, query: str = "") -> dict:
        """
        반려동물 정보와 질문 내용 기반 메타데이터 필터 생성 (더 엄격한 필터링)
        """
        if not pet_records:
            return {}
        
        pet_info = pet_records.get("pet", {})
        filters = []
        
        # 1. 동물 종류별 엄격한 필터링
        species_filter = None
        if pet_info.get('species_name'):
            species = pet_info['species_name']
            if '강아지' in species or '개' in species or 'dog' in species.lower():
                # 강아지면 고양이 관련 문서는 완전 제외
                species_filter = {
                    "$and": [
                        # 포함할 조건
                        {
                            "$or": [
                                {"categories": {"$in": ["반려견건강", "강아지", "예방접종", "종합건강관리"]}},
                                {"keywords": {"$in": ["강아지", "개", "dog", "반려견", "견"]}},
                                {"data_type": {"$ne": "medication"}},  # 의약품이 아니거나
                                {
                                    "$and": [
                                        {"data_type": "medication"},
                                        {
                                            "$or": [
                                                {"text": {"$contains": "강아지"}},
                                                {"text": {"$contains": "개"}},
                                                {"text": {"$contains": "dog"}},
                                                {"text": {"$contains": "반려견"}}
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        # 제외할 조건 (고양이 관련)
                        {
                            "$not": {
                                "$or": [
                                    {"categories": {"$in": ["반려묘건강", "고양이"]}},
                                    {"keywords": {"$in": ["고양이", "냥이", "cat", "반려묘"]}},
                                    {"text": {"$contains": "고양이"}},
                                    {"text": {"$contains": "cat"}}
                                ]
                            }
                        }
                    ]
                }
            elif '고양이' in species or '냥이' in species or 'cat' in species.lower():
                # 고양이면 강아지 관련 문서는 완전 제외
                species_filter = {
                    "$and": [
                        # 포함할 조건
                        {
                            "$or": [
                                {"categories": {"$in": ["반려묘건강", "고양이", "예방접종", "종합건강관리"]}},
                                {"keywords": {"$in": ["고양이", "냥이", "cat", "반려묘"]}},
                                {"data_type": {"$ne": "medication"}},  # 의약품이 아니거나
                                {
                                    "$and": [
                                        {"data_type": "medication"},
                                        {
                                            "$or": [
                                                {"text": {"$contains": "고양이"}},
                                                {"text": {"$contains": "cat"}},
                                                {"text": {"$contains": "냥이"}},
                                                {"text": {"$contains": "반려묘"}}
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        # 제외할 조건 (강아지 관련)
                        {
                            "$not": {
                                "$or": [
                                    {"categories": {"$in": ["반려견건강", "강아지"]}},
                                    {"keywords": {"$in": ["강아지", "개", "dog", "반려견"]}},
                                    {"text": {"$contains": "강아지"}},
                                    {"text": {"$contains": "dog"}}
                                ]
                            }
                        }
                    ]
                }
        
        if species_filter:
            filters.append(species_filter)
        
        # 2. 질문 내용에 따른 추가 필터링
        if query:
            query_lower = query.lower()
            
            # 예방접종 관련 질문이면 의약품 데이터 제한
            if any(word in query_lower for word in ['예방접종', '백신', '접종', 'vaccine']):
                filters.append({
                    "$or": [
                        {"data_type": {"$ne": "medication"}},  # 의약품이 아니거나
                        {
                            "$and": [
                                {"data_type": "medication"},
                                {
                                    "$or": [
                                        {"text": {"$contains": "백신"}},
                                        {"text": {"$contains": "vaccine"}},
                                        {"text": {"$contains": "예방접종"}}
                                    ]
                                }
                            ]
                        }
                    ]
                })
            
            # 건강관리, 사료, 운동 관련이면 의약품 우선순위 낮춤
            elif any(word in query_lower for word in ['건강관리', '사료', '운동', '산책', '관리', '키우기']):
                filters.append({
                    "$or": [
                        {"data_type": {"$ne": "medication"}},  # 의약품이 아닌 문서 우선
                        {"categories": {"$in": ["종합건강관리", "사료관리", "기본관리"]}}
                    ]
                })
        
        # 3. 의약품 데이터 비중 줄이기 (전체적으로)
        # 질병/약물 관련 질문이 아니면 의약품 데이터 제한
        disease_related = any(word in query.lower() for word in ['약', '치료', '병', '질병', '아파', 'medication', 'treatment'])
        
        if not disease_related:
            # 질병 관련이 아니면 일반 가이드 문서 우선
            filters.append({
                "$or": [
                    {"data_type": {"$ne": "medication"}},
                    {
                        "$and": [
                            {"data_type": "medication"},
                            {"item_index": {"$lt": 50}}  # 의약품 중에서도 앞쪽 50개만
                        ]
                    }
                ]
            })
        
        # 최종 필터 조합 (AND 조건: 모든 조건을 만족해야 함)
        if len(filters) == 1:
            return filters[0]
        elif len(filters) > 1:
            return {"$and": filters}
        
        return {}

    @staticmethod
    def _debug_vector_metadata(vector_store):
        """벡터DB에 저장된 메타데이터 샘플 확인 (하위 호환성)"""
        print("_debug_vector_metadata는 멀티 콜렉션에서 사용되지 않습니다.")

    @staticmethod
    def _test_metadata_filter(vector_store, metadata_filter):
        """메타데이터 필터 테스트 (멀티 콜렉션에서는 사용 안 함)"""
        print("메타데이터 필터는 멀티 콜렉션에서 사용되지 않습니다.")

    @staticmethod
    def _debug_multi_collection_metadata(vector_store, collections_to_search):
        """멀티 콜렉션 메타데이터 디버깅"""
        try:
            print("\n=== 멀티 콜렉션 메타데이터 샘플 확인 ===")
            
            for collection_type in collections_to_search:
                if collection_type in vector_store.stores and vector_store.stores[collection_type]:
                    print(f"\n--- {collection_type} 콜렉션 ---")
                    store = vector_store.stores[collection_type]
                    sample_docs = store.similarity_search("강아지", k=3)
                    
                    for i, doc in enumerate(sample_docs):
                        print(f"  {i+1}. {doc.page_content[:80]}...")
                        print(f"     collection_type: {doc.metadata.get('collection_type', 'None')}")
                        print(f"     data_type: {doc.metadata.get('data_type', 'None')}")
                else:
                    print(f"{collection_type} 콜렉션이 초기화되지 않음")
                    
            print("=== 멀티 콜렉션 샘플 확인 완료 ===\n")
            
        except Exception as e:
            print(f"멀티 콜렉션 디버깅 중 오류: {e}")

    @staticmethod
    def search_knowledge_base(query: str, pet_records: dict = None, k: int = 5, search_type: str = "hybrid") -> str:
        """
        지식 베이스에서 관련 문서 검색
        search_type: "vector", "keyword", "hybrid"
        """
        try:
            if not query or not query.strip():
                print("검색어가 비어있습니다.")
                return ""

            # 반려동물 정보를 포함한 향상된 쿼리 생성
            enhanced_query = CareChatbotService._create_enhanced_query(query, pet_records)
            print(f"원본 쿼리: {query}")
            print(f"향상된 쿼리: {enhanced_query}")
            
            # 메타데이터 필터 생성
            metadata_filter = CareChatbotService._create_metadata_filter(pet_records, query)
            if metadata_filter:
                print(f"메타데이터 필터: {metadata_filter}")
            else:
                print("메타데이터 필터: 없음")

            vector_store = CareChatbotService.get_vector_store()
            if not vector_store:
                print("벡터 스토어 서비스를 가져올 수 없습니다.")
                return ""

            if not hasattr(vector_store, "stores") or not any(vector_store.stores.values()):
                print("멀티 콜렉션 벡터 스토어가 초기화되지 않았습니다.")
                return ""
            
            # 질문 유형에 따른 콜렉션 선택
            collections_to_search = vector_store.get_collection_by_query_type(query, pet_records)
            print(f"검색할 콜렉션: {collections_to_search}")
            
            # 벡터DB 메타데이터 샘플 확인
            CareChatbotService._debug_multi_collection_metadata(vector_store, collections_to_search)

            # 멀티 콜렉션에서 검색
            try:
                print(f"실행할 검색 타입: {search_type}")
                
                # 멀티 콜렉션 검색 (현재는 벡터 검색만 지원)
                if search_type in ["vector", "hybrid"]:
                    search_results = vector_store.search_multi_collections(
                        enhanced_query, 
                        collections_to_search, 
                        k=k
                    )
                    print(f"멀티 콜렉션 벡터 검색 완료")
                    
                elif search_type == "keyword":
                    # 키워드 검색은 첫 번째 콜렉션에서만
                    if collections_to_search and vector_store.stores.get(collections_to_search[0]):
                        first_collection = collections_to_search[0]
                        keyword_results = vector_store.keyword_search(enhanced_query, k=k, collection_type=first_collection)
                        search_results = [doc for doc, _ in keyword_results]
                        print(f"{first_collection}에서 키워드 검색 완료")
                        # 키워드 검색 점수 출력
                        for i, (doc, score) in enumerate(keyword_results[:5]):
                            print(f"키워드 점수 {i+1}: {score:.2f} - {doc.page_content[:100]}...")
                    else:
                        search_results = []
                        print("키워드 검색할 콜렉션이 없습니다.")
                        
                else:
                    print(f"지원하지 않는 검색 타입: {search_type}")
                    search_results = vector_store.search_multi_collections(
                        enhanced_query, 
                        collections_to_search, 
                        k=k
                    )
                    
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
                    search_results = vector_store.search_multi_collections(
                        query, 
                        collections_to_search, 
                        k=k
                    )
                    print("멀티 콜렉션 벡터 검색으로 폴백 완료")
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
                    user_input, pet_records=records, k=10, search_type=search_type
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
