"""
Fetch list of solved LeetCode problems for your profile
"""

import os
import sys
import argparse
import json
from datetime import datetime
from typing import List, Dict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.leetcode_client import LeetCodeClient


def format_timestamp(timestamp: str) -> str:
    """Convert timestamp to readable date"""
    try:
        dt = datetime.fromtimestamp(int(timestamp))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return timestamp


def display_solved_problems(problems: List[Dict], show_details: bool = False):
    """Display solved problems in a formatted way"""
    if not problems:
        print("No solved problems found.")
        return
    
    print(f"\n{'='*80}")
    print(f"Found {len(problems)} solved problems")
    print(f"{'='*80}\n")
    
    for i, problem in enumerate(problems, 1):
        title = problem.get('title', 'Unknown')
        title_slug = problem.get('titleSlug', '')
        problem_id = problem.get('id', '')
        timestamp = problem.get('timestamp', '')
        
        if show_details:
            date_str = format_timestamp(timestamp) if timestamp else 'Unknown date'
            url = f"https://leetcode.com/problems/{title_slug}/"
            print(f"{i}. {title}")
            print(f"   URL: {url}")
            print(f"   Solved: {date_str}")
            print()
        else:
            print(f"{i}. {title} ({title_slug})")


def get_solved_by_status(client: LeetCodeClient) -> Dict[str, List[Dict]]:
    """Get all problems categorized by solve status"""
    print("Fetching all problems with status...")
    all_problems = client.fetch_all_problems_with_status()
    
    if not all_problems:
        return {}
    
    categorized = {
        'solved': [],
        'attempted': [],
        'not_started': []
    }
    
    for problem in all_problems:
        status = problem.get('status')
        if status == 'ac':  # Accepted
            categorized['solved'].append(problem)
        elif status == 'notac':  # Attempted but not accepted
            categorized['attempted'].append(problem)
        else:  # Not started
            categorized['not_started'].append(problem)
    
    return categorized


def save_to_file(problems: List[Dict], filename: str, format_type: str = 'json', urls_only: bool = False):
    """Save problems to file"""
    if urls_only:
        # Save only URLs, one per line
        with open(filename, 'w', encoding='utf-8') as f:
            for problem in problems:
                title_slug = problem.get('titleSlug', '')
                if title_slug:
                    url = f"https://leetcode.com/problems/{title_slug}/"
                    f.write(f"{url}\n")
        print(f"\n✓ Saved {len(problems)} URLs to {filename}")
        return
    
    if format_type == 'json':
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(problems, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Saved to {filename}")
    
    elif format_type == 'txt':
        with open(filename, 'w', encoding='utf-8') as f:
            for i, problem in enumerate(problems, 1):
                title = problem.get('title', 'Unknown')
                title_slug = problem.get('titleSlug', '')
                url = f"https://leetcode.com/problems/{title_slug}/"
                f.write(f"{i}. {title}\n")
                f.write(f"   {url}\n\n")
        print(f"\n✓ Saved to {filename}")
    
    elif format_type == 'md':
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# My Solved LeetCode Problems\n\n")
            f.write(f"Total: {len(problems)} problems\n\n")
            
            for i, problem in enumerate(problems, 1):
                title = problem.get('title', 'Unknown')
                title_slug = problem.get('titleSlug', '')
                difficulty = problem.get('difficulty', 'Unknown')
                url = f"https://leetcode.com/problems/{title_slug}/"
                
                # Get topics if available
                topics = problem.get('topicTags', [])
                topic_names = [tag.get('name', '') for tag in topics]
                topic_str = ', '.join(topic_names) if topic_names else 'N/A'
                
                f.write(f"## {i}. {title}\n\n")
                f.write(f"- **Difficulty:** {difficulty}\n")
                f.write(f"- **Topics:** {topic_str}\n")
                f.write(f"- **Link:** [{title}]({url})\n\n")
        print(f"\n✓ Saved to {filename}")


def main():
    parser = argparse.ArgumentParser(
        description='Fetch your solved LeetCode problems',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch recent solved problems
  python fetch_solved_problems.py
  
  # Fetch with authentication
  python fetch_solved_problems.py --session "your-session" --csrf "your-csrf"
  
  # Get all problems with status
  python fetch_solved_problems.py --all-with-status
  
  # Save to file
  python fetch_solved_problems.py --output solved.json
  python fetch_solved_problems.py --output solved.txt --format txt
  python fetch_solved_problems.py --output solved.md --format md
  
  # Show detailed information
  python fetch_solved_problems.py --details
        """
    )
    
    parser.add_argument('--session', help='LEETCODE_SESSION cookie value',
                       default=os.getenv('LEETCODE_SESSION'))
    parser.add_argument('--csrf', help='csrftoken cookie value',
                       default=os.getenv('LEETCODE_CSRF'))
    parser.add_argument('--username', help='LeetCode username (optional)')
    parser.add_argument('--limit', type=int, default=100,
                       help='Number of recent problems to fetch (default: 100)')
    parser.add_argument('--all-with-status', action='store_true',
                       help='Fetch all problems with solve status (slower)')
    parser.add_argument('--details', action='store_true',
                       help='Show detailed information')
    parser.add_argument('--urls-only', action='store_true',
                       help='Output only URLs (one per line, requires --output)')
    parser.add_argument('--output', '-o', help='Output filename')
    parser.add_argument('--format', choices=['json', 'txt', 'md'], default='json',
                       help='Output format (default: json, ignored if --urls-only)')
    
    args = parser.parse_args()
    
    # Initialize client
    client = LeetCodeClient(
        session_cookie=args.session,
        csrf_token=args.csrf
    )
    
    if not client.authenticated:
        print("⚠ Warning: No authentication provided. Some features may not work.")
        print("Set LEETCODE_SESSION and LEETCODE_CSRF environment variables.")
        return
    
    print("✓ Authenticated session detected")
    
    # Get user profile
    profile = client.fetch_user_profile(args.username)
    if profile:
        username = profile.get('username', 'Unknown')
        print(f"✓ Fetching problems for user: {username}\n")
    
    # Fetch problems
    if args.all_with_status:
        categorized = get_solved_by_status(client)
        
        if categorized:
            solved = categorized['solved']
            attempted = categorized['attempted']
            
            print(f"\n{'='*80}")
            print(f"Problem Statistics:")
            print(f"  Solved: {len(solved)}")
            print(f"  Attempted: {len(attempted)}")
            print(f"  Not Started: {len(categorized['not_started'])}")
            print(f"{'='*80}")
            
            # Display solved problems
            if solved:
                print("\nSolved Problems:")
                display_solved_problems(solved, args.details)
            
            # Save if requested
            if args.output:
                save_to_file(solved, args.output, args.format, args.urls_only)
    else:
        # Fetch recent solved problems
        print(f"Fetching recent {args.limit} solved problems...")
        problems = client.fetch_solved_problems(args.username, limit=args.limit)
        
        if problems:
            display_solved_problems(problems, args.details)
            
            # Save if requested
            if args.output:
                save_to_file(problems, args.output, args.format, args.urls_only)
        else:
            print("Failed to fetch solved problems.")


if __name__ == "__main__":
    main()
