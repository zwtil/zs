import requests
import sys
#import json

def custom_match(repo):
    return True

def get_repos(api_url):

    repos = []
    page = 1
    
    while True:
        params = {
            'page': page,
            'per_page': 100
        }
        
        response = requests.get(api_url, params=params)
        
        if response.status_code != 200:
            print(f"Error fetching repos: {response.status_code}")
            sys.exit(1)
            
        page_repos = response.json()
        
        if not page_repos:
            break
            
        repos.extend(page_repos)
        page += 1
    
    return repos

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <github_org_or_user>")
        sys.exit(1)
    
    api_url = sys.argv[1]
    print(api_url)

    repos = get_repos(api_url)
    
    output = []

    # Print repository information
    for repo in repos:
        if repo:
            continue

        output.append({
            "name": repo['name'],
            "url": repo['html_url'],
            "description": repo['description'],
            "language": repo['language'],
        }
        )
    
if __name__ == "__main__":
    main()
