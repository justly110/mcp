# MCP (Model Context Protocol) 仓库

本仓库用于收集与维护实用的 **Model Context Protocol (MCP)** 工具与服务。

## 目录结构

- [`google-search/`](./google-search/): 谷歌搜索 MCP 工具，支持本地 `stdio` 标准输入输出模式以及远程 `HTTP/SSE` 模式。

---

## 常见疑问解答：可以通过 HTTP 直接安装吗？

关于 **"把代码放在 GitHub 某个文件夹里，以后能否直接通过 HTTP 安装？"**，需要区分以下几种情况：

### 1. 如果你指的是客户端直接通过 HTTP URL 连接该工具（推荐，真正的云端 HTTP 模式）：
**完全可以！**
本项目中的 `google-search` 提供了 **SSE (Server-Sent Events) HTTP 传输模式** (`src/http.ts`)。
你可以将这个服务部署在任何有公网 IP 的云服务器、VPS、Docker 或 Serverless 平台上。客户端（如 Cursor、Claude 等）只需要配置一个 HTTP URL 即可直接使用，无需在本地安装任何 Node/Python 运行环境：
```json
{
  "mcpServers": {
    "google-search": {
      "url": "https://your-server-domain.com/sse"
    }
  }
}
```

### 2. 如果你指的是像 `npx https://github.com/...` 那样直接从 GitHub 某个子文件夹安装：
- **原生 npm/npx 限制**：`npx` 或 `npm install` 直接接 GitHub URL 时，只能识别仓库根目录下的 `package.json`，**无法直接通过 HTTP URL 安装仓库内某一个子文件夹**。
- **解决方案 A（发布到 npm 仓库）**：
  进入 `google-search/` 目录运行 `npm publish`。发布后，全世界用户都可以随时随地通过 HTTP/网络一键运行：
  ```bash
  npx -y @justly110/google-search-mcp
  ```
- **解决方案 B（通过 Git Clone 运行）**：
  下载该仓库到本地后，直接以本地路径运行：
  ```bash
  git clone https://github.com/justly110/mcp.git
  cd mcp/google-search
  npm install && npm run build
  ```

---

## License

MIT
