# 1. 导入类型注解和相关模块
# Generic: 用于创建泛型类
# TypeVar: 用于定义类型变量
# jsonable_encoder: FastAPI工具函数，将Pydantic模型转换为可JSON序列化的字典
# BaseModel: Pydantic基础模型类
# Session: SQLAlchemy会话类
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

# 2. 导入基础模型类
from app.db.base_class import Base

# 3. 定义类型变量，用于泛型约束
# ModelType: SQLAlchemy模型类型，继承自Base
# CreateSchemaType: 创建用Pydantic模型类型，继承自BaseModel
# UpdateSchemaType: 更新用Pydantic模型类型，继承自BaseModel
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


# 4. 定义基础CRUD类，使用泛型支持不同类型的操作
class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    # 5. 初始化方法，接收模型类作为参数
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        # 6. 存储模型类引用，供后续操作使用
        self.model = model

    # 7. 根据ID获取单个记录的方法
    # db: Session - 数据库会话
    # id: Any - 记录ID
    # 返回值: Optional[ModelType] - 找到的记录或None
    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        # 8. 使用SQLAlchemy查询接口
        # db.query(self.model): 创建针对指定模型的查询
        # filter(self.model.id == id): 添加过滤条件，根据ID筛选
        # first(): 获取第一条匹配记录，如果没有则返回None
        return db.query(self.model).filter(self.model.id == id).first()

    # 9. 获取多个记录的方法
    # db: Session - 数据库会话
    # skip: int = 0 - 跳过的记录数（偏移量），默认0
    # limit: int = 100 - 返回的最大记录数，默认100
    # 返回值: List[ModelType] - 记录列表
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        # 10. 使用SQLAlchemy查询接口实现分页
        # db.query(self.model): 创建针对指定模型的查询
        # offset(skip): 跳过指定数量的前面一定数量的记录
        # limit(limit): 限制最多返回记录数量
        # all(): 获取所有匹配记录
        # 
        return db.query(self.model).offset(skip).limit(limit).all()

    # 11. 创建新记录的方法
    # db: Session - 数据库会话
    # obj_in: CreateSchemaType - 创建数据（Pydantic模型）
    # 返回值: ModelType - 创建的记录
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        # 12. 将Pydantic模型转换为可JSON序列化的字典
        # jsonable_encoder: FastAPI提供的工具函数
        # 将Pydantic模型转换为普通Python字典
        obj_in_data = jsonable_encoder(obj_in)
        
        # 13. 创建数据库模型实例
        # self.model(**obj_in_data): 使用字典解包创建模型实例
        # type: ignore: 忽略类型检查警告
        db_obj = self.model(**obj_in_data)  # type: ignore
        
        # 14. 将新对象添加到数据库会话
        # db.add(db_obj): 将对象标记为待插入
        db.add(db_obj)
        
        # 15. 提交事务，将更改保存到数据库
        # db.commit(): 提交当前事务
        db.commit()
        
        # 16. 刷新对象，获取数据库生成的字段值（如自增ID）
        # db.refresh(db_obj): 从数据库重新加载对象状态
        db.refresh(db_obj)
        
        # 17. 返回创建的记录
        return db_obj

    # 18. 更新记录的方法
    # db: Session - 数据库会话
    # db_obj: ModelType - 要更新的数据库对象
    # obj_in: Union[UpdateSchemaType, Dict[str, Any]] - 更新数据
    # 返回值: ModelType - 更新后的记录
    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        # 19. 将数据库对象编码为可JSON序列化的字典
        obj_data = jsonable_encoder(db_obj)
        
        # 20. 处理不同类型的更新数据
        # 如果是字典类型，直接使用
        if isinstance(obj_in, dict):
            update_data = obj_in
        # 如果是Pydantic模型，转换为字典并排除未设置的字段
        else:
            update_data = obj_in.dict(exclude_unset=True)
            
        # 21. 遍历对象字段，更新有变化的字段
        for field in obj_data:
            # 22. 如果更新数据中包含该字段，则更新
            if field in update_data:
                # setattr: 设置对象属性值
                setattr(db_obj, field, update_data[field])
                
        # 23. 将更新后的对象添加到数据库会话
        db.add(db_obj)
        
        # 24. 提交事务，保存更改
        db.commit()
        
        # 25. 刷新对象，同步数据库状态
        db.refresh(db_obj)
        
        # 26. 返回更新后的记录
        return db_obj

    # 27. 删除记录的方法
    # db: Session - 数据库会话
    # id: int - 要删除记录的ID
    # 返回值: ModelType - 删除的记录
    def remove(self, db: Session, *, id: int) -> ModelType:
        # 28. 根据ID获取要删除的对象
        # db.query(self.model).get(id): 根据主键获取记录
        obj = db.query(self.model).get(id)
        
        # 29. 从数据库会话中删除对象
        # db.delete(obj): 标记对象为待删除
        db.delete(obj)
        
        # 30. 提交事务，执行删除操作
        db.commit()
        
        # 31. 返回删除的记录
        return obj
