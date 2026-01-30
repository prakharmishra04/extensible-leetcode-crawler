"""
LeetCode Problem Crawler
Crawls LeetCode problem pages and extracts problem details including solutions (requires authentication)
"""

import json
import os
from typing import Dict
import argparse
from utils.leetcode_client import LeetCodeClient
from utils.formatters import wrap_text


class LeetCodeCrawler:
    def __init__(self, session_cookie: str = None, csrf_token: str = None):
        """
        Initialize crawler with optional authentication
        
        Args:
            session_cookie: LEETCODE_SESSION cookie value from your browser
            csrf_token: csrftoken cookie value from your browser
        """
        self.client = LeetCodeClient(session_cookie, csrf_token)
        self.authenticated = self.client.authenticated

    
    def crawl(self, url: str, include_solutions: bool = True, include_my_submission: bool = True) -> Dict:
        """Main crawl method"""
        title_slug = self.client.extract_problem_slug(url)
        if not title_slug:
            return {"error": "Invalid URL"}
        
        print(f"Fetching problem: {title_slug}")
        problem_data = self.client.fetch_problem(title_slug)
        
        if not problem_data:
            return {"error": "Failed to fetch problem data"}
        
        solutions = None
        official_solution = None
        my_submission = None
        
        if self.authenticated:
            if include_my_submission:
                print("Fetching your last submission...")
                my_submission = self.client.get_last_accepted_submission(title_slug)
                if my_submission:
                    print(f"✓ Found your submission in {my_submission['language']}")
                else:
                    print("No accepted submissions found")
            
            if include_solutions:
                print("Fetching solutions...")
                official_solution = self.client.fetch_official_solution(title_slug)
                solutions = self.client.fetch_solution_articles(title_slug)
        elif include_solutions or include_my_submission:
            print("Warning: Authentication required to fetch solutions/submissions. Provide session cookies.")
        
        return self.client.parse_problem(problem_data, solutions, official_solution, my_submission)
    
    def save_to_file(self, problem_data: Dict, filename: str = None, output_dir: str = None):
        """Save problem data to file"""
        if not filename:
            title = problem_data.get('title', 'problem').replace(' ', '_').lower()
            filename = f"{title}.json"
        
        # Create output directory if specified
        if output_dir:
            import os
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, filename)
        else:
            filepath = filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(problem_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved to {filepath}")
    
    def create_python_template(self, problem_data: Dict, filename: str = None):
        """Create a Python solution template"""
        if not filename:
            title = problem_data.get('title', 'problem').replace(' ', '_').lower()
            filename = f"{title}.py"
        
        # Format the description for better readability
        description = problem_data.get('description', '')
        formatted_description = wrap_text(description, width=78)
        
        # Use my submission if available, otherwise use the template
        if 'my_last_submission' in problem_data and problem_data['my_last_submission'].get('code'):
            submission = problem_data['my_last_submission']
            code = submission['code']
            
            # Format hints if available
            hints_section = ""
            if problem_data.get('hints'):
                hints_section = "\n\nHints:\n"
                for i, hint in enumerate(problem_data['hints'], 1):
                    hints_section += f"  {i}. {hint}\n"
            
            template = f'''"""
LeetCode Problem #{problem_data.get('id')}: {problem_data.get('title')}
Difficulty: {problem_data.get('difficulty')}
Topics: {', '.join(problem_data.get('topics', []))}

My Last Accepted Submission:
  Language: {submission.get('language')}
  Runtime: {submission.get('runtime')} (beats {submission.get('runtime_percentile', 'N/A')}%)
  Memory: {submission.get('memory')} (beats {submission.get('memory_percentile', 'N/A')}%)
  Submitted: {submission.get('timestamp')}

Problem Description:
{formatted_description}{hints_section}
"""

{code}


if __name__ == "__main__":
    # Test cases
    solution = Solution()
    
    # Add your test cases here
    pass
'''
        else:
            python_code = problem_data.get('code_snippets', {}).get('Python3', '')
            
            # Format hints if available
            hints_section = ""
            if problem_data.get('hints'):
                hints_section = "\n\nHints:\n"
                for i, hint in enumerate(problem_data['hints'], 1):
                    hints_section += f"  {i}. {hint}\n"
            
            template = f'''"""
LeetCode Problem #{problem_data.get('id')}: {problem_data.get('title')}
Difficulty: {problem_data.get('difficulty')}
Topics: {', '.join(problem_data.get('topics', []))}

Problem Description:
{formatted_description}{hints_section}
"""

{python_code}


if __name__ == "__main__":
    # Test cases
    solution = Solution()
    
    # Add your test cases here
    pass
'''
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(template)
        
        print(f"Created template: {filename}")


def main():
    parser = argparse.ArgumentParser(
        description='Crawl LeetCode problems and solutions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (no authentication)
  python leetcode_crawler.py https://leetcode.com/problems/two-sum/
  
  # With authentication (access solutions)
  python leetcode_crawler.py https://leetcode.com/problems/two-sum/ \\
    --session "your-session-cookie" \\
    --csrf "your-csrf-token"
  
  # Using environment variables
  export LEETCODE_SESSION="your-session-cookie"
  export LEETCODE_CSRF="your-csrf-token"
  python leetcode_crawler.py https://leetcode.com/problems/two-sum/
  
  # Skip solutions
  python leetcode_crawler.py https://leetcode.com/problems/two-sum/ --no-solutions

How to get your session cookies:
  1. Open LeetCode in your browser and log in
  2. Open Developer Tools (F12)
  3. Go to Application/Storage > Cookies > https://leetcode.com
  4. Copy the values of 'LEETCODE_SESSION' and 'csrftoken'
        """
    )
    
    parser.add_argument('url', help='LeetCode problem URL')
    parser.add_argument('--session', help='LEETCODE_SESSION cookie value', 
                       default=os.getenv('LEETCODE_SESSION'))
    parser.add_argument('--csrf', help='csrftoken cookie value',
                       default=os.getenv('LEETCODE_CSRF'))
    parser.add_argument('--with-solutions', action='store_true',
                       help='Fetch community solutions (disabled by default for faster crawling)')
    parser.add_argument('--no-my-submission', action='store_true',
                       help='Skip fetching your last submission')
    parser.add_argument('--save-json', action='store_true',
                       help='Save problem data as JSON file (disabled by default)')
    parser.add_argument('--json-dir', default='../leetcode_data',
                       help='Directory to save JSON files (default: ../leetcode_data)')
    parser.add_argument('--output', '-o', help='Output JSON filename (implies --save-json)')
    parser.add_argument('--template', '-t', help='Output Python template filename')
    
    args = parser.parse_args()
    
    # Initialize crawler with authentication if provided
    crawler = LeetCodeCrawler(
        session_cookie=args.session,
        csrf_token=args.csrf
    )
    
    if args.session:
        print("✓ Authenticated session detected")
    else:
        print("⚠ No authentication provided - solutions/submissions will not be available")
    
    # Crawl the problem
    problem_data = crawler.crawl(
        args.url, 
        include_solutions=args.with_solutions,  # Changed: now opt-in instead of opt-out
        include_my_submission=not args.no_my_submission
    )
    
    if 'error' in problem_data:
        print(f"Error: {problem_data['error']}")
        return
    
    # Display problem info
    print("\n" + "="*60)
    print(f"Problem #{problem_data['id']}: {problem_data['title']}")
    print(f"Difficulty: {problem_data['difficulty']}")
    print(f"Topics: {', '.join(problem_data['topics'])}")
    print(f"Acceptance Rate: {problem_data['acceptance_rate']}")
    
    if 'my_last_submission' in problem_data:
        sub = problem_data['my_last_submission']
        print(f"\n✓ Your Last Submission ({sub['language']}):")
        print(f"  Runtime: {sub['runtime']} (beats {sub.get('runtime_percentile', 'N/A')}%)")
        print(f"  Memory: {sub['memory']} (beats {sub.get('memory_percentile', 'N/A')}%)")
    
    if 'official_solution' in problem_data:
        if problem_data['official_solution'].get('available') == False:
            print(f"\nOfficial Solution: {problem_data['official_solution'].get('message')}")
        else:
            print("\n✓ Official Solution: Available")
    
    if 'community_solutions' in problem_data:
        print(f"✓ Community Solutions: {len(problem_data['community_solutions'])} fetched")
    
    print("="*60)
    
    # Save to JSON only if requested
    if args.save_json or args.output:
        output_file = args.output
        output_dir = args.json_dir if not args.output else None
        crawler.save_to_file(problem_data, output_file, output_dir)
    
    # Create Python template
    template_file = args.template
    crawler.create_python_template(problem_data, template_file)


if __name__ == "__main__":
    main()
