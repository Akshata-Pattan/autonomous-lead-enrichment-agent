import json

from src.crawler import crawl_homepage, crawl_relevant_pages
from src.llm import extract_company_intelligence


DOMAINS = [
    "postman.com",
    "supabase.com",
    "vapi.ai",
]


def process_domain(domain: str) -> dict:
    homepage, initial_links = crawl_homepage(domain)

    crawled_pages = crawl_relevant_pages(
        homepage,
        initial_links,
        max_pages=10,
    )

    all_text = []

    for url, text in crawled_pages:
        all_text.append(
            f"PAGE URL: {url}\n{text}"
        )

    website_content = "\n\n".join(all_text)

    # Keep the LLM request within the free-tier token limit.
    max_chars = 24000
    website_content = website_content[:max_chars]

    result = extract_company_intelligence(
        domain,
        website_content,
    )

    return result.model_dump()


def main() -> None:
    results = []

    for domain in DOMAINS:
        print(f"\nProcessing: {domain}")

        try:
            result = process_domain(domain)
            results.append(result)
            print("Success")

        except Exception as error:
            print(f"[FAILED] {domain} -> {error}")

    with open(
        "output/output.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print("\nFinished.")
    print(
        f"Successful domains: "
        f"{len(results)}/{len(DOMAINS)}"
    )


if __name__ == "__main__":
    main()