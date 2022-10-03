"""
Usage:
* Create environment variables:
  * githab_server_addr (your githab server address i.e. https://github.com/)
  * githab_token (your gitlab access token)

* Set list of groups in the variable: gitlab_group_names
* Set clone root directory in the variable: repo_root_dir

Output directory will be /repo_root/githab_group_name/githab_repo_name/

If the directory exists, this tool will instead perform a fetch on all remotes for the given repo
"""
import json
import os
from collections import defaultdict
from pathlib import Path
from github import Github

from utils import EnhancedJSONEncoder

github_token = os.getenv("github_token")
proxy_user = os.getenv("username")
proxy_pass = os.getenv("password")

org = "nbnco"

git_group_names = [
    "ignite",
    "elms",
    # "pni",
    # 'ccoe'
]

repo_root_dir = os.path.join(str(Path.home()), "git", "nbnco")

g = Github(
    github_token,
    proxies={"https": f"http://{proxy_user}:{proxy_pass}@proxy.nbnco.net.au:80"},
)

print("Retrieving All Repo Names")
all_groups = [x for x in g.get_organization("nbnco").get_repos()]

print(len(all_groups))

results = defaultdict(lambda: {})

for group_name in git_group_names:
    print(f"Retrieving list of repos for {group_name} team")
    repos = [x for x in all_groups if x.name.startswith(group_name)]

    for repo in repos:
        print(f"Processing Repo: {repo.name}")
        results[group_name][repo.name] = []
        for branch in repo.get_branches():
            results[group_name][repo.name].append(
                {
                    "branch_name": branch.name,
                    "last_commit": {
                        "modified_date": branch.commit.commit.last_modified or None,
                        "commit_author": branch.commit.commit.author.name or None,
                        "url": branch.commit.url or None,
                        "commit_message": branch.commit.commit.message or None,
                    },
                }
            )

with open("repo_data.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=4, cls=EnhancedJSONEncoder)
