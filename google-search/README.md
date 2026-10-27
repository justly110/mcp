# Google Search MCP Server (Gemini 驱动版)

基于 **Gemini API 的 Google Search Grounding（原生联网搜索能力）** 实现的 MCP 搜索工具。

### 为什么使用 Gemini API 替代传统的 Google Custom Search？
1. **无需繁琐配置**：传统 Custom Search 必须创建 Programmable Search Engine 并获取 `cx`，限制极多；而 Gemini 只需一个 `GEMINI_API_KEY`。
2. **全网实时搜索**：直接由 Google 的大模型调用 Google 搜索引擎进行实时检索。
3. **带来源引用与智能摘要**：不仅返回搜索结果的网页来源和链接，还会自动归纳整理答案。
4. **免费额度充足**：在 [Google AI Studio](https://aistudio.google.com/app/apikey) 即可直接免费申请 API Key。

---

## 1. 获取 Gemini API Key

1. 打开 [Google AI Studio API Keys](https://aistudio.google.com/app/apikey)。
2. 点击 **Create API Key** 创建密钥。
3. 复制生成的密钥备用。

---

## 2. 通过 uv / uvx 一键运行（推荐，免克隆）

无需手动下载代码，只要系统安装了 `uv`，客户端就可以直接通过 Git 链接从子目录拉取并运行：

```bash
# 测试运行
export GEMINI_API_KEY="你的Gemini_API_Key"

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
        "GEMINI_API_KEY": "你的Gemini_API_Key"
      }
    }
  }
}
```

### Cursor 配置示例
在 Cursor 的 **Features -> MCP Servers** 中添加：
- **Type**: `command`
- **Command**: `uvx --from "git+https://github.com/justly110/mcp.git#subdirectory=google-search" google-search-mcp`
- **Environment Variables**: 添加 `GEMINI_API_KEY=你的Key`

---

## 3. 本地安装与调试 (uv)

如果你已经克隆了仓库：

```bash
cd google-search

# 安装依赖并构建环境
uv sync

# 本地执行
uv run google-search-mcp
```

---

## 4. 远程 HTTP / SSE 模式

如需将该服务部署到云服务器供多人/多客户端通过 HTTP 直连：

```bash
# 启动 SSE 模式（默认监听 0.0.0.0:3000）
uvx --from "git+https://github.com/justly110/mcp.git#subdirectory=google-search" google-search-mcp --transport sse --port 3000
```

远程客户端配置：
```json
{
  "mcpServers": {
    "google-search": {
      "url": "http://<你的服务器IP或域名>:3000/sse"
    }
  }
}
```

---

## 5. 工具说明

### `google_search`
- `query` (str, 必填): 搜索关键词或用户问题。
- `prompt` (str, 选填): 额外的指示或搜索重点要求。
- `model` (str, 选填): 指定模型（默认 `gemini-2.5-flash`，可选 `gemini-2.0-flash` 等）。
- `api_key` (str, 选填): 临时传入 API Key（未配置环境变量时）。
