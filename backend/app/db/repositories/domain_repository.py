from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CharacterArchetype, GameGenre, InterviewQuestion, ProductionConstraint, SkillTree, StatSystem


class DomainRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_genres(self) -> list[GameGenre]:
        return list(self.db.scalars(select(GameGenre)).all())

    def get_archetypes(self) -> list[CharacterArchetype]:
        return list(self.db.scalars(select(CharacterArchetype)).all())

    def get_constraints(self) -> list[ProductionConstraint]:
        return list(self.db.scalars(select(ProductionConstraint)).all())

    def get_skill_trees(self) -> list[SkillTree]:
        return list(self.db.scalars(select(SkillTree)).all())

    def get_stat_systems(self) -> list[StatSystem]:
        return list(self.db.scalars(select(StatSystem)).all())

    def get_questions_by_category(self, category: str) -> list[InterviewQuestion]:
        stmt = select(InterviewQuestion).where(InterviewQuestion.category.ilike(f"%{category}%"))
        return list(self.db.scalars(stmt).all())
