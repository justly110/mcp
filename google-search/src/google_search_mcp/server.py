import os
import sys
import argparse
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# 加载 .env 环境变量（如果本地存在）
load_dotenv()

# 初始化 FastMCP 服务器
mcp = FastMCP("Google Search")


@mcp.tool()
async def google_search(
    query: str,
    num: int = 5,
    start: int = 1,
    date_restrict: str | None = None,
    language: str | None = None,
    api_key: str | None = None,
    cx: str | None = None,
) -> str:
    """使用 Google Custom Search API 搜索网页、新闻、文档和实时信息。

    Args:
        query: 搜索关键词或短语
        num: 返回结果数量 (1-10，默认 5)
        start: 分页起始偏移量 (默认 1)
        date_restrict: 时间范围过滤，如 d1 (1天内), w1 (1周内), m1 (1月内), y1 (1年内)
        language: 搜索结果语言限制，如 lang_zh-CN (简体中文), lang_en (英文)
        api_key: 可选，临时传入的 Google API Key（未配置环境变量时传入）
        cx: 可选，临时传入的 Google Search Engine ID (cx)
    """
    final_api_key = api_key or os.getenv("GOOGLE_API_KEY")
    final_cx = cx or os.getenv("GOOGLE_SEARCH_ENGINE_ID")

    if not final_api_key or not final_cx:
        return (
            "【配置错误】缺少 Google Search API 凭据！\n"
            "请设置环境变量 GOOGLE_API_KEY 和 GOOGLE_SEARCH_ENGINE_ID (cx)，"
            "或者在工具调用参数中提供 api_key 与 cx。\n\n"
            "1. 获取 API Key: https://console.cloud.google.com/apis/credentials\n"
            "2. 获取搜索引擎 ID (cx): https://programmablesearchengine.google.com/"
        )

    num = min(max(num, 1), 10)
    start = max(start, 1)

    params: dict[str, str | int] = {
        "key": final_api_key,
        "cx": final_cx,
        "q": query,
        "num": num,
        "start": start,
    }
    if date_restrict:
        params["dateRestrict"] = date_restrict
    if language:
        params["lr"] = language

    url = "https://www.googleapis.com/customsearch/v1"

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as e:
            try:
                err_msg = e.response.json().get("error", {}).get("message", str(e))
            except Exception:
                err_msg = str(e)
            return f"Google Search API 请求失败 [HTTP {e.response.status_code}]: {err_msg}"
        except Exception as e:
            return f"网络请求异常: {str(e)}"

    items = data.get("items", [])
    if not items:
        return f'未检索到关于 "{query}" 的结果。'

    search_info = data.get("searchInformation", {})
    total_results = search_info.get("totalResults", "多")
    search_time = search_info.get("searchTime", "0")

    result_lines = [f"已找到约 {total_results} 条结果（耗时 {search_time} 秒）：\n"]
    for i, item in enumerate(items, 1):
        title = item.get("title", "")
        link = item.get("link", "")
        snippet = item.get("snippet", "").replace("\n", " ")
        display_link = item.get("displayLink", link)
        result_lines.append(f"### {i}. [{title}]({link})")
        result_lines.append(f"**来源**: {display_link}")
        result_lines.append(f"**摘要**: {snippet}\n")

    return "\n".join(result_lines)


def main():
    parser = argparse.ArgumentParser(description="Google Search MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="传输协议: stdio (默认，适合本地 Claude/Cursor) 或 sse (适合远程 HTTP)",
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
