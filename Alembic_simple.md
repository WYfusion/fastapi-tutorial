1) 初始化 (只做一次)
- 在项目根目录执行 `alembic init migrations`，目录名建议 migrations。
- 在 alembic.ini 设置文件名模板，方便按时间排序：
    `file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s`

app/db/base.py 示例：
```python
from app.db.base_class import Base  # noqa
from app.models.user import User  # noqa
from app.models.recipe import Recipe  # noqa
```

2) env.py 关键配置
- Base中需要有所有需要注册的数据类的导入即可，不然程序在第一次跑的时候认不到那些被注册的数据类
- 引入聚合后的 Base：`from app.db.base import Base`
- 设置 `target_metadata = Base.metadata`
3) 日常流转
- 生成脚本：`alembic revision --autogenerate -m "add phone to user"`
- 审核脚本：检查新增/删除/修改是否符合预期（重命名需手工改成 alter_column）。
- 执行升级，正式的建表：`alembic upgrade head`
- 回退：`alembic downgrade -1` 或指定版本前缀。

4) 常用命令速查
- `alembic history --verbose` 查看历史
- `alembic current` 查看当前版本
- `alembic check` 校验模型与 DB 是否同步（支持 SQLAlchemy 1.4+）
- `alembic stamp head` 将现有 DB 标记为最新（谨慎使用）
- `alembic upgrade head --sql > migration.sql` 离线导出 SQL 给 DBA 审核
