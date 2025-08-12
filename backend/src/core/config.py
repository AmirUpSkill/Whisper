from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    A Pydantic model to manage application settings and secrets.
    It automatically reads variables from the .env file.
    """
    # Load environment variables from a .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # AI Service API Keys
    GROQ_API_KEY: str
    GEMINI_API_KEY: str

    # Database connection URL
    DATABASE_URL: str

# Create a single, globally accessible instance of the settings
settings = Settings()
