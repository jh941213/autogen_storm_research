"""AutoGen STORM Research Assistant Tools

이 모듈은 연구 과정에서 사용되는 다양한 도구들을 정의합니다.
"""

import os
from typing import Optional, List
from autogen_core.tools import FunctionTool
import aiohttp
import asyncio


async def search_web(query: str, max_results: int = 3) -> str:
    """웹에서 정보를 검색합니다
    
    Args:
        query: 검색 쿼리
        max_results: 최대 결과 수
        
    Returns:
        포맷된 검색 결과
    """
    try:
        # Tavily API를 사용한 웹 검색
        api_key = os.environ.get("TAVILY_API_KEY")
        if not api_key:
            return "<e>Tavily API 키가 설정되지 않았습니다. TAVILY_API_KEY 환경변수를 설정해주세요.</e>"
        
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": api_key,
            "query": query,
            "search_depth": "advanced",
            "include_answer": True,
            "include_raw_content": True,
            "max_results": max_results
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get("results", [])
                    
                    # 결과를 문서 형태로 포맷
                    formatted_results = []
                    for doc in results:
                        formatted_doc = (
                            f'<Document href="{doc.get("url", "")}"/>\n'
                            f'{doc.get("content", "")}\n'
                            f'</Document>'
                        )
                        formatted_results.append(formatted_doc)
                    
                    return "\n\n---\n\n".join(formatted_results)
                else:
                    return f"<e>웹 검색 중 오류가 발생했습니다: HTTP {response.status}</e>"
                    
    except Exception as e:
        return f"<e>웹 검색 중 오류가 발생했습니다: {str(e)}</e>"


async def search_duckduckgo(query: str, max_results: int = 3) -> str:
    """DuckDuckGo에서 정보를 검색합니다
    
    Args:
        query: 검색 쿼리
        max_results: 최대 결과 수
        
    Returns:
        포맷된 검색 결과
    """
    try:
        # DuckDuckGo Instant Answer API 사용
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": "1",
            "skip_disambig": "1"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    formatted_results = []
                    
                    # Abstract (요약 정보)
                    if data.get("Abstract"):
                        abstract_doc = (
                            f'<Document source="{data.get("AbstractURL", "DuckDuckGo")}" '
                            f'type="abstract"/>\n'
                            f'<Title>\n{data.get("Heading", query)}\n</Title>\n\n'
                            f'<Content>\n{data.get("Abstract")}\n</Content>\n'
                            f'</Document>'
                        )
                        formatted_results.append(abstract_doc)
                    
                    # Related Topics
                    related_topics = data.get("RelatedTopics", [])[:max_results]
                    for topic in related_topics:
                        if isinstance(topic, dict) and topic.get("Text"):
                            topic_doc = (
                                f'<Document source="{topic.get("FirstURL", "DuckDuckGo")}" '
                                f'type="related_topic"/>\n'
                                f'<Content>\n{topic.get("Text")}\n</Content>\n'
                                f'</Document>'
                            )
                            formatted_results.append(topic_doc)
                    
                    # Answer (직접 답변)
                    if data.get("Answer"):
                        answer_doc = (
                            f'<Document source="DuckDuckGo" type="answer"/>\n'
                            f'<Content>\n{data.get("Answer")}\n</Content>\n'
                            f'</Document>'
                        )
                        formatted_results.append(answer_doc)
                    
                    if formatted_results:
                        return "\n\n---\n\n".join(formatted_results)
                    else:
                        return f"<e>'{query}'에 대한 DuckDuckGo 검색 결과를 찾을 수 없습니다.</e>"
                else:
                    return f"<e>DuckDuckGo 검색 중 오류가 발생했습니다: HTTP {response.status}</e>"
                    
    except Exception as e:
        return f"<e>DuckDuckGo 검색 중 오류가 발생했습니다: {str(e)}</e>"


async def search_naver_news(query: str, max_results: int = 10, sort: str = "sim") -> str:
    """네이버 뉴스에서 정보를 검색합니다
    
    Args:
        query: 검색 쿼리
        max_results: 최대 결과 수 (기본값: 10, 최댓값: 100)
        sort: 정렬 방법 ("sim": 정확도순, "date": 날짜순)
        
    Returns:
        포맷된 검색 결과
    """
    try:
        # 네이버 검색 API 키 확인
        client_id = os.environ.get("NAVER_CLIENT_ID")
        client_secret = os.environ.get("NAVER_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            return "<e>네이버 API 키가 설정되지 않았습니다. NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET 환경변수를 설정해주세요.</e>"
        
        # 네이버 뉴스 검색 API 호출
        url = "https://openapi.naver.com/v1/search/news.json"
        headers = {
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret
        }
        params = {
            "query": query,
            "display": min(max_results, 100),  # 최대 100개
            "start": 1,
            "sort": sort
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get("items", [])
                    
                    if not items:
                        return f"<e>'{query}'에 대한 네이버 뉴스 검색 결과를 찾을 수 없습니다.</e>"
                    
                    # 결과를 문서 형태로 포맷
                    formatted_results = []
                    for item in items:
                        # HTML 태그 제거 (간단한 방법)
                        title = item.get("title", "").replace("<b>", "").replace("</b>", "")
                        description = item.get("description", "").replace("<b>", "").replace("</b>", "")
                        
                        formatted_doc = (
                            f'<Document source="{item.get("originallink", item.get("link", ""))}" '
                            f'type="news" '
                            f'date="{item.get("pubDate", "")}"/>\n'
                            f'<Title>\n{title}\n</Title>\n\n'
                            f'<Content>\n{description}\n</Content>\n'
                            f'<NaverLink>\n{item.get("link", "")}\n</NaverLink>\n'
                            f'</Document>'
                        )
                        formatted_results.append(formatted_doc)
                    
                    return "\n\n---\n\n".join(formatted_results)
                    
                elif response.status == 403:
                    return "<e>네이버 API 권한이 없습니다. 개발자 센터에서 검색 API 권한을 확인해주세요.</e>"
                elif response.status == 400:
                    error_text = await response.text()
                    return f"<e>네이버 뉴스 검색 요청 오류: {error_text}</e>"
                else:
                    return f"<e>네이버 뉴스 검색 중 오류가 발생했습니다: HTTP {response.status}</e>"
                    
    except Exception as e:
        return f"<e>네이버 뉴스 검색 중 오류가 발생했습니다: {str(e)}</e>"


async def search_wikipedia(query: str, max_results: int = 3, lang: str = "ko") -> str:
    """Wikipedia에서 정보를 검색합니다
    
    Args:
        query: 검색 쿼리
        max_results: 최대 결과 수
        lang: 언어 코드 ("ko": 한국어, "en": 영어)
        
    Returns:
        포맷된 검색 결과
    """
    try:
        # Wikipedia API를 사용한 검색
        base_url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/"
        search_url = f"https://{lang}.wikipedia.org/w/api.php"
        
        # 먼저 검색으로 관련 페이지들을 찾기
        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srlimit": max_results
        }
        
        async with aiohttp.ClientSession() as session:
            # 검색 실행
            async with session.get(search_url, params=search_params) as response:
                if response.status != 200:
                    return f"<e>Wikipedia 검색 중 오류가 발생했습니다: HTTP {response.status}</e>"
                
                search_data = await response.json()
                search_results = search_data.get("query", {}).get("search", [])
                
                if not search_results:
                    return f"<e>'{query}'에 대한 Wikipedia 검색 결과를 찾을 수 없습니다.</e>"
                
                formatted_results = []
                
                # 각 검색 결과에 대해 상세 정보 가져오기
                for result in search_results[:max_results]:
                    title = result.get("title", "")
                    page_id = result.get("pageid", "")
                    
                    # 페이지 요약 정보 가져오기
                    summary_url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}"
                    
                    try:
                        async with session.get(summary_url) as summary_response:
                            if summary_response.status == 200:
                                summary_data = await summary_response.json()
                                
                                page_url = summary_data.get("content_urls", {}).get("desktop", {}).get("page", "")
                                extract = summary_data.get("extract", "")
                                thumbnail = summary_data.get("thumbnail", {}).get("source", "") if summary_data.get("thumbnail") else ""
                                
                                formatted_doc = (
                                    f'<Document source="{page_url}" '
                                    f'type="wikipedia" '
                                    f'lang="{lang}" '
                                    f'page_id="{page_id}"/>\n'
                                    f'<Title>\n{title}\n</Title>\n\n'
                                    f'<Summary>\n{extract}\n</Summary>\n'
                                )
                                
                                if thumbnail:
                                    formatted_doc += f'<Thumbnail>\n{thumbnail}\n</Thumbnail>\n'
                                
                                formatted_doc += '</Document>'
                                formatted_results.append(formatted_doc)
                            else:
                                # 요약을 가져올 수 없으면 검색 결과의 snippet 사용
                                snippet = result.get("snippet", "").replace("<span class=\"searchmatch\">", "").replace("</span>", "")
                                page_url = f"https://{lang}.wikipedia.org/wiki/{title.replace(' ', '_')}"
                                
                                formatted_doc = (
                                    f'<Document source="{page_url}" '
                                    f'type="wikipedia" '
                                    f'lang="{lang}" '
                                    f'page_id="{page_id}"/>\n'
                                    f'<Title>\n{title}\n</Title>\n\n'
                                    f'<Snippet>\n{snippet}\n</Snippet>\n'
                                    f'</Document>'
                                )
                                formatted_results.append(formatted_doc)
                    except Exception as e:
                        # 개별 페이지 오류는 무시하고 계속 진행
                        continue
                
                if formatted_results:
                    return "\n\n---\n\n".join(formatted_results)
                else:
                    return f"<e>'{query}'에 대한 Wikipedia 상세 정보를 가져올 수 없습니다.</e>"
                    
    except Exception as e:
        return f"<e>Wikipedia 검색 중 오류가 발생했습니다: {str(e)}</e>"


async def search_arxiv(query: str, max_docs: int = 3) -> str:
    """ArXiv에서 학술 논문을 검색합니다
    
    Args:
        query: 검색 쿼리
        max_docs: 최대 문서 수
        
    Returns:
        포맷된 검색 결과
    """
    try:
        import feedparser
        
        # ArXiv API를 사용한 논문 검색
        base_url = "http://export.arxiv.org/api/query?"
        search_query = f"search_query=all:{query}&start=0&max_results={max_docs}"
        url = base_url + search_query
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    feed = feedparser.parse(content)
                    
                    # 결과를 문서 형태로 포맷
                    formatted_results = []
                    for entry in feed.entries:
                        authors = ", ".join([author.name for author in entry.authors]) if hasattr(entry, 'authors') else ""
                        published = entry.published if hasattr(entry, 'published') else ""
                        
                        formatted_doc = (
                            f'<Document source="{entry.id}" '
                            f'date="{published}" '
                            f'authors="{authors}"/>\n'
                            f'<Title>\n{entry.title}\n</Title>\n\n'
                            f'<Summary>\n{entry.summary}\n</Summary>\n'
                            f'</Document>'
                        )
                        formatted_results.append(formatted_doc)
                    
                    return "\n\n---\n\n".join(formatted_results)
                else:
                    return f"<e>ArXiv 검색 중 오류가 발생했습니다: HTTP {response.status}</e>"
                    
    except Exception as e:
        return f"<e>ArXiv 검색 중 오류가 발생했습니다: {str(e)}</e>"


# AutoGen FunctionTool로 래핑
web_search_tool = FunctionTool(
    search_web,
    description="웹에서 정보를 검색합니다. 최신 정보와 일반적인 주제에 대한 검색에 유용합니다."
)

duckduckgo_search_tool = FunctionTool(
    search_duckduckgo,
    description="DuckDuckGo에서 정보를 검색합니다. 프라이버시를 중시하는 검색과 즉석 답변에 유용합니다."
)

naver_news_search_tool = FunctionTool(
    search_naver_news,
    description="네이버 뉴스에서 최신 뉴스를 검색합니다. 한국 관련 뉴스와 최신 이슈에 특히 유용합니다."
)

wikipedia_search_tool = FunctionTool(
    search_wikipedia,
    description="Wikipedia에서 백과사전 정보를 검색합니다. 기본 개념, 정의, 역사적 배경 정보에 유용합니다."
)

arxiv_search_tool = FunctionTool(
    search_arxiv,
    description="ArXiv에서 학술 논문을 검색합니다. 과학적, 기술적 주제에 대한 학술 연구에 유용합니다."
)


def get_search_tools() -> List[FunctionTool]:
    """검색 도구 목록을 반환합니다
    
    Returns:
        FunctionTool 목록
    """
    return [web_search_tool, duckduckgo_search_tool, naver_news_search_tool, wikipedia_search_tool, arxiv_search_tool]