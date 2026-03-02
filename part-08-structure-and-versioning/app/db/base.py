# 为了方便 Alembic 和 FastAPI，通常会创建一个“聚合导入文件”（例如 app/db/base.py），内容如下
# 然后在 Alembic 的 env.py 中，你导入的是这个聚合后的文件：from app.db.base import Base。这样，通过一次导入，链式地触发了所有模型的注册。
from app.db.base_class import Base  # noqa
from app.models.user import User  # noqa
from app.models.recipe import Recipe  # noqa
'''
可以把 Base.metadata 想象成一个名单。
每一个模型类（如 Recipe）就像一个学生。
“导入”动作就像是学生进教室报到。
如果学生（代码）没进教室（没被导入），老师（Alembic/SQLAlchemy）点名（检查 Metadata）时就找不到人。
这就是为什么在 FastAPI 项目中，我们通常有一个专门的文件（通常是 app/db/base.py）来集中导入所有的模型。
'''

