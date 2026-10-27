import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ErrorCode,
  McpError,
} from "@modelcontextprotocol/sdk/types.js";
import { executeGoogleSearch } from "./search.js";

export function createGoogleSearchMcpServer() {
  const server = new Server(
    {
      name: "google-search-mcp",
      version: "1.0.0",
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  // 注册可用工具列表
  server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
      tools: [
        {
          name: "google_search",
          description:
            "通过 Google Custom Search API 搜索网页信息、新闻、文档和实时内容。返回标题、链接、摘要等信息。",
          inputSchema: {
            type: "object",
            properties: {
              query: {
                type: "string",
                description: "搜索关键词或查询短语",
              },
              num: {
                type: "number",
                description: "返回的搜索结果条数，默认 5，最大 10",
                minimum: 1,
                maximum: 10,
              },
              start: {
                type: "number",
                description: "搜索结果的分页起始索引，默认为 1（第 1 页）",
                minimum: 1,
              },
              dateRestrict: {
                type: "string",
                description:
                  "按时间范围过滤结果。例如: d1 (最近1天), w1 (最近1周), m1 (最近1个月), y1 (最近1年)",
              },
              language: {
                type: "string",
                description:
                  "搜索结果语言限制。例如: lang_zh-CN (简体中文), lang_en (英文)",
              },
              apiKey: {
                type: "string",
                description:
                  "可选：临时传入的 Google API Key（若未配置环境变量）",
              },
              cx: {
                type: "string",
                description:
                  "可选：临时传入的 Google Search Engine ID (cx)（若未配置环境变量）",
              },
            },
            required: ["query"],
          },
        },
      ],
    };
  });

  // 处理工具调用
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    if (request.params.name !== "google_search") {
      throw new McpError(
        ErrorCode.MethodNotFound,
        `未知工具: ${request.params.name}`
      );
    }

    const args = request.params.arguments as any;
    if (!args || typeof args.query !== "string" || !args.query.trim()) {
      throw new McpError(ErrorCode.InvalidParams, "必须提供有效的 query 搜索词");
    }

    try {
      const result = await executeGoogleSearch(
        {
          query: args.query.trim(),
          num: args.num ? Number(args.num) : 5,
          start: args.start ? Number(args.start) : 1,
          dateRestrict: args.dateRestrict,
          language: args.language,
        },
        args.apiKey,
        args.cx
      );

      if (result.items.length === 0) {
        return {
          content: [
            {
              type: "text",
              text: `未检索到关于 "${args.query}" 的结果。`,
            },
          ],
        };
      }

      const formattedResults = result.items
        .map(
          (item, index) =>
            `### ${index + 1}. [${item.title}](${item.link})\n**来源**: ${item.displayLink || item.link}\n**摘要**: ${item.snippet}\n`
        )
        .join("\n");

      const header = `已找到约 ${result.totalResults || "多条"} 条结果（耗时 ${result.searchTime || "0"} 秒）：\n\n`;

      return {
        content: [
          {
            type: "text",
            text: header + formattedResults,
          },
        ],
      };
    } catch (error: any) {
      return {
        isError: true,
        content: [
          {
            type: "text",
            text: `Google 搜索出错: ${error.message}`,
          },
        ],
      };
    }
  });

  return server;
}
