from fastapi import APIRouter, HTTPException
from app.schemas.recipe import RecipeCreate, RecipeResponse

router = APIRouter(prefix="/recipes", tags=["recipes"])

recipes_db: list[dict] = []
next_id: int = 1


@router.get("/", response_model=list[RecipeResponse])
def list_recipes():
    return recipes_db


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(recipe_id: int):
    for recipe in recipes_db:
        if recipe["id"] == recipe_id:
            return recipe
    raise HTTPException(status_code=404, detail=f"Recipe {recipe_id} not found")


@router.post("/", response_model=RecipeResponse, status_code=201)
def create_recipe(recipe: RecipeCreate):
    global next_id
    new_recipe = {"id": next_id, **recipe.model_dump()}
    recipes_db.append(new_recipe)
    next_id += 1
    return new_recipe