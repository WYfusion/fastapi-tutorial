from fastapi import FastAPI, APIRouter, Query

from typing import Optional

from schemas import RecipeSearchResults, Recipe, RecipeCreate
from recipe_data import RECIPES


app = FastAPI(title="Recipe API", openapi_url="/openapi.json")

api_router = APIRouter()


@api_router.get("/", status_code=200)
def root() -> dict:
    """
    Root GET
    """
    return {"msg": "Hello, World!"}


# Updated using to use a response_model
# https://fastapi.tiangolo.com/tutorial/response-model/
@api_router.get("/recipe/{recipe_id}", status_code=200, response_model=Recipe)
def fetch_recipe(*, recipe_id: int) -> dict:
    """
    Fetch a single recipe by ID
    """

    result = [recipe for recipe in RECIPES if recipe["id"] == recipe_id]
    if result:
        return result[0]


''' 
response_model 参数的作用和意义：
 1. **文档生成**：
    - `response_model` 会被 FastAPI 用于生成 OpenAPI 文档（例如 `/docs` 中的 Swagger UI）。
    - 它定义了 API 的返回数据结构，帮助开发者和用户理解 API 的输出。
 2. **数据序列化**：
    - 无论返回什么内容，都会使用 `response_model` 进行序列化，将 Python 对象转换为 JSON。
    - 如果返回的数据包含未在 `response_model` 中定义的字段，这些字段会被过滤掉。
 3. **数据验证**：
    - FastAPI 会验证返回的数据是否符合 `response_model` 的定义。
    - 如果返回的数据不符合模型定义，会抛出 500 错误，提示开发者修复。
 4. **数据转换**：
    - 如果返回的数据类型与 `response_model` 不完全匹配，FastAPI 会尝试转换数据以符合模型定义。
    - 例如，将字符串 URL 转换为 `HttpUrl` 类型。

 示例：
 - `response_model=RecipeSearchResults`：
    - 定义了 `/search/` 路径返回的数据结构为 `RecipeSearchResults` 模型。
    - 返回的数据必须包含一个 `results` 字段，且该字段是 `Recipe` 对象的列表。
 - `response_model=Recipe`：
    - 定义了 `/recipe/{recipe_id}` 路径返回的数据结构为 `Recipe` 模型。
    - 返回的数据必须包含 `id`, `label`, `source`, `url` 字段。
'''
@api_router.get("/search/", status_code=200, response_model=RecipeSearchResults)
def search_recipes(
    *,
    keyword: Optional[str] = Query(
        None,
        min_length=3,
        openapi_examples={
            "chickenExample": {
                "summary": "A chicken search example",
                "value": "chicken",
            }
        },
    ),
    max_results: Optional[int] = 10
) -> dict:
    """
    Search for recipes based on label keyword
    参数：
    - `keyword` (Optional[str]): 查询的关键字，用于匹配食谱的 `label` 字段。
        - 如果未提供关键字，则返回前 `max_results` 个食谱。
        - Query() 的作用是定义查询参数的元数据，例如最小长度和示例值，这些信息会被 OpenAPI 文档使用。
    - `max_results` (Optional[int]): 限制返回的最大结果
    """
    if not keyword:
        # 使用 Python 的列表切片语法 `RECIPES[:max_results]`，返回前 `max_results` 个食谱。
        # 基于 max_results 参数限制返回的结果数量，默认为 10。
        return {"results": RECIPES[:max_results]}

    results = filter(lambda recipe: keyword.lower() in recipe["label"].lower(), RECIPES)
    return {"results": list(results)[:max_results]}


# 新加的使用 Pydantic 模块的 `RecipeCreate` 模型来验证 POST 请求体
# the POST request body
@api_router.post("/recipe/", status_code=201, response_model=Recipe)
def create_recipe(*, recipe_in: RecipeCreate) -> dict:
    """
    Create a new recipe (in memory only)
    FastAPI 会自动的生成一个 OpenAPI 文档（Swagger UI）
    其中包含了查询参数的详细信息，例如参数名称、类型、是否必需、默认值以及示例值。
    这些信息对于 API 的使用者来说非常有帮助，可以更好地理解如何正确地调用 API。
    访问方式：
    1、打开浏览器，访问 http://127.0.0.1:8001/docs
        在这里你可以看到你设置的Recipe API名称和openapi_url：/openapi.json
    2、在 Swagger UI 中找到 POST /recipe/ 路径，点击 "Try it out" 按钮。
    3、在请求体中输入 JSON 格式的数据，这里要求的是符合schemas中设置的RecipeCreate的格式，即例如：
    {
        "label": "New Recipe",
        "source": "My Cookbook",
        "url": "http://example.com/new-recipe",
        "submitter_id": 123
    }
    4、点击 "Execute" 按钮，查看响应结果。

    3、也可以用cURL命令行工具来测试这个 POST 请求，例如：
'''
curl -X POST "http://127.0.0.1:8001/recipe/" \
-H "Content-Type: application/json" \
-d '{
"label": "Spaghetti Carbonara",
"source": "Italian Recipes",
"url": "http://example.com/spaghetti-carbonara",
"submitter_id": 123
}'
'''
    4、查看相应结果，应该会返回一个新的食谱条目的详细信息，例如：
    {"id":5,"label":"Spaghetti Carbonara","source":"Italian Recipes","url":"http://example.com/spaghetti-carbonara"}
    这个响应结果(return)表明新的食谱条目已经成功创建，并且包含了一个新的 `id` 字段，这个字段是自动生成的，表示新创建的食谱条目的唯一标识符。
    这个 `id` 字段是基于当前 `RECIPES` 列表的长度加 1 来生成的，因此每次创建新的食谱条目时，都会得到一个新的唯一 `id`。
    
    最终实现的效果是在内存中创建一个新的食谱条目，并返回该条目的详细信息，
    由于是绑定到/recipe/路径上使用 POST 方法来创建新的食谱条目，所以提交新的菜单后
    可以用/recipe/4...来访问新创建的食谱条目。
    """
    new_entry_id = len(RECIPES) + 1
    recipe_entry = Recipe(
        id=new_entry_id,
        label=recipe_in.label,
        source=recipe_in.source,
        url=recipe_in.url,
    )   
    # 提取传入的RecipeCreate格式的recipe_in数据中对应的Recipe中需要的数据，
    # 并创建一个新的Recipe对象，赋予一个新的唯一id。
    RECIPES.append(recipe_entry.dict())

    return recipe_entry


app.include_router(api_router)


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
