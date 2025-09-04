#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV to RAG Document Converter for Pet Medicine Data
의약품 CSV 데이터를 RAG용 문서로 변환하는 스크립트
"""

import pandas as pd
import json
import ast
import os
from datetime import datetime
from typing import List, Dict, Any

class MedicineRAGConverter:
    """의약품 CSV 데이터를 RAG용 문서로 변환하는 클래스"""
    
    def __init__(self, csv_files: List[str]):
        """
        Args:
            csv_files: 변환할 CSV 파일 경로 리스트
        """
        self.csv_files = csv_files
        self.products = []
        self.ingredients = []
        
    def load_csv_data(self):
        """모든 CSV 파일을 로드하여 데이터프레임으로 통합"""
        all_data = []
        
        for csv_file in self.csv_files:
            try:
                df = pd.read_csv(csv_file, encoding='utf-8')
                print(f"로드됨: {csv_file} - {len(df)} 제품")
                all_data.append(df)
            except Exception as e:
                print(f"파일 로드 실패 {csv_file}: {e}")
                
        if all_data:
            self.df = pd.concat(all_data, ignore_index=True)
            print(f"전체 데이터: {len(self.df)} 제품")
        else:
            raise Exception("로드된 데이터가 없습니다.")
    
    def parse_json_field(self, json_str: str) -> Dict[str, Any]:
        """JSON 형태의 문자열을 파싱"""
        if pd.isna(json_str) or json_str == '없음':
            return {}
        try:
            # 문자열에서 딕셔너리로 변환
            return ast.literal_eval(json_str)
        except:
            return {}
    
    def parse_ingredients_field(self, ingredients_str: str) -> List[List[str]]:
        """성분 정보 리스트를 파싱"""
        if pd.isna(ingredients_str) or ingredients_str == '없음':
            return []
        try:
            return ast.literal_eval(ingredients_str)
        except:
            return []
    
    def format_ingredients(self, ingredients: List[List[str]]) -> str:
        """성분 리스트를 자연어 형태로 변환"""
        if not ingredients:
            return "성분 정보 없음"
        
        formatted = []
        for ingredient in ingredients:
            if len(ingredient) >= 4:
                name = ingredient[1] if len(ingredient) > 1 else "이름 없음"
                amount = ingredient[2] if len(ingredient) > 2 else ""
                unit = ingredient[3] if len(ingredient) > 3 else ""
                
                if amount and unit:
                    formatted.append(f"- {name}: {amount} {unit}")
                else:
                    formatted.append(f"- {name}")
        
        return "\n".join(formatted) if formatted else "성분 정보 없음"
    
    def convert_to_product_document(self, row) -> str:
        """제품 정보를 RAG용 문서로 변환"""
        basic_info = self.parse_json_field(row['기본정보'])
        ingredients = self.parse_ingredients_field(row['원료약품 및 분량'])
        
        # 기본 정보 추출
        product_name = basic_info.get('제품명', '제품명 없음')
        english_name = basic_info.get('제품 영문명', '')
        company = basic_info.get('업체명', '')
        approval_date = basic_info.get('허가일', '')
        form_type = basic_info.get('성상', '')
        storage = basic_info.get('저장방법', '')
        package_info = basic_info.get('포장단위', '')
        
        # 문서 생성
        document = f"""제품명: {product_name}
{f"영문명: {english_name}" if english_name else ""}
제조업체: {company}
허가일자: {approval_date}
제형: {form_type}

주요 성분 및 함량:
{self.format_ingredients(ingredients)}

저장방법: {storage}
포장단위: {package_info}

효능효과: {row.get('효능효과', '정보 없음')}
용법용량: {row.get('용법용량', '정보 없음')}
주의사항: {row.get('주의사항', '정보 없음')}

--- 검색 키워드 ---
동물용의약품, 반려동물, 의약품, {product_name}, {company}
"""
        
        return document.strip()
    
    def extract_ingredient_documents(self, row) -> List[str]:
        """성분별 검색용 문서 생성"""
        basic_info = self.parse_json_field(row['기본정보'])
        ingredients = self.parse_ingredients_field(row['원료약품 및 분량'])
        
        product_name = basic_info.get('제품명', '제품명 없음')
        company = basic_info.get('업체명', '')
        
        ingredient_docs = []
        for ingredient in ingredients:
            if len(ingredient) >= 2:
                ingredient_name = ingredient[1]
                amount = ingredient[2] if len(ingredient) > 2 else ""
                unit = ingredient[3] if len(ingredient) > 3 else ""
                
                doc = f"""성분명: {ingredient_name}
함유제품: {product_name}
제조업체: {company}
{f"함량: {amount} {unit}" if amount and unit else ""}

이 성분이 포함된 동물용의약품 정보입니다.
--- 검색 키워드 ---
{ingredient_name}, 성분, 원료, 동물용의약품, {product_name}
"""
                ingredient_docs.append(doc.strip())
        
        return ingredient_docs
    
    def convert_all_data(self):
        """모든 데이터를 RAG 문서로 변환"""
        print("데이터 변환 시작...")
        
        for idx, row in self.df.iterrows():
            # 제품 문서 생성
            product_doc = self.convert_to_product_document(row)
            self.products.append({
                'id': f"product_{idx}",
                'type': 'product',
                'content': product_doc
            })
            
            # 성분 문서 생성
            ingredient_docs = self.extract_ingredient_documents(row)
            for i, ingredient_doc in enumerate(ingredient_docs):
                self.ingredients.append({
                    'id': f"ingredient_{idx}_{i}",
                    'type': 'ingredient',
                    'content': ingredient_doc
                })
        
        print(f"변환 완료: 제품 문서 {len(self.products)}개, 성분 문서 {len(self.ingredients)}개")
    
    def save_documents(self, output_dir: str = "rag_documents"):
        """변환된 문서들을 파일로 저장"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 제품 문서 저장
        products_file = os.path.join(output_dir, "product_documents.txt")
        with open(products_file, 'w', encoding='utf-8') as f:
            for doc in self.products:
                f.write(f"=== {doc['id']} ===\n")
                f.write(doc['content'])
                f.write("\n\n" + "="*50 + "\n\n")
        
        # 성분 문서 저장
        ingredients_file = os.path.join(output_dir, "ingredient_documents.txt")
        with open(ingredients_file, 'w', encoding='utf-8') as f:
            for doc in self.ingredients:
                f.write(f"=== {doc['id']} ===\n")
                f.write(doc['content'])
                f.write("\n\n" + "="*50 + "\n\n")
        
        # JSON 형태로도 저장 (메타데이터 포함)
        all_docs = self.products + self.ingredients
        json_file = os.path.join(output_dir, "all_documents.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(all_docs, f, ensure_ascii=False, indent=2)
        
        print(f"문서 저장 완료:")
        print(f"- 제품 문서: {products_file}")
        print(f"- 성분 문서: {ingredients_file}")
        print(f"- JSON 형태: {json_file}")

def main():
    """메인 실행 함수"""
    # CSV 파일 목록
    csv_files = [
        "medicine_data_1~500.csv",
        "medicine_data_501-730.csv", 
        "medicine_data731.csv",
        "medicine_data755.csv"
    ]
    
    # 변환기 초기화
    converter = MedicineRAGConverter(csv_files)
    
    try:
        # 데이터 로드
        converter.load_csv_data()
        
        # 문서 변환
        converter.convert_all_data()
        
        # 파일 저장
        converter.save_documents()
        
        print("\n=== 변환 완료 ===")
        print("RAG 시스템에서 사용할 수 있는 문서가 준비되었습니다.")
        
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()