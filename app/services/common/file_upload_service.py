import os
from datetime import datetime
from werkzeug.utils import secure_filename
import logging
from config import Config

logger = logging.getLogger(__name__)

class FileUploadService:
    # 파일 업로드 설정
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # 최대 파일 크기 (16MB)
    MAX_FILE_SIZE = 16 * 1024 * 1024

    def __init__(self):
        # 환경변수로 저장 경로 설정
        self.storage_path = Config.STORAGE_PATH

    # 허용 파일 확장자 확인
    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS


    # 파일 유효성 검사, 크기 제한


    # 파일 저장
    def save_file(self, file, subfolder, filename=None):
        save_folder = os.path.join(self.storage_path, subfolder)
        os.makedirs(save_folder, exist_ok=True)

        if not filename:
            safe_filename = secure_filename(file.filename)
            # secure_filename이 빈 문자열을 반환하는 경우 기본 확장자 사용
            if not safe_filename:
                file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
                safe_filename = f'upload.{file_ext}'
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + safe_filename

        file_path = os.path.join(save_folder, filename)
        file.save(file_path)

        file_url = f'/static/uploads/{subfolder}/{filename}'

        logger.info(f'파일 저장 완료 : {file_url}')

        return file_url

    # 파일 삭제
    def delete_file(self, file_url):

        os.remove(file_url)


file_uploader = FileUploadService()