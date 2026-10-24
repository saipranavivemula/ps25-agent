from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./ps25.db"
    protected_brands: str = "acmepay.com,acmebank.com,google.com,paypal.com,netflix.com,amazon.com,microsoft.com,apple.com,facebook.com,instagram.com"
    high_threshold: float = 0.95
    medium_threshold: float = 0.70
    auto_actions_enabled: bool = False
    certstream_url: str = "wss://certstream.calidog.io/"
    shuffle_webhook_url: str = ""
    artifacts_dir: str = "./artifacts"
    api_key: str = "change-me"
    cors_origins: str = "http://localhost:5173"
    text_model: str = "tfidf"
    allow_local_demo_hosts: str = ""


settings = Settings()