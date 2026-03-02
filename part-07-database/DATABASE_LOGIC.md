# 数据库逻辑实现详解

## 整体架构

该项目采用典型的三层架构模式：
1. **Models层**：负责数据库表结构定义（SQLAlchemy ORM模型）
2. **Schemas层**：负责数据验证和序列化（Pydantic模型）
3. **CRUD层**：负责数据库操作实现
4. **Dependencies层**：负责依赖注入（数据库会话管理）

## 详细实现流程

### 1. 数据库连接配置 (`db/session.py`)
```python
# 创建SQLite数据库引擎
engine = create_engine(SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False})

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

注意默认未创建像前面的recipe_data.py中的各个菜品的信息，所以打开是空白的，因此这里需要在/docs那里添加好到数据库中去，也可以用其他的方式实现，但是这个比较简单。

### 2. 基础模型类 (`db/base_class.py`)
```python
# 声明式基类，所有模型都继承自此基类
@as_declarative(class_registry=class_registry)
class Base:
    @declared_attr
    def __tablename__(cls) -> str:
        # 自动生成表名（类名小写）
        return cls.__name__.lower()
```

### 3. 数据模型定义 (`models/recipe.py`)
```python
class Recipe(Base):
    # 表列定义
    id = Column(Integer, primary_key=True, index=True)
    label = Column(String(256), nullable=False)
    url = Column(String(256), index=True, nullable=True)
    source = Column(String(256), nullable=True)
    submitter_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    submitter = relationship("User", back_populates="recipes")
```

### 4. 数据验证模型 (`schemas/recipe.py`)
```python
# 基础模型
class RecipeBase(BaseModel):
    label: str
    source: str
    url: HttpUrl

# 创建模型
class RecipeCreate(RecipeBase):
    submitter_id: int

# 数据库返回模型
class RecipeInDBBase(RecipeBase):
    id: int
    submitter_id: int
    
    class Config:
        orm_mode = True  # 支持从ORM对象读取数据
```

### 5. CRUD操作实现 (`crud/base.py`)
```python
class CRUDBase:
    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        # 根据ID查询单条记录
        return db.query(self.model).filter(self.model.id == id).first()
        
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        # 创建新记录
        obj_in_data = jsonable_encoder(obj_in)  # 转换为字典
        db_obj = self.model(**obj_in_data)      # 创建模型实例
        db.add(db_obj)                          # 添加到会话
        db.commit()                             # 提交事务
        db.refresh(db_obj)                      # 刷新获取数据库生成的值
        return db_obj
```

### 6. 数据库依赖项 (`deps.py`)
```python
def get_db() -> Generator:
    db = SessionLocal()     # 创建数据库会话
    try:
        yield db            # 提供给路由处理函数
    finally:
        db.close()          # 处理完成后关闭会话
```

### 7. 路由处理 (`main.py`)
```python
# 依赖注入方式获取数据库会话
def root(request: Request, db: Session = Depends(deps.get_db)):
    # 调用CRUD操作
    recipes = crud.recipe.get_multi(db=db, limit=10)
    return TEMPLATES.TemplateResponse(
        "index.html",
        {"request": request, "recipes": recipes}
    )
```

## 数据流向

1. **请求到达**：FastAPI接收到HTTP请求
2. **依赖注入**：通过`Depends(deps.get_db)`自动创建数据库会话
3. **业务处理**：调用相应的CRUD方法操作数据库
4. **数据验证**：使用Pydantic模型进行输入验证和输出序列化
5. **响应返回**：将结果返回给客户端

## 关键特性

1. **连接管理**：自动化的数据库会话管理，确保连接正确打开和关闭
2. **事务处理**：显式的事务控制（commit/rollback）
3. **数据验证**：使用Pydantic进行严格的输入验证
4. **类型安全**：全面的类型注解，提高代码可靠性
5. **ORM映射**：使用SQLAlchemy ORM简化数据库操作