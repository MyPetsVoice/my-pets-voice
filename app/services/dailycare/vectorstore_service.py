import os
import re
import json
import time
import pickle
import hashlib
import logging
from flask import current_app as app

import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import tiktoken

from config import Config


logger = logging.getLogger(__name__)

class VectorStoreService:
    def __init__(self, persist_directory: str = "./vector_db"):
        self.documents_path = Path(Config.DOCUMENTS_PATH)
        self.vector_db = Path(Config.VECTOR_DB)
        self.persist_directory = persist_directory
        self.collection_name = Config.COLLECTION_NAME
        self.store: Optional[Chroma] = None
        self.embedding = OpenAIEmbeddings(api_key=Config.OPENAI_API_KEY)

        self.cache_dir = os.path.join(os.path.dirname(str(self.vector_db)), "embedding_cache")
        os.makedirs(self.cache_dir, exist_ok=True)

        logger.info(f"VectorStoreService initialized. documents_path={self.documents_path}, vector_db={self.vector_db}")

    # -------------------------
    # Public: initialize DB
    # -------------------------
    def initialize_vector_db(self) -> Optional[Chroma]:
        """
        Load existing Chroma store if present and healthy; otherwise create a new one.
        """
        logger.info("벡터 스토어 초기화 시작...")
        try:
            # ensure vector_db exists
            if not self.vector_db.exists():
                self.vector_db.mkdir(parents=True, exist_ok=True)
                logger.info("벡터 DB 디렉토리가 없어서 새로 생성합니다.")
                return self.create_vector_db()

            # Try to load existing collection (do NOT pass embedding here)
            try:
                self.store = Chroma(
                    collection_name=self.collection_name,
                    embedding_function=self.embedding,
                    persist_directory=str(self.vector_db),
                )
                # quick health check
                try:
                    count = self.store._collection.count()
                    if count == 0:
                        logger.info("기존 벡터 DB가 비어있어서 새로 생성합니다.")
                        return self.create_vector_db()
                    logger.info(f"기존 벡터 DB 로딩 성공 (문서 수: {count})")
                    return self.store
                except Exception as e:
                    logger.warning(f"기존 벡터 DB 로딩 후 검증 실패: {e}")
                    return self.create_vector_db()

            except Exception as e:
                logger.warning(f"기존 벡터 DB 로딩 중 오류 발생: {e}")
                logger.info("새로운 벡터 DB를 생성합니다.")
                return self.create_vector_db()

        except Exception as e:
            logger.error(f"벡터 DB 초기화 중 치명적 오류: {e}", exc_info=True)
            return None


    def create_vector_db(self):
        all_documents = self.load_documents()
        if not all_documents:
            logger.error("문서가 없어 벡터 DB를 생성할 수 없습니다.")
            return None

        texts = [doc.page_content for doc in all_documents]
        metadatas = [doc.metadata for doc in all_documents]

        BATCH_SIZE = 200  # 입력 배열 길이 제한
        MAX_TOKENS_PER_BATCH = 200_000  # 안전 마진 적용
        encoder = tiktoken.get_encoding("cl100k_base")

        self.store = None
        batch_texts, batch_metadatas = [], []
        token_count = 0

        for i, (text, metadata) in enumerate(zip(texts, metadatas)):
            text_tokens = len(encoder.encode(text))
            # 토큰 수 또는 배열 길이 초과 시 현재 배치 전송
            if token_count + text_tokens > MAX_TOKENS_PER_BATCH or len(batch_texts) >= BATCH_SIZE:
                try:
                    if self.store is None:
                        logger.info(f"첫 배치({i-len(batch_texts)}~{i})로 벡터 DB 생성")
                        self.store = Chroma.from_texts(
                            texts=batch_texts,
                            embedding=self.embedding,
                            metadatas=batch_metadatas,
                            persist_directory=str(self.vector_db),
                            collection_name=self.collection_name
                        )
                    else:
                        logger.info(f"추가 배치({i-len(batch_texts)}~{i}) 저장")
                        self.store.add_texts(
                            texts=batch_texts,
                            metadatas=batch_metadatas,
                            collection_name=self.collection_name, 
                            persist_directory=str(self.vector_db),
                        )
                    # 배치 초기화
                    batch_texts, batch_metadatas = [], []
                    token_count = 0
                except Exception as e:
                    logger.error(f"배치 {i//BATCH_SIZE} Embedding 실패: {e}")
                    batch_texts, batch_metadatas = [], []
                    token_count = 0
                    continue

            batch_texts.append(text)
            batch_metadatas.append(metadata)
            token_count += text_tokens

        # 남은 배치 처리
        if batch_texts:
            try:
                if self.store is None:
                    logger.info(f"마지막 배치({len(all_documents)-len(batch_texts)}~{len(all_documents)})로 벡터 DB 생성")
                    self.store = Chroma.from_texts(
                        texts=batch_texts,
                        embedding=self.embedding,
                        metadatas=batch_metadatas,
                        persist_directory=self.persist_directory,
                        collection_name=self.collection_name, 
                        #colloection_name,persi..설정해야 DB찾을 수 있음!
                    )
                else:
                    logger.info(f"마지막 배치({len(all_documents)-len(batch_texts)}~{len(all_documents)}) 저장")
                    self.store.add_texts(
                        texts=batch_texts,
                        metadatas=batch_metadatas,
                        persist_directory=str(self.vector_db),        # ✅ 수정
                        collection_name=self.collection_name, 
                    )
            except Exception as e:
                logger.error(f"마지막 배치 Embedding 실패: {e}")

        if self.store:
            logger.info(f"총 {len(all_documents)}개 문서를 벡터 DB에 저장 완료")
        else:
            logger.error("벡터 DB 생성 실패")

        return self.store

    # -------------------------
    # Load documents (md + json)
    # -------------------------
    def load_documents(self) -> List[Document]:
        if not self.documents_path.exists():
            logger.error(f"문서 경로가 존재하지 않습니다: {self.documents_path}")
            return []

        all_documents: List[Document] = []

        md_files = list(self.documents_path.glob("**/*.md"))
        json_files = list(self.documents_path.glob("**/*.json"))

        logger.info(f"Markdown 파일 수: {len(md_files)}, JSON 파일 수: {len(json_files)}")

        for md_file in md_files:
            try:
                docs = self.load_markdown(md_file)
                all_documents.extend(docs)
            except Exception as e:
                logger.warning(f"Markdown 파일 처리 실패 ({md_file}): {e}")

        for json_file in json_files:
            try:
                docs = self.load_json(json_file)
                all_documents.extend(docs)
            except Exception as e:
                logger.warning(f"JSON 파일 처리 실패 ({json_file}): {e}")

        logger.info(f"총 {len(all_documents)}개 문서 청크 로딩 완료")
        return all_documents

    # -------------------------
    # Markdown loader
    # -------------------------
    def load_markdown(self, file_path: Path) -> List[Document]:
        try:
            text = file_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning(f"Markdown 파일 읽기 실패 ({file_path}): {e}")
            return []

        meta = self.extract_document_metadata(text)
        splitter = MarkdownHeaderTextSplitter([("#", "title"), ("##", "subtitle")])

        try:
            sections = splitter.split_text(text)
        except Exception as e:
            logger.warning(f"Markdown 분할 실패({file_path}), 전체를 하나로 처리: {e}")
            sections = [text]

        docs: List[Document] = []
        for i, sec in enumerate(sections):
            if isinstance(sec, Document):
                content = sec.page_content
                sec_meta = sec.metadata or {}
            else:
                content = str(sec)
                sec_meta = {}

            clean = self.remove_metadata_blocks(content)
            if not clean.strip():
                continue

            metadata = {**meta, **sec_meta, "source_file": file_path.name, "file_path": str(file_path), "section_index": i}
            metadata = self._sanitize_metadata(metadata)
            docs.append(Document(page_content=clean, metadata=metadata))

        return docs

    # -------------------------
    # JSON loader (robust)
    # -------------------------
    def load_json(self, file_path: Path) -> List[Document]:
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning(f"JSON 파일 읽기 실패 ({file_path}): {e}")
            return []

        docs: List[Document] = []

        # If data is a list of items (common in your medication files)
        if isinstance(data, list):
            for idx, item in enumerate(data):
                try:
                    if isinstance(item, dict):
                        # prefer 'text' if present and non-empty
                        content = item.get("text") if isinstance(item.get("text"), str) and item.get("text").strip() else None
                        if content is None:
                            # fallback: serialize entire item
                            content = json.dumps(item, ensure_ascii=False, indent=2)
                        metadata = {
                            "file_path": str(file_path),
                            "data_type": "medication",
                            "item_index": idx,
                        }
                        # merge item metadata if present
                        if "metadata" in item and isinstance(item["metadata"], dict):
                            metadata.update(item["metadata"])
                        if "id" in item:
                            metadata["document_id"] = item["id"]

                    else:
                        # non-dict item -> stringify
                        content = json.dumps(item, ensure_ascii=False)
                        metadata = {"file_path": str(file_path), "data_type": "medication", "item_index": idx}

                    # safe chunking (avoids RecursiveJsonSplitter crashes)
                    chunks = self._safe_chunk_text(content, max_chunk_size=1000)
                    for c_i, chunk in enumerate(chunks):
                        meta_copy = dict(metadata)
                        meta_copy.update({"chunk_index": c_i, "total_chunks": len(chunks)})
                        docs.append(Document(page_content=chunk, metadata=self._sanitize_metadata(meta_copy)))

                except Exception as item_e:
                    logger.warning(f"JSON item 처리 실패 ({file_path}, index={idx}): {item_e}")
                    continue

        elif isinstance(data, dict):
            # single JSON object: serialize and chunk
            content = json.dumps(data, ensure_ascii=False, indent=2)
            chunks = self._safe_chunk_text(content, max_chunk_size=1000)
            for c_i, chunk in enumerate(chunks):
                meta = {"file_path": str(file_path), "data_type": "medication", "chunk_index": c_i, "total_chunks": len(chunks)}
                docs.append(Document(page_content=chunk, metadata=self._sanitize_metadata(meta)))
        else:
            # fallback: stringify whole file
            content = str(data)
            chunks = self._safe_chunk_text(content, max_chunk_size=1000)
            for c_i, chunk in enumerate(chunks):
                meta = {"file_path": str(file_path), "data_type": "medication", "chunk_index": c_i, "total_chunks": len(chunks)}
                docs.append(Document(page_content=chunk, metadata=self._sanitize_metadata(meta)))

        return docs

    # -------------------------
    # Utilities
    # -------------------------
    def _safe_chunk_text(self, text: str, max_chunk_size: int = 1000) -> List[str]:
        """
        Split text into chunks of <= max_chunk_size by sentence boundaries (best-effort).
        """
        if not text:
            return []

        text = text.strip()
        if len(text) <= max_chunk_size:
            return [text]

        # Split into sentences (preserve punctuation)
        sentences = re.split(r'(?<=[\.\?\!\n])\s+', text)
        chunks = []
        current = ""
        for sent in sentences:
            if not sent:
                continue
            if len(current) + len(sent) + 1 <= max_chunk_size:
                current += (sent if current == "" else " " + sent)
            else:
                if current:
                    chunks.append(current.strip())
                # if single sentence itself too long, break by characters
                if len(sent) > max_chunk_size:
                    for i in range(0, len(sent), max_chunk_size):
                        part = sent[i:i + max_chunk_size].strip()
                        if part:
                            chunks.append(part)
                    current = ""
                else:
                    current = sent
        if current:
            chunks.append(current.strip())
        return chunks

    def extract_document_metadata(self, content: str) -> Dict[str, Any]:
        metadata: Dict[str, Any] = {}
        yaml_pattern = r"^---\s*\nmetadata:\s*\n(.*?)\n---"
        match = re.search(yaml_pattern, content, flags=re.MULTILINE | re.DOTALL)
        if not match:
            return metadata

        yaml_content = match.group(1)
        for line in yaml_content.splitlines():
            line = line.strip()
            if ":" in line and not line.startswith("-"):
                key, val = line.split(":", 1)
                key = key.strip()
                value = val.strip().strip('"\'')
                if key == "categories":
                    metadata[key] = self.parse_yaml_list(value)
                else:
                    metadata[key] = value
        return metadata

    def parse_yaml_list(self, value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(v).strip().strip('"\'') for v in value]
        if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
            items = value[1:-1].split(",")
            return [item.strip().strip('"\'') for item in items]
        return [str(value).strip().strip('"\'')]

    def remove_metadata_blocks(self, content: str) -> str:
        yaml_pattern = r"^---\s*\nmetadata:\s*\n.*?\n---\s*\n"
        cleaned = re.sub(yaml_pattern, "", content, flags=re.MULTILINE | re.DOTALL)
        cleaned = re.sub(r"\n\s*\n\s*\n", "\n\n", cleaned)
        return cleaned.strip()

    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert metadata values to primitives (str/int/float/bool). Lists/dicts -> JSON string.
        """
        safe: Dict[str, Any] = {}
        for k, v in (metadata or {}).items():
            if isinstance(v, (str, int, float, bool)) or v is None:
                safe[k] = v
            else:
                try:
                    safe[k] = json.dumps(v, ensure_ascii=False) if not isinstance(v, (str, int, float, bool)) else v
                except Exception:
                    safe[k] = str(v)
        return safe

    # -------------------------
    # Embedding cache helpers
    # -------------------------
    def get_cache_key(self, text: str) -> str:
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def save_embedding_cache(self, text: str, embedding: List[float]):
        cache_file = os.path.join(self.cache_dir, f"{self.get_cache_key(text)}.pkl")
        try:
            with open(cache_file, "wb") as f:
                pickle.dump(embedding, f)
        except Exception as e:
            logger.warning(f"임베딩 캐시 저장 실패: {e}")

    def load_embedding_cache(self, text: str) -> Optional[List[float]]:
        cache_file = os.path.join(self.cache_dir, f"{self.get_cache_key(text)}.pkl")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "rb") as f:
                    return pickle.load(f)
            except Exception as e:
                logger.warning(f"임베딩 캐시 로드 실패: {e}")
        return None
