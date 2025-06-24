"""
Example usage of the top_news agent.
"""

from src.top_news.agent import top_news

if __name__ == "__main__":
    # Fetch and print the top 5 news stories of the day
    result = top_news(5)
    print(result)
