#!/usr/bin/env python3
"""Script to analyze stories from the API and check for shared articles."""

import httpx
from collections import defaultdict

API_URL = "http://context-dev-api-alb-1959489086.eu-west-2.elb.amazonaws.com/stories/"


def main():
    response = httpx.get(API_URL)
    response.raise_for_status()
    stories = response.json()

    print(f"Total number of stories: {len(stories)}")
    print("=" * 80)

    # Track which stories each article URL appears in
    url_to_stories: dict[str, list[str]] = defaultdict(list)

    for story in stories:
        story_id = story.get("id", "unknown")
        story_title = story.get("title", "No title")
        articles = story.get("articles", [])

        print(f"\nStory: {story_title}")
        print(f"  ID: {story_id}")
        print(f"  Articles ({len(articles)}):")

        for article in articles:
            article_url = article.get("url", "No URL")
            article_title = article.get("title", "No title")
            print(f"    - {article_title}")
            print(f"      URL: {article_url}")

            # Track this URL
            url_to_stories[article_url].append(story_title)

    # Check for shared articles
    print("\n" + "=" * 80)
    print("SHARED ARTICLES CHECK")
    print("=" * 80)

    shared_articles = {url: story_list for url, story_list in url_to_stories.items() if len(story_list) > 1}

    if shared_articles:
        print(f"\nFound {len(shared_articles)} article(s) shared between stories:\n")
        for url, story_list in shared_articles.items():
            print(f"URL: {url}")
            print(f"  Shared by {len(story_list)} stories:")
            for story_title in story_list:
                print(f"    - {story_title}")
            print()
    else:
        print("\nNo articles are shared between stories.")


if __name__ == "__main__":
    main()
