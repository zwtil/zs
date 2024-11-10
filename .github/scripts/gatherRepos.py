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
    
    repos = get_repos(api_url)
    
    # Print repository information
    for repo in repos:
        if repo:
            continue

        print(f"Name: {repo['name']}")
        print(f"URL: {repo['html_url']}")
        print(f"Description: {repo['description']}")
        print("---")

if __name__ == "__main__":
    main()
