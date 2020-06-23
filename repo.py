import json
import os
import requests
from subprocess import check_output

###
#  FIXME: This class needs to be redone with api calls instead of commands
#  https://github.com/JakeQuilty/git-manager/issues/1
class repo:

    def __init__(self, logger, org, repo, tmp_dir):
        self.LOGGER = logger
        self.title = os.path.join(org,repo)
        self.org = org
        self.repo = repo
        self.parent_dir = tmp_dir # parent dir of the cloned repo
        self.curr_dir = os.path.join(tmp_dir, self.repo) # dir of repo
        self.branch = "" # TODO: have this grab the branch name from API on instantiation
        self.auth_info = self.get_auth_information() # 0: user, 1: auth_token

    def subprocess_command(self, command, working_dir):
        self.LOGGER.info("Executing: {}".format(" ".join(command)))
        command_output = check_output(command, cwd = working_dir).decode('utf-8')
        if len(command_output) > 0:
            self.LOGGER.info("Response:\n{}".format(command_output))

    # Clones repo to the parent directory that was provided on instantiation
    def git_clone(self):
        git_url = "https://github.com/{}/{}.git".format(self.org, self.repo)
        command = ['git', 'clone', git_url]
        self.subprocess_command(command, self.parent_dir)

    def git_branch(self, branch_name):
        command = ['git', 'branch', branch_name]
        self.subprocess_command(command, self.curr_dir)

    def git_checkout(self, branch_name):
        command = ['git', 'checkout', branch_name]
        self.subprocess_command(command, self.curr_dir)
        self.branch = branch_name

    # add_files is expected to be a list
    def git_add(self, add_files):
        command = ['git', 'add']
        command.append(add_files)
        self.subprocess_command(command, self.curr_dir)

    def git_commit(self, commit_message):
        # Make sure commit_message is in quotes
        if commit_message[0] != "\"":
            commit_message = "\"{}".format(commit_message)
        if commit_message[len(commit_message)-1] != "\"":
            commit_message = "{}\"".format(commit_message)

        command = ['git', 'commit', '-m', commit_message]
        self.subprocess_command(command, self.curr_dir)

    def git_push(self):
        command = ['git', 'push', '--set-upstream', 'origin', self.branch]
        self.subprocess_command(command, self.curr_dir)

    def git_create_pull_request(self, pr_title, pr_head, pr_base, pr_body = None):
        self.LOGGER.info("{}: Creating Pull Request... {} -> {}".format(self.get_title(), pr_head, pr_base))
        BASE_URL = "https://api.github.com"
        pr_api_url = "{base}/repos/{org_name}/{repo_name}/pulls".format(base = BASE_URL, org_name = self.org, repo_name = self.repo)
        self.LOGGER.info("URL: {}".format(pr_api_url))

        # Create payload
        payload = {
            "title": pr_title,
            "body": pr_body,
            "head": pr_head,
            "base": pr_base,
        }
        self.LOGGER.info("Payload: {}".format(str(payload)))
        
        response = requests.post(pr_api_url, json = payload, auth = (self.auth_info[0], self.auth_info[1]))
        self.LOGGER.info("Statuse Code: {}".format(response.status_code))

        if response.status_code != 201:
            self.LOGGER.error("{}: pull request FAIL".format(self.get_title()))
            self.LOGGER.info("Response: {}".format(response.text))
            return None

	## TODO Throw an exception if pr fails!!
        raw_response = json.loads(response.text)

        return raw_response['html_url']

    def get_auth_information(self):
        user = os.getenv('GITHUB_USERNAME')
        auth_token = os.getenv('GITHUB_AUTH_TOKEN')
        if not user or not auth_token:
            raise Exception("ERROR: GITHUB_USERNAME or GITHUB_AUTH_TOKEN not provided!")
        return [user, auth_token]

    def get_dir(self):
        return str(self.curr_dir)

    def get_title(self):
        return str(self.title)
    
    def get_parent_dir(self):
        return str(self.parent_dir)

    def get_branch(self):
        return str(self.branch)