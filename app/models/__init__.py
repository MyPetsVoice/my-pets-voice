from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    # PostgreSQL 데이터베이스 자동 생성
    create_database_if_not_exists(app)
    
    db.init_app(app)

    # 모든 모델 import (테이블 생성을 위함)
    from app.models.base import BaseModel
    from app.models.user import User
    from app.models.chat_history import ChatHistory
    from app.models.diary import Diary, DiaryPhoto
    from app.models.dailycare.healthCare.healthCare import HealthCare
    from app.models.dailycare.healthCare.healthcareMedication import HealthCareMedication
    from app.models.dailycare.medicalCare.allergy import Allergy
    from app.models.dailycare.medicalCare.disease import Disease
    from app.models.dailycare.medicalCare.medication import Medication
    from app.models.dailycare.medicalCare.surgery import Surgery
    from app.models.dailycare.medicalCare.vaccination import Vaccination
    from app.models.pet import Pet, PetSpecies, PetBreed
    from app.models.pet_persona import PetPersona, PersonaTrait, PersonalityTrait, SpeechStyle

    with app.app_context():
        db.create_all()
        
        # 기존 init_db_with_check.py의 함수 import하여 사용
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(app.root_path), 'app/models'))
        
        try:
            from init_db_with_check import check_and_insert_initial_data
            check_and_insert_initial_data()
        except ImportError:
            print("초기 데이터 삽입 함수를 찾을 수 없습니다. 수동으로 init_db_with_check.py를 실행해주세요.")

def create_database_if_not_exists(app):
    """PostgreSQL 데이터베이스가 존재하지 않으면 생성"""
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    from urllib.parse import urlparse
    
    database_url = app.config.get('SQLALCHEMY_DATABASE_URI')
    if not database_url or not database_url.startswith('postgresql'):
        return  # PostgreSQL이 아니면 스킵
    
    try:
        # URL 파싱
        parsed = urlparse(database_url)
        db_name = parsed.path[1:]  # '/' 제거
        
        # postgres 데이터베이스에 연결
        postgres_url = database_url.replace(f'/{db_name}', '/postgres')
        parsed_postgres = urlparse(postgres_url)
        
        conn = psycopg2.connect(
            host=parsed_postgres.hostname,
            port=parsed_postgres.port or 5432,
            user=parsed_postgres.username,
            password=parsed_postgres.password,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # 데이터베이스 존재 확인
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"데이터베이스 '{db_name}'가 생성되었습니다.")
        else:
            print(f"데이터베이스 '{db_name}'가 이미 존재합니다.")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"데이터베이스 생성 중 오류: {e}")
        # 오류가 발생해도 앱 실행은 계속

# 모델들을 import하여 다른 모듈에서 사용할 수 있도록 함
from app.models.base import BaseModel
from app.models.user import User
from app.models.dailycare.healthCare.healthCare import HealthCare
from app.models.dailycare.healthCare.healthcareMedication import HealthCareMedication
from app.models.dailycare.medicalCare.allergy import Allergy
from app.models.dailycare.medicalCare.disease import Disease
from app.models.dailycare.medicalCare.medication import Medication
from app.models.dailycare.medicalCare.surgery import Surgery
from app.models.dailycare.medicalCare.vaccination import Vaccination
from app.models.dailycare.healthCare.todo import TodoList
from app.models.pet import Pet, PetSpecies, PetBreed
from app.models.pet_persona import PetPersona, PersonaTrait, PersonalityTrait, SpeechStyle
from app.models.chat_history import ChatHistory
    
    


__all__ = ['db', 'init_db', 'BaseModel', 'User', 'Pet', 'PetPersona', 'PersonaTrait', 'PetSpecies', 'PetBreed', 'PersonalityTrait', 'SpeechStyle', 'ChatHistory','HealthCare', 'HealthCareMedication','Allergy','Disease','Medication','Surgery','Vaccination','TodoList', 'Diary', 'DiaryPhoto']

