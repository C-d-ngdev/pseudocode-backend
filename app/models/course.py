from datetime import datetime, timezone

from sqlmodel import SQLModel, Field, Relationship


class Course(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    slug: str = Field(unique=True, index=True)
    description: str = ""
    published: bool = False
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    lessons: list["Lesson"] = Relationship(back_populates="course")


class Lesson(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key="course.id", index=True)
    title: str
    content: str  # contenu en Markdown
    position: int = 0  # ordre dans le cours

    course: Course | None = Relationship(back_populates="lessons")
    