import os, requests, re, json, glob, time
from icecream import ic as logger
from datetime import datetime

if not os.path.exists(f'{os.getcwd()}/logs'):
    os.makedirs(f'{os.getcwd()}/logs')

if not os.path.exists(f'{os.getcwd()}/outputs'):
    os.makedirs(f'{os.getcwd()}/outputs')

# Define a file to log IceCream output
log_file_path = os.path.join(f'{os.getcwd()}/logs', f'{datetime.now().strftime("%Y-%m-%d-%H:%M:%S")}.log')

# Replace logging configuration with IceCream configuration
logger.configureOutput(prefix=' - ', outputFunction=lambda x: open(log_file_path, 'a').write(x + '\n'))

import requests
import time

def find_repo_by_name(repo_name, username, token):
    repositories = []
    page = 1
    
    while True:
        # Construct the URL to search for repositories
        url = f"https://api.github.com/search/repositories?q={repo_name}&page={page}"

        # Make the request with authentication
        response = requests.get(url, auth=(username, token))

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            result = response.json()
            items = result.get('items', [])
            
            # Add the repositories to the list
            repositories.extend(items)
            
            # Check if there are more pages
            if 'next' in response.links:
                page += 1
                time.sleep(3)  # Add a delay to avoid hitting rate limits
            else:
                break
        else:
            # If the request was unsuccessful, print an error message
            logger(f"{repo_name}-{response.status_code}")
            return None

    return repositories

def generate_commit_link(repo_url, commit_hash):
    # Construct GitHub commit link
    commit_link = f"{repo_url.rstrip('/')}/commit/{commit_hash}"
    
    # Check if the commit link exists
    response = requests.get(commit_link)
    if response.status_code == 200:
        return commit_link
    else:
        logger(f"{repo_url}-{commit_hash}-{response.status_code}")
        return None

def save_to_file(commit_link):
    with open('outputs/commits.txt', 'a') as file:
        file.write(f"{commit_link}\n")

def extract_commit_info(pattern):
    commit_info_list = []

    # Find all files matching the pattern
    file_paths = glob.glob(pattern)

    for path in file_paths:

        # Extract language and repo from the pattern
        match = re.match(r'.*/InferredBugs/inferredbugs/([^/]+)/([^/]+)/[^/]+/commit_info\.json', path)
        if match:
            language = match.group(1)
            repo = match.group(2)

            try:
                # Load commit_info.json file
                commit_info = json.load(open(path, 'r'))
                commit_hash = commit_info['hash']

                # Extract additional information from commit_info.json
                commit_info_list.append({'language': language, 'repo': repo, 'commit_hash': commit_hash})
            except Exception as e:
                logger(f"Error loading or processing file {path}: {e}")
        else:
            logger("Pattern does not match expected format.")

    return commit_info_list