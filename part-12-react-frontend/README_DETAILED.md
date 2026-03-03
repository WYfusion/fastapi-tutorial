# Part 12: React Frontend - 完整项目架构与实现流程

## 项目概述

这是一个完整的全栈应用，采用 **前后端分离** 架构：
- **后端 (Backend)**: FastAPI + SQLAlchemy + JWT 认证
- **前端 (Frontend)**: React + React Router + Tailwind CSS
- **通信方式**: RESTful API + CORS
- **认证机制**: JWT Token (存储在 localStorage)

---

## 🏗️ 项目架构详解

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      用户浏览器                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  React 前端应用 (localhost:3000)                     │   │
│  │  ├── React Router (页面路由)                        │   │
│  │  ├── FastAPIClient (API 客户端)                     │   │
│  │  ├── localStorage (Token 存储)                      │   │
│  │  └── Components (UI 组件)                           │   │
│  └─────────────────────────────────────────────────────┘   │
│                          ▲  │                               │
│                     GET  │  │ POST/PUT/DELETE               │
│                     JSON │  │ JSON + JWT Token              │
│                          │  ▼                               │
└─────────────────────────────────────────────────────────────┘
                            │
                   CORS 跨域请求
                            │
┌─────────────────────────────────────────────────────────────┐
│              FastAPI 后端服务 (localhost:8001)               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  API 层                                              │   │
│  │  ├── /api/v1/auth/login       (登录)               │   │
│  │  ├── /api/v1/auth/signup      (注册)               │   │
│  │  ├── /api/v1/auth/me          (获取当前用户)        │   │
│  │  ├── /api/v1/recipes/search   (搜索菜谱)           │   │
│  │  ├── /api/v1/recipes/my-recipes (我的菜谱)         │   │
│  │  └── /api/v1/recipes/         (增删改查)           │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  业务逻辑层 (CRUD)                                   │   │
│  │  ├── crud.user   (用户操作)                         │   │
│  │  └── crud.recipe (菜谱操作)                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  数据库层 (SQLAlchemy + SQLite)                     │   │
│  │  ├── User 表     (id, email, password, full_name)  │   │
│  │  └── Recipe 表   (id, label, url, source, ...)     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 核心业务流程详解

### 1. 用户注册流程

**前端 → 后端数据流:**

```javascript
// 前端: src/pages/sign-up/index.jsx
用户填写表单 → client.register(email, password, fullName)
                    ↓
// 前端: src/client.js
FastAPIClient.register() → POST /api/v1/auth/signup
发送: { email, password, full_name, is_active: true }
                    ↓
// 后端: app/api/api_v1/endpoints/auth.py
@router.post("/signup")
1. 检查邮箱是否已存在
2. crud.user.create() 创建新用户 (密码会被哈希)
3. 返回用户信息: { id, email, full_name }
                    ↓
// 前端接收响应
注册成功 → 跳转到登录页
```

**实现细节:**
- 密码在后端使用 bcrypt 进行哈希存储，绝不明文保存
- 前端表单验证 + 后端二次验证
- 邮箱唯一性约束

---

### 2. 用户登录与认证流程

**完整的 JWT 认证流程:**

```javascript
// 步骤 1: 前端提交登录表单
// src/pages/login/index.jsx
用户输入邮箱和密码 → client.login(email, password)
                         ↓
// 步骤 2: 构造 OAuth2 表单数据
// src/client.js - login()
创建 FormData:
  - grant_type: "password"
  - username: email
  - password: password
                         ↓
发送: POST /api/v1/auth/login (FormData 格式)
                         ↓
// 步骤 3: 后端验证凭据
// app/api/api_v1/endpoints/auth.py
@router.post("/login")
1. authenticate(email, password, db)
   - 查询数据库获取用户
   - verify_password(plain_password, hashed_password)
2. create_access_token(sub=user.id)
   - 生成 JWT: { sub: user_id, exp: 过期时间 }
   - 使用密钥签名
3. 返回: { access_token: "eyJ...", token_type: "bearer" }
                         ↓
// 步骤 4: 前端存储 Token
// src/client.js
localStorage.setItem('token', JSON.stringify(resp.data))
                         ↓
// 步骤 5: 获取用户信息
client.fetchUser() → GET /api/v1/auth/me
请求头: Authorization: Bearer eyJ...
                         ↓
// 后端验证 Token 并返回用户信息
localStorage.setItem('user', JSON.stringify(data))
                         ↓
// 步骤 6: 跳转到用户仪表盘
navigate('/my-recipes')
```

**JWT Token 结构:**
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_id",
    "exp": 1234567890
  },
  "signature": "加密签名"
}
```

---

### 3. 请求拦截器与自动认证

**每个 API 请求的自动化流程:**

```javascript
// src/client.js - localStorageTokenInterceptor()
每次发送 API 请求前:
1. 从 localStorage 读取 token
2. 使用 jwt-decode 解码 token
3. 检查 token 是否过期:
   decodedToken.exp > 当前时间?
4. 如果有效: 添加请求头
   headers['Authorization'] = `Bearer ${token.access_token}`
5. 如果过期: 弹出提示 "Your login session has expired"
```

**这意味着:**
- 用户登录一次，8 天内所有请求自动携带认证信息
- Token 过期自动提示，无需手动检查
- 所有受保护的 API 都无需额外处理认证

---

### 4. 搜索菜谱流程 (公开访问)

```javascript
// 前端: src/pages/home/index.jsx
用户输入关键词 "chicken" → 点击 Search
                              ↓
client.getRecipes("chicken")
  → GET /api/v1/recipes/search/?keyword=chicken&max_results=10
                              ↓
// 后端: app/api/api_v1/endpoints/recipe.py
@router.get("/search/")
1. crud.recipe.get_multi(db, limit=10) - 从数据库获取菜谱
2. 使用 filter() 过滤包含关键词的菜谱
3. 返回: { results: [ {id, label, url, source}, ... ] }
                              ↓
// 前端更新状态
setRecipes(data.results)
                              ↓
// UI 渲染: RecipeTable 组件显示菜谱列表
```

---

### 5. 创建菜谱流程 (需要认证)

```javascript
// 前端: src/pages/my-recipes/index.jsx
用户点击 "Add Recipe" → 显示表单模态框
                          ↓
填写表单:
  - label: "Chicken Soup"
  - url: "https://example.com/recipe"
  - source: "My Kitchen"
                          ↓
提交表单 → onCreateRecipe()
  1. 表单验证 (前端)
  2. client.fetchUser() - 获取当前用户 ID
  3. client.createRecipe(label, url, source, user.id)
     → POST /api/v1/recipes/
     请求头: Authorization: Bearer eyJ...
     请求体: { label, url, source, submitter_id }
                          ↓
// 后端: app/api/api_v1/endpoints/recipe.py
@router.post("/")
1. deps.get_current_user - 从 JWT 验证用户身份
2. 检查 submitter_id 是否匹配当前用户 (安全检查)
3. crud.recipe.create() - 保存到数据库
4. 返回新创建的菜谱对象
                          ↓
// 前端刷新列表
fetchUserRecipes() - 重新获取用户的所有菜谱
setShowForm(false) - 关闭模态框
```

**安全机制:**
- 只有登录用户才能创建菜谱 (JWT 验证)
- 用户只能以自己的身份提交 (submitter_id 检查)
- 前端 URL 格式验证 + 后端数据验证

---

### 6. CORS 跨域处理

**为什么需要 CORS?**
- 前端运行在 `localhost:3000`
- 后端运行在 `localhost:8001`
- 浏览器安全策略阻止跨域请求

**后端配置 (app/main.py):**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允许的前端地址
    allow_credentials=True,                    # 允许携带 Cookie/Token
    allow_methods=["*"],                       # 允许所有 HTTP 方法
    allow_headers=["*"],                       # 允许所有请求头
)
```

**前端配置 (src/config.js):**
```javascript
const config = {
  apiBasePath: env.REACT_APP_API_BASE_PATH || 'http://localhost:8001',
};
```

---

## 📂 关键代码文件说明

### 后端核心文件

| 文件路径 | 功能说明 |
|---------|---------|
| `app/main.py` | FastAPI 应用入口，配置 CORS、中间件、路由 |
| `app/api/api_v1/endpoints/auth.py` | 认证端点：登录、注册、获取用户信息 |
| `app/api/api_v1/endpoints/recipe.py` | 菜谱端点：CRUD 操作、搜索 |
| `app/crud/crud_user.py` | 用户数据库操作：创建、查询、密码验证 |
| `app/crud/crud_recipe.py` | 菜谱数据库操作：增删改查 |
| `app/core/auth.py` | JWT 生成与验证逻辑 |
| `app/core/security.py` | 密码哈希与验证 (bcrypt) |
| `app/models/user.py` | User 数据模型 (SQLAlchemy ORM) |
| `app/models/recipe.py` | Recipe 数据模型 (SQLAlchemy ORM) |

### 前端核心文件

| 文件路径 | 功能说明 |
|---------|---------|
| `src/App.js` | React 应用入口，配置路由 |
| `src/client.js` | **FastAPIClient 类**：封装所有 API 调用 |
| `src/config.js` | 配置文件：API 基础路径 |
| `src/pages/home/index.jsx` | 首页：搜索和浏览菜谱 |
| `src/pages/login/index.jsx` | 登录页 |
| `src/pages/sign-up/index.jsx` | 注册页 |
| `src/pages/my-recipes/index.jsx` | 用户仪表盘：管理个人菜谱 |
| `src/components/RecipeTable/index.jsx` | 菜谱列表组件 |

---

## 🚀 运行项目步骤

### 第一步: 启动后端服务

```bash
# 1. 进入后端目录
cd part-12-react-frontend/backend

# 2. 配置 Python 环境 (如果还没有)
# conda create -n fastapi-react python=3.9
# conda activate fastapi-react

# 3. 安装依赖
pip install -r requirements.txt
# 或使用 poetry: poetry install

# 4. 运行数据库迁移 (初始化数据库)
alembic upgrade head

# 5. 启动 FastAPI 服务
uvicorn app.main:app --reload --port 8001

# 服务运行在: http://localhost:8001
# API 文档: http://localhost:8001/docs
```

### 第二步: 启动前端应用

```bash
# 1. 进入前端目录
cd part-12-react-frontend/frontend

# 2. 安装依赖 (首次运行)
npm install

# 3. 启动开发服务器
npm start

# 应用运行在: http://localhost:3000
# 浏览器会自动打开
```

---

## 🎯 完整用户操作流程演示

### 场景 1: 新用户注册并创建菜谱

1. **打开应用**: 访问 `http://localhost:3000`
2. **点击注册**: 右上角 "Sign Up" 或登录页的 "Create Account"
3. **填写信息**:
   - Email: `test@example.com`
   - Password: `password123`
   - Full Name: `Test User`
4. **提交注册**: 
   - 前端验证表单
   - 发送 POST 请求到 `/api/v1/auth/signup`
   - 后端创建用户，密码哈希存储
5. **跳转登录**: 自动跳转到登录页
6. **登录账号**:
   - 输入邮箱和密码
   - 后端验证凭据，生成 JWT
   - Token 存储到 localStorage
   - 获取用户信息
   - 跳转到 `/my-recipes`
7. **创建菜谱**:
   - 点击 "Add Recipe" 按钮
   - 填写菜谱信息
   - 提交后自动刷新列表
8. **查看菜谱**: 在 "My Recipes" 页面看到刚创建的菜谱

### 场景 2: 搜索菜谱 (无需登录)

1. **访问首页**: `http://localhost:3000`
2. **输入关键词**: 例如 "chicken"
3. **点击 Search**:
   - 发送 GET 请求到 `/api/v1/recipes/search/?keyword=chicken`
   - 后端过滤数据库中的菜谱
   - 返回匹配结果
4. **浏览结果**: 页面显示所有包含 "chicken" 的菜谱

---

## 🛡️ 安全机制说明

### 1. 密码安全
- 使用 bcrypt 算法进行密码哈希
- 永不存储明文密码
- 登录时验证哈希值

### 2. JWT 认证
- Token 包含用户 ID 和过期时间
- 使用密钥 (JWT_SECRET) 签名，防止篡改
- 8 天有效期，过期需重新登录

### 3. API 权限控制
```python
# 受保护的端点示例
@router.get("/my-recipes/")
def fetch_user_recipes(
    current_user: User = Depends(deps.get_current_user),  # 必须登录
):
    return current_user.recipes
```

### 4. CSRF 防护
- JWT 存储在 localStorage (非 Cookie)
- 每次请求通过 Authorization 头发送
- 避免 CSRF 攻击

---

## 🎨 实现的功能效果

### ✅ 已实现功能

| 功能 | 描述 | 是否需要登录 |
|-----|------|------------|
| 🏠 浏览首页 | 查看所有菜谱 | ❌ |
| 🔍 搜索菜谱 | 按关键词搜索 | ❌ |
| 📝 用户注册 | 创建新账号 | ❌ |
| 🔐 用户登录 | JWT 认证 | ❌ |
| ➕ 创建菜谱 | 添加新菜谱 | ✅ |
| 📋 我的菜谱 | 查看个人菜谱列表 | ✅ |
| 🚪 退出登录 | 清除 Token | ✅ |

### 🎭 用户界面特点

- **响应式设计**: 使用 Tailwind CSS，适配各种屏幕尺寸
- **加载状态**: 请求时显示 Loader 组件
- **错误提示**: 表单验证失败时显示错误信息
- **模态框**: 使用 PopupModal 创建菜谱
- **路由保护**: 未登录访问 `/my-recipes` 显示提示信息

---

## 🔧 配置说明

### 后端配置 (app/core/config.py)

```python
API_V1_STR = "/api/v1"                    # API 路径前缀
JWT_SECRET = "TEST_SECRET_DO_NOT_USE"     # JWT 密钥 (生产环境请更改!)
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 8 # Token 有效期 8 天
BACKEND_CORS_ORIGINS = [
    "http://localhost:3000",               # 允许的前端地址
]
SQLALCHEMY_DATABASE_URI = "sqlite:///example_part12.db"  # 数据库
```

### 前端环境变量 (.env)

```bash
REACT_APP_API_BASE_PATH=http://localhost:8001  # 后端 API 地址
SKIP_PREFLIGHT_CHECK=true                       # 跳过依赖检查
```

---

## 📚 技术栈总结

### 后端技术栈
- **FastAPI**: 高性能异步 Web 框架
- **SQLAlchemy**: ORM 数据库操作
- **Alembic**: 数据库迁移工具
- **Pydantic**: 数据验证和序列化
- **python-jose**: JWT 生成与验证
- **passlib**: 密码哈希 (bcrypt)

### 前端技术栈
- **React 18**: UI 框架
- **React Router v6**: 客户端路由
- **Axios**: HTTP 客户端
- **jwt-decode**: JWT 解码
- **Moment.js**: 时间处理
- **Tailwind CSS**: 样式框架

---

## 🐛 常见问题

### 1. CORS 错误
**问题**: 前端请求被阻止，提示 CORS 错误
**解决**: 
- 确保后端 `settings.BACKEND_CORS_ORIGINS` 包含前端地址
- 检查前端 `config.js` 的 API 地址是否正确

### 2. Token 过期
**问题**: 提示 "Your login session has expired"
**解决**: 重新登录即可，Token 默认 8 天有效期

### 3. 数据库未初始化
**问题**: 启动后端时报错找不到表
**解决**: 运行 `alembic upgrade head` 初始化数据库

### 4. 端口被占用
**问题**: 启动时提示端口已被使用
**解决**: 
- 后端: 修改 `uvicorn` 的 `--port` 参数
- 前端: 修改 `package.json` 的启动脚本或环境变量 `PORT`

---

## 📖 学习要点

通过这个项目，你将学会:
1. ✅ 如何设计前后端分离架构
2. ✅ 如何实现 JWT 认证机制
3. ✅ 如何处理 CORS 跨域问题
4. ✅ 如何使用 React Hooks 管理状态
5. ✅ 如何封装可复用的 API 客户端
6. ✅ 如何使用 Axios 拦截器自动添加认证头
7. ✅ 如何使用 localStorage 持久化用户状态
8. ✅ 如何设计 RESTful API
9. ✅ 如何使用 SQLAlchemy ORM 操作数据库
10. ✅ 如何使用 Alembic 管理数据库迁移

---

## 🎓 扩展建议

如果你想继续提升，可以尝试添加以下功能:
- 🔄 刷新 Token 机制 (Refresh Token)
- 🖼️ 图片上传功能
- 👤 用户个人资料编辑
- ⭐ 菜谱收藏和评分
- 💬 评论功能
- 🔔 消息通知
- 📱 移动端适配优化
- 🧪 单元测试和集成测试
- 🐳 Docker 部署

---

**Happy Coding! 🎉**
