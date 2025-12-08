# 🚀 Docker 快速部署

本项目已配置完整的 Docker Compose 环境，可通过以下方式快速启动。

## 📖 完整文档

👉 **详细部署文档请查看**: [DEPLOYMENT.md](./DEPLOYMENT.md)

## ⚡ 快速开始

### Windows 用户

```powershell
# 1. 配置环境变量
copy .env.template .env
# 编辑 .env 文件，至少配置一个 LLM API Key

# 2. 使用部署脚本启动
.\deploy.ps1 start

# 或直接使用 docker compose
docker compose up --build -d
```

### Linux/macOS 用户

```bash
# 1. 配置环境变量
cp .env.template .env
# 编辑 .env 文件，至少配置一个 LLM API Key

# 2. 使用部署脚本启动
chmod +x deploy.sh
./deploy.sh start

# 或直接使用 docker compose
docker compose up --build -d
```

## 🔧 部署脚本使用

### Windows (PowerShell)

```powershell
.\deploy.ps1 start      # 启动基础服务
.\deploy.ps1 start-all  # 启动所有服务（包含 GPU）
.\deploy.ps1 status     # 查看服务状态
.\deploy.ps1 logs       # 查看服务日志
.\deploy.ps1 stop       # 停止服务
.\deploy.ps1 restart    # 重启服务
```

### Linux/macOS (Bash)

```bash
./deploy.sh start      # 启动基础服务
./deploy.sh start-all  # 启动所有服务（包含 GPU）
./deploy.sh status     # 查看服务状态
./deploy.sh logs       # 查看服务日志
./deploy.sh stop       # 停止服务
./deploy.sh restart    # 重启服务
```

## 🌐 服务访问

启动成功后，访问以下地址：

| 服务 | 地址 | 说明 |
|------|------|------|
| 🎨 前端界面 | http://localhost:5173 | 主应用 |
| 📚 API 文档 | http://localhost:5050/docs | 后端 API |
| 🔍 Neo4j | http://localhost:7474 | 图数据库 |
| 📦 MinIO | http://localhost:9001 | 对象存储 |

## 📋 最小环境配置

编辑 `.env` 文件，至少需要配置以下之一：

```env
# 推荐：硅基流动（有免费额度）
SILICONFLOW_API_KEY=sk-xxxxxx

# 或其他 LLM 提供商
OPENAI_API_KEY=sk-xxxxxx
DEEPSEEK_API_KEY=sk-xxxxxx
```

## ⚠️ 注意事项

- **首次启动**: 需要 5-10 分钟下载镜像和初始化数据库
- **内存要求**: 至少 8GB RAM，推荐 16GB
- **GPU 服务**: 仅在有 NVIDIA GPU 时启动 `start-all`

## 🆘 遇到问题？

查看 [DEPLOYMENT.md](./DEPLOYMENT.md) 的**常见问题**部分，或查看服务日志：

```bash
# Windows
.\deploy.ps1 logs

# Linux/macOS
./deploy.sh logs
```

---

**祝使用愉快！** 🎉
