这份指南帮助你落地一套生产可用的 Alembic 迁移方案。

1) 初始化 (只做一次)
- 在项目根目录执行 `alembic init migrations`，目录名建议 migrations。
- 在 alembic.ini 设置文件名模板，方便按时间排序：
    `file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s`

2) 必要结构
```
.
├── alembic.ini
├── migrations/
│   ├── env.py        # 链接模型与数据库
│   └── versions/     # 历史脚本
└── app/
        ├── db/
        │   ├── base_class.py
        │   ├── base.py   # 导入 Base + 所有模型
        │   └── session.py
        └── models/
                ├── user.py
                └── recipe.py
```
app/db/base.py 示例：
```python
from app.db.base_class import Base  # noqa
from app.models.user import User  # noqa
from app.models.recipe import Recipe  # noqa
```

3) env.py 关键配置
- 引入聚合后的 Base：`from app.db.base import Base`
- 设置 `target_metadata = Base.metadata`
- URL 建议动态读取 settings 以避免硬编码：
    ```python
    from app.core.config import settings
    def get_url():
            return str(settings.SQLALCHEMY_DATABASE_URI)
    ```

4) 日常流转
- 生成脚本：`alembic revision --autogenerate -m "add phone to user"`
- 审核脚本：检查新增/删除/修改是否符合预期（重命名需手工改成 alter_column）。
- 执行升级，正式的建表：`alembic upgrade head`
- 回退：`alembic downgrade -1` 或指定版本前缀。

5) 生产落地建议
- 同步 URL：确保 alembic.ini/sqlalchemy.url 与应用的 settings 一致（或统一走 env.py 动态 URL）。
- 启动前迁移：在 run.sh/Entrypoint 加 `alembic upgrade head`，失败即退出。
- 只升不降：生产环境默认只允许 upgrade；若需降级，先做备份并走审批。
- 备份与锁：升级前备份数据库；在高并发场景可在 DB 层加维护窗口/锁，避免长事务写入。
- 可重复执行：迁移脚本保持幂等（尽量 avoid 手写 DDL 依赖现存状态）。
- 审核重命名：autogenerate 对重命名不敏感，手工改为 `op.alter_column` 避免数据丢失。
- 健康检查：上线后运行 `alembic current` 与 `alembic history --verbose` 校验版本。

6) 常用命令速查
- `alembic history --verbose` 查看历史
- `alembic current` 查看当前版本
- `alembic check` 校验模型与 DB 是否同步（支持 SQLAlchemy 1.4+）
- `alembic stamp head` 将现有 DB 标记为最新（谨慎使用）
- `alembic upgrade head --sql > migration.sql` 离线导出 SQL 给 DBA 审核
