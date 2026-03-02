# 1. 导入SQLAlchemy核心组件
# Column: 用于定义表列
# Integer, String: SQL数据类型
# ForeignKey: 外键约束
from sqlalchemy import Column, Integer, String, ForeignKey
# relationship: 用于定义表间关系
from sqlalchemy.orm import relationship

# 2. 导入基础模型类
from app.db.base_class import Base


# 3. 定义Recipe模型类，继承自Base
# 该类将被SQLAlchemy映射为数据库表
class Recipe(Base):
    # 4. 定义表列
    # id: 主键列，整数类型，自动递增，建立索引
    id = Column(Integer, primary_key=True, index=True)
    # label: 菜谱标签列，字符串类型，最大长度256，不允许为空
    label = Column(String(256), nullable=False)
    # url: 菜谱链接列，字符串类型，最大长度256，允许为空，建立索引
    url = Column(String(256), index=True, nullable=True)
    # source: 来源列，字符串类型，最大长度256，允许为空
    source = Column(String(256), nullable=True)
    # submitter_id: 提交者ID列，整数类型，外键引用"user.id"，允许为空
    submitter_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    # submitter: 关系属性，关联到User模型
    # back_populates="recipes": 与User模型的recipes属性建立双向关系
    submitter = relationship("User", back_populates="recipes")
