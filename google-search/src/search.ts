import axios from "axios";

export interface SearchOptions {
  query: string;
  num?: number;
  start?: number;
  dateRestrict?: string;
  language?: string;
}

export interface SearchResultItem {
  title: string;
  link: string;
  snippet: string;
  displayLink?: string;
}

export interface SearchResponse {
  totalResults?: string;
  searchTime?: number;
  items: SearchResultItem[];
}

export async function executeGoogleSearch(
  options: SearchOptions,
  apiKey?: string,
  cx?: string
): Promise<SearchResponse> {
  const finalApiKey = apiKey || process.env.GOOGLE_API_KEY;
  const finalCx = cx || process.env.GOOGLE_SEARCH_ENGINE_ID;

  if (!finalApiKey || !finalCx) {
    throw new Error(
      "缺少 Google Search API 配置！请在环境变量中设置 GOOGLE_API_KEY 和 GOOGLE_SEARCH_ENGINE_ID (cx)，或在工具调用参数中提供。"
    );
  }

  const { query, num = 5, start = 1, dateRestrict, language } = options;

  const params: Record<string, any> = {
    key: finalApiKey,
    cx: finalCx,
    q: query,
    num: Math.min(Math.max(num, 1), 10),
    start: Math.max(start, 1),
  };

  if (dateRestrict) {
    params.dateRestrict = dateRestrict;
  }

  if (language) {
    params.lr = language;
  }

  try {
    const response = await axios.get("https://www.googleapis.com/customsearch/v1", {
      params,
      timeout: 10000,
    });

    const data = response.data;
    const items: SearchResultItem[] = (data.items || []).map((item: any) => ({
      title: item.title,
      link: item.link,
      snippet: item.snippet,
      displayLink: item.displayLink,
    }));

    return {
      totalResults: data.searchInformation?.totalResults,
      searchTime: data.searchInformation?.searchTime,
      items,
    };
  } catch (error: any) {
    if (axios.isAxiosError(error)) {
      const status = error.response?.status;
      const apiError = error.response?.data?.error?.message || error.message;
      throw new Error(`Google Search API 请求失败 [HTTP ${status}]: ${apiError}`);
    }
    throw error;
  }
}
