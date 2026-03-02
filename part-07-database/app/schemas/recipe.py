# 1. 导入Pydantic核心组件
# BaseModel: Pydantic基础模型类
# HttpUrl: URL类型验证器
from pydantic import BaseModel, ConfigDict, HttpUrl

# 2. 导入类型注解
# Sequence: 序列类型注解
from typing import Sequence


# 3. 定义基础菜谱模型
# 继承自BaseModel，提供基本的菜谱属性
class RecipeBase(BaseModel):
    # label: 菜谱标签，字符串类型
    label: str
    # source: 来源，字符串类型
    source: str
    # url: URL链接，使用HttpUrl类型进行验证
    url: HttpUrl


# 4. 定义创建菜谱模型
# 继承自RecipeBase，添加创建所需的额外字段
class RecipeCreate(RecipeBase):
    # 重复定义字段以确保类型正确性
    label: str
    source: str
    url: HttpUrl
    # submitter_id: 提交者ID，整数类型
    submitter_id: int


# 5. 定义更新菜谱模型
# 继承自RecipeBase，只包含需要更新的字段
class RecipeUpdate(RecipeBase):
    # label: 菜谱标签，字符串类型
    label: str


# 6. 定义数据库基础菜谱模型
# Properties shared by models stored in DB
class RecipeInDBBase(RecipeBase):
    # id: 菜谱ID，整数类型
    id: int
    # submitter_id: 提交者ID，整数类型
    submitter_id: int
    # 7. Pydantic模型配置（from_attributes替代V1的orm_mode）
    class Config:
        from_attributes = True

# 8. 定义返回给客户端的菜谱模型
# Properties to return to client
class Recipe(RecipeInDBBase):
    # 继承RecipeInDBBase的所有属性
    # 不添加额外属性，直接pass
    pass


# 9. 定义存储在数据库中的菜谱模型
# Properties properties stored in DB
class RecipeInDB(RecipeInDBBase):
    # 继承RecipeInDBBase的所有属性
    # 不添加额外属性，直接pass
    pass


# 10. 定义菜谱搜索结果模型
class RecipeSearchResults(BaseModel):
    # results: 搜索结果列表，Sequence[Recipe]类型
    # Sequence是抽象基类，支持列表、元组等序列类型
    results: Sequence[Recipe]
