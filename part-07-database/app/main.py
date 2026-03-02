from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates

from typing import Optional, Any
from pathlib import Path
from sqlalchemy.orm import Session
# 1. 导入数据模型和依赖项
# schemas.recipe: 包含Pydantic模型，用于数据验证和序列化
# deps: 包含依赖项函数，用于获取数据库会话
# crud: 包含数据库操作的CRUD函数
from app.schemas.recipe import RecipeSearchResults, Recipe, RecipeCreate
from app import deps
from app import crud


# Project Directories
# 2. 设置项目路径和模板引擎
# ROOT: 项目根目录路径
# BASE_PATH: 当前文件所在目录路径
# TEMPLATES: Jinja2模板引擎实例，指定模板文件目录为"templates"
ROOT = Path(__file__).resolve().parent.parent
BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))


# 3. 初始化FastAPI应用实例
# title: API标题
# openapi_url: OpenAPI规范文档的URL路径
app = FastAPI(title="Recipe API", openapi_url="/openapi.json")

# Ensure tables exist for demo purposes (normally use Alembic migrations)
# Base.metadata.create_all(bind=engine)
'''
在简单的 FastAPI 示例中， Base.metadata.create_all(bind=engine)。 
局限性：create_all() 只能在表不存在时创建它。如果你后来想在现有表中增加一个字段，它无能为力。
Alembic 的优势：它允许你在保留现有数据的情况下，安全地修改数据库结构，并像 Git 一样通过版本号管理每一次变更。
'''

# 4. 创建API路由器实例，用于组织路由
api_router = APIRouter()


# 5. 根路径路由处理器，返回渲染后的HTML模板
# @api_router.get: 装饰器，定义GET请求路由
# status_code=200: 响应状态码
# db: Session = Depends(deps.get_db): 数据库会话依赖注入
#    - Depends(deps.get_db)自动调用deps.get_db函数获取数据库会话
#    - 将数据库会话作为参数传递给路由处理函数
@api_router.get("/", status_code=200)
def root(
    request: Request,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Root GET
    """
    # 6. 调用CRUD操作获取多条记录
    # crud.recipe.get_multi: 调用recipe CRUD对象的get_multi方法
    # db=db: 传递数据库会话
    # limit=10: 限制返回记录数量为10条
    recipes = crud.recipe.get_multi(db=db, limit=10)
    
    # 7. 渲染HTML模板并返回响应
    # TEMPLATES.TemplateResponse: 使用Jinja2模板引擎渲染模板
    # "index.html": 模板文件名（相对于templates目录）
    # {"request": request, "recipes": recipes}: 传递给模板的上下文变量
    #    - "request": 请求对象，Jinja2模板必需
    #    - "recipes": 查询结果，将在模板中使用
    return TEMPLATES.TemplateResponse(
        "index.html",
        {"request": request, "recipes": recipes},
    )


# 8. 获取单个菜谱详情的路由处理器
# response_model=Recipe: 指定响应数据模型，用于自动验证和文档生成
@api_router.get("/recipe/{recipe_id}", status_code=200, response_model=Recipe)
def fetch_recipe(
    *,
    recipe_id: int,  # 从URL路径参数中提取recipe_id
    db: Session = Depends(deps.get_db),  # 数据库会话依赖注入
) -> Any:
    """
    Fetch a single recipe by ID
    """
    # 9. 调用CRUD操作获取单条记录
    # crud.recipe.get: 调用recipe CRUD对象的get方法
    # db=db: 传递数据库会话
    # id=recipe_id: 根据ID查询特定记录
    result = crud.recipe.get(db=db, id=recipe_id)
    
    # 10. 处理查询结果不存在的情况
    if not result:
        # 如果未找到记录，则抛出HTTP异常
        # status_code=404: HTTP状态码404（未找到）
        # detail: 异常详细信息
        raise HTTPException(
            status_code=404, detail=f"Recipe with ID {recipe_id} not found"
        )

    # 11. 返回查询结果
    # FastAPI会自动将Pydantic模型序列化为JSON响应
    return result


# 12. 搜索菜谱的路由处理器
# response_model=RecipeSearchResults: 指定响应数据模型
@api_router.get("/search/", status_code=200, response_model=RecipeSearchResults)
def search_recipes(
    *,
    # 查询参数：keyword（可选，最小长度3，默认值None）
    keyword: Optional[str] = Query(None, min_length=3, examples={"default": {"value": "chicken"}}),
    # 查询参数：max_results（可选，默认值10）
    max_results: Optional[int] = 10,
    # 数据库会话依赖注入
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Depends(deps.get_db)是 FastAPI 的依赖注入标记：
    当有请求命中对应路由时，FastAPI 会先调用 deps.get_db() 拿到一个数据库会话，
    把它注入到参数 db，然后再执行路由函数，最后无论成功/异常都会执行 finally 里的 db.close() 来释放连接。
    这只是在每次请求生命周期内创建/关闭一个 SQLAlchemy Session，不会“记录当前数据库内容”，也不是缓存或快照。

    触发逻辑：
    每个请求匹配到带 db: Session = Depends(deps.get_db) 的路由时自动触发。
    路由函数里直接使用 db 进行查询/写入即可，完成后框架负责调用 finally 关闭会话。
    
    Search for recipes based on label keyword
    """
    # 13. 获取所有菜谱（限制数量）
    recipes = crud.recipe.get_multi(db=db, limit=max_results)
    
    # 14. 如果没有提供搜索关键词，则返回所有菜谱
    if not keyword:
        return {"results": recipes}

    # 15. 如果提供了搜索关键词，则过滤结果
    # filter: Python内置函数，用于过滤序列
    # lambda recipe: 匿名函数，检查菜谱标签是否包含关键词
    # recipe.label.lower(): 将菜谱标签转换为小写
    # keyword.lower(): 将搜索关键词转换为小写
    # in: 检查关键词是否在标签中
    results = filter(lambda recipe: keyword.lower() in recipe.label.lower(), recipes)
    
    # 16. 返回过滤后的结果（限制数量）
    return {"results": list(results)[:max_results]}


# 17. 创建新菜谱的路由处理器
# status_code=201: 响应状态码201（已创建）
# response_model=Recipe: 指定响应数据模型
@api_router.post("/recipe/", status_code=201, response_model=Recipe)
def create_recipe(
    *, 
    # 请求体参数，使用RecipeCreate模型进行验证
    recipe_in: RecipeCreate, 
    # 数据库会话依赖注入
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Create a new recipe in the database.
    """
    # 18. 调用CRUD操作创建新记录
    # crud.recipe.create: 调用recipe CRUD对象的create方法
    # db=db: 传递数据库会话
    # obj_in=recipe_in: 传递要创建的对象数据
    recipe = crud.recipe.create(db=db, obj_in=recipe_in)

    # 19. 返回创建的记录
    return recipe


# 20. 将API路由器注册到主应用
app.include_router(api_router)


# 21. 应用入口点（调试用途）
if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    # 启动Uvicorn服务器
    # app: FastAPI应用实例
    # host="0.0.0.0": 监听所有网络接口
    # port=8001: 监听端口
    # log_level="debug": 日志级别
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
