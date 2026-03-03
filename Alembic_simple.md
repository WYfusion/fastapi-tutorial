概念速览
- alembic.ini 决定版本仓库位置、文件名模板、数据库连接。
- env.py 设置上下文，核心是 `target_metadata = Base.metadata`，Base 必须包含所有需要迁移的模型。
- migrations/versions 下是一条条升级脚本，版本号写入数据库的 alembic_version 表。

1) 初始化 (只做一次)
- 在项目根目录执行 `alembic init migrations`（目录名可自定义，常用 migrations）。
- 在 alembic.ini 设置文件名模板，方便按时间排序：`file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s`。
- Base 聚合示例（确保所有模型被导入）：
```python
from app.db.base_class import Base  # noqa
from app.models.user import User  # noqa
from app.models.recipe import Recipe  # noqa
```

2) env.py 关键配置
- 引入聚合后的 Base：`from app.db.base import Base`
- 设置 `target_metadata = Base.metadata`
- 若使用自定义 config.get_main_option("sqlalchemy.url")，确认与运行时数据库一致。

3) 日常流转
- 生成脚本：`alembic revision --autogenerate -m "添加了**"`
- 审核脚本：检查新增/删除/修改是否符合预期；重命名需改成 `op.alter_column`，避免 drop/create。
- 升级到最新：`alembic upgrade head`
- 回退一步：`alembic downgrade -1`（或指定 revision 前缀）。

4) 指定版本与相对移动
- 升级到指定 revision：`alembic upgrade <revision_id>`，例：`alembic upgrade bd31ef3fe973`。
- 从当前版本向前一步：`alembic upgrade +1`（注意是 upgrade 而非 downgrade）。
- 向后一步：`alembic downgrade -1`。
- 查看当前与历史：`alembic current`、`alembic history --verbose`。

5) 常用命令速查
- `alembic check` 校验模型与 DB 是否同步（SQLAlchemy 1.4+）。
- `alembic stamp head` 将现有 DB 标记为最新（谨慎使用，不执行 DDL）。
- `alembic upgrade head --sql > migration.sql` 离线导出 SQL 供审核。
- `alembic history --verbose` 全量历史；`alembic current` 当前版本。

6) 常见问题排查
- autogenerate 为空：确认 Base 已导入全部模型，且模型 metadata 与 env.py 中的 Base 一致。
- SQLite 限制：DDL 多为非事务，复杂操作（如 rename）可能需要手工改脚本。
- 已有老库想接管：用 `alembic stamp <revision>` 打标，然后再生成/升级。
- 相对移动写错：向前用 `upgrade +N`，向后用 `downgrade -N`。

7) **数据安全提示**
- `downgrade` 会执行脚本中的 drop/alter，可能直接删除表，数据无法自动恢复；`upgrade` 只重建结构，不会恢复旧数据。
- 生产环境慎用 `downgrade`，先备份：SQLite 可复制整个数据库文件；Postgres/MySQL 用逻辑/物理备份。
- 若需要回滚但保留数据，可先备份，再 `downgrade`，或用 `stamp` 改版本号而不执行 DDL（确保结构一致）。
- 涉及数据迁移（如列拆分合并）时，编写 `op.execute`/`sa.text` 进行数据搬迁并准备回滚脚本。

8) 当前案例：切换到 bd31ef3fe973
- 你现在停在 fa22a81039dd，想前进到 bd31ef3fe973（即 head）。
- 直接执行：`alembic upgrade bd31ef3fe973`（或简写 `alembic upgrade head`）。
- 若想逐步前进，可用：`alembic upgrade +1`。
- 升级后用 `alembic current` 确认应显示 bd31ef3fe973（head）。
