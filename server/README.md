# LLM Tool Server - Docker 沙盒环境

一个专为 LLM Agent 设计的安全独立工具调用服务，提供 31 种工具的统一 API 接口，所有工具运行在隔离的 Docker 容器中。

## 🚀 快速启动

### 方法一：使用简化启动脚本（推荐）

```bash
# 进入项目目录
cd docker_start

# 使用默认配置启动（端口 8001）
python simple_start.py

# 自定义配置启动
python simple_start.py --port 8002 --workspace ./my_workspace --rag-url http://localhost:8892
```


### 方法二：直接启动 Docker 容器

```bash
# 构建镜像（如果需要）
docker build -t tool_server_uni .

# 启动容器
docker run -d \
  --name tool_server_uni_container \
  -p 8001:8001 \
  -v $(pwd)/workspace:/workspace \
  -e PYTHONUNBUFFERED=1 \
  tool_server_uni python -m core.server --port 8001 --rag-url http://129.204.156.144:8892

# 如果有 GPU 支持
docker run -d \
  --name tool_server_uni_container \
  --runtime=nvidia \
  -e NVIDIA_VISIBLE_DEVICES=all \
  -e NVIDIA_DRIVER_CAPABILITIES=compute,utility \
  -p 8001:8001 \
  -v $(pwd)/workspace:/workspace \
  -e PYTHONUNBUFFERED=1 \
  tool_server_uni python -m core.server --port 8001 --rag-url http://129.204.156.144:8892
```

## 📋 系统要求

- **Docker**: 版本 20.10+
- **Python**: 3.8+（仅启动脚本需要）
- **GPU 支持**（可选）: NVIDIA Docker Runtime
- **内存**: 建议 4GB+
- **存储**: 建议 10GB+ 可用空间

## 🛠️ 启动参数配置

### simple_start.py 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--workspace` | `../workspace` | 工作空间路径 |
| `--port` | `8001` | API 服务端口 |
| `--rag-url` | `http://129.204.156.144:8892` | RAG 服务地址 |

### 使用示例

```bash
# 基本启动
python simple_start.py

# 自定义端口
python simple_start.py --port 8002

# 自定义工作空间
python simple_start.py --workspace ./my_project

# 完整配置
python simple_start.py \
  --port 8003 \
  --workspace ./custom_workspace \
  --rag-url http://localhost:8892
```

## 🔧 功能特性

### 自动化管理
- ✅ **自动清理**：启动前清理旧容器
- ✅ **GPU 检测**：自动检测并启用 GPU 支持
- ✅ **健康检查**：容器状态监控
- ✅ **优雅停止**：Ctrl+C 安全停止服务

### 安全隔离
- 🔒 **容器隔离**：所有工具运行在独立容器中
- 🔒 **文件沙盒**：工作空间完全隔离
- 🔒 **网络隔离**：仅暴露必要端口

## 🎯 可用工具（31个）

### 📁 文件操作工具（8个）
- `file_upload` - 上传文件到工作空间
- `file_read` - 读取文件内容
- `file_write` - 写入文件内容
- `file_replace_lines` - 替换文件行
- `file_delete` - 删除文件或目录
- `file_move` - 移动/重命名文件
- `dir_create` - 创建目录
- `dir_list` - 列出目录内容

### 💻 代码与执行工具（7个）
- `execute_code` - 执行 Python 脚本
- `execute_shell` - 执行 Shell 命令
- `pip_install` - 安装 Python 包
- `git_clone` - 克隆 Git 仓库/upload文件夹
- `parse_document` - 解析文档（PDF/Word/PPT/MD）
- `code_task_execute` - AI 代码助手
- `tex2pdf_convert` - LaTeX 转 PDF

### 🌐 网络与搜索工具（5个）
- `google_search` - Google 搜索
- `crawl_page` - 网页爬取
- `google_scholar_search` - Google Scholar 搜索
- `github_search_repositories` - GitHub 仓库搜索
- `github_get_repository_info` - GitHub 仓库信息

### 🔍 RAG 向量搜索工具（11个）
- `rag_health_check` - 健康检查
- `rag_get_stats` - 获取统计信息
- `rag_search_abstracts` - 摘要搜索
- `rag_search_abstracts_filtered` - 过滤摘要搜索
- `rag_search_details` - 详细内容搜索
- `rag_get_paper_content` - 获取论文内容
- `rag_get_paper_chunks` - 获取论文块信息
- `rag_get_specific_content` - 获取特定内容
- `rag_cache_stats` - 缓存统计
- `rag_cache_clear` - 清空缓存
- `rag_service_info` - 服务信息

## 📖 API 使用指南

### 服务地址
启动成功后，服务将在以下地址提供 API：
```
http://localhost:8001
```

### 基本 API 调用格式

```bash
curl -X POST "http://localhost:8001/api/tool/execute" \
-H "Content-Type: application/json" \
-d '{
  "task_id": "my_task",
  "tool_name": "file_read",
  "params": {
    "file_path": "example.txt"
  }
}'
```

### 任务管理

```bash
# 创建任务
curl -X POST "http://localhost:8001/api/task/create?task_id=my_task&task_name=Test_Task"

# 查看任务列表
curl "http://localhost:8001/api/task/list"

# 查看任务状态
curl "http://localhost:8001/api/task/my_task/status"

# 删除任务
curl -X DELETE "http://localhost:8001/api/task/my_task"
```

## 📚 详细文档

更多详细的 API 文档和使用示例，请参考：
- [tool.md](tool.md) - 完整的 API 文档和工具说明

## 🔍 常见问题

### Q: 如何检查服务是否正常运行？
```bash
curl http://localhost:8001/health
```

### Q: 如何查看容器日志？
```bash
docker logs tool_server_uni_container
```

### Q: 如何重启服务？
```bash
# 停止服务（Ctrl+C 或）
docker stop tool_server_uni_container
docker rm tool_server_uni_container

# 重新启动
python simple_start.py
```

### Q: 工作空间文件在哪里？
工作空间文件默认保存在 `../workspace` 目录中，可以通过 `--workspace` 参数自定义。

### Q: 如何启用 GPU 支持？
脚本会自动检测 GPU 支持。确保安装了 NVIDIA Docker Runtime：
```bash
# 检查 GPU 支持
nvidia-smi
docker info | grep nvidia
```

## 🛡️ 安全注意事项

1. **网络安全**：默认只绑定本地端口，生产环境请配置适当的网络策略
2. **文件权限**：工作空间文件具有容器内的权限设置
3. **资源限制**：建议为容器设置适当的资源限制
4. **敏感信息**：避免在工作空间中存储敏感信息

## 📝 开发说明

### 项目结构
```
docker_start/
├── simple_start.py      # 简化启动脚本
├── docker_manager.py    # Docker 管理器
├── docker_launcher.py   # 完整启动器
├── tool.md             # API 文档
└── utils/
    ├── logger.py       # 日志工具
    └── response.py     # 响应工具
```

### 自定义配置
可以通过修改 `simple_start.py` 中的默认参数来自定义配置：
```python
# 默认配置
DEFAULT_PORT = 8001
DEFAULT_WORKSPACE = "../workspace"
DEFAULT_RAG_URL = "http://129.204.156.144:8892"
```

## 📄 许可证

本项目采用 MIT 许可证，详情请参阅 LICENSE 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

---

**开始使用**: `python simple_start.py`

**获取帮助**: `python simple_start.py --help` 