import requests
import itertools
from collections import defaultdict
from sys import argv
from dotenv import load_dotenv
from tabulate import tabulate
import os

load_dotenv()
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
BASE_URL = 'https://api.github.com'


def get_commits(owner, repo):
    commits_url = f"{BASE_URL}/repos/{owner}/{repo}/commits"
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(commits_url, headers=headers)
    commits = response.json()

    return commits


def get_commit_files(owner, repo, commit_sha):
    files_url = f"{BASE_URL}/repos/{owner}/{repo}/commits/{commit_sha}"
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(files_url, headers=headers)
    commit_data = response.json()

    return [file['filename'] for file in commit_data.get('files', [])]


def main(owner, repo):
    file_developers = defaultdict(set)
    developer_pairs = defaultdict(lambda: {'count': 0, 'files': set()})

    commits = get_commits(owner, repo)
    for commit in commits:
        author = commit['commit']['author']['name']
        commit_sha = commit['sha']
        files = get_commit_files(owner, repo, commit_sha)

        for file in files:
            file_developers[file].add(author)

    for file, devs in file_developers.items():
        for dev_pair in itertools.combinations(devs, 2):
            sorted_pair = tuple(sorted(dev_pair))
            developer_pairs[sorted_pair]['count'] += 1
            developer_pairs[sorted_pair]['files'].add(file)

    sorted_pairs = sorted(developer_pairs.items(), key=lambda item: item[1]['count'], reverse=True)
    table = [[pair, info['count'], ', '.join(info['files'])] for pair, info in sorted_pairs]
    print(tabulate(table, headers=['Developer Pair', 'Count', 'Files']))


if __name__ == "__main__":
    if len(argv) != 3:
        print("Usage: python3 main.py <owner> <repo>")
    else:
        main(argv[1], argv[2])
