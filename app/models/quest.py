from sqlmodel import Field, SQLModel


class Quest(SQLModel, table=True):
    """The editable quest catalog — seeded from `app/data/quests.yaml`.

    XP/coin values live here (and only here). Clients reference a quest by
    `id`; they never send an XP amount — see `services/game.py` (Sprint 2).
    """

    __tablename__ = "quests"

    id: str = Field(primary_key=True)  # slug, e.g. "ml_study"
    category: str = Field(index=True)  # "main" | "side" | "health" | "leisure" | "penalty"
    title: str
    xp: int
    coins: int = Field(default=0)
    stat_key: str | None = Field(default=None)  # e.g. "prs_merged" — feeds achievements
    active: bool = Field(default=True)
