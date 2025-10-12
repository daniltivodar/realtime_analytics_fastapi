from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_title: str = 'Realtime analytics dashboard'
    database_url: str = (
        'postgresql+asyncpg://user:password@postgres:5432/analytics'
    )
    secret: str = 'SECRET'

    postgres_db: str = 'analytics'
    postgres_user: str = 'user'
    postgres_password: str = 'password'

    redis_url: str = 'redis://localhost:6379'
    redis_password: str = 'password'

    class Config:
        env_file = '.env'


settings = Settings()
