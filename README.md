
# Autonomous Lead Enrichment Agent

A Python-based autonomous lead enrichment agent that crawls public company websites, extracts relevant information, and uses an LLM to generate structured company intelligence.

## Features

- Automated website crawling using Playwright
- Relevant subpage discovery
- Deeper relevant-page discovery
- Clean text extraction from web pages
- Removes scripts, styles, SVGs, navigation, and footer content
- LLM-based company intelligence extraction
- Structured JSON validation using Pydantic
- Graceful handling of page-level failures
- Processes multiple company domains independently

## Extracted Information

For each company, the agent extracts:

- Company overview
- Target audience / Ideal Customer Profile (ICP)
- Public or generic contact email addresses
- Key leadership/team members
- Leadership roles/titles
- LinkedIn URLs when explicitly available
- Data confidence score from 0.0 to 1.0

## Architecture

Company Domains
      |
      v
Playwright Browser
      |
      v
Homepage Crawling
      |
      v
Relevant Page Discovery
      |
      v
Deeper Page Discovery
      |
      v
Clean Text Extraction
      |
      v
Context Size Limiting
      |
      v
Groq LLM
      |
      v
JSON Response
      |
      v
Pydantic Validation
      |
      v
output/output.json

## Project Structure

autonomous-lead-enrichment-agent/
|
├── data/
│   └── input_domains.json
|
├── output/
│   └── output.json
|
├── src/
│   ├── crawler.py
│   ├── llm.py
│   ├── models.py
│   └── prompts.py
|
├── tests/
|
├── main.py
├── requirements.txt
├── .gitignore
├── README.md
└── .env

## Requirements

- Python 3.10+
- Internet connection
- Groq API key
- Playwright Chromium browser

## Installation

Clone the repository and move into the project directory.

    git clone <https://github.com/Akshata-Pattan/autonomous-lead-enrichment-agent>
    cd autonomous-lead-enrichment-agent

Create a virtual environment.

    python -m venv venv

Activate the virtual environment on Windows.

    venv\Scripts\activate

Install dependencies.

    pip install -r requirements.txt

Install the Playwright Chromium browser.

    playwright install chromium

## Environment Setup

Create a .env file in the project root.

    GROQ_API_KEY=your_groq_api_key

Never commit the .env file or expose the API key publicly.

## Input

The default test domains are stored in:

data/input_domains.json

Example:

    [
      "postman.com",
      "supabase.com",
      "vapi.ai"
    ]

Additional company domains can be added to this file.

## Running the Agent

From the project root, run:

    python main.py

The agent processes each domain independently and saves the results to:

output/output.json

## Output

The generated JSON contains:

- Domain
- Company overview
- Target audience
- Public contact points
- Leadership/team members
- Leadership roles
- LinkedIn URLs when available
- Confidence score

## Error Handling

The agent is designed so that a failure on one page or company does not stop the complete pipeline.

It handles situations such as:

- Page timeouts
- Failed HTTP responses
- Individual page crawling failures
- Missing page content
- Missing contact information
- Missing leadership information
- Missing LinkedIn URLs
- Partial company information

If one domain fails, the remaining domains continue processing.

## LLM and Structured Output

The project uses the Groq API with the openai/gpt-oss-20b model.

The LLM receives cleaned website text instead of raw HTML. The response is requested as JSON and validated using Pydantic before being written to the final output.

The extraction prompt instructs the model not to invent unsupported names, roles, emails, LinkedIn URLs, or company facts.

## Context Preprocessing

Raw HTML is not directly sent to the LLM.

The crawler removes unnecessary elements such as:

- JavaScript
- CSS
- SVG elements
- Navigation
- Footer content
- Other non-essential page markup

The remaining content is converted into clean text and limited before being sent to the LLM to control context size and API usage.

## Test Domains

The implementation was tested against:

- postman.com
- supabase.com
- vapi.ai

The final pipeline successfully processed all three test domains.

## Technologies Used

- Python
- Playwright
- BeautifulSoup
- lxml
- Groq
- Pydantic
- python-dotenv

## Future Improvements

Possible extensions include:

- External search integration for LinkedIn discovery
- Token and API cost tracking
- More advanced agentic workflows
- Additional website fallback strategies
- More sophisticated relevance ranking for discovered pages

## Author

**Akshata Pattan**

AI/ML Undergraduate

LinkedIn: linkedin.com/in/akshata-pattan-b39832342
GitHub: github.com/Akshata-Pattan
