# 1. 导入类型注解模块
# typing as t: 导入typing模块并重命名为t，简化后续使用
import typing as t

# 2. 导入SQLAlchemy声明式扩展
# as_declarative: 装饰器，用于创建声明式基类
# declared_attr: 装饰器，用于定义声明式属性
from sqlalchemy.ext.declarative import as_declarative, declared_attr


# 3. 类注册表，用于跟踪所有声明式类
# t.Dict: 类型注解，表示字典类型
class_registry: t.Dict = {}


# 4. 声明式基类装饰器
# @as_declarative: 将Base类标记为声明式基类
# class_registry=class_registry: 使用类注册表跟踪所有模型类
@as_declarative(class_registry=class_registry)
class Base:
    # 5. 基础属性定义
    # id: 主键属性，类型为任意类型
    id: t.Any
    # __name__: 类名属性，字符串类型
    __name__: str

    # 6. 自动生成表名的属性
    # @declared_attr: 声明式属性装饰器
    # 该方法会在每个继承Base的类中自动调用
    @declared_attr
    def __tablename__(cls) -> str:
        # 7. 返回小写的类名作为表名
        # cls.__name__: 获取类名
        # .lower(): 转换为小写
        return cls.__name__.lower()
