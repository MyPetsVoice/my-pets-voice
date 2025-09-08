"""
CSV 약품 데이터를 RAG 시스템용으로 처리하는 모듈
대용량 CSV 파일을 효율적으로 처리하여 벡터화 가능한 형태로 변환
"""

import pandas as pd
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Iterator, Optional
from dataclasses import dataclass
import ast

@dataclass
class MedicationDocument:
    """약품 정보 문서 구조"""
    product_name: str
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    keywords: List[str]

class CSVMedicationProcessor:
    """CSV 약품 데이터 처리 클래스"""
    
    def __init__(self, batch_size: int = 1000, max_content_length: int = 2000):
        self.batch_size = batch_size
        self.max_content_length = max_content_length
    
    def process_csv_files(self, csv_files: List[str]) -> Iterator[List[MedicationDocument]]:
        """여러 CSV 파일을 배치 처리"""
        for csv_file in csv_files:
            print(f"처리 중: {csv_file}")
            yield from self.process_single_csv(csv_file)
    
    def process_single_csv(self, csv_file: str) -> Iterator[List[MedicationDocument]]:
        """단일 CSV 파일을 배치별로 처리"""
        try:
            # CSV 파일을 청크 단위로 읽기 (메모리 효율성)
            chunk_reader = pd.read_csv(
                csv_file, 
                chunksize=self.batch_size,
                encoding='utf-8-sig',  # BOM 처리
                na_values=['', 'NaN', 'None'],
                keep_default_na=False
            )
            
            batch_num = 0
            for chunk in chunk_reader:
                batch_num += 1
                print(f"  배치 {batch_num} 처리 중... ({len(chunk)}행)")
                
                documents = []
                for _, row in chunk.iterrows():
                    try:
                        doc = self._convert_row_to_document(row, csv_file, batch_num)
                        if doc:
                            documents.append(doc)
                    except Exception as e:
                        print(f"    행 처리 실패: {e}")
                        continue
                
                if documents:
                    yield documents
                    
        except Exception as e:
            print(f"CSV 파일 처리 실패 {csv_file}: {e}")
    
    def _convert_row_to_document(self, row: pd.Series, source_file: str, batch_num: int) -> Optional[MedicationDocument]:
        """CSV 행을 MedicationDocument로 변환"""
        try:
            # 제품명 추출
            product_name = str(row.get('제품명', '')).strip()
            if not product_name or product_name == 'nan':
                return None
            
            # 기본정보 파싱 (JSON 형태의 문자열)
            basic_info = self._parse_basic_info(row.get('기본정보', '{}'))
            
            # 원료약품 파싱
            ingredients = self._parse_ingredients(row.get('원료약품 및 분량', '[]'))
            
            # 콘텐츠 생성
            content = self._build_structured_content(
                product_name, basic_info, ingredients, row
            )
            
            # 콘텐츠 길이 제한
            if len(content) > self.max_content_length:
                content = content[:self.max_content_length] + "..."
            
            # 메타데이터 구성
            metadata = self._build_metadata(basic_info, source_file, batch_num)
            
            # 키워드 추출
            keywords = self._extract_keywords(product_name, basic_info, row)
            
            # 청크 ID 생성
            chunk_id = f"med_{Path(source_file).stem}_{batch_num}_{product_name.replace(' ', '_')}"
            
            return MedicationDocument(
                product_name=product_name,
                content=content,
                metadata=metadata,
                chunk_id=chunk_id,
                keywords=keywords
            )
            
        except Exception as e:
            print(f"문서 변환 실패: {e}")
            return None
    
    def _parse_basic_info(self, basic_info_str: str) -> Dict[str, str]:
        """기본정보 JSON 문자열 파싱"""
        try:
            if pd.isna(basic_info_str) or not basic_info_str.strip():
                return {}
            
            # JSON 형태 문자열을 dict로 변환
            basic_info = ast.literal_eval(basic_info_str)
            if isinstance(basic_info, dict):
                return basic_info
            else:
                return {}
        except:
            return {}
    
    def _parse_ingredients(self, ingredients_str: str) -> List[Dict[str, str]]:
        """원료약품 리스트 문자열 파싱"""
        try:
            if pd.isna(ingredients_str) or not ingredients_str.strip():
                return []
            
            # 리스트 형태 문자열을 list로 변환
            ingredients_list = ast.literal_eval(ingredients_str)
            
            parsed_ingredients = []
            for ingredient in ingredients_list:
                if isinstance(ingredient, list) and len(ingredient) >= 4:
                    parsed_ingredients.append({
                        'name': ingredient[1] if len(ingredient) > 1 else '',
                        'amount': ingredient[2] if len(ingredient) > 2 else '',
                        'unit': ingredient[3] if len(ingredient) > 3 else ''
                    })
            
            return parsed_ingredients
        except:
            return []
    
    def _build_structured_content(self, product_name: str, basic_info: Dict, 
                                 ingredients: List[Dict], row: pd.Series) -> str:
        """구조화된 콘텐츠 생성"""
        content_parts = []
        
        # 제품 기본 정보
        content_parts.append(f"제품명: {product_name}")
        
        if basic_info.get('제품 영문명'):
            content_parts.append(f"영문명: {basic_info['제품 영문명']}")
        
        if basic_info.get('업체명'):
            content_parts.append(f"제조업체: {basic_info['업체명']}")
        
        if basic_info.get('허가일'):
            content_parts.append(f"허가일: {basic_info['허가일']}")
        
        if basic_info.get('성상'):
            content_parts.append(f"성상: {basic_info['성상']}")
        
        # 원료약품 정보
        if ingredients:
            content_parts.append("\\n주요 원료약품:")
            for ingredient in ingredients[:10]:  # 상위 10개만
                name = ingredient.get('name', '').strip()
                amount = ingredient.get('amount', '').strip()
                unit = ingredient.get('unit', '').strip()
                if name:
                    ingredient_info = f"• {name}"
                    if amount and amount != '-':
                        ingredient_info += f": {amount}"
                        if unit and unit != '-':
                            ingredient_info += f" {unit}"
                    content_parts.append(ingredient_info)
        
        # 효능효과
        efficacy = str(row.get('효능효과', '')).strip()
        if efficacy and efficacy != 'nan':
            content_parts.append(f"\\n효능효과: {efficacy}")
        
        # 용법용량
        dosage = str(row.get('용법용량', '')).strip()
        if dosage and dosage != 'nan':
            # 용법용량 정리 (너무 길면 축약)
            if len(dosage) > 500:
                dosage = dosage[:500] + "..."
            content_parts.append(f"\\n용법용량:\\n{dosage}")
        
        # 주의사항
        warnings = str(row.get('주의사항', '')).strip()
        if warnings and warnings != 'nan':
            # 주의사항 정리 (너무 길면 축약)
            if len(warnings) > 300:
                warnings = warnings[:300] + "..."
            content_parts.append(f"\\n주의사항: {warnings}")
        
        return "\\n".join(content_parts)
    
    def _build_metadata(self, basic_info: Dict, source_file: str, batch_num: int) -> Dict[str, Any]:
        """메타데이터 구성"""
        metadata = {
            'source_file': Path(source_file).name,
            'source_type': 'csv_medication',
            'batch_number': batch_num,
            'company': basic_info.get('업체명', ''),
            'approval_date': basic_info.get('허가일', ''),
            'product_type': basic_info.get('품목정보', ''),
            'approval_status': basic_info.get('업상태', ''),
            'manufacturing_type': basic_info.get('제조/수입구분', ''),
        }
        
        # 빈 값 제거
        metadata = {k: v for k, v in metadata.items() if v and v != 'nan'}
        
        return metadata
    
    def _extract_keywords(self, product_name: str, basic_info: Dict, row: pd.Series) -> List[str]:
        """키워드 추출"""
        keywords = []
        
        # 제품명에서 키워드 추출
        keywords.append(product_name)
        
        # 영문명
        if basic_info.get('제품 영문명'):
            keywords.append(basic_info['제품 영문명'])
        
        # 업체명
        if basic_info.get('업체명'):
            keywords.append(basic_info['업체명'])
        
        # 효능효과에서 키워드 추출
        efficacy = str(row.get('효능효과', '')).strip()
        if efficacy and efficacy != 'nan':
            # 쉼표로 구분된 효능들 추출
            efficacy_keywords = [kw.strip() for kw in efficacy.split(',') if kw.strip()]
            keywords.extend(efficacy_keywords[:5])  # 상위 5개만
        
        # 중복 제거하고 정리
        unique_keywords = []
        for kw in keywords:
            if kw and kw not in unique_keywords and len(kw.strip()) > 1:
                unique_keywords.append(kw.strip())
        
        return unique_keywords[:10]  # 최대 10개

class MedicationRAGProcessor:
    """약품 데이터를 RAG용으로 최종 처리"""
    
    @staticmethod
    def prepare_for_vectorization(documents: List[MedicationDocument]) -> List[Dict[str, Any]]:
        """벡터화를 위한 데이터 준비"""
        vector_docs = []
        
        for doc in documents:
            # 컨텍스트가 포함된 텍스트 구성
            context_text = MedicationRAGProcessor._build_context_text(doc)
            
            vector_doc = {
                'id': doc.chunk_id,
                'text': context_text,
                'metadata': {
                    **doc.metadata,
                    'product_name': doc.product_name,
                    'keywords': doc.keywords,
                    'content_type': 'medication_info'
                }
            }
            vector_docs.append(vector_doc)
        
        return vector_docs
    
    @staticmethod
    def _build_context_text(doc: MedicationDocument) -> str:
        """컨텍스트가 포함된 텍스트 구성"""
        context_parts = []
        
        # 기본 컨텍스트
        context_parts.append(f"문서유형: 동물용의약품")
        context_parts.append(f"제품명: {doc.product_name}")
        
        # 메타데이터에서 중요 정보 추출
        if doc.metadata.get('company'):
            context_parts.append(f"제조업체: {doc.metadata['company']}")
        
        if doc.metadata.get('product_type'):
            context_parts.append(f"품목정보: {doc.metadata['product_type']}")
        
        # 키워드
        if doc.keywords:
            context_parts.append(f"키워드: {', '.join(doc.keywords[:5])}")
        
        # 컨텍스트와 내용 결합
        context = ' | '.join(context_parts)
        return f"{context}\\n\\n{doc.content}"
    
    @staticmethod
    def save_processed_data(vector_docs: List[Dict], output_path: str):
        """처리된 데이터를 JSON으로 저장"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(vector_docs, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {len(vector_docs)}개 문서가 {output_path}에 저장되었습니다.")

# 사용 예제 및 배치 처리
class BatchMedicationProcessor:
    """대용량 CSV 파일의 배치 처리를 위한 클래스"""
    
    def __init__(self, output_dir: str = "processed_medications"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def process_all_csv_files(self, csv_files: List[str]):
        """모든 CSV 파일을 배치 처리"""
        processor = CSVMedicationProcessor(batch_size=500)  # 메모리 절약
        rag_processor = MedicationRAGProcessor()
        
        total_processed = 0
        
        for csv_file in csv_files:
            file_processed = 0
            output_parts = []
            
            # 파일별 배치 처리
            for batch_documents in processor.process_single_csv(csv_file):
                # RAG용 데이터 준비
                vector_docs = rag_processor.prepare_for_vectorization(batch_documents)
                output_parts.extend(vector_docs)
                
                file_processed += len(batch_documents)
                
                # 중간 저장 (메모리 관리)
                if len(output_parts) >= 2000:  # 2000개씩 저장
                    self._save_batch(output_parts, csv_file, len(output_parts))
                    output_parts = []
            
            # 남은 데이터 저장
            if output_parts:
                self._save_batch(output_parts, csv_file, file_processed)
            
            total_processed += file_processed
            print(f"✅ {csv_file}: {file_processed}개 처리 완료")
        
        print(f"🎉 전체 처리 완료: {total_processed}개 약품 정보")
    
    def _save_batch(self, data: List[Dict], source_file: str, batch_id: int):
        """배치 데이터 저장"""
        filename = f"{Path(source_file).stem}_batch_{batch_id}.json"
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

# 실행 예제
if __name__ == "__main__":
    # CSV 파일 목록
    csv_files = [
        "medications/medicine_data_1p~500p.csv",
        "medications/medicine_data_fixed(401-730).csv", 
        "medications/medicine_data_fixed731.csv"
    ]
    
    # 배치 처리 실행
    batch_processor = BatchMedicationProcessor("processed_medications")
    batch_processor.process_all_csv_files(csv_files)
    
    print("\\n📊 처리 통계:")
    print(f"- 원본 파일: {len(csv_files)}개")
    print(f"- 예상 처리량: ~40만 개 약품 정보")
    print(f"- 출력 형식: 구조화된 JSON (RAG 최적화)")
    print(f"- 저장 위치: processed_medications/ 폴더")