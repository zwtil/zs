import json
import requests
import sys

def custom_match(repo):
    if repo["visibility"] != "public":
        return None

    if repo["archived"]:
        return None
    
    if repo["name"] == "zs":
        return None

    repoc = {
        "name" : repo["name"],
        "description" : repo["description"],
        "url" : repo["html_url"],
        "click" : False,
        "isPython" :  repo["language"] == "Python",
        "giturl" : repo["clone_url"],
    }

    if repo["name"].startswith("zuu"):
        return repoc
    
    #query contents 
    contents_url = repo["contents_url"].replace("{+path}", "CLICK")
    response = requests.get(contents_url)

    if response.status_code != 200:
        return repoc

    contents = response.json()
    if contents["status"] != "404":
        repoc["click"] = True

    return repoc

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
    if len(sys.argv) != 3:
        print("Usage: python script.py <github_org_or_user>")
        sys.exit(1)
    
    api_url = sys.argv[1]
    save_path = sys.argv[2]
    print(api_url)

    repos = get_repos(api_url)
    
    output = []

    # Print repository information
    for repo in repos:
        res = custom_match(repo)
        if res is None:
            continue
        output.append(res)
    
    with open(save_path, "w") as f:
        json.dump(output, f, indent=4)

if __name__ == "__main__":
    main()
