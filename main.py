from utils import *
import argparse, json
from tqdm import tqdm
import pandas as pd

def read_args():
    parser = argparse.ArgumentParser(description='Process JSON data.')
    parser.add_argument('-data_path', help='Path to the dataset_cleaned.json')
    parser.add_argument('-github_info')
    return parser.parse_args()

def main():
    args = read_args()

    # Example usage:
    if not os.path.exists('outputs/commit_info.csv'):
        repo_commits = extract_commit_info(args.data_path)
    else:
        repo_commits = pd.read_csv('outputs/commit_info.csv')

    github_info = json.load(open(args.github_info, 'r'))

    for index, row in repo_commits.iterrows():
        print(f"{index + 1}/{repo_commits.shape[0]} repos:")
        if row['found']:
            continue
    
        repositories = find_repo_by_name(row['repo'], github_info['user'], github_info['token'])

        if repositories:
            for repo in tqdm(repositories):
                repo_url = repo['html_url']

                # Generate commit link and save to file
                commit_link = generate_version_link(repo_url, version=row['version'])
                if commit_link:
                    repo_commits.at[index, 'found'] = True
                    repo_commits.at[index, 'link'] = commit_link
                    break

    repo_commits.to_csv('outputs/commit_info.csv', index=False)

if __name__ == "__main__":
    main()