import os
import sys
import argparse
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# 加载 .env 环境变量
load_dotenv()

# 初始化 FastMCP 服务器
mcp = FastMCP("Google Search (Gemini Grounding)")

DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com"


async def request_gemini_search(
    client: httpx.AsyncClient,
    base_url: str,
    model: str,
    api_key: str,
    query: str,
    prompt: str | None = None,
) -> tuple[dict, str]:
    """发送请求给 Gemini API，启用 Google Search Grounding 工具"""
    clean_model = model.replace("models/", "")
    url = f"{base_url}/v1beta/models/{clean_model}:generateContent"

    user_text = query
    if prompt:
        user_text = f"{query}\n\n额外要求与侧重点: {prompt}"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": user_text}
                ]
            }
        ],
        "tools": [
            {
                "google_search": {}
            }
        ]
    }

    response = await client.post(
        url,
        params={"key": api_key},
        json=payload,
        headers={"Content-Type": "application/json"},
    )
    return response.json(), clean_model


@mcp.tool()
async def google_search(
    query: str,
    prompt: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
) -> str:
    """使用 Gemini API 的 Google Search Grounding（联网谷歌搜索能力）检索实时网页、新闻和资料。

    只需要提供 GEMINI_API_KEY，无需注册繁琐的 Google Custom Search 引擎 ID (cx)。

    Args:
        query: 搜索关键词或问题描述
        prompt: 可选，具体的搜索侧重点或额外指示（如“重点关注最新发布的内容并列出核心更新”）
        model: 可选，Gemini 模型名称（默认 gemini-2.5-flash，也支持 gemini-2.0-flash 等）
        api_key: 可选，临时传入的 Gemini API Key（若未配置环境变量 GEMINI_API_KEY）
    """
    final_api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not final_api_key:
        return (
            "【配置错误】缺少 Gemini API Key！\n"
            "请设置环境变量 GEMINI_API_KEY，或在工具调用参数中提供 api_key。\n\n"
            "获取免费的 Gemini API Key:\n"
            "👉 https://aistudio.google.com/app/apikey"
        )

    base_url = (os.getenv("GEMINI_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
    target_model = model or os.getenv("GEMINI_MODEL") or DEFAULT_MODEL

    async with httpx.AsyncClient(timeout=45.0) as client:
        try:
            data, used_model = await request_gemini_search(
                client, base_url, target_model, final_api_key, query, prompt
            )
        except httpx.HTTPStatusError as e:
            # 如果指定模型返回 404，尝试自动回退到 gemini-2.0-flash
            if e.response.status_code == 404 and target_model != "gemini-2.0-flash":
                try:
                    data, used_model = await request_gemini_search(
                        client, base_url, "gemini-2.0-flash", final_api_key, query, prompt
                    )
                except Exception as retry_err:
                    return f"Gemini API 请求失败 [HTTP {e.response.status_code}]: {str(retry_err)}"
            else:
                try:
                    err_json = e.response.json()
                    err_msg = err_json.get("error", {}).get("message", str(e))
                except Exception:
                    err_msg = str(e)
                return f"Gemini API 请求失败 [HTTP {e.response.status_code}]: {err_msg}"
        except Exception as e:
            return f"网络连接异常: {str(e)}"

    candidates = data.get("candidates", [])
    if not candidates:
        if "error" in data:
            return f"Gemini API 报错: {data['error'].get('message', str(data['error']))}"
        return f'未能通过 Gemini 获取关于 "{query}" 的搜索结果。'

    candidate = candidates[0]
    parts = candidate.get("content", {}).get("parts", [])
    answer_text = "".join(part.get("text", "") for part in parts).strip()

    grounding_metadata = candidate.get("groundingMetadata", {})
    queries = grounding_metadata.get("webSearchQueries", [])
    chunks = grounding_metadata.get("groundingChunks", [])

    output_lines = []
    if answer_text:
        output_lines.append(answer_text)
        output_lines.append("")

    # 提取搜索到的网页来源与参考链接
    sources = []
    seen_urls = set()
    for chunk in chunks:
        web = chunk.get("web", {})
        uri = web.get("uri")
        title = web.get("title") or uri
        if uri and uri not in seen_urls:
            seen_urls.add(uri)
            sources.append(f"- [{title}]({uri})")

    if sources:
        output_lines.append("### 🌐 搜索来源与参考链接：")
        output_lines.extend(sources)
        output_lines.append("")

    if queries:
        output_lines.append(f"*(Google 检索词: {', '.join(queries)})*")

    return "\n".join(output_lines)


def main():
    parser = argparse.ArgumentParser(description="Google Search MCP Server (Gemini Grounding)")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="传输协议: stdio (默认，适合本地 Claude/Cursor) 或 sse (适合远程 HTTP 服务)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", "3000")),
        help="SSE 模式监听端口 (默认 3000)",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="SSE 模式监听地址 (默认 0.0.0.0)",
    )
    args = parser.parse_args()

    if args.transport == "sse":
        mcp.settings.port = args.port
        mcp.settings.host = args.host
        print(f"Google Search MCP Server (SSE 模式) 正在监听 http://{args.host}:{args.port}/sse", file=sys.stderr)
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
