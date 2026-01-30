"""
LeetCode API Client
"""

import requests
from typing import Dict, Optional, List


class LeetCodeClient:
    """Client for interacting with LeetCode API"""
    
    def __init__(self, session_cookie: str = None, csrf_token: str = None):
        """
        Initialize LeetCode client with optional authentication
        
        Args:
            session_cookie: LEETCODE_SESSION cookie value from your browser
            csrf_token: csrftoken cookie value from your browser
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Referer': 'https://leetcode.com',
        })
        
        # Set authentication cookies if provided
        if session_cookie:
            self.session.cookies.set('LEETCODE_SESSION', session_cookie, domain='.leetcode.com')
        if csrf_token:
            self.session.cookies.set('csrftoken', csrf_token, domain='.leetcode.com')
            self.session.headers['X-CSRFToken'] = csrf_token
        
        self.authenticated = bool(session_cookie)
    
    def extract_problem_slug(self, url: str) -> str:
        """Extract problem slug from URL"""
        import re
        match = re.search(r'/problems/([^/]+)', url)
        return match.group(1) if match else ""
    
    def fetch_problem_graphql(self, title_slug: str) -> Optional[Dict]:
        """Fetch problem data using LeetCode's GraphQL API"""
        graphql_url = "https://leetcode.com/graphql"
        
        query = """
        query questionData($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                questionId
                questionFrontendId
                title
                titleSlug
                content
                difficulty
                likes
                dislikes
                categoryTitle
                topicTags {
                    name
                    slug
                }
                codeSnippets {
                    lang
                    langSlug
                    code
                }
                stats
                hints
                solution {
                    id
                    canSeeDetail
                    paidOnly
                    hasVideoSolution
                    paidOnlyVideo
                }
                exampleTestcases
            }
        }
        """
        
        payload = {
            "query": query,
            "variables": {"titleSlug": title_slug}
        }
        
        try:
            response = self.session.post(graphql_url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get('data', {}).get('question')
        except Exception as e:
            print(f"Error fetching problem data: {e}")
            return None
    
    def fetch_user_profile(self, username: str = None) -> Optional[Dict]:
        """Fetch user profile data"""
        graphql_url = "https://leetcode.com/graphql"
        
        # If no username provided, get current user
        if not username:
            query = """
            query globalData {
                userStatus {
                    username
                    isSignedIn
                    isPremium
                    avatar
                }
            }
            """
            payload = {"query": query}
        else:
            query = """
            query userPublicProfile($username: String!) {
                matchedUser(username: $username) {
                    username
                    profile {
                        realName
                        userAvatar
                        reputation
                        ranking
                    }
                    submitStats {
                        acSubmissionNum {
                            difficulty
                            count
                        }
                    }
                }
            }
            """
            payload = {
                "query": query,
                "variables": {"username": username}
            }
        
        try:
            response = self.session.post(graphql_url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            if username:
                return data.get('data', {}).get('matchedUser')
            else:
                return data.get('data', {}).get('userStatus')
        except Exception as e:
            print(f"Error fetching user profile: {e}")
            return None
    
    def fetch_solved_problems(self, username: str = None, limit: int = 100, skip: int = 0) -> Optional[List[Dict]]:
        """Fetch list of solved problems for a user"""
        graphql_url = "https://leetcode.com/graphql"
        
        # Get current username if not provided
        if not username:
            profile = self.fetch_user_profile()
            if not profile:
                return None
            username = profile.get('username')
        
        query = """
        query recentAcSubmissions($username: String!, $limit: Int!) {
            recentAcSubmissionList(username: $username, limit: $limit) {
                id
                title
                titleSlug
                timestamp
            }
        }
        """
        
        payload = {
            "query": query,
            "variables": {
                "username": username,
                "limit": limit
            }
        }
        
        try:
            response = self.session.post(graphql_url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get('data', {}).get('recentAcSubmissionList', [])
        except Exception as e:
            print(f"Error fetching solved problems: {e}")
            return None
    
    def fetch_all_problems_with_status(self) -> Optional[List[Dict]]:
        """Fetch all problems with user's solve status"""
        graphql_url = "https://leetcode.com/graphql"
        
        query = """
        query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
            problemsetQuestionList: questionList(
                categorySlug: $categorySlug
                limit: $limit
                skip: $skip
                filters: $filters
            ) {
                total: totalNum
                questions: data {
                    acRate
                    difficulty
                    freqBar
                    frontendQuestionId: questionFrontendId
                    isFavor
                    paidOnly: isPaidOnly
                    status
                    title
                    titleSlug
                    topicTags {
                        name
                        id
                        slug
                    }
                }
            }
        }
        """
        
        all_questions = []
        skip = 0
        limit = 100
        
        try:
            while True:
                payload = {
                    "query": query,
                    "variables": {
                        "categorySlug": "",
                        "skip": skip,
                        "limit": limit,
                        "filters": {}
                    }
                }
                
                response = self.session.post(graphql_url, json=payload)
                response.raise_for_status()
                data = response.json()
                
                question_list = data.get('data', {}).get('problemsetQuestionList', {})
                questions = question_list.get('questions', [])
                total = question_list.get('total', 0)
                
                if not questions:
                    break
                
                all_questions.extend(questions)
                skip += limit
                
                # Stop if we've fetched all questions
                if skip >= total:
                    break
            
            return all_questions
        except Exception as e:
            print(f"Error fetching all problems: {e}")
            return None
    
    def fetch_my_submissions(self, title_slug: str, limit: int = 20) -> Optional[List[Dict]]:
        """Fetch user's submission history for a problem"""
        url = f"https://leetcode.com/api/submissions/{title_slug}/"
        
        try:
            response = self.session.get(url, params={'limit': limit, 'offset': 0})
            response.raise_for_status()
            data = response.json()
            submissions = data.get('submissions_dump', [])
            return submissions
        except Exception as e:
            print(f"Error fetching submissions: {e}")
            return None
    
    def fetch_submission_detail(self, submission_id: str) -> Optional[Dict]:
        """Fetch detailed code for a specific submission"""
        url = f"https://leetcode.com/api/submissions/detail/{submission_id}/"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            return data
        except Exception as e:
            return None
    
    def fetch_solution_articles(self, title_slug: str) -> Optional[List[Dict]]:
        """Fetch community solution articles"""
        graphql_url = "https://leetcode.com/graphql"
        
        query = """
        query communitySolutions($questionSlug: String!, $skip: Int!, $first: Int!, $orderBy: TopicSortingOption) {
            questionSolutions(
                filters: {questionSlug: $questionSlug, skip: $skip, first: $first, orderBy: $orderBy}
            ) {
                hasDirectResults
                totalNum
                solutions {
                    id
                    title
                    commentCount
                    topLevelCommentCount
                    viewCount
                    pinned
                    isFavorite
                    solutionTags {
                        name
                        slug
                    }
                    post {
                        id
                        status
                        voteCount
                        creationDate
                        isHidden
                        author {
                            username
                            isActive
                            profile {
                                userAvatar
                                reputation
                            }
                        }
                        content
                        contentTypeId
                    }
                }
            }
        }
        """
        
        payload = {
            "query": query,
            "variables": {
                "questionSlug": title_slug,
                "skip": 0,
                "first": 10,
                "orderBy": "hot"
            }
        }
        
        try:
            response = self.session.post(graphql_url, json=payload)
            response.raise_for_status()
            data = response.json()
            solutions = data.get('data', {}).get('questionSolutions', {}).get('solutions', [])
            return solutions
        except Exception as e:
            print(f"Error fetching solutions: {e}")
            return None
    
    def fetch_official_solution(self, title_slug: str) -> Optional[Dict]:
        """Fetch official LeetCode solution (requires premium)"""
        graphql_url = "https://leetcode.com/graphql"
        
        query = """
        query officialSolution($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                solution {
                    id
                    title
                    content
                    contentTypeId
                    paidOnly
                    hasVideoSolution
                    paidOnlyVideo
                    canSeeDetail
                    rating {
                        count
                        average
                    }
                }
            }
        }
        """
        
        payload = {
            "query": query,
            "variables": {"titleSlug": title_slug}
        }
        
        try:
            response = self.session.post(graphql_url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get('data', {}).get('question', {}).get('solution')
        except Exception as e:
            print(f"Error fetching official solution: {e}")
            return None

    def get_last_accepted_submission(self, title_slug: str) -> Optional[Dict]:
        """Get the last accepted submission for a problem"""
        submissions = self.fetch_my_submissions(title_slug)
        
        if not submissions:
            return None
        
        # Find the first accepted submission
        for submission in submissions:
            if submission.get('status_display') == 'Accepted':
                # Try to get more details
                detail = self.fetch_submission_detail(submission['id'])
                
                code = None
                if detail:
                    code = detail.get('code')
                
                # If no code from detail, try from submission itself
                if not code:
                    code = submission.get('code')
                
                if code:
                    return {
                        'id': submission['id'],
                        'status': submission['status_display'],
                        'language': submission['lang'],
                        'runtime': submission['runtime'],
                        'memory': submission.get('memory', 'N/A'),
                        'timestamp': submission['timestamp'],
                        'code': code,
                        'runtime_percentile': detail.get('runtime_percentile') if detail else None,
                        'memory_percentile': detail.get('memory_percentile') if detail else None,
                        'notes': detail.get('notes') if detail else None
                    }
        
        return None
    
    def parse_problem(self, problem_data: Dict, solutions: List[Dict] = None, 
                     official_solution: Dict = None, my_submission: Dict = None) -> Dict:
        """Parse and format problem data"""
        import json
        from utils.formatters import clean_html
        
        if not problem_data:
            return {}
        
        # Parse stats
        stats = json.loads(problem_data.get('stats', '{}'))
        
        result = {
            'id': problem_data.get('questionFrontendId'),
            'title': problem_data.get('title'),
            'difficulty': problem_data.get('difficulty'),
            'description': clean_html(problem_data.get('content', '')),
            'topics': [tag['name'] for tag in problem_data.get('topicTags', [])],
            'likes': problem_data.get('likes'),
            'dislikes': problem_data.get('dislikes'),
            'acceptance_rate': stats.get('acRate'),
            'total_accepted': stats.get('totalAcceptedRaw'),
            'total_submissions': stats.get('totalSubmissionRaw'),
            'hints': problem_data.get('hints', []),
            'example_testcases': problem_data.get('exampleTestcases'),
            'code_snippets': {
                snippet['lang']: snippet['code'] 
                for snippet in problem_data.get('codeSnippets', [])
            }
        }
        
        # Add my submission if available
        if my_submission:
            result['my_last_submission'] = {
                'language': my_submission.get('language'),
                'runtime': my_submission.get('runtime'),
                'memory': my_submission.get('memory'),
                'runtime_percentile': my_submission.get('runtime_percentile'),
                'memory_percentile': my_submission.get('memory_percentile'),
                'timestamp': my_submission.get('timestamp'),
                'code': my_submission.get('code'),
                'notes': my_submission.get('notes')
            }
        
        # Add official solution if available
        if official_solution and official_solution.get('canSeeDetail'):
            result['official_solution'] = {
                'title': official_solution.get('title'),
                'content': clean_html(official_solution.get('content', '')),
                'has_video': official_solution.get('hasVideoSolution', False),
                'rating': official_solution.get('rating', {})
            }
        elif official_solution:
            result['official_solution'] = {
                'available': False,
                'paid_only': official_solution.get('paidOnly', True),
                'message': 'Premium subscription required'
            }
        
        # Add community solutions if available
        if solutions:
            result['community_solutions'] = []
            for sol in solutions[:5]:  # Top 5 solutions
                post = sol.get('post', {})
                result['community_solutions'].append({
                    'title': sol.get('title'),
                    'author': post.get('author', {}).get('username'),
                    'votes': post.get('voteCount'),
                    'views': sol.get('viewCount'),
                    'content': clean_html(post.get('content', '')),
                    'tags': [tag['name'] for tag in sol.get('solutionTags', [])]
                })
        
        return result
    
    # Alias for backward compatibility
    def fetch_problem(self, title_slug: str) -> Optional[Dict]:
        """Alias for fetch_problem_graphql"""
        return self.fetch_problem_graphql(title_slug)
