# Model Provider Web Search Source URLs Analysis
## Executive Summary Report

**Date:** November 23, 2025
**Models Tested:** Claude Haiku 4.5, Qwen3-max, Gemini 2.5 Flash, Grok 4

Each provider was tested with three web search queries: SF weather forecast, Alibaba stock price, and Nobel Prize winners. Non-streaming API calls captured complete responses for source URL analysis.

### Key Findings by Provider

**Claude Haiku 4.5 ✓ Success**

Claude provides comprehensive source access through structured `web_search_tool_result` blocks. Each result includes:
- Full source URL (plaintext, not encrypted)
- Page title
- Optional page age indicator (e.g., "3 days ago")

Average of 10 sources per query. URLs are easily accessible at `response.content[].web_search_tool_result.content[].url`.

**Qwen3-max ✗ Non-functional**

Despite proper API configuration with `enable_search=True` and `enable_source=True`, web search did not trigger. The `search_info.search_results` array remained empty across all queries. Model provided generic responses directing users to external websites.

**Gemini 2.5 Flash ✗ Access Denied**

All API requests failed with HTTP 403 Forbidden errors across multiple model variants (`gemini-2.0-flash-exp`, `gemini-flash-latest`, `gemini-1.5-flash`). API key lacks necessary permissions for Google Search tool feature.

**Grok 4 ✗ Connection Failure**

Both `grok-4-fast` and `grok-4` failed with SSL certificate verification errors, preventing connection to xAI's gRPC endpoints. Environment-specific certificate chain issue.

### Markdown Source Rendering

Successfully implemented programmatic markdown rendering for Claude responses. The script:
- Concatenates all text blocks from multi-part responses
- Extracts source URLs from `web_search_tool_result` blocks
- Appends numbered Sources section with markdown links and page age metadata

**Example Output:**
```markdown
Based on the National Weather Service forecast, SF on Nov 24 will be sunny...

**Sources:**
1. [National Weather Service](https://forecast.weather.gov/...)
2. [AccuWeather SF November](https://www.accuweather.com/...) (2 days ago)
```

### Model Self-Citation Testing

When explicitly prompted to include markdown links (e.g., "Please provide markdown links [like this](url) to your sources"), Claude Haiku 4.5:

- **Successfully generated inline markdown citations** in all three test cases
- **Selected relevant sources** (typically 1-5 from the 10 available) rather than dumping all results
- **Provided descriptive link text** like "National Weather Service" instead of raw URLs
- **Achieved 100% accuracy** - every model-generated link matched the API-provided source URLs

### Critical Finding: No Link Hallucination

Across all three prompts, **100% of Claude's model-generated markdown links matched the URLs in the API grounding metadata**. Claude did not fabricate or hallucinate any URLs. When asked to cite sources, it correctly selected from and accurately transcribed the web search results provided by the API.

Example verification (Nobel Prize prompt):
- Model generated 5 markdown links
- All 5 URLs matched API-provided sources exactly
- Links included: nobelprize.org, universityofcalifornia.edu, berkeley.edu, aljazeera.com

### Implementation Recommendations

1. **Claude Haiku 4.5 is production-ready** for applications requiring AI responses with verifiable source citations.

2. **Request explicit markdown formatting** from the model rather than post-processing. The model naturally generates well-formatted citations when prompted.

3. **Source URL structure** is developer-friendly: direct JSON access, no decryption needed, includes useful metadata.

4. **Verify API access** before deploying Gemini or Grok implementations, as permission and connectivity issues may vary by environment.

5. **Investigate Qwen3-max trigger conditions** if considering deployment, as web search activation behavior needs clarification.

### Conclusion

Of the four providers tested, only Claude Haiku 4.5 successfully provided accessible source URLs and demonstrated reliable markdown citation generation without hallucination. The structured API response format makes both programmatic rendering and model self-citation straightforward to implement. Access limitations prevented full evaluation of Gemini and Grok, while Qwen3-max requires further investigation of web search activation conditions.

---

**Generated Assets:**
- 10 raw API response JSON files (Claude + Qwen)
- 4 rendered markdown files with sources
- 5 analysis and testing Python scripts
- Complete findings in 852-word detailed report: `model_source_urls_analysis.md`
