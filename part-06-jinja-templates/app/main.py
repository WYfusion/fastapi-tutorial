from fastapi import FastAPI, APIRouter, Query, HTTPException, Request
from fastapi.templating import Jinja2Templates

from typing import Optional, Any
from pathlib import Path

from schemas import RecipeSearchResults, Recipe, RecipeCreate
from recipe_data import RECIPES


# 1. 定义模板的基础路径，指向当前文件所在目录
BASE_PATH = Path(__file__).resolve().parent
# 2. 初始化Jinja2Templates对象，指定模板文件所在的目录
#    这里将templates目录作为模板渲染的根目录
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))


app = FastAPI(title="Recipe API", openapi_url="/openapi.json")

api_router = APIRouter()


# Updated to serve a Jinja2 template
# https://www.starlette.io/templates/
# https://jinja.palletsprojects.com/en/3.0.x/templates/#synopsis
@api_router.get("/", status_code=200)
def root(request: Request) -> dict:
    """
    Root GET

    3. 使用TEMPLATES.TemplateResponse方法渲染HTML模板
    第一个参数是模板文件名（相对于templates目录）
    第二个参数是一个字典，包含传递给模板的变量
    其中"request"是必须传递的，用于在模板中访问请求上下文
    "recipes"是我们自定义的数据，将在模板中通过Jinja语法遍历显示，这里传递了RECIPES列表
    在Jinja2模板中，{% for recipe in recipes %} 中的 recipes 变量名必须与 TemplateResponse 中字典的键名完全一致。

    具体来说：

    在Python代码中：{"request": request, "recipes": RECIPES}
    "recipes" 是键名
    RECIPES 是实际的数据值
    在HTML模板第16行处：{% for recipe in recipes %}
    recipes 必须与Python字典中的键名 "recipes" 完全匹配
    这样Jinja2模板引擎才能找到对应的数据进行渲染
    如果将Python代码改为：

    return TEMPLATES.TemplateResponse(
        "index.html",
        {"request": request, "recipe_list": RECIPES},  # 键名改为recipe_list
    )
    那么模板中也必须相应修改为：

    {% for recipe in recipe_list %}  <!-- 变量名也要改为recipe_list -->
    这就是模板与Python代码之间的数据绑定机制。
    """
    return TEMPLATES.TemplateResponse(
        "index.html",
        {"request": request, "recipes": RECIPES},
    )


@api_router.get("/recipe/{recipe_id}", status_code=200, response_model=Recipe)
def fetch_recipe(*, recipe_id: int) -> Any:
    """
    Fetch a single recipe by ID
    """

    result = [recipe for recipe in RECIPES if recipe["id"] == recipe_id]
    if not result:
        # the exception is raised, not returned - you will get a validation
        # error otherwise.
        raise HTTPException(
            status_code=404, detail=f"Recipe with ID {recipe_id} not found"
        )

    return result[0]


@api_router.get("/search/", status_code=200, response_model=RecipeSearchResults)
def search_recipes(
    *,
    keyword: Optional[str] = Query(None, min_length=3, examples="chicken"),
    max_results: Optional[int] = 10,
) -> dict:
    """
    Search for recipes based on label keyword
    """
    if not keyword:
        # we use Python list slicing to limit results
        # based on the max_results query parameter
        return {"results": RECIPES[:max_results]}

    results = filter(lambda recipe: keyword.lower() in recipe["label"].lower(), RECIPES)
    return {"results": list(results)[:max_results]}


@api_router.post("/recipe/", status_code=201, response_model=Recipe)
def create_recipe(*, recipe_in: RecipeCreate) -> dict:
    """
    Create a new recipe (in memory only)
    """
    new_entry_id = len(RECIPES) + 1
    recipe_entry = Recipe(
        id=new_entry_id,
        label=recipe_in.label,
        source=recipe_in.source,
        url=recipe_in.url,
    )
    RECIPES.append(recipe_entry.dict())

    return recipe_entry


app.include_router(api_router)


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
