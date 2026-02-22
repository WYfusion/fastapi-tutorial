from fastapi import FastAPI, APIRouter

from typing import Optional


RECIPES = [
    {
        "id": 1,
        "label": "Chicken Vesuvio",
        "source": "Serious Eats",
        "url": "http://www.seriouseats.com/recipes/2011/12/chicken-vesuvio-recipe.html",
    },
    {
        "id": 2,
        "label": "Cauliflower and Tofu Curry Recipe",
        "source": "Serious Eats",
        "url": "http://www.seriouseats.com/recipes/2011/02/cauliflower-and-tofu-curry-recipe.html",
    },
    {
        "id": 3,
        "label": "Chicken Paprikash",
        "source": "No Recipes",
        "url": "http://norecipes.com/recipe/chicken-paprikash/",
    },
]


app = FastAPI(title="Recipe API", openapi_url="/openapi.json")

api_router = APIRouter()


@api_router.get("/", status_code=200)
def root() -> dict:
    """
    Root GET
    """
    return {"msg": "Hello, World!"}


@api_router.get("/recipe/{recipe_id}", status_code=200)
def fetch_recipe(*, recipe_id: int) -> dict:
    """
    Fetch a single recipe by ID
    """

    result = [recipe for recipe in RECIPES if recipe["id"] == recipe_id]
    if result:
        return result[0]


# New addition, query parameter
# https://fastapi.tiangolo.com/tutorial/query-params/
@api_router.get("/search/", status_code=200)
def search_recipes(
    keyword: Optional[str] = None, max_results: Optional[int] = 2
) -> dict:
    """
    Search for recipes based on label keyword

    参数：
    - `keyword` (Optional[str]): 查询的关键字，用于匹配食谱的 `label` 字段。
      - 如果未提供关键字，则返回前 `max_results` 个食谱。
    - `max_results` (Optional[int]): 限制返回的最大结果数量，默认为 2。

    返回：
    - dict: 包含搜索结果的字典，格式为：`{"results": [...]}`。

    逻辑：
    1. 如果未提供 `keyword`：
       - 使用 Python 的列表切片语法 `RECIPES[:max_results]`，返回前 `max_results` 个食谱。
    2. 如果提供了 `keyword`：
       - 使用 `filter` 和 `lambda` 表达式筛选出符合条件的食谱。
       - `filter` 的作用：
         - 遍历 `RECIPES` 列表中的每个食谱，调用 `lambda` 表达式。
         - `lambda` 表达式的逻辑：
           - 将 `keyword` 转换为小写，与每个食谱的 `label` 字段（小写）进行匹配。
           - 如果 `keyword` 是 `label` 的子字符串，则返回 `True`，表示该食谱符合条件。
       - 将 `filter` 的结果转换为列表，并使用切片 `[:max_results]` 限制返回的结果数量。

    示例：
    - 如果 `keyword="chicken"`，`max_results=2`：
      - 匹配到的食谱为：
        ```
        [
            {"id": 1, "label": "Chicken Vesuvio", ...},
            {"id": 2, "label": "Chicken Paprikash", ...}
        ]
        ```
    - 如果未提供 `keyword`，`max_results=1`：
      - 返回：
        ```
        [
            {"id": 1, "label": "Chicken Vesuvio", ...}
        ]
        ```

    正确的请求示例：
    访问 /search/ 路径，不带查询参数：
    URL: http://localhost:8001/search/
    结果：返回前 max_results（默认为 2）个食谱。

    访问 /search/ 路径，带 keyword 查询参数：
    URL: http://localhost:8001/search/?keyword=Cauliflower
    结果：返回 label 中包含 Cauliflower 的食谱。

    访问 /search/ 路径，带 keyword 和 max_results 查询参数：
    URL: http://localhost:8001/search/?keyword=Chicken&max_results=1
    结果：返回 label 中包含 Chicken 的最多 1 个食谱。
    """
    if not keyword:
        # we use Python list slicing to limit results
        # based on the max_results query parameter
        return {"results": RECIPES[:max_results]}

    # 使用 filter 和 lambda 筛选符合条件的食谱
    results = filter(lambda recipe: keyword.lower() in recipe["label"].lower(), RECIPES)
    return {"results": list(results)[:max_results]}


app.include_router(api_router)


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
