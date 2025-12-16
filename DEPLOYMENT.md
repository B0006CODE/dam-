# Smart Water 项目 Docker 部署指南

> 本文档提供 Smart Water 智能水利问答平台的完整 Docker 部署说明

## 📋 目录

- [系统要求](#系统要求)
- [快速启动](#快速启动)
- [服务架构](#服务架构)
- [环境变量配置](#环境变量配置)
- [服务说明](#服务说明)
- [数据持久化](#数据持久化)
- [GPU 服务配置](#gpu-服务配置可选)
- [常见问题](#常见问题)
- [服务管理](#服务管理)

## 🎯 系统要求

### 基础要求

- **Docker**: 版本 20.10 或更高
- **Docker Compose**: 版本 2.0 或更高
- **系统内存**: 至少 8GB RAM（推荐 16GB）
- **磁盘空间**: 至少 20GB 可用空间（用于镜像和数据）

### GPU 服务要求（可选）

如果需要使用 MinerU OCR 或 PaddleX 文档处理服务：

- **NVIDIA GPU**: 支持 CUDA 的显卡
- **NVIDIA Docker Runtime**: nvidia-container-toolkit
- **显存**: 至少 6GB

检查 Docker 和 Docker Compose 版本：

```bash
docker --version
docker compose version
```

## 🚀 快速启动

### 1. 克隆项目（如果还没有）

```bash
git clone <repository-url>
cd smart-water
```

### 2. 配置环境变量

复制环境变量模板并编辑：

```bash
# Windows PowerShell
copy .env.template .env

# Linux/macOS
cp .env.template .env
```

编辑 `.env` 文件，配置必要的变量（详见[环境变量配置](#环境变量配置)）。

**最小必要配置**（至少配置一个 LLM API）：

```env
# 推荐使用硅基流动免费服务
SILICONFLOW_API_KEY=your_api_key_here

# 或者使用其他 LLM 提供商
# OPENAI_API_KEY=your_openai_key
# DEEPSEEK_API_KEY=your_deepseek_key

# 管理员账号（可选，但推荐设置）
YUXI_SUPER_ADMIN_NAME=admin
YUXI_SUPER_ADMIN_PASSWORD=your_secure_password
```

### 3. 启动服务

```bash
# 启动所有基础服务（不包含 GPU 服务）
docker compose up --build -d

# 或者启动包含 GPU 服务的完整配置
docker compose --profile all up --build -d
```

> **⏱️ 首次启动时间**
> 
> 首次启动需要下载镜像、构建自定义镜像并初始化数据库，整个过程可能需要 **5-10 分钟**。
> 请耐心等待所有服务的健康检查通过。

### 4. 检查服务状态

```bash
# 查看所有服务状态
docker compose ps

# 查看服务日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f api
docker compose logs -f web
```

所有服务应该显示为 `Up (healthy)` 状态。

### 5. 访问服务

服务启动成功后，可以通过以下地址访问：

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端界面 | http://localhost:5173 | 主应用界面 |
| API 文档 | http://localhost:5050/docs | FastAPI 交互式文档 |
| Neo4j 浏览器 | http://localhost:7474 | 图数据库管理界面 |
| MinIO 控制台 | http://localhost:9001 | 对象存储管理界面 |

## 🏗️ 服务架构

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户访问层                              │
├─────────────────────────────────────────────────────────────┤
│  Web 前端 (Vue 3 + Vite)                    :5173           │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP API
┌──────────────────────▼──────────────────────────────────────┐
│  API 服务 (FastAPI + Python)                :5050           │
└──┬────────┬─────────┬─────────┬────────────────────────────┘
   │        │         │         │
   │        │         │         └─────────────┐
   │        │         │                       │
   ▼        ▼         ▼                       ▼
┌─────┐ ┌──────┐ ┌────────┐          ┌──────────────┐
│Neo4j│ │Milvus│ │ MinIO  │          │ GPU Services │
│:7474│ │:19530│ │ :9000  │          │  (Optional)  │
│:7687│ │      │ │ :9001  │          ├──────────────┤
└─────┘ └──┬───┘ └────────┘          │MinerU  :30000│
           │                          │PaddleX :8080 │
           ▼                          └──────────────┘
        ┌──────┐
        │ Etcd │
        │:2379 │
        └──────┘
```

### 核心服务

#### 前端服务 (web)
- **技术栈**: Vue 3 + Vite + Pnpm
- **端口**: 5173
- **功能**: 提供 Web 用户界面

#### 后端服务 (api)
- **技术栈**: FastAPI + Python 3.12 + UV
- **端口**: 5050
- **功能**: 提供 RESTful API 接口

#### 图数据库 (graph)
- **技术**: Neo4j 5.26
- **端口**: 7474 (HTTP), 7687 (Bolt)
- **功能**: 存储知识图谱数据
- **默认账号**: neo4j / 0123456789

#### 向量数据库 (milvus)
- **技术**: Milvus 2.5.6
- **端口**: 19530 (API), 9091 (Metrics)
- **功能**: 存储和检索向量嵌入

#### 对象存储 (minio)
- **技术**: MinIO
- **端口**: 9000 (API), 9001 (Console)
- **功能**: 存储文件和对象
- **默认账号**: minioadmin / minioadmin

#### 配置中心 (etcd)
- **技术**: Etcd v3.5.5
- **端口**: 2379
- **功能**: Milvus 的配置管理

### GPU 服务（可选）

#### MinerU OCR (mineru)
- **功能**: 文档 OCR 识别服务
- **端口**: 30000
- **启动方式**: `docker compose --profile all up -d`
- **要求**: NVIDIA GPU

#### PaddleX 文档处理 (paddlex)
- **功能**: 高级文档处理服务
- **端口**: 8080
- **启动方式**: `docker compose --profile all up -d`
- **要求**: NVIDIA GPU

## ⚙️ 环境变量配置

### LLM 配置（必需）

至少配置一个 LLM 提供商的 API Key：

```env
# 推荐：硅基流动（免费额度）
SILICONFLOW_API_KEY=sk-xxxxxxxxxxxx

# 或者其他提供商
OPENAI_API_KEY=sk-xxxxxxxxxxxx
OPENAI_API_BASE=https://api.openai.com/v1  # 可选，自定义 API 地址

ZHIPUAI_API_KEY=xxxxxxxxxxxx
DASHSCOPE_API_KEY=xxxxxxxxxxxx
DEEPSEEK_API_KEY=xxxxxxxxxxxx
ARK_API_KEY=xxxxxxxxxxxx
TOGETHER_API_KEY=xxxxxxxxxxxx
```

### 模型路径配置

```env
# 模型存储目录（宿主机路径）
MODEL_DIR=./models

# 数据存储目录
SAVE_DIR=./saves
```

### 数据库配置

Docker Compose 已配置默认值，通常无需修改：

```env
# Neo4j 配置（已在 docker-compose.yml 中配置）
NEO4J_URI=bolt://graph:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=0123456789

# Milvus 配置（已在 docker-compose.yml 中配置）
MILVUS_URI=http://milvus:19530

# MinIO 配置（已在 docker-compose.yml 中配置）
MINIO_URI=http://milvus-minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

### 系统管理员配置

```env
# 超级管理员账号
YUXI_SUPER_ADMIN_NAME=admin
YUXI_SUPER_ADMIN_PASSWORD=your_secure_password
```

### 其他可选配置

```env
# 功能服务
TAVILY_API_KEY=xxxxxxxxxxxx  # 网络搜索服务

# MinerU OCR
MINERU_API_KEY=xxxxxxxxxxxx  # 如果需要

# MySQL 配置（如果使用）
MYSQL_HOST=192.168.1.100
MYSQL_USER=username
MYSQL_PASSWORD=your_secure_password
MYSQL_DATABASE=database_name
MYSQL_PORT=3306
MYSQL_CHARSET=utf8mb4

# LightRAG 配置
LIGHTRAG_LLM_PROVIDER=siliconflow
LIGHTRAG_LLM_NAME=Qwen/Qwen2.5-7B-Instruct
```

## 💾 数据持久化

所有服务数据都存储在 `./docker/volumes/` 目录下，确保数据在容器重启后不会丢失。

### 数据目录结构

```
docker/volumes/
├── neo4j/
│   ├── data/          # Neo4j 数据库数据
│   └── logs/          # Neo4j 日志
├── milvus/
│   ├── etcd/          # Etcd 数据
│   ├── minio/         # MinIO 对象存储
│   ├── minio_config/  # MinIO 配置
│   ├── milvus/        # Milvus 向量数据
│   └── logs/          # Milvus 日志
└── paddlex/           # PaddleX 数据（如果使用）
```

### 备份数据

```bash
# 停止服务
docker compose down

# 备份整个 volumes 目录
tar -czf yuxi-know-backup-$(date +%Y%m%d).tar.gz docker/volumes/

# 或者使用 zip (Windows)
Compress-Archive -Path .\docker\volumes -DestinationPath "yuxi-know-backup-$(Get-Date -Format yyyyMMdd).zip"
```

### 恢复数据

```bash
# 停止并删除现有容器
docker compose down

# 恢复备份
tar -xzf yuxi-know-backup-20241208.tar.gz

# 或者使用 unzip (Windows)
Expand-Archive -Path yuxi-know-backup-20241208.zip -DestinationPath .

# 重新启动服务
docker compose up -d
```

### 清除所有数据

```bash
# ⚠️ 警告：这将删除所有数据！
docker compose down -v

# 或者手动删除 volumes 目录
rm -rf docker/volumes/
# Windows: Remove-Item -Recurse -Force .\docker\volumes\
```

## 🎮 GPU 服务配置（可选）

### 前置要求

#### 1. 安装 NVIDIA 驱动

确保已安装最新的 NVIDIA 显卡驱动。

验证：
```bash
nvidia-smi
```

#### 2. 安装 NVIDIA Container Toolkit

**Ubuntu/Debian:**
```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

**Windows with WSL2:**
确保使用最新版本的 Docker Desktop 并启用 WSL2 backend，NVIDIA Container Toolkit 已默认集成。

验证：
```bash
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

### 启动 GPU 服务

```bash
# 启动包含 GPU 服务的完整配置
docker compose --profile all up --build -d

# 检查 GPU 服务状态
docker compose ps mineru
docker compose ps paddlex

# 查看 GPU 服务日志
docker compose logs -f mineru
docker compose logs -f paddlex
```

### GPU 资源分配

默认配置中，MinerU 和 PaddleX 都使用 GPU 0。如果有多个 GPU，可以在 `docker-compose.yml` 中修改设备分配：

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          device_ids: ["0"]  # 修改为其他 GPU ID，如 "1", "2"
          capabilities: [gpu]
```

## 🔧 服务管理

### 启动服务

```bash
# 启动所有基础服务
docker compose up -d

# 启动特定服务
docker compose up -d api web

# 启动并查看日志
docker compose up

# 启动包含 GPU 服务
docker compose --profile all up -d
```

### 停止服务

```bash
# 停止所有服务
docker compose down

# 停止特定服务
docker compose stop api

# 停止并删除数据卷（⚠️ 会删除所有数据）
docker compose down -v
```

### 重启服务

```bash
# 重启所有服务
docker compose restart

# 重启特定服务
docker compose restart api
docker compose restart web
```

### 查看日志

```bash
# 查看所有服务日志
docker compose logs

# 实时跟踪日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f api

# 查看最近 100 行日志
docker compose logs --tail=100 api
```

### 更新服务

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker compose up --build -d

# 或者只重新构建特定服务
docker compose up --build -d api
docker compose up --build -d web
```

### 进入容器

```bash
# 进入 API 容器
docker compose exec api bash

# 进入 Web 容器
docker compose exec web sh

# 进入 Neo4j 容器
docker compose exec graph bash

# 执行一次性命令
docker compose exec api uv run python -c "print('Hello')"
```

## ❓ 常见问题

### 1. 服务启动失败

**问题**: 某个服务一直重启或健康检查失败

**排查步骤**:
```bash
# 1. 查看服务状态
docker compose ps

# 2. 查看服务日志
docker compose logs <service-name>

# 3. 检查端口占用
# Windows
netstat -ano | findstr :5050
netstat -ano | findstr :5173

# Linux
sudo lsof -i :5050
sudo lsof -i :5173

# 4. 检查磁盘空间
df -h  # Linux
Get-PSDrive  # Windows PowerShell
```

### 2. API 服务连接数据库失败

**问题**: API 日志显示无法连接 Neo4j 或 Milvus

**解决方案**:
- 确保数据库服务已启动并健康：`docker compose ps`
- 等待数据库完成初始化（Neo4j 首次启动需要 1-2 分钟）
- 检查网络连接：`docker compose exec api ping graph`

### 3. 前端无法访问 API

**问题**: 浏览器控制台显示 API 请求失败

**解决方案**:
- 检查 API 服务是否正常运行：`docker compose logs api`
- 访问 http://localhost:5050/docs 确认 API 可访问
- 检查浏览器控制台的实际请求地址
- 确认防火墙没有阻止 5050 端口

### 4. GPU 服务无法启动

**问题**: MinerU 或 PaddleX 启动失败

**排查步骤**:
```bash
# 1. 检查 NVIDIA 驱动
nvidia-smi

# 2. 检查 Docker GPU 支持
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# 3. 查看服务日志
docker compose logs mineru
docker compose logs paddlex

# 4. 检查 CUDA 版本兼容性
```

### 5. 内存不足

**问题**: 服务因内存不足被 OOM Killer 终止

**解决方案**:
- 增加系统可用内存
- 在 `docker-compose.yml` 中为服务添加内存限制：
  ```yaml
  deploy:
    resources:
      limits:
        memory: 2G
  ```
- 减少同时运行的服务（不启动 GPU 服务）

### 6. 镜像拉取失败

**问题**: 网络原因导致 Docker 镜像下载失败

**解决方案**:
```bash
# 使用镜像加速器（中国大陆用户）
# 编辑 /etc/docker/daemon.json (Linux) 或 Docker Desktop 设置 (Windows)
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://mirror.ccs.tencentyun.com"
  ]
}

# 重启 Docker 服务
sudo systemctl restart docker  # Linux
# Windows: 重启 Docker Desktop
```

### 7. 端口已被占用

**问题**: 启动时提示端口已被占用

**解决方案**:
- 停止占用端口的其他程序
- 或修改 `docker-compose.yml` 中的端口映射：
  ```yaml
  ports:
    - "15173:5173"  # 使用其他端口
  ```

### 8. 环境变量未生效

**问题**: 配置的环境变量没有生效

**检查步骤**:
```bash
# 1. 确认 .env 文件存在且格式正确
cat .env

# 2. 检查容器内的环境变量
docker compose exec api env | grep API_KEY

# 3. 重新启动服务
docker compose down
docker compose up -d
```

### 9. 数据丢失

**问题**: 容器重启后数据丢失

**原因**: 可能使用了 `docker compose down -v` 删除了数据卷

**预防措施**:
- 定期备份 `docker/volumes/` 目录
- 避免使用 `-v` 参数，除非确实要清除数据
- 使用版本控制管理配置文件（但不要提交 `.env` 和 `volumes/`）

### 10. 首次启动很慢

**原因**: 正常现象，首次启动需要：
- 下载 Docker 镜像（数 GB）
- 构建自定义镜像
- 初始化数据库
- 安装依赖

**建议**:
- 耐心等待 5-10 分钟
- 使用 `docker compose logs -f` 观察进度
- 确保网络连接稳定

## 📚 其他资源

- **项目源码**: [GitHub Repository]
- **API 文档**: http://localhost:5050/docs （启动后访问）
- **Neo4j 文档**: https://neo4j.com/docs/
- **Milvus 文档**: https://milvus.io/docs
- **FastAPI 文档**: https://fastapi.tiangolo.com/
- **Vue 3 文档**: https://vuejs.org/

## 🆘 获取帮助

如果遇到问题：

1. 查看上述[常见问题](#常见问题)部分
2. 检查服务日志：`docker compose logs -f`
3. 搜索项目 Issues
4. 提交新的 Issue 并附上：
   - 错误信息
   - 服务日志
   - 系统环境信息
   - 复现步骤

---

**祝您使用愉快！** 🎉
