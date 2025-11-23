from sqlmodel import Field, SQLModel, select, Relationship

class OvmfPath(SQLModel, table=True):
    __tablename__ = "ovmfpath"
    id: int | None = Field(primary_key=True)
    name: str = Field(nullable=False, unique=True)
    path: str = Field(nullable=False)
    description: str = Field(nullable=True)
