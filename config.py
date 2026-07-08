from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Конфигурация бота из .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str
    admin_ids: str = ""            # список id админов через запятую: "123,456"
    db_url: str = "postgresql+asyncpg://santexnik:santexnik@db:5432/santexnik"
    reminder_hour: int = 9         # час ежедневной проверки напоминаний (по времени сервера)
    reminder_minute: int = 0
    # за сколько дней до профилактики слать напоминания
    reminder_stages_days: str = "14,3,0"

    @property
    def admin_ids_list(self) -> list[int]:
        return [int(x) for x in self.admin_ids.replace(" ", "").split(",") if x]

    @property
    def stages(self) -> list[int]:
        """Этапы напоминаний в днях до даты (по убыванию): [14, 3, 0]."""
        return sorted((int(x) for x in self.reminder_stages_days.split(",") if x.strip()), reverse=True)


settings = Settings()
