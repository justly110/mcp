#!/usr/bin/env node

import dotenv from "dotenv";
import express from "express";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import { createGoogleSearchMcpServer } from "./server.js";

dotenv.config();

const app = express();
const port = parseInt(process.env.PORT || "3000", 10);

const transports = new Map<string, SSEServerTransport>();

app.get("/health", (req, res) => {
  res.json({ status: "ok", service: "google-search-mcp" });
});

// SSE 端点：客户端长连接
app.get("/sse", async (req, res) => {
  console.log("收到新的 SSE 客户端连接请求");
  const transport = new SSEServerTransport("/message", res);
  const server = createGoogleSearchMcpServer();

  transports.set(transport.sessionId, transport);

  res.on("close", () => {
    console.log(`客户端连接断开: ${transport.sessionId}`);
    transports.delete(transport.sessionId);
  });

  await server.connect(transport);
});

// 消息端点：客户端发送 JSON-RPC
app.post("/message", async (req, res) => {
  const sessionId = req.query.sessionId as string;
  if (!sessionId) {
    res.status(400).send("缺少 sessionId 参数");
    return;
  }

  const transport = transports.get(sessionId);
  if (!transport) {
    res.status(404).send("未找到对应的 SSE 会话，连接可能已过期或未建立");
    return;
  }

  await transport.handlePostMessage(req, res);
});

app.listen(port, "0.0.0.0", () => {
  console.log(`===============================================`);
  console.log(`Google Search MCP Server (HTTP/SSE) 已启动:`);
  console.log(`- 访问地址: http://0.0.0.0:${port}`);
  console.log(`- SSE 端点: http://<服务器IP或域名>:${port}/sse`);
  console.log(`===============================================`);
});
