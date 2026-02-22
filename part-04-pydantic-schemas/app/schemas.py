from pydantic import BaseModel, HttpUrl

from typing import Sequence

'''
pydantic 的作用是用于数据验证和序列化。
它通过定义数据模型（如 Recipe 和 RecipeSearchResults）来确保输入和输出的数据符合预期的格式和约束。
'''


class Recipe(BaseModel):
    id: int
    label: str
    source: str
    url: HttpUrl


class RecipeSearchResults(BaseModel):
    '''
    这里的 `results` 字段是一个包含 `Recipe` 对象的序列（Sequence[Recipe]），表示搜索结果中的多个食谱。
    '''
    results: Sequence[Recipe]


class RecipeCreate(BaseModel):
    label: str
    source: str
    url: HttpUrl
    submitter_id: int
