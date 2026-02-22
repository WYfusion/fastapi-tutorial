from fastapi import FastAPI, APIRouter


app = FastAPI(title="Recipe API", openapi_url="/openapi.json")

api_router = APIRouter()


@api_router.get("/", status_code=200)
def root() -> dict:
    """
    Root GET

    1. `@api_router.get("/")` 是一个装饰器，用于将函数 `root` 绑定到路径 `/` 的 HTTP GET 请求上。
       - **路径 `/`**：表示根路径，访问 `http://localhost:8001/` 时会触发这个函数。
       - **`status_code=200`**：指定返回的 HTTP 状态码为 200，表示请求成功。

    2. **装饰器的作用**：
       - 装饰器会将函数 `root` 注册到 FastAPI 的路由系统中。
       - FastAPI 会在收到对应路径的 HTTP 请求时调用注册的函数。

    3. **FastAPI 源码解析**：
       - 装饰器内部调用了 `add_api_route` 方法，将路径、函数及其他参数注册到路由表中。
       - 源码示例：
         ```python
         def decorator(func: DecoratedCallable) -> DecoratedCallable:
             self.add_api_route(
                 path,
                 func,
                 response_model=response_model,
                 status_code=status_code,
                 tags=tags,
                 dependencies=dependencies,
                 summary=summary,
                 description=description,
                 response_description=response_description,
                 responses=responses,
                 deprecated=deprecated,
                 methods=methods,
                 operation_id=operation_id,
                 response_model_include=response_model_include,
                 response_model_exclude=response_model_exclude,
                 response_model_by_alias=response_model_by_alias,
                 response_model_exclude_unset=response_model_exclude_unset,
                 response_model_exclude_defaults=response_model_exclude_defaults,
                 response_model_exclude_none=response_model_exclude_none,
                 include_in_schema=include_in_schema,
                 response_class=response_class,
                 name=name,
                 callbacks=callbacks,
                 openapi_extra=openapi_extra,
                 generate_unique_id_function=generate_unique_id_function,
             )
             return func
         ```

    4. **执行流程**：
       - 当有 HTTP GET 请求到达路径 `/` 后，FastAPI 会调用注册的 `root` 函数。
       - 函数的返回值（如 `{"msg": "Hello, World!"}`）会作为 HTTP 响应返回给客户端。
    """
    return {"msg": "Hello, World!"}


app.include_router(api_router)
'''
include_router: 将 api_router 中定义的路由注册到主应用 app 中。

路由的含义：
- 路由（Route）是指 URL 路径与处理函数之间的映射关系。
- 例如：
  - 路径 `/` 表示根路径，对应的处理函数是 `root`。
  - 如果定义了路径 `/1/w/`，则表示访问 `http://localhost:8001/1/w/` 时会触发对应的处理函数。
- 路由的作用是根据客户端请求的路径，找到并调用对应的处理函数。

作用: 使得 api_router 中的所有路由都可以通过主应用访问。
例如：
- 如果在 `api_router` 中定义了路径 `/example`，那么通过 `app.include_router(api_router)` 后，访问 `http://localhost:8001/example` 就会触发对应的处理函数。
'''


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
