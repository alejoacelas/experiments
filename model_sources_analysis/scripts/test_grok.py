#!/usr/bin/env python3
"""
Test Grok with web search
"""
import os
import json
from datetime import datetime
from xai_sdk import Client
from xai_sdk.tools import web_search

TEST_PROMPTS = [
    "What's the predicted weather in SF for Nov 24?",
    "What's the current Alibaba stock price?",
    "Who won the latest Nobel Prize in Physics?"
]

def test_grok(prompt, prompt_idx):
    """Test Grok 4 with web search"""
    print(f"\n{'='*60}")
    print(f"Testing Grok 4 - Prompt {prompt_idx+1}")
    print(f"{'='*60}")
    print(f"Prompt: {prompt}")

    try:
        client = Client(
            api_key=os.getenv("XAI_API_KEY"),
            timeout=3600
        )

        # Test both grok-4-fast and grok-4
        for model_name in ["grok-4-fast", "grok-4"]:
            try:
                print(f"Trying model: {model_name}")

                chat = client.chat.create(
                    model=model_name,
                    tools=[web_search()],
                )

                # Append message using the user() helper
                from xai_sdk.chat import user
                chat.append(user(prompt))
                response = chat.sample()

                print(f"✓ Success with {model_name}")

                # Extract response info
                response_dict = {
                    "provider": "grok",
                    "model": model_name,
                    "prompt": prompt,
                    "prompt_index": prompt_idx,
                    "timestamp": datetime.now().isoformat(),
                    "response": {
                        "content": response.content if hasattr(response, 'content') else str(response),
                        "tool_calls": [],
                        "chat_history": []
                    }
                }

                # Get chat history
                for msg in chat.messages:
                    msg_dict = {
                        "role": msg.role if hasattr(msg, 'role') else None,
                        "content": msg.content if hasattr(msg, 'content') else None,
                    }
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        msg_dict["tool_calls"] = [
                            {
                                "id": tc.id if hasattr(tc, 'id') else None,
                                "type": tc.type if hasattr(tc, 'type') else None,
                                "function": {
                                    "name": tc.function.name if hasattr(tc.function, 'name') else None,
                                    "arguments": tc.function.arguments if hasattr(tc.function, 'arguments') else None,
                                } if hasattr(tc, 'function') else None
                            }
                            for tc in msg.tool_calls
                        ]
                    if hasattr(msg, 'tool_call_id'):
                        msg_dict["tool_call_id"] = msg.tool_call_id
                    response_dict["response"]["chat_history"].append(msg_dict)

                # Save to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"grok_{model_name.replace('-', '_')}_prompt{prompt_idx+1}_{timestamp}.json"
                filepath = f"/home/user/experiments/model_sources_analysis/raw_responses/{filename}"

                with open(filepath, 'w') as f:
                    json.dump(response_dict, f, indent=2, default=str)

                print(f"✓ Saved to {filename}")
                print(f"\nResponse content: {str(response.content)[:200] if hasattr(response, 'content') else 'N/A'}...")

                return response_dict

            except Exception as e:
                print(f"❌ Failed with {model_name}: {e}")
                import traceback
                traceback.print_exc()
                continue

        print("❌ All model names failed")
        return None

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("Testing Grok with web search")
    for idx, prompt in enumerate(TEST_PROMPTS):
        result = test_grok(prompt, idx)
        if result:
            print(f"✓ Prompt {idx+1} completed successfully")
        else:
            print(f"❌ Prompt {idx+1} failed")
