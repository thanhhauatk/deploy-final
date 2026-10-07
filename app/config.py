from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://postgres:postgres@db:5432/appdb"
    aws_region: str = "us-east-1"
    s3_bucket_name: str = ""
    app_name: str = "deploy-final-api"


settings = Settings()
