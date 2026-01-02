# 基础镜像
FROM python:3.10-slim
WORKDIR /app

# 安装系统依赖
RUN apt update && apt install -y gcc libmariadb-dev-compat libmariadb-dev

# 复制并安装 Python 依赖
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 复制代码
COPY backend/ .

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]