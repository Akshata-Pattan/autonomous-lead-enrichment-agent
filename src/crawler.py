from urllib.parse import urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


RELEVANT_KEYWORDS = {
    "team": 10,
    "leadership": 10,
    "founder": 9,
    "founders": 9,
    "people": 8,
    "executive": 8,
    "management": 7,
    "about": 6,
    "company": 6,
    "contact": 6,
    "pricing": 4,
    "product": 3,
    "solutions": 3,
    "customers": 3,
    "careers": 2,
}

EXCLUDED_KEYWORDS = {
    "privacy",
    "terms",
    "cookie",
    "login",
    "signup",
    "signin",
}


def normalize_url(base_url: str, href: str) -> str | None:
    if not href:
        return None

    absolute_url = urljoin(base_url, href)
    parsed = urlparse(absolute_url)

    if parsed.scheme not in {"http", "https"}:
        return None

    clean_url = urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path.rstrip("/"),
            "",
            parsed.query,
            "",
        )
    )

    return clean_url


def is_same_domain(url: str, base_url: str) -> bool:
    url_host = urlparse(url).hostname
    base_host = urlparse(base_url).hostname

    if not url_host or not base_host:
        return False

    return url_host.removeprefix("www.") == base_host.removeprefix("www.")


def score_link(url: str, anchor_text: str) -> int:
    text = f"{url} {anchor_text}".lower()

    if any(keyword in text for keyword in EXCLUDED_KEYWORDS):
        return -1

    score = 0

    for keyword, points in RELEVANT_KEYWORDS.items():
        if keyword in text:
            score += points

    return score


def discover_relevant_links(
    page,
    base_url: str,
    max_links: int = 8,
) -> list[str]:
    discovered: dict[str, int] = {}

    for link in page.locator("a[href]").all():
        try:
            href = link.get_attribute("href")
            anchor_text = link.inner_text().strip()
        except Exception:
            continue

        url = normalize_url(base_url, href)

        if not url or not is_same_domain(url, base_url):
            continue

        score = score_link(url, anchor_text)

        if score > 0:
            discovered[url] = max(
                score,
                discovered.get(url, 0),
            )

    ranked_links = sorted(
        discovered.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return [url for url, _ in ranked_links[:max_links]]


def crawl_homepage(domain: str) -> tuple[str, list[str]]:
    base_url = f"https://{domain}"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)

        try:
            page = browser.new_page()

            page.goto(
                base_url,
                wait_until="domcontentloaded",
                timeout=30000,
            )

            links = discover_relevant_links(
                page,
                base_url,
                max_links=8,
            )

            return page.url, links

        finally:
            browser.close()


def crawl_relevant_pages(
    homepage: str,
    initial_links: list[str],
    max_pages: int = 10,
) -> list[tuple[str, str]]:
    pages_to_visit = list(initial_links)
    visited: set[str] = set()
    collected: list[tuple[str, str]] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)

        try:
            page = browser.new_page()

            while pages_to_visit and len(collected) < max_pages:
                url = pages_to_visit.pop(0)

                if url in visited:
                    continue

                visited.add(url)

                try:
                    response = page.goto(
                        url,
                        wait_until="domcontentloaded",
                        timeout=30000,
                    )

                    if not response or not response.ok:
                        continue

                    text = extract_clean_text(page)

                    if text:
                        collected.append((url, text))

                    deeper_links = discover_relevant_links(
                        page,
                        homepage,
                        max_links=5,
                    )

                    for deeper_link in deeper_links:
                        if (
                            deeper_link not in visited
                            and deeper_link not in pages_to_visit
                        ):
                            pages_to_visit.append(deeper_link)

                except Exception as error:
                    print(
                        f"[ERROR] {homepage} - {url} -> {error}"
                    )

        finally:
            browser.close()

    return collected


def extract_clean_text(page) -> str:
    html = page.content()

    soup = BeautifulSoup(html, "lxml")

    for element in soup(
        [
            "script",
            "style",
            "svg",
            "noscript",
            "nav",
            "footer",
        ]
    ):
        element.decompose()

    main_content = soup.find("main")

    if main_content:
        text = main_content.get_text(
            separator=" ",
            strip=True,
        )
    else:
        text = soup.get_text(
            separator=" ",
            strip=True,
        )

    return " ".join(text.split())