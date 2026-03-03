# FastAPI 依赖注入（Dependency Injection）完全指南

## 📌 核心概念

### 什么是 Depends？

`Depends` 是 FastAPI 中用于**依赖注入**的核心工具。它的作用是：

- **自动调用**指定的函数获取某个"依赖资源"
- **自动传递**这个资源给路由函数的参数
- **自动管理**这些资源的生命周期（创建和销毁）

简单理解：FastAPI 会帮你自动执行某个函数，并把它的返回值传给你的路由。

### 核心问题：为什么需要 Depends？

#### 1. **代码复用**（DRY 原则）
- 数据库连接、用户验证、日志记录等通用逻辑可以提取成独立函数
- 避免在每个路由中重复写相同的代码

#### 2. **代码解耦**（关注点分离）
- 路由函数只关注业务逻辑
- 依赖的资源（数据库、认证等）由 Depends 统一管理

#### 3. **自动文档生成和参数校验**
- FastAPI 自动识别依赖函数的参数和返回值
- 在 OpenAPI 文档中自动展示依赖关系
- 支持自动参数校验

#### 4. **异常处理和资源清理**
- 自动处理异常情况
- 确保资源被正确释放（如数据库连接关闭）

---

## 🔧 基础使用：获取数据库连接

### 定义依赖函数

```python
from typing import Generator
from sqlalchemy.orm.session import Session
from app.db.session import SessionLocal

def get_db() -> Generator:
    """
    创建并获取数据库会话
    - 使用 yield 关键字：yield 前的代码在请求前执行，yield 后的代码在请求后执行
    - 确保数据库连接在请求结束后自动关闭
    """
    db = SessionLocal()
    db.current_user_id = None  # 可以为数据库会话添加自定义属性
    try:
        yield db  # 将 db 传给路由函数
    finally:
        db.close()  # 请求结束后自动关闭连接
```

### 在路由中注入依赖

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import crud
from app.api import deps
from app.schemas.recipe import Recipe

router = APIRouter()

@router.get("/{recipe_id}", response_model=Recipe)
def fetch_recipe(
    *,
    recipe_id: int,
    db: Session = Depends(deps.get_db),  # ← 注入数据库连接
) -> Any:
    """
    获取单个菜谱
    
    FastAPI 会：
    1. 调用 deps.get_db() 创建数据库连接
    2. 将 db 传给这个路由函数
    3. 请求完成后，自动执行 finally 块关闭连接
    """
    result = crud.recipe.get(db=db, id=recipe_id)
    if not result:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return result
```

**执行流程图：**
```
┌─ 请求到达 ─────────────┐
│                        │
├─ 调用 get_db()         │
│   ├─ 创建数据库连接     │
│   └─ yield db           │
├─ 调用路由函数           │
│   ├─ 使用 db 查询数据   │
│   └─ 返回结果           │
├─ 执行 finally           │
│   └─ 关闭数据库连接     │
│                        │
└─ 返回响应 ──────────────┘
```

---

## 🔐 进阶：链式依赖（依赖的依赖）

### 场景：获取当前用户

某些路由需要当前用户的信息。我们可以构建一个依赖链：

**步骤 1：获取数据库连接**（已有）
```python
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**步骤 2：解析 JWT Token 并获取当前用户**
```python
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel
from app.models.user import User
from app.core.config import settings

# 定义 OAuth2 scheme（自动在请求头中寻找 Authorization: Bearer <token>）
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

class TokenData(BaseModel):
    username: Optional[str] = None

async def get_current_user(
    db: Session = Depends(get_db),          # ← 依赖 1：获取数据库
    token: str = Depends(oauth2_scheme),    # ← 依赖 2：获取 Token
) -> User:
    """
    获取当前认证用户
    
    依赖链：
    oauth2_scheme ──┐
                   ├──> get_current_user ──> 路由
    get_db ────────┘
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解析 JWT Token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False},
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    # 从数据库查询用户
    user = db.query(User).filter(User.id == token_data.username).first()
    if user is None:
        raise credentials_exception
    
    return user
```

**步骤 3：在路由中使用链式依赖**
```python
@router.post("/", response_model=Recipe)
def create_recipe(
    *,
    recipe_in: RecipeCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),  # ← 链式依赖！
) -> dict:
    """
    创建新菜谱
    
    FastAPI 执行流程：
    1. 调用 get_db() → 获得 db
    2. 调用 oauth2_scheme → 获得 token
    3. 调用 get_current_user(db, token) → 获得 current_user
    4. 调用路由函数 → 使用所有依赖
    """
    if recipe_in.submitter_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only submit recipes as yourself")
    
    recipe = crud.recipe.create(db=db, obj_in=recipe_in)
    return recipe
```

---

## 👮 权限控制：派生依赖

### 获取超级用户权限

```python
def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    只允许超级用户访问
    
    依赖链：
    oauth2_scheme ──┐
                   ├──> get_current_user ──┐
    get_db ────────┘                      ├──> get_current_active_superuser ──> 路由
                                          └─────────────────────────────────┘
    """
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, 
            detail="The user doesn't have enough privileges"
        )
    return current_user
```

### 在受保护路由中使用

```python
@router.get("/ideas/async/")
async def fetch_ideas_async(
    user: User = Depends(deps.get_current_active_superuser),  # ← 只有超级用户能访问
) -> dict:
    """获取来自 Reddit 的菜谱想法（仅超级用户）"""
    results = await asyncio.gather(
        *[get_reddit_top_async(subreddit=subreddit) for subreddit in RECIPE_SUBREDDITS]
    )
    return dict(zip(RECIPE_SUBREDDITS, results))
```

---

## 🔧 实用依赖：注入工具类实例

### 定义工具类依赖

```python
from app.clients.reddit import RedditClient

def get_reddit_client() -> RedditClient:
    """
    创建 Reddit 客户端实例
    
    如果需要复杂的初始化，可以使用 yield：
    def get_reddit_client() -> Generator[RedditClient, None, None]:
        client = RedditClient()
        try:
            yield client
        finally:
            client.close()  # 清理资源
    """
    return RedditClient()
```

### 在路由中使用

```python
RECIPE_SUBREDDITS = ["recipes", "easyrecipes", "TopSecretRecipes"]

@router.get("/ideas/")
def fetch_ideas(
    reddit_client: RedditClient = Depends(deps.get_reddit_client),  # ← 注入客户端
) -> dict:
    """获取来自 Reddit 的菜谱想法"""
    return {
        key: reddit_client.get_reddit_top(subreddit=key) 
        for key in RECIPE_SUBREDDITS
    }
```

---

## 📁 项目结构（依赖注入组织方式）

```
app/
├── api/
│   ├── deps.py                 # ← 集中管理所有依赖函数
│   │   ├── get_db()
│   │   ├── get_reddit_client()
│   │   ├── get_current_user()
│   │   └── get_current_active_superuser()
│   │
│   └── api_v1/
│       ├── api.py
│       └── endpoints/
│           ├── recipe.py       # ← 使用依赖的路由
│           └── auth.py
│
├── core/
│   ├── auth.py                # ← 认证逻辑（oauth2_scheme）
│   ├── config.py              # ← 配置管理
│   └── security.py            # ← 密码加密/验证
│
├── db/
│   └── session.py             # ← SessionLocal 定义
│
├── models/                    # ← ORM 模型
│   ├── user.py
│   └── recipe.py
│
├── crud/                      # ← 数据库操作
│   ├── crud_user.py
│   └── crud_recipe.py
│
├── clients/
│   └── reddit.py              # ← 第三方 API 客户端
│
└── main.py                    # ← FastAPI 应用入口
```

**最佳实践：在 `app/api/deps.py` 中集中管理所有依赖！**

---

## 🎯 常见使用模式总结

### 模式 1：简单依赖
```python
@router.get("/")
def endpoint(db: Session = Depends(get_db)):
    pass
```

### 模式 2：链式依赖
```python
@router.post("/")
def endpoint(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),  # 依赖已经得到的 db
):
    pass
```

### 模式 3：权限依赖
```python
@router.delete("/")
def endpoint(admin: User = Depends(get_current_active_superuser)):
    pass
```

### 模式 4：工具类依赖
```python
@router.get("/ideas/")
def endpoint(client: RedditClient = Depends(get_reddit_client)):
    pass
```

---

## ⚙️ 运行项目

### 启动服务器
```bash
# 进入项目目录
cd part-11-dependency-injection

# 安装依赖
pip install -r requirements.txt

# 运行应用
python -m uvicorn app.main:app --reload

# 或使用 run.sh
./run.sh
```

### 查看 API 文档
```
http://localhost:8000/docs          # Swagger UI
http://localhost:8000/redoc         # ReDoc
```

---

## 🔑 核心要点速记

| 特性 | 说明 |
|------|------|
| **Depends** | 声明一个依赖函数 |
| **yield** | 在函数中表示"请求前执行代码，请求后执行代码" |
| **链式依赖** | 依赖可以依赖其他依赖 |
| **隐式缓存** | 同一请求中，相同的依赖只执行一次 |
| **自动文档** | 依赖会自动出现在 OpenAPI 文档中 |
| **异常处理** | 依赖中的异常会自动返回 HTTP 异常 |

---

## 📚 核心优势总结

✅ **代码复用**：不重复编写获取 db、用户等通用逻辑  
✅ **清晰可读**：依赖关系明确，易于理解数据流  
✅ **自动管理**：资源创建和销毁自动处理  
✅ **易于测试**：可以轻松替换真实依赖为 Mock 对象  
✅ **自动文档**：依赖信息自动生成在 API 文档中  
✅ **权限控制**：构建权限依赖链，实现灵活的访问控制  

---

