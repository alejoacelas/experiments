# Model Provider Web Search Source URLs Analysis

Analysis of how different AI model provider APIs expose web search source URLs and handle citation generation.

## Project Structure

```
model_sources_analysis/
├── raw_responses/          # Raw API response JSON files and rendered markdown
│   ├── claude_haiku_*.json
│   ├── qwen3_max_*.json
│   └── *_rendered.md
├── scripts/                # Analysis and testing scripts
│   ├── test_all_providers.py
│   ├── test_gemini.py
│   ├── test_grok.py
│   ├── analyze_claude_sources.py
│   └── test_claude_with_markdown_request.py
└── reports/                # Final analysis reports
    ├── executive_summary.md          # <600 word summary
    └── model_source_urls_analysis.md # Full detailed report
```

## Quick Start

View the reports:
- **Executive Summary** (599 words): `reports/executive_summary.md`
- **Detailed Analysis** (852 words): `reports/model_source_urls_analysis.md`

## Key Findings

- **Claude Haiku 4.5**: ✓ Full source URL access, 100% accurate markdown link generation
- **Qwen3-max**: ✗ Web search did not trigger
- **Gemini 2.5 Flash**: ✗ API access denied (403)
- **Grok 4**: ✗ SSL connection failures

## Running the Analysis

```bash
# Install dependencies
pip install anthropic dashscope google-genai xai-sdk

# Set API keys
export ANTHROPIC_API_KEY="your-key"
export DASHSCOPE_API_KEY="your-key"
export GEMINI_API_KEY="your-key"
export XAI_API_KEY="your-key"

# Run tests
python scripts/test_all_providers.py
python scripts/test_claude_with_markdown_request.py
python scripts/analyze_claude_sources.py
```

## Artifacts

- **10 raw API responses** (JSON)
- **7 rendered markdown files** with sources
- **5 analysis scripts** (Python)
- **2 comprehensive reports**
