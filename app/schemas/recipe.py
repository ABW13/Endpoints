from pydantic import BaseModel, Field


class RecipeCreate(BaseModel):
    """Schema for creating a new recipe."""

    title: str = Field(min_length=1, max_length=120)
    cuisine: str = Field(min_length=1, max_length=60)
    servings: int = Field(gt=0, le=100)
    ingredients: list[str] = Field(min_length=1)


class RecipeResponse(BaseModel):
    """Schema for returning a recipe."""

    id: int
    title: str
    cuisine: str
    servings: int
    ingredients: list[str]

RecipeResponse.model_config = {
    "from_attributes": True,
    "json_schema_extra": {
        "example": {
            "id": 1,
            "title": "Pad Thai",
            "cuisine": "Thai",
            "servings": 4,
            "ingredients": ["rice noodles", "tamarind", "peanuts"],
        }
    },
}
