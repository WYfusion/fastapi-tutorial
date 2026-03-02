Depends 是 FastAPI 中用于依赖注入的核心工具，简单来说：
它的作用是「自动帮你获取某个函数 / 类的执行结果，并把结果传递给路由函数的参数」。
你可以把它理解为：路由函数需要某个 “依赖资源”（比如数据库连接、用户信息、工具类实例），Depends 会自动去调用指定的函数获取这个资源，再把资源 “喂” 给路由函数，无需你在路由里手动调用。


为什么需要 Depends？
核心解决 3 个问题：
1、代码复用：把重复的逻辑（比如获取数据库连接、校验用户身份）抽成独立函数，通过 Depends 注入，避免每个路由都写一遍；
2、解耦：路由函数只关注核心业务，依赖的资源由 Depends 统一管理；
3、自动校验 / 文档生成：FastAPI 会识别 Depends 中函数的参数和返回值，自动生成接口文档，且支持参数校验。

场景 1：获取通用资源（比如数据库连接）
```
# 定义依赖函数：获取数据库会话
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db  # 生成数据库连接
    finally:
        db.close()  # 请求结束后自动关闭

# 路由中注入数据库连接
@router.get("/{recipe_id}")
def fetch_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),  # Depends 自动调用 get_db，把 db 传给路由
):
    result = crud.recipe.get(db=db, id=recipe_id)
    ...
```
每次请求 /recipe_id 时，Depends(get_db) 会自动执行 get_db()，获取数据库连接 db；
请求结束后，get_db 中的 finally 会自动关闭连接，无需手动处理。




Depends 是 FastAPI 的依赖注入工具，核心是自动获取并传递路由函数所需的 “依赖资源”；
主要用途：复用通用逻辑（数据库连接、参数校验）、权限控制、注入工具类实例；
核心优势：代码解耦、自动异常处理、支持嵌套依赖、自动生成接口文档。
简单记：Depends 帮你把 “路由之外的准备工作”（比如连数据库、验权限）抽离出来，让路由函数只专注于核心业务逻辑。