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

    celery_broker_url: str = 'amqp://guest:guest@rabbitmq:5672//'
    celery_result_backend: str = 'redis://:password@redis:6379/0'

    rabbitmq_user: str = 'guest'
    rabbitmq_password: str = 'guest'

    flower_user: str = 'admin'
    flower_password: str = 'password'

    class Config:
        env_file = '.env'


settings = Settings()
