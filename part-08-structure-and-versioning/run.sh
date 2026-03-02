#!/bin/bash

# 1. 强制激活 Conda 环境
# 注意：在脚本中激活 Conda 需要先 source conda.sh
# 这里的路径通常是你的 Conda 安装路径，请根据实际情况微调
##  git bash 中的路径示例
CONDA_PATH=$(conda info --base)
source "$CONDA_PATH/etc/profile.d/conda.sh"
conda activate fastapi310

# 2. 设置变量

export APP_MODULE=${APP_MODULE:-app.main:app}
# 含义：设置环境变量 APP_MODULE。
# 语法逻辑：${变量-默认值} 表示如果系统之前没定义过 APP_MODULE，就用 app.main:app。
# 作用：告诉 Uvicorn 去哪里找 FastAPI 实例。app.main 对应你的 app/main.py 文件，:app 是文件里的变量名。
export HOST=${HOST:-0.0.0.0}
# 含义：设置监听地址。0.0.0.0 表示允许局域网内所有 IP 访问（如果在服务器上跑，这是必须的）。
export PORT=${PORT:-8001}

# 3. 打印当前使用的 Python 路径（用于验证是否切换成功）
echo "正在使用环境: $CONDA_DEFAULT_ENV"
echo "Python 路径: $(which python)"

# 4. 执行 Uvicorn
exec uvicorn --reload --host "$HOST" --port "$PORT" "$APP_MODULE"

# exec：用新进程替换当前 shell 进程（更节省资源，且能正确接收停止信号）。
# uvicorn：高性能的 ASGI 服务器，FastAPI 的“发动机”。
# --reload：热重载模式（开发必备）。你改动代码保存后服务会自动重启,无需手动重启。
# 作用：最终执行的完整命令等同于：uvicorn --reload --host 0.0.0.0 --port 8001 app.main:app。
