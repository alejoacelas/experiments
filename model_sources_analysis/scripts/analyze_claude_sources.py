#!/usr/bin/env python3
"""
Analyze Claude Haiku responses and render sources as markdown links
"""
import os
import json
import glob

def extract_sources_from_claude(response_data):
    """Extract source URLs and metadata from Claude response"""
    sources = []

    if 'response' not in response_data:
        return sources

    content_blocks = response_data['response'].get('content', [])

    for block in content_blocks:
        if block.get('type') == 'web_search_tool_result':
            # This block contains the search results
            search_results = block.get('content', [])
            for result in search_results:
                if result.get('type') == 'web_search_result':
                    sources.append({
                        'title': result.get('title', 'Untitled'),
                        'url': result.get('url', ''),
                        'page_age': result.get('page_age'),
                    })

    return sources

def render_claude_response_with_sources(response_data):
    """Render Claude response with inline markdown source links"""
    if 'response' not in response_data:
        return None

    content_blocks = response_data['response'].get('content', [])

    # Extract all text blocks and concatenate them
    text_blocks = []
    sources = []

    for block in content_blocks:
        if block.get('type') == 'text':
            text_blocks.append(block.get('text', ''))
        elif block.get('type') == 'web_search_tool_result':
            search_results = block.get('content', [])
            for result in search_results:
                if result.get('type') == 'web_search_result':
                    sources.append({
                        'title': result.get('title', 'Untitled'),
                        'url': result.get('url', ''),
                        'page_age': result.get('page_age'),
                    })

    # Concatenate all text blocks
    response_text = ''.join(text_blocks)

    if not response_text:
        return None

    # Render response with sources appended
    output = f"{response_text}\n\n"

    if sources:
        output += "**Sources:**\n\n"
        for i, source in enumerate(sources, 1):
            age_str = f" ({source['page_age']})" if source['page_age'] else ""
            output += f"{i}. [{source['title']}]({source['url']}){age_str}\n"

    return output

def analyze_all_claude_responses():
    """Analyze all Claude response files"""
    response_files = glob.glob('/home/user/experiments/model_sources_analysis/raw_responses/claude_haiku*.json')

    print(f"Found {len(response_files)} Claude Haiku response files\n")
    print("="*60)

    for file_path in sorted(response_files):
        print(f"\nFile: {os.path.basename(file_path)}")
        print("-"*60)

        with open(file_path, 'r') as f:
            data = json.load(f)

        prompt = data.get('prompt', 'Unknown prompt')
        print(f"Prompt: {prompt}\n")

        # Extract sources
        sources = extract_sources_from_claude(data)
        print(f"Number of sources found: {len(sources)}\n")

        if sources:
            print("Source URLs:")
            for i, source in enumerate(sources, 1):
                print(f"  {i}. {source['url']}")
                print(f"     Title: {source['title']}")
                if source['page_age']:
                    print(f"     Age: {source['page_age']}")
                print()

        # Render with markdown
        rendered = render_claude_response_with_sources(data)
        if rendered:
            # Save rendered version
            output_file = file_path.replace('.json', '_rendered.md')
            with open(output_file, 'w') as f:
                f.write(f"# Prompt: {prompt}\n\n")
                f.write(rendered)
            print(f"✓ Saved rendered version to: {os.path.basename(output_file)}")

        print("="*60)

if __name__ == "__main__":
    analyze_all_claude_responses()
