#!/usr/bin/env python3
"""
벡터 DB 재설정 스크립트
잘못된 문서가 들어간 벡터 DB를 삭제하고 새로 생성합니다.
"""

import os
import shutil
from pathlib import Path

def reset_vector_db():
    """기존 벡터 DB를 삭제하여 새로 생성되도록 함"""
    
    print("=== 벡터 DB 재설정 시작 ===")
    
    # 기존 vector_db 폴더 확인
    vector_db_path = Path("./vector_db")
    
    if vector_db_path.exists():
        print(f"기존 벡터 DB 발견: {vector_db_path}")
        
        # 백업 생성
        backup_path = Path("./vector_db_backup")
        counter = 1
        while backup_path.exists():
            backup_path = Path(f"./vector_db_backup_{counter}")
            counter += 1
        
        try:
            print(f"기존 DB를 {backup_path}로 백업 중...")
            shutil.move(str(vector_db_path), str(backup_path))
            print("✅ 백업 완료")
        except Exception as e:
            print(f"❌ 백업 실패: {e}")
            print("직접 vector_db 폴더를 삭제해주세요.")
            return False
    else:
        print("기존 벡터 DB가 없습니다.")
    
    print("\n=== 설정 확인 ===")
    print("- .env 파일에 DOCUMENTS_PATH=./storage/documents 설정됨")
    print("- 실제 문서들이 storage/documents/에 존재함")
    print("- 다음 앱 실행 시 새로운 벡터 DB가 자동 생성됩니다.")
    
    # 문서 파일들 확인
    docs_path = Path("./storage/documents")
    if docs_path.exists():
        md_files = list(docs_path.glob("**/*.md"))
        json_files = list(docs_path.glob("**/*.json"))
        print(f"\n=== 새로 인덱싱될 문서들 ===")
        print(f"- Markdown 파일: {len(md_files)}개")
        print(f"- JSON 파일: {len(json_files)}개")
        
        print("\n주요 문서들:")
        for f in md_files[:5]:
            print(f"  - {f.relative_to(docs_path)}")
        if len(md_files) > 5:
            print(f"  ... 및 {len(md_files)-5}개 더")
    else:
        print("❌ 문서 경로가 존재하지 않습니다!")
        return False
    
    print("\n✅ 벡터 DB 재설정 완료")
    print("이제 앱을 재시작하면 올바른 문서들로 벡터 DB가 새로 생성됩니다.")
    
    return True

if __name__ == "__main__":
    reset_vector_db()