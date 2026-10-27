# Google Search MCP Server

基于 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 实现的谷歌搜索工具服务。

同时支持：
1. **本地 stdio 模式**：供 Claude Desktop、Cursor 等客户端通过本地进程调用。
2. **远程 HTTP/SSE 模式**：通过 HTTP 提供 SSE (Server-Sent Events) 长连接服务，客户端直接填写 URL 即可连接，无需在客户端本地安装 Node.js 环境。

---

## 1. 准备工作：获取 Google API 凭据

Google Custom Search JSON API 每日提供 **100 次免费搜索请求**。

1. **获取 API Key**:
   - 访问 [Google Cloud Console Credentials](https://console.cloud.google.com/apis/credentials)。
   - 创建或选择项目，点击 **创建凭据** -> **API 密钥**。
   - 在 API 库中搜索并启用 **Custom Search API**。
2. **获取搜索引擎 ID (cx)**:
   - 访问 [Programmable Search Engine 控制台](https://programmablesearchengine.google.com/)。
   - 点击 **添加**，名称自填。
   - 在“要搜索的内容”中选择 **在整个网络中搜索**。
   - 创建完成后，进入搜索引擎概览页面，复制 **搜索引擎 ID**（即 `cx`）。

---

## 2. 本地安装与编译

```bash
cd google-search

# 安装依赖
npm install

# 复制环境变量配置并填入你的 Google 凭据
cp .env.example .env

# 编译 TypeScript
npm run build
```

---

## 3. 使用方式一：本地 stdio 模式 (Claude Desktop / Cursor)

编译完成后，在客户端配置文件中加入配置即可。

### Claude Desktop 配置示例
修改 `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) 或 `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "google-search": {
      "command": "node",
      "args": [
        "/绝对路径/mcp/google-search/dist/index.js"
      ],
      "env": {
        "GOOGLE_API_KEY": "你的Google_API_Key",
        "GOOGLE_SEARCH_ENGINE_ID": "你的搜索引擎_cx"
      }
    }
  }
}
```

---

## 4. 使用方式二：远程 HTTP / SSE 模式（无需本地安装客户端代码）

如果你把此服务部署在云服务器或容器中：

```bash
# 启动 HTTP/SSE 服务 (默认端口 3000)
npm run start:http
```

此时服务将监听：
- 健康检查: `GET http://<服务器IP>:3000/health`
- SSE 连接端点: `GET http://<服务器IP>:3000/sse`
- 消息处理端点: `POST http://<服务器IP>:3000/message?sessionId=...`

在支持远程 MCP 的客户端配置中，只需填写 URL：
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

## 5. 工具功能与参数说明

### `google_search`
- `query` (string, 必填): 搜索关键词或短语
- `num` (number, 选填): 返回条数，默认 5，最大 10
- `start` (number, 选填): 分页起始位置，默认 1
- `dateRestrict` (string, 选填): 时间范围过滤（例如 `d1` 过去一天，`w1` 过去一周，`m1` 过去一个月，`y1` 过去一年）
- `language` (string, 选填): 语言限制（例如 `lang_zh-CN`, `lang_en`）
