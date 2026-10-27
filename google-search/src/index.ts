#!/usr/bin/env node

import dotenv from "dotenv";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { createGoogleSearchMcpServer } from "./server.js";

dotenv.config();

async function main() {
  const server = createGoogleSearchMcpServer();
  const transport = new StdioServerTransport();

  await server.connect(transport);
  console.error("Google Search MCP Server (stdio 模式) 已启动并运行。");
}

main().catch((error) => {
  console.error("Server 发生严重错误:", error);
  process.exit(1);
});
