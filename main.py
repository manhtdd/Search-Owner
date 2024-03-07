from utils import *
import argparse, json, pickle
from tqdm import tqdm

def read_args():
    parser = argparse.ArgumentParser(description='Process JSON data.')
    parser.add_argument('-data_path', help='Path to the dataset_cleaned.json')
    parser.add_argument('-github_info')
    return parser.parse_args()

def main():
    args = read_args()

    # Example usage:
    repo_commits = extract_commit_info(args.data_path)
    github_info = json.load(open(args.github_info, 'r'))
    found_repos = []
    try:
        with open('outputs/found_repos.jsonl', 'r') as f:
            for line in f:
                data = json.loads(line)
                found_repos.append(data)
    except:
        found_repos = []

    not_found_repos = []
    for index, repo_commit in enumerate(repo_commits):
        print(f"{index}/{len(repo_commits)} repos:")
        if repo_commit in found_repos:
            continue
    
        repositories = find_repo_by_name(repo_commit['repo'], github_info['user'], github_info['token'])

        if repositories:
            for repo in tqdm(repositories):
                repo_url = repo['html_url']

                # Generate commit link and save to file
                commit_link = generate_version_link(repo_url, version=repo_commit['version'])
                if commit_link:
                    save_to_file(commit_link)
                    found_repos.append(repo_commit)
                    json_data = json.dumps(repo_commit)
                    with open('outputs/found_repos.jsonl', 'a') as f:
                        f.write(json_data + '\n')
                    break
            
            not_found_repos.append(repo_commit)
            json_data = json.dumps(repo_commit)
            with open('outputs/not_found_repos.jsonl', 'a') as f:
                f.write(json_data + '\n')

if __name__ == "__main__":
    main()