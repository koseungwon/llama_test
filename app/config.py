from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    embedding_model: str = "jhgan/ko-sroberta-multitask"
    chroma_persist_dir: str = "./chroma_db"
    upload_dir: str = "./documents"
    chunk_size: int = 500
    chunk_overlap: int = 50
    retriever_k: int = 5

    class Config:
        env_file = ".env"


settings = Settings()
