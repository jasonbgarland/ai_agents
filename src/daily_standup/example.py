#!/usr/bin/env python3
"""
Example usage script for the Daily Standup Agent.

This script demonstrates how to use the daily_standup agent to process
natural language status updates into structured daily standup reports.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from daily_standup import daily_standup, format_daily_status


def main():
    """Run example usage of the daily standup agent."""
    print("Daily Standup Agent - Example Usage")
    print("=" * 40)
    
    # Example 1: Complete status update
    print("\n📅 Example 1: Complete Status Update")
    status1 = "Yesterday I worked on the login feature and fixed some bugs. Today I will continue with the login feature and start on the signup feature. No blockers."
    
    try:
        result1 = daily_standup(status1)
        formatted1 = format_daily_status(result1)
        print(f"\nInput: {status1}")
        print(f"\nParsed Output:\n{formatted1}")
    except Exception as e:
        print(f"Error processing status 1: {e}")
    
    # Example 2: Status with blockers
    print("\n📅 Example 2: Status with Blockers")
    status2 = "Yesterday I researched the new API endpoints. Today I'm implementing the authentication flow. I'm blocked by waiting for API keys from the platform team."
    
    try:
        result2 = daily_standup(status2)
        formatted2 = format_daily_status(result2)
        print(f"\nInput: {status2}")
        print(f"\nParsed Output:\n{formatted2}")
    except Exception as e:
        print(f"Error processing status 2: {e}")
    
    # Example 3: Interactive mode
    print("\n📅 Example 3: Interactive Mode")
    print("Enter your daily status update (or 'quit' to exit):")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_input:
                print("Please enter a status update.")
                continue
                
            result = daily_standup(user_input)
            formatted = format_daily_status(result)
            print(f"\n{formatted}")
            
        except ValueError as e:
            print(f"❌ Error: {e}")
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
