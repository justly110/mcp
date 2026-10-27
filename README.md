# MCP (Model Context Protocol) 仓库

本仓库收集和维护实用的 **Model Context Protocol (MCP)** 工具与服务。

## 目录结构

- [`google-search/`](./google-search/): 基于 **Gemini API Google Search Grounding** 实现的实时谷歌搜索工具。

---

## 特性亮点

- **无需配置复杂的 Custom Search Engine (cx)**：只需一个 `GEMINI_API_KEY`（免费申请）。
- **Google 全网实时搜索**：利用 Gemini 原生联网搜索能力，获取实时资讯与网页来源。
- **支持 `uv` / `uvx` 一键网络运行**：无需手动 git clone，客户端自动拉取运行。
- **同时支持本地 stdio 与远程 HTTP/SSE 模式**。

---

## 如何通过 `uv` / `uvx` 直接一键安装与运行？

### 1. 终端命令行执行测试
```bash
export GEMINI_API_KEY="你的Gemini_API_Key"
uvx --from "git+https://github.com/justly110/mcp.git#subdirectory=google-search" google-search-mcp
```

### 2. 在 Claude Desktop / Cursor 配置文件中直接配置
只需在 `claude_desktop_config.json` 或 Cursor MCP 配置中填写以下内容，`uvx` 会自动通过网络拉取并运行该子文件夹内的 MCP 工具：

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

---

## 常见疑问解答：支持通过 HTTP 安装吗？

1. **通过 `uvx` 从 GitHub 链接安装运行**：
   - **完全支持！** 借助 `uvx` 的 `git+https://...#subdirectory=...` 特性，用户不需要手动下载源码，客户端启动时 `uvx` 会自动拉取并构建隔离运行环境。
2. **通过 HTTP / SSE URL 远程直连（免安装）**：
   - **完全支持！** 支持 `--transport sse` 参数启动为在线 Web 服务，客户端只需填写 `http://<服务器IP>:3000/sse` 即可直接使用。

---

## License

MIT
