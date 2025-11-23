#!/usr/bin/env python3
"""
Test all model providers with web search and save raw responses.
"""

import os
import json
import time
from datetime import datetime

# Define test prompts
TEST_PROMPTS = [
    "What's the predicted weather in SF for Nov 24?",
    "What's the current Alibaba stock price?",
    "Who won the latest Nobel Prize in Physics?"
]

def save_response(provider, prompt_idx, response_data):
    """Save raw response to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{provider}_prompt{prompt_idx+1}_{timestamp}.json"
    filepath = f"/home/user/experiments/model_sources_analysis/raw_responses/{filename}"

    with open(filepath, 'w') as f:
        json.dump(response_data, f, indent=2, default=str)

    print(f"✓ Saved {provider} response for prompt {prompt_idx+1} to {filename}")
    return filepath

def test_claude_haiku(prompt, prompt_idx):
    """Test Claude Haiku 4.5 with web search"""
    import anthropic

    print(f"\n{'='*60}")
    print(f"Testing Claude Haiku 4.5 - Prompt {prompt_idx+1}")
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

        filepath = save_response("claude_haiku", prompt_idx, response_dict)

        print(f"\nResponse preview:")
        print(f"Model: {response.model}")
        print(f"Stop reason: {response.stop_reason}")
        print(f"Content blocks: {len(response.content)}")

        return response_dict

    except Exception as e:
        print(f"❌ Error testing Claude: {e}")
        return {"error": str(e), "provider": "claude-haiku-4.5", "prompt": prompt}

def test_qwen3_max(prompt, prompt_idx):
    """Test Qwen3-max with web search"""
    import dashscope

    print(f"\n{'='*60}")
    print(f"Testing Qwen3-max - Prompt {prompt_idx+1}")
    print(f"{'='*60}")
    print(f"Prompt: {prompt}")

    try:
        dashscope.base_http_api_url = "https://dashscope-intl.aliyuncs.com/api/v1"

        response = dashscope.Generation.call(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            model="qwen3-max",
            messages=[{"role": "user", "content": prompt}],
            enable_search=True,
            search_options={
                "search_strategy": "agent",
                "enable_source": True
            },
            result_format="message",
        )

        # Convert response to dict for saving
        response_dict = {
            "provider": "qwen3-max",
            "prompt": prompt,
            "prompt_index": prompt_idx,
            "timestamp": datetime.now().isoformat(),
            "response": response if isinstance(response, dict) else vars(response)
        }

        filepath = save_response("qwen3_max", prompt_idx, response_dict)

        print(f"\nResponse preview:")
        print(f"Request ID: {response.get('request_id', 'N/A')}")
        print(f"Output: {str(response.get('output', {}))[:100]}...")

        return response_dict

    except Exception as e:
        print(f"❌ Error testing Qwen3: {e}")
        return {"error": str(e), "provider": "qwen3-max", "prompt": prompt}

def test_gemini_flash(prompt, prompt_idx):
    """Test Gemini 2.5 Flash with web search"""
    from google import genai
    from google.genai import types

    print(f"\n{'='*60}")
    print(f"Testing Gemini 2.5 Flash - Prompt {prompt_idx+1}")
    print(f"{'='*60}")
    print(f"Prompt: {prompt}")

    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ]

        tools = [types.Tool(google_search=types.GoogleSearch())]

        generate_content_config = types.GenerateContentConfig(
            tools=tools,
        )

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=contents,
            config=generate_content_config,
        )

        # Convert response to dict for saving
        response_dict = {
            "provider": "gemini-2.5-flash",
            "prompt": prompt,
            "prompt_index": prompt_idx,
            "timestamp": datetime.now().isoformat(),
            "response": {
                "text": response.text if hasattr(response, 'text') else None,
                "candidates": [
                    {
                        "content": {
                            "parts": [{"text": part.text} if hasattr(part, 'text') else str(part) for part in candidate.content.parts]
                        } if hasattr(candidate, 'content') else None,
                        "grounding_metadata": candidate.grounding_metadata if hasattr(candidate, 'grounding_metadata') else None,
                    }
                    for candidate in (response.candidates if hasattr(response, 'candidates') else [])
                ]
            }
        }

        filepath = save_response("gemini_flash", prompt_idx, response_dict)

        print(f"\nResponse preview:")
        print(f"Text: {response.text[:100] if hasattr(response, 'text') else 'N/A'}...")

        return response_dict

    except Exception as e:
        print(f"❌ Error testing Gemini: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "provider": "gemini-2.5-flash", "prompt": prompt}

def test_grok_4(prompt, prompt_idx):
    """Test Grok 4 with web search"""
    from xai_sdk import Client
    from xai_sdk.tools import web_search

    print(f"\n{'='*60}")
    print(f"Testing Grok 4 - Prompt {prompt_idx+1}")
    print(f"{'='*60}")
    print(f"Prompt: {prompt}")

    try:
        client = Client(
            api_key=os.getenv("XAI_API_KEY"),
            timeout=3600
        )

        chat = client.chat.create(
            model="grok-4-fast",
            tools=[web_search()],
        )

        chat.append({"role": "user", "content": prompt})
        response = chat.sample()

        # Convert response to dict for saving
        response_dict = {
            "provider": "grok-4",
            "prompt": prompt,
            "prompt_index": prompt_idx,
            "timestamp": datetime.now().isoformat(),
            "response": {
                "content": response.content if hasattr(response, 'content') else str(response),
                "raw": vars(response) if hasattr(response, '__dict__') else str(response),
                "chat_history": [vars(msg) if hasattr(msg, '__dict__') else str(msg) for msg in chat.messages]
            }
        }

        filepath = save_response("grok_4", prompt_idx, response_dict)

        print(f"\nResponse preview:")
        print(f"Content: {str(response.content)[:100] if hasattr(response, 'content') else 'N/A'}...")

        return response_dict

    except Exception as e:
        print(f"❌ Error testing Grok: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "provider": "grok-4", "prompt": prompt}

def main():
    """Run tests for all providers"""
    print("="*60)
    print("MODEL PROVIDER WEB SEARCH SOURCE ANALYSIS")
    print("="*60)
    print(f"Testing {len(TEST_PROMPTS)} prompts across 4 providers")
    print(f"Total tests: {len(TEST_PROMPTS) * 4}")

    results = {
        "claude_haiku": [],
        "qwen3_max": [],
        "gemini_flash": [],
        "grok_4": []
    }

    # Test each prompt across all providers
    for idx, prompt in enumerate(TEST_PROMPTS):
        print(f"\n\n{'#'*60}")
        print(f"PROMPT {idx+1}/{len(TEST_PROMPTS)}: {prompt}")
        print(f"{'#'*60}")

        # Test Claude Haiku
        try:
            results["claude_haiku"].append(test_claude_haiku(prompt, idx))
        except Exception as e:
            print(f"❌ Failed Claude Haiku: {e}")
            results["claude_haiku"].append({"error": str(e), "provider": "claude-haiku-4.5", "prompt": prompt})
        time.sleep(2)  # Rate limiting

        # Test Qwen3-max
        try:
            results["qwen3_max"].append(test_qwen3_max(prompt, idx))
        except Exception as e:
            print(f"❌ Failed Qwen3-max: {e}")
            results["qwen3_max"].append({"error": str(e), "provider": "qwen3-max", "prompt": prompt})
        time.sleep(2)

        # Test Gemini Flash
        try:
            results["gemini_flash"].append(test_gemini_flash(prompt, idx))
        except Exception as e:
            print(f"❌ Failed Gemini Flash: {e}")
            results["gemini_flash"].append({"error": str(e), "provider": "gemini-2.5-flash", "prompt": prompt})
        time.sleep(2)

        # Test Grok 4
        try:
            results["grok_4"].append(test_grok_4(prompt, idx))
        except Exception as e:
            print(f"❌ Failed Grok 4: {e}")
            results["grok_4"].append({"error": str(e), "provider": "grok-4", "prompt": prompt})
        time.sleep(2)

    # Save summary
    summary_file = f"/home/user/experiments/model_sources_analysis/raw_responses/summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, 'w') as f:
        json.dump({
            "test_prompts": TEST_PROMPTS,
            "results_summary": {
                provider: [
                    {
                        "prompt_idx": i,
                        "has_error": "error" in r,
                        "error": r.get("error") if "error" in r else None
                    }
                    for i, r in enumerate(results_list)
                ]
                for provider, results_list in results.items()
            },
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)

    print(f"\n\n{'='*60}")
    print("TESTING COMPLETE")
    print(f"{'='*60}")
    print(f"Summary saved to: {summary_file}")
    print("\nAll raw responses saved to: /home/user/experiments/model_sources_analysis/raw_responses/")

if __name__ == "__main__":
    main()
