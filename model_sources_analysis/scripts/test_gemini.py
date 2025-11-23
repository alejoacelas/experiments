#!/usr/bin/env python3
"""
Test Gemini with web search
"""
import os
import json
from datetime import datetime
from google import genai
from google.genai import types

TEST_PROMPTS = [
    "What's the predicted weather in SF for Nov 24?",
    "What's the current Alibaba stock price?",
    "Who won the latest Nobel Prize in Physics?"
]

def test_gemini(prompt, prompt_idx):
    """Test Gemini 2.0 Flash with web search"""
    print(f"\n{'='*60}")
    print(f"Testing Gemini 2.0 Flash - Prompt {prompt_idx+1}")
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

        # Try different model names
        model_names = ["gemini-2.0-flash-exp", "gemini-flash-latest", "gemini-1.5-flash"]

        for model_name in model_names:
            try:
                print(f"Trying model: {model_name}")
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=generate_content_config,
                )
                print(f"✓ Success with {model_name}")

                # Save response
                response_dict = {
                    "provider": "gemini",
                    "model": model_name,
                    "prompt": prompt,
                    "prompt_index": prompt_idx,
                    "timestamp": datetime.now().isoformat(),
                    "response": {
                        "text": response.text if hasattr(response, 'text') else None,
                        "candidates": []
                    }
                }

                # Extract grounding metadata
                if hasattr(response, 'candidates'):
                    for candidate in response.candidates:
                        cand_dict = {
                            "content": None,
                            "grounding_metadata": None,
                        }
                        if hasattr(candidate, 'content') and candidate.content:
                            cand_dict["content"] = {
                                "parts": [{"text": part.text} if hasattr(part, 'text') else str(part) for part in candidate.content.parts]
                            }
                        if hasattr(candidate, 'grounding_metadata'):
                            meta = candidate.grounding_metadata
                            if meta:
                                cand_dict["grounding_metadata"] = {
                                    "search_entry_point": str(meta.search_entry_point) if hasattr(meta, 'search_entry_point') else None,
                                    "grounding_chunks": []
                                }
                                if hasattr(meta, 'grounding_chunks'):
                                    for chunk in meta.grounding_chunks:
                                        chunk_dict = {
                                            "web": None
                                        }
                                        if hasattr(chunk, 'web'):
                                            chunk_dict["web"] = {
                                                "uri": chunk.web.uri if hasattr(chunk.web, 'uri') else None,
                                                "title": chunk.web.title if hasattr(chunk.web, 'title') else None,
                                            }
                                        cand_dict["grounding_metadata"]["grounding_chunks"].append(chunk_dict)

                        response_dict["response"]["candidates"].append(cand_dict)

                # Save to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"gemini_{model_name.replace('-', '_')}_prompt{prompt_idx+1}_{timestamp}.json"
                filepath = f"/home/user/experiments/model_sources_analysis/raw_responses/{filename}"

                with open(filepath, 'w') as f:
                    json.dump(response_dict, f, indent=2, default=str)

                print(f"✓ Saved to {filename}")
                print(f"\nResponse text: {response.text[:200] if hasattr(response, 'text') else 'N/A'}...")

                return response_dict

            except Exception as e:
                print(f"❌ Failed with {model_name}: {e}")
                continue

        print("❌ All model names failed")
        return None

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("Testing Gemini with web search")
    for idx, prompt in enumerate(TEST_PROMPTS):
        result = test_gemini(prompt, idx)
        if result:
            print(f"✓ Prompt {idx+1} completed successfully")
        else:
            print(f"❌ Prompt {idx+1} failed")
