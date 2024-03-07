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

def find_repo_by_name(repo_name, username, token):
    # Construct the URL to search for repositories
    url = f"https://api.github.com/search/repositories?q={repo_name}"

    # Make the request with authentication
    response = requests.get(url, auth=(username, token))

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        result = response.json()
        items = result.get('items', [])
        
        return items
    else:
        # If the request was unsuccessful, print an error message
        logger(f"{repo_name} {response.status_code}")
        return None

def generate_commit_link(repo_url, commit_hash):
    # Construct GitHub commit link
    commit_link = f"{repo_url.rstrip('/')}/commit/{commit_hash}"
    
    # Check if the commit link exists
    response = requests.get(commit_link)
    if response.status_code == 200:
        return commit_link
    else:
        logger(f"{commit_link} {response.status_code}")
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
                commit_info_list.append({'repo': repo, 'commit_hash': commit_hash})
            except Exception as e:
                logger(f"Error loading or processing file {path}: {e}")
        else:
            logger("Pattern does not match expected format.")

    return commit_info_list