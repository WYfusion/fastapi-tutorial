# 1. 导入SQLAlchemy核心组件
# create_engine: 用于创建数据库引擎
# sessionmaker: 用于创建会话工厂
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 2. 数据库连接URI配置
# SQLite数据库文件路径，example.db为数据库文件名
# sqlite:/// 表示使用SQLite数据库
SQLALCHEMY_DATABASE_URI = "sqlite:///example_part07_alembic.db"


# 3. 创建数据库引擎
# create_engine: 创建SQLAlchemy引擎实例
# SQLALCHEMY_DATABASE_URI: 数据库连接字符串
# connect_args={"check_same_thread": False}: SQLite特有参数，允许多线程访问
#    - SQLite默认不允许在不同线程间共享连接
#    - 此参数禁用线程检查，使FastAPI能够在不同线程中使用数据库连接
engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    # required for sqlite
    connect_args={"check_same_thread": False},
)

# 4. 创建会话工厂
# sessionmaker: 创建会话工厂类
# autocommit=False: 禁用自动提交，需要显式调用commit()
# autoflush=False: 禁用自动刷新，需要显式调用flush()
# bind=engine: 绑定到之前创建的数据库引擎
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
