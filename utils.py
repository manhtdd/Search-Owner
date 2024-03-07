import os, requests, re, glob, time
from icecream import ic as logger
from datetime import datetime
from tqdm import tqdm

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

def generate_version_link(repo_url, version):
    # Construct GitHub commit link
    commit_link = f"{repo_url.rstrip('/')}/tree/{version}"
    
    # Check if the commit link exists
    response = requests.get(commit_link)
    if response.status_code == 200:
        return commit_link
    else:
        logger(f"{commit_link} {response.status_code}")
        return None

def save_to_file(commit_link):
    with open('outputs/versions.txt', 'a') as file:
        file.write(f"{commit_link}\n")

def get_version(version, project_name):
    return version[len(project_name)+1:]

def extract_commit_info(pattern):
    version_info_list = []

    # Find all files matching the pattern
    file_paths = glob.glob(pattern)

    for path in tqdm(file_paths):
        file_name = os.path.basename(path)

        # Extract language and repo from the pattern
        match = re.match(r'^(?P<project_name>.*?)_(?P<cve>.*?)_(?P<version>.*?)\.csv$', file_name)
        if match:
            project_name = match.group('project_name')
            cve = match.group('cve')
            version = match.group('version')

            version = get_version(version, project_name)

            try:
                # Extract additional information from commit_info.json
                version_info_list.append({'repo': project_name, 'version': version})
            except Exception as e:
                logger(f"Error loading or processing file {path}: {e}")
        else:
            logger("Pattern does not match expected format.")

    return version_info_list