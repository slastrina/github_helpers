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

import os
from pathlib import Path
from github import Github
from git import Repo, GitCommandError

github_token = os.getenv("github_token")
proxy_user = os.getenv("username")
proxy_pass = os.getenv("password")

org = "nbnco"

git_group_names = ["ignite", "elms", "pni", "ccoe"]

repo_root_dir = os.path.join(str(Path.home()), "git", "nbnco")

g = Github(
    github_token,
    proxies={"https": f"http://{proxy_user}:{proxy_pass}@proxy.nbnco.net.au:80"},
)

print("Retrieving All Repo Names")
all_groups = [x for x in g.get_organization("nbnco").get_repos()]

print(len(all_groups))

for group_name in git_group_names:
    destination = os.path.join(repo_root_dir, group_name)
    os.makedirs(destination, exist_ok=True)

    print(f"Retrieving list of repos for {group_name} team")
    projects = [x for x in all_groups if x.name.startswith(group_name)]

    for project in projects:
        clone_path = os.path.join(destination, project.name)

        if os.path.exists(clone_path):
            if "github" not in Repo(clone_path).remote("origin").urls:
                Repo(clone_path).remote("origin").set_url(project.clone_url)

            print(f"Fetching {group_name}:", project.name, "origin")
            Repo(clone_path).remote("origin").fetch()
        else:
            print(f"Cloning {group_name}:", project.name, project.clone_url)
            try:
                Repo.clone_from(
                    project.clone_url, os.path.join(destination, clone_path)
                )
            except GitCommandError as ex:
                print(f"Probably dont have permission to download: {ex}")
            except Exception as ex:
                print(ex)
