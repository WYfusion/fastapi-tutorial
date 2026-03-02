接入 Alembic 的核心在于建立 Alembic 与你代码中 Base 的连接。
按照以下步骤操作，即可实现根据你的 schemas（即 Base 模型）自动管理数据库。
第一步：初始化 Alembic
在你的项目根目录下运行：
```bash
alembic init migrations
```

这会创建一个 migrations/ 目录和一个 alembic.ini 文件。
第二步：配置 Alembic 连接你的数据库
修改根目录下的 alembic.ini 文件，找到 sqlalchemy.url，将其改为你的 SQLite 路径：
```ini
# 注意：如果是相对路径，建议使用绝对路径或确保运行路径正确
sqlalchemy.url = sqlite:///example_part07_alembic.db
```

第三步：关键步骤 - 修改 env.py 关联模型
这是最重要的一步。Alembic 需要知道你的 Base 在哪里，才能对比代码和数据库的差异。
打开 migrations/env.py，修改以下两处：
导入你的 Base：
```python
# 导入你定义的 Base
from app.db.base import Base  
```

设置元数据目标：
找到 target_metadata = None，修改为：
```python
target_metadata = Base.metadata
```

第四步：生成首次迁移脚本
现在，Alembic 已经可以“看到”你的模型了。运行以下命令让它自动检测：
```bash
alembic revision --autogenerate -m "Initial migration"
```

发生了什么？ Alembic 会扫描继承了 Base 的所有类（如 User, Recipe），并对比当前的 example_part07.db。
产生了什么？ 在 migrations/versions/ 下会生成一个类似 1a2b3c_initial_migration.py 的文件。
第五步：应用迁移到数据库
运行以下命令真正创建表：
```bash
alembic upgrade head
```

此时，你的 example_part07.db 文件才会被真正创建（或更新），里面会包含所有的表结构，以及一个叫 alembic_version 的表（用来记录当前数据库的版本）。
之后如何结合使用？（思路总结）
当你需要修改数据库（例如给 Recipe 增加一个 cooking_time 字段）时：
改代码：在你的 models.py（继承自 Base 的类）里增加字段。
存快照：运行 alembic revision --autogenerate -m "add cooking_time"。
刷数据库：运行 alembic upgrade head。