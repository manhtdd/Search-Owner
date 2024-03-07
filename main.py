from utils import *
import argparse

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
    for repo_commit in repo_commits:
        if repo_commit in found_repos:
            continue
        
        repositories = find_repo_by_name(repo_commit['repo'], github_info['user'], github_info['token'])

        if repositories:
            for repo in repositories:
                repo_url = repo['html_url']

                # Generate commit link and save to file
                commit_link = generate_commit_link(repo_url, commit_hash=repo_commit['commit_hash'])
                if commit_link:
                    save_to_file(commit_link)
                    found_repos.append(repo_commit)
                    break

if __name__ == "__main__":
    main()