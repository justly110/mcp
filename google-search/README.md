# Google Search MCP Server

基于 Python [FastMCP](https://github.com/modelcontextprotocol/python-sdk) 实现的谷歌搜索工具服务。

支持：
1. **`uvx` 远程一键安装运行**（无需克隆仓库，直接从 GitHub 子文件夹拉取并运行）
2. **`uv` 本地安装与开发**
3. **HTTP / SSE 远程模式**（云服务器部署）

---

## 1. 准备 Google Search API 凭据

Google Custom Search API 每日提供 **100 次免费请求**。

1. **获取 API Key**:
   - 访问 [Google Cloud Console Credentials](https://console.cloud.google.com/apis/credentials)。
   - 创建凭据 -> API 密钥。并在 API 库中启用 **Custom Search API**。
2. **获取搜索引擎 ID (cx)**:
   - 访问 [Programmable Search Engine 控制台](https://programmablesearchengine.google.com/)。
   - 新建搜索引擎，开启 **“在整个网络中搜索”**。
   - 复制生成的 **搜索引擎 ID (cx)**。

---

## 2. 通过 uv / uvx 一键运行（推荐，免克隆）

Python 的 `uv` / `uvx` 原生支持通过 `#subdirectory=` 直接定位 GitHub 仓库的子文件夹：

```bash
# 测试运行
export GOOGLE_API_KEY="你的APIKey"
export GOOGLE_SEARCH_ENGINE_ID="你的cx"

uvx --from "git+https://github.com/justly110/mcp.git#subdirectory=google-search" google-search-mcp
```

### Claude Desktop 配置示例
修改 `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "google-search": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/justly110/mcp.git#subdirectory=google-search",
        "google-search-mcp"
      ],
      "env": {
        "GOOGLE_API_KEY": "你的API_KEY",
        "GOOGLE_SEARCH_ENGINE_ID": "你的搜索引擎ID_cx"
      }
    }
  }
}
```

---

## 3. 本地安装与开发 (uv)

如果你已经克隆了仓库：

```bash
cd google-search

# 使用 uv 创建虚拟环境并安装依赖
uv sync

# 本地运行
uv run google-search-mcp
```

---

## 4. 远程 HTTP / SSE 模式

如需部署为在线 HTTP 服务供远程客户端连接：

```bash
# 启动 SSE HTTP 服务（默认端口 3000）
uvx --from "git+https://github.com/justly110/mcp.git#subdirectory=google-search" google-search-mcp --transport sse --port 3000
```

远程客户端配置：
```json
{
  "mcpServers": {
    "google-search": {
      "url": "http://<服务器IP或域名>:3000/sse"
    }
  }
}
```

---

## 5. 工具说明

### `google_search`
- `query` (str, 必填): 搜索关键词
- `num` (int, 选填): 返回数量（1-10，默认 5）
- `start` (int, 选填): 搜索起始偏移（默认 1）
- `date_restrict` (str, 选填): 时间范围（`d1` 1天内, `w1` 1周内, `m1` 1月内, `y1` 1年内）
- `language` (str, 选填): 语言限制（`lang_zh-CN`, `lang_en` 等）
