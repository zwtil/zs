import datetime
import json
import os
import requests
import sys
from hashlib import sha256

EXCLUDED_REPOS = ["zs"]
def CUSTOM_FILTER(repo):
    name : str = repo["name"]
    if name.startswith("z"):
        return False
    
    return True

def UPDATE_REPO_META(repo : dict, repoInData : dict, alreadyPresent : bool):
    if not repoInData:
        repoInData = {
            "name" : repo["name"],
            "url" : repo["clone_url"],
            "_html" : repo["html_url"], 
        }

        try:
            analyse_repo(repo, repoInData)
        except Exception:
            pass
    return repoInData


def analyse_repo(repo : dict, repoInData : dict):
    repoInData.pop("click", None)

    # get root level contents
    contents_url = repo["contents_url"]
    root_contents_res = requests.get(contents_url.replace("{+path}", ""))

    root_contents : dict | list = root_contents_res.json()
    if isinstance(root_contents, dict):
        return
    
    has_src = False
    for file in root_contents:
        if file["name"] == "cli.py":
            repoInData["click"] = "cli.py"
            repoInData["req"] = "requirements.txt"
            return
        
        if file["name"] == "src":
            has_src = True

    if not has_src:
        return

    src_contents_res = requests.get(contents_url.replace("{+path}", f"src/{repo['name']}"))
    src_contents :dict | list = src_contents_res.json()

    if isinstance(src_contents, dict):
        return
    
    for file in src_contents:
        if file["name"] == "cli.py":
            repoInData["click"] = f"src/{repo['name']}/cli.py"
        elif file["name"] == "__main__.py":
            repoInData["click"] = f"src/{repo['name']}/__main__.py"
        else:
            continue

        repoInData["req"] = "pyproject.toml"
        return
        

def get_matching_repos(api_url, data: dict, last_updated : datetime.datetime):
    candidate_repos = get_all_repos(api_url)

    for crepo in candidate_repos:
        if crepo["visibility"] != "public":
            continue

        if crepo["archived"]:
            continue

        name = crepo["name"]
        if name in EXCLUDED_REPOS:
            continue
        
        # updated in the past
        crepo_last_updated = datetime.datetime.strptime(crepo["updated_at"], "%Y-%m-%dT%H:%M:%SZ")
        if name in data and crepo_last_updated < last_updated:
            continue

        if not CUSTOM_FILTER(crepo):
            continue

        data[name] = UPDATE_REPO_META(crepo, data.get(name, None), name in data)
        
            
        
def get_all_repos(api_url):

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
    
    if os.path.exists(save_path):
        with open(save_path, "r") as f:
            jdata = json.load(f)
    else:
        jdata = {}

    repodata = jdata.get("repos", {})
    prev_sha256 = sha256(json.dumps(repodata).encode()).hexdigest()
    
    last_updated = datetime.datetime.strptime(jdata.get("last_updated", "1970-01-01T00:00:00Z"), "%Y-%m-%dT%H:%M:%SZ")

    get_matching_repos(api_url, repodata, last_updated)
    
    curr_sha256 = sha256(json.dumps(repodata).encode()).hexdigest()

    if prev_sha256 == curr_sha256:
        print("No changes detected.")
        return

    with open(save_path, "w") as f:
        json.dump({
            "last_updated" : datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "repos" : repodata
        }, f, indent=4)

if __name__ == "__main__":
    main()
