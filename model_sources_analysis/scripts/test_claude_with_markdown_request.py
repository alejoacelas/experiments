#!/usr/bin/env python3
"""
Test Claude's ability to generate markdown links itself
"""
import os
import json
from datetime import datetime
import anthropic

TEST_PROMPTS = [
    "What's the predicted weather in SF for Nov 24? Please provide markdown links [like this](url) to your sources inline in your response.",
    "What's the current Alibaba stock price? Include markdown-formatted source links [like this](url) in your answer.",
    "Who won the latest Nobel Prize in Physics? Provide markdown links to sources inline in your response."
]

def test_claude_with_markdown_request(prompt, prompt_idx):
    """Test Claude with explicit request for markdown links"""
    print(f"\n{'='*60}")
    print(f"Testing Claude Haiku 4.5 with Markdown Request - Prompt {prompt_idx+1}")
    print(f"{'='*60}")
    print(f"Prompt: {prompt}")

    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            tools=[{
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 5
            }]
        )

        # Convert response to dict for saving
        response_dict = {
            "provider": "claude-haiku-4.5",
            "prompt": prompt,
            "prompt_index": prompt_idx,
            "timestamp": datetime.now().isoformat(),
            "response": response.model_dump()
        }

        # Save response
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"claude_haiku_markdown_request_prompt{prompt_idx+1}_{timestamp}.json"
        filepath = f"/home/user/experiments/model_sources_analysis/raw_responses/{filename}"

        with open(filepath, 'w') as f:
            json.dump(response_dict, f, indent=2, default=str)

        print(f"✓ Saved to {filename}")

        # Extract and display text response
        text_blocks = []
        for block in response.content:
            if block.type == 'text':
                text_blocks.append(block.text)

        full_text = ''.join(text_blocks)
        print(f"\nFull Response:\n{full_text}\n")

        # Extract source URLs from web_search_tool_result
        api_sources = []
        for block in response.content:
            if block.type == 'tool_result':
                for item in block.content:
                    if hasattr(item, 'url'):
                        api_sources.append(item.url)

        print(f"\nAPI-provided sources ({len(api_sources)}):")
        for i, url in enumerate(api_sources, 1):
            print(f"  {i}. {url}")

        # Check if response contains markdown links
        import re
        markdown_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', full_text)

        print(f"\nMarkdown links in response ({len(markdown_links)}):")
        for link_text, link_url in markdown_links:
            print(f"  [{link_text}]({link_url})")
            # Check if this URL matches any API-provided source
            if link_url in api_sources:
                print(f"    ✓ Matches API source")
            else:
                print(f"    ❌ Does NOT match API sources (possible hallucination)")

        return response_dict

    except Exception as e:
        print(f"❌ Error testing Claude: {e}")
        return {"error": str(e), "provider": "claude-haiku-4.5", "prompt": prompt}

if __name__ == "__main__":
    print("Testing Claude's ability to generate markdown links")
    for idx, prompt in enumerate(TEST_PROMPTS):
        test_claude_with_markdown_request(prompt, idx)
        print("\n")
