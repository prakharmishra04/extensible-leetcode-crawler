"""
Batch download all your solved LeetCode problems
Chains fetch_solved_problems.py and leetcode_crawler.py to download all solutions
"""

import os
import sys
import argparse
import subprocess
import time
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.leetcode_client import LeetCodeClient


def get_solved_problem_urls(session: str, csrf: str, limit: int = None) -> list:
    """Get list of all solved problem URLs"""
    print("Fetching your solved problems...")
    
    client = LeetCodeClient(session_cookie=session, csrf_token=csrf)
    
    if not client.authenticated:
        print("❌ Authentication required. Set LEETCODE_SESSION and LEETCODE_CSRF.")
        return []
    
    # Fetch all solved problems
    if limit:
        problems = client.fetch_solved_problems(limit=limit)
    else:
        # Get all problems with status
        all_problems = client.fetch_all_problems_with_status()
        if not all_problems:
            return []
        
        # Filter only solved problems
        problems = [p for p in all_problems if p.get('status') == 'ac']
    
    if not problems:
        print("No solved problems found.")
        return []
    
    # Extract URLs
    urls = []
    for problem in problems:
        title_slug = problem.get('titleSlug', '')
        if title_slug:
            url = f"https://leetcode.com/problems/{title_slug}/"
            urls.append(url)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_urls = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
    
    print(f"✓ Found {len(unique_urls)} unique solved problems")
    return unique_urls


def get_file_submission_timestamp(filepath: str) -> Optional[int]:
    """Extract submission timestamp from existing file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # Read first 20 lines to find timestamp
            for _ in range(20):
                line = f.readline()
                if 'Submitted:' in line:
                    # Extract timestamp (Unix timestamp)
                    import re
                    match = re.search(r'Submitted:\s*(\d+)', line)
                    if match:
                        return int(match.group(1))
        return None
    except:
        return None


def check_needs_update(url: str, filepath: str, session: str, csrf: str) -> tuple[bool, Optional[int]]:
    """
    Check if file needs update by comparing timestamps
    Returns: (needs_update, new_timestamp)
    """
    if not os.path.exists(filepath):
        return True, None  # File doesn't exist, needs download
    
    # Get timestamp from existing file
    file_timestamp = get_file_submission_timestamp(filepath)
    if file_timestamp is None:
        # Old format without timestamp, assume needs update
        return True, None
    
    # Get latest submission timestamp from LeetCode
    from utils.leetcode_client import LeetCodeClient
    import re
    
    client = LeetCodeClient(session_cookie=session, csrf_token=csrf)
    match = re.search(r'/problems/([^/]+)', url)
    if not match:
        return False, None
    
    title_slug = match.group(1)
    submission = client.get_last_accepted_submission(title_slug)
    
    if not submission:
        return False, None  # No submission found
    
    new_timestamp = int(submission.get('timestamp', 0))
    
    # Compare timestamps
    if new_timestamp > file_timestamp:
        return True, new_timestamp  # Newer submission available
    
    return False, new_timestamp  # File is up to date


def download_problem(url: str, output_dir: str, session: str, csrf: str, 
                    with_solutions: bool = False, delay: float = 1.0) -> bool:
    """Download a single problem using leetcode_crawler.py"""
    
    # Build command
    script_path = os.path.join(os.path.dirname(__file__), 'leetcode_crawler.py')
    
    cmd = [
        sys.executable,
        script_path,
        url,
        '--session', session,
        '--csrf', csrf,
    ]
    
    if with_solutions:
        cmd.append('--with-solutions')
    
    # Extract problem slug for filename
    import re
    match = re.search(r'/problems/([^/]+)', url)
    if match:
        problem_slug = match.group(1)
        # Convert to absolute path
        abs_output_dir = os.path.abspath(output_dir)
        output_file = os.path.join(abs_output_dir, f"{problem_slug}.py")
        cmd.extend(['--template', output_file])
    
    try:
        # Run the crawler
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return True
        else:
            print(f"  ⚠ Error: {result.stderr[:100]}")
            return False
    
    except subprocess.TimeoutExpired:
        print(f"  ⚠ Timeout")
        return False
    except Exception as e:
        print(f"  ⚠ Error: {str(e)[:100]}")
        return False
    finally:
        # Rate limiting - be nice to LeetCode servers
        time.sleep(delay)


def main():
    parser = argparse.ArgumentParser(
        description='Batch download all your solved LeetCode problems',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all solved problems
  python batch_download_solutions.py
  
  # Download with community solutions (slower)
  python batch_download_solutions.py --with-solutions
  
  # Download only recent 50 problems
  python batch_download_solutions.py --limit 50
  
  # Update files with newer submissions
  python batch_download_solutions.py --update
  
  # Force re-download (overwrite existing files)
  python batch_download_solutions.py --force
  
  # Custom output directory
  python batch_download_solutions.py --output-dir "Leet code/My-Solutions"
  
  # Faster download (shorter delay between requests)
  python batch_download_solutions.py --delay 0.5

Note: Files are saved to "Leet code/To-Revise" by default
      Existing files are skipped automatically (use --force to overwrite)
      Use --update to refresh files with newer submissions
        """
    )
    
    parser.add_argument('--session', help='LEETCODE_SESSION cookie value',
                       default=os.getenv('LEETCODE_SESSION'))
    parser.add_argument('--csrf', help='csrftoken cookie value',
                       default=os.getenv('LEETCODE_CSRF'))
    parser.add_argument('--output-dir', default='Leet code/To-Revise',
                       help='Output directory (default: Leet code/To-Revise)')
    parser.add_argument('--with-solutions', action='store_true',
                       help='Include community solutions (slower)')
    parser.add_argument('--limit', type=int,
                       help='Limit number of problems to download (default: all)')
    parser.add_argument('--delay', type=float, default=1.0,
                       help='Delay between requests in seconds (default: 1.0)')
    parser.add_argument('--resume', action='store_true',
                       help='Skip already downloaded files (default behavior)')
    parser.add_argument('--update', action='store_true',
                       help='Update files if newer submission exists')
    parser.add_argument('--force', action='store_true',
                       help='Force re-download even if files exist (overwrite)')
    
    args = parser.parse_args()
    
    # Validate authentication
    if not args.session or not args.csrf:
        print("❌ Error: Authentication required")
        print("Set LEETCODE_SESSION and LEETCODE_CSRF environment variables")
        print("\nExample:")
        print("  export LEETCODE_SESSION='your-session-cookie'")
        print("  export LEETCODE_CSRF='your-csrf-token'")
        return
    
    # Create output directory
    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)
    print(f"✓ Output directory: {output_dir}\n")
    
    # Get list of solved problems
    urls = get_solved_problem_urls(args.session, args.csrf, args.limit)
    
    if not urls:
        return
    
    print(f"\n{'='*80}")
    print(f"Starting batch download of {len(urls)} problems")
    print(f"Output: {output_dir}")
    print(f"Delay: {args.delay}s between requests")
    if args.with_solutions:
        print("Including community solutions (this will take longer)")
    print(f"{'='*80}\n")
    
    # Download each problem
    success_count = 0
    skip_count = 0
    fail_count = 0
    update_count = 0
    
    for i, url in enumerate(urls, 1):
        # Extract problem name for display
        import re
        match = re.search(r'/problems/([^/]+)', url)
        problem_name = match.group(1) if match else url
        
        output_file = os.path.join(output_dir, f"{problem_name}.py")
        
        # Handle different modes
        if args.force:
            # Force mode: always download
            action = "Downloading"
        elif args.update and os.path.exists(output_file):
            # Update mode: check if newer submission exists
            print(f"[{i}/{len(urls)}] Checking {problem_name}...", end=' ')
            needs_update, new_timestamp = check_needs_update(
                url, output_file, args.session, args.csrf
            )
            if needs_update:
                print("🔄 (newer submission found)")
                action = "Updating"
                update_count += 1
            else:
                print("✓ (up to date)")
                skip_count += 1
                continue
        elif os.path.exists(output_file):
            # Default mode: skip existing files
            print(f"[{i}/{len(urls)}] ⏭  Skipping {problem_name} (already exists)")
            skip_count += 1
            continue
        else:
            # File doesn't exist: download
            action = "Downloading"
        
        print(f"[{i}/{len(urls)}] {action} {problem_name}...", end=' ')
        
        success = download_problem(
            url, 
            output_dir, 
            args.session, 
            args.csrf,
            args.with_solutions,
            args.delay
        )
        
        if success:
            print("✓")
            success_count += 1
        else:
            print("✗")
            fail_count += 1
    
    # Summary
    print(f"\n{'='*80}")
    print("Batch Download Complete!")
    print(f"{'='*80}")
    print(f"  ✓ Success: {success_count}")
    if update_count > 0:
        print(f"  🔄 Updated: {update_count}")
    if skip_count > 0:
        print(f"  ⏭  Skipped: {skip_count}")
    if fail_count > 0:
        print(f"  ✗ Failed:  {fail_count}")
    print(f"  Total:     {len(urls)}")
    print(f"\nFiles saved to: {output_dir}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
