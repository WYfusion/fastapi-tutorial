from typing import Generator

# 1. 导入数据库会话工厂
# SessionLocal: SQLAlchemy会话工厂，用于创建数据库会话
from app.db.session import SessionLocal


# 2. 数据库依赖项函数
# 返回类型为Generator，支持依赖注入系统使用yield语法
def get_db() -> Generator:
    # 3. 创建数据库会话实例
    # SessionLocal(): 调用会话工厂创建新的数据库会话
    db = SessionLocal()
    # 4. 设置当前用户ID（此处为None，可在实际应用中设置）
    db.current_user_id = None
    try:
        # 5. 通过yield将数据库会话传递给路由处理函数
        # 依赖注入系统会在此处暂停，等待路由处理函数执行完毕
        yield db
    finally:
        # 6. 路由处理函数执行完毕后，关闭数据库会话
        # 确保数据库连接被正确释放，避免连接泄漏
        db.close()
