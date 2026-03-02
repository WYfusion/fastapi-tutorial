from pathlib import Path

from fastapi import FastAPI, APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.api.api_v1.api import api_router
from app.core.config import settings

BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))

root_router = APIRouter()
app = FastAPI(title="Recipe API")


# @app.on_event("startup")
# def on_startup() -> None:
#     # Ensure tables exist in the local SQLite DB (for demo/dev); in real apps use migrations
#     Base.metadata.create_all(bind=engine)


@root_router.get("/", status_code=200)
def root(
    request: Request,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Root GET
    """
    recipes = crud.recipe.get_multi(db=db, limit=10)
    return TEMPLATES.TemplateResponse(
        "index.html",
        {"request": request, "recipes": recipes},
    )


app.include_router(api_router, prefix=settings.API_V1_STR)
'''
prefix 参数的作用确实是为路由添加一个固定的上级路径前缀。

让我详细解释一下：
app.include_router(api_router, prefix=settings.API_V1_STR)
这里的 prefix 参数会为 api_router 中定义的所有路由添加一个统一的前缀。举个例子：

如果 settings.API_V1_STR 的值是 /api/v1 （这通常在配置文件中定义）
而 api_router 中定义了一个路由 /users
那么最终访问这个路由的实际路径就会变成 /api/v1/users


'''
app.include_router(root_router)


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
