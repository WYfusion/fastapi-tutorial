# Part 10 - FastAPI JWT Auth 说明文档

本章实现了一个最小可用的 JWT 认证系统，核心能力包括：

- 用户注册（`/auth/signup`）
- 用户登录并签发 JWT（`/auth/login`）
- 使用 Bearer Token 获取当前用户（`/auth/me`）

---

## 1. 整体认证流程（先注册，再登录，再访问受保护接口）

推荐顺序：

1. **注册**：创建用户并存储 `hashed_password`
2. **登录**：验证邮箱 + 密码，返回 `access_token`
3. **授权访问**：请求头携带 `Authorization: Bearer <token>` 访问 `/auth/me`

可用一句话概括：

> Signup 创建账号 → Login 换取 JWT → 带 JWT 调用 Me 获取当前登录用户。

---

## 2. 关键文件与职责

- 路由层（接口定义）  
	[app/api/api_v1/endpoints/auth.py](app/api/api_v1/endpoints/auth.py)
- 认证核心（校验密码、签发 token）  
	[app/core/auth.py](app/core/auth.py)
- 依赖注入（解析 token、注入当前用户）  
	[app/api/deps.py](app/api/deps.py)
- 密码哈希与验证  
	[app/core/security.py](app/core/security.py)
- 用户 Schema（请求/响应结构）  
	[app/schemas/user.py](app/schemas/user.py)

---

## 3. 接口说明

基础前缀：`/api/v1/auth`

### 3.1 注册：`POST /signup`

请求体（JSON）：

```json
{
	"first_name": "wy",
	"surname": "fusion",
	"email": "fusion@163.com",
	"is_superuser": false,
	"password": "1"
}
```

逻辑：

1. 检查邮箱是否已存在。
2. 使用 `bcrypt` 对明文密码哈希。
3. 保存用户（数据库里存 `hashed_password`，不会返回明文密码）。
4. 返回用户公开字段（不含 `hashed_password`）。

返回码：

- `201 Created`：注册成功
- `400 Bad Request`：邮箱已存在

---

### 3.2 登录：`POST /login`

> 注意：登录使用 `OAuth2PasswordRequestForm`，即 **`application/x-www-form-urlencoded`**，不是 JSON。

表单字段：

- `username`：这里实际填 **邮箱**
- `password`：明文密码

示例（curl）：

```bash
curl -X POST "http://127.0.0.1:8001/api/v1/auth/login" \
	-H "Content-Type: application/x-www-form-urlencoded" \
	-d "username=fusion@163.com&password=1"
```

成功响应：

```json
{
	"access_token": "<JWT_TOKEN>",
	"token_type": "bearer"
}
```

返回码：

- `200 OK`：登录成功
- `400 Bad Request`：邮箱或密码错误
- `405 Method Not Allowed`：你用 `GET /login`（应使用 `POST`）

---

### 3.3 获取当前用户：`GET /me`

请求头必须携带：

```http
Authorization: Bearer <JWT_TOKEN>
```

示例（curl）：

```bash
curl -X GET "http://127.0.0.1:8001/api/v1/auth/me" \
	-H "Authorization: Bearer <JWT_TOKEN>"
```

成功响应示例：

```json
{
	"id": 1,
	"first_name": "wy",
	"surname": "fusion",
	"email": "fusion@163.com",
	"is_superuser": false
}
```

返回码：

- `200 OK`：token 有效且用户存在
- `401 Unauthorized`：未带 token、token 无效、token 过期、或用户不存在

---

## 4. 代码执行链路（按函数调用顺序）

### 4.1 Signup 链路

`POST /auth/signup`  
→ `create_user_signup()`  
→ 查询邮箱是否已存在  
→ `crud.user.create()`  
→ `get_password_hash(password)`  
→ 保存 `hashed_password`  
→ 返回 `schemas.User`

### 4.2 Login 链路

`POST /auth/login`  
→ `login()`  
→ `authenticate(email, password, db)`  
→ `verify_password(plain, hashed)`  
→ `create_access_token(sub=user.id)`  
→ 返回 `{access_token, token_type}`

### 4.3 Me 链路

`GET /auth/me`  
→ `Depends(get_current_user)`  
→ `oauth2_scheme` 从 Header 取 Bearer Token  
→ `jwt.decode(token, JWT_SECRET, algorithm)`  
→ 读取 payload 中的 `sub`（用户 id）  
→ 数据库查用户并返回

---

## 5. Swagger 文档中的正确操作

1. 打开 `/docs`
2. 点击右上角 **Authorize**，输入 `邮箱`+`密码`,不要点击绿色的logout登出！！！
3. 再执行 `GET /api/v1/auth/me`

如果你跳过第 4 步，`/me` 通常会是 `401`。

---

## 6. 常见问题排查

### 问题 A：`/me` 返回 401

检查点：

- 是否真的调用了 `POST /login`（不是 `GET /login`）
- 是否把 `access_token` 放到 `Authorization: Bearer ...`
- token 是否过期
- `JWT_SECRET` 是否在登录与解析时一致

### 问题 B：登录 400

检查点：

- 登录是 Form，不是 JSON
- `username` 填的是邮箱
- 密码是否正确

### 问题 C：`GET /auth/login` 报 405

原因：登录路由只定义了 `POST`。

---

## 7. 安全与实践建议

- 生产环境务必更换 `JWT_SECRET`，并放到环境变量。
- 缩短 token 过期时间，并配合刷新机制（Refresh Token）。
- 给登录接口增加限流、防爆破与审计日志。
- 注册/登录错误信息建议避免暴露过多细节。

---

## 8. 一次完整示例（从零到 me）

1. `POST /signup` 注册账号。
2. `POST /login` 获取 token。
3. 带 `Authorization: Bearer <token>` 调用 `GET /me`。
4. 收到当前用户信息，即认证链路完成。

---

## 9. access_token 的作用

`access_token` 是一种短期有效的令牌，用于标识用户的身份并授权访问受保护的资源。

### 9.1 作用

1. **身份验证**：
   - `access_token` 是用户登录成功后生成的唯一标识。
   - 服务端通过解析 `access_token` 确认用户身份。

2. **授权访问**：
   - 用户携带 `access_token` 访问受保护的接口（如 `/me`）。
   - 服务端验证 `access_token` 是否有效后，允许用户访问资源。

3. **无状态认证**：
   - `access_token` 是无状态的，服务端无需存储用户的登录状态。
   - 所有认证信息都包含在 `access_token` 的加密内容中。

### 9.2 生成方式

`access_token` 是通过以下步骤生成的：

1. 用户登录时，调用 `create_access_token` 函数。
2. 函数内部调用 `_create_token`，生成一个 JWT（JSON Web Token）。
3. JWT 的内容包括：
   - `sub`：用户 ID（标识用户身份）
   - `iat`：签发时间
   - `exp`：过期时间
   - `type`：令牌类型（如 `access_token`）
4. 使用 `JWT_SECRET` 和 `HS256` 算法对内容进行加密。

示例生成的 `access_token`：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzX3Rva2VuIiwiZXhwIjoxNzcyNTQwMDAwLCJpYXQiOjE3NzI0NTM2MDAsInN1YiI6IjEifQ.abc123",
  "token_type": "bearer"
}
```

### 9.3 使用场景

1. **携带 `access_token` 访问受保护接口**：
   - 请求头中添加：
     ```http
     Authorization: Bearer <access_token>
     ```
   - 服务端通过 `get_current_user` 解码 `access_token`，验证用户身份。

2. **短期有效性**：
   - `access_token` 的有效期较短（如 8 小时）。
   - 如果过期，用户需要重新登录获取新的 `access_token`。

3. **无状态认证**：
   - 适合分布式系统，服务端无需存储用户会话。

### 9.4 安全注意事项

1. **保护 `access_token`**：
   - 不要在 URL 中传递 `access_token`，避免泄露。
   - 仅通过 HTTPS 传输，防止中间人攻击。

2. **设置合理的过期时间**：
   - 避免令牌长期有效，增加安全风险。

3. **刷新机制**：
   - 配合 `refresh_token` 实现令牌刷新，减少频繁登录。

---

