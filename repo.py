import os
from subprocess import check_output

class repo:
    def __init__(self, logger, org, repo, tmp_dir):
        self.LOGGER = logger
        self.title = os.path.join(org,repo)
        self.org = org
        self.repo = repo
        self.parent_dir = tmp_dir # parent dir of the cloned repo
        self.curr_dir = os.path.join(tmp_dir, self.repo) # dir of repo
        self.branch = "" # TODO: have this grab the branch name from API on instantiation

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

    def get_dir(self):
        return str(self.curr_dir)

    def get_title(self):
        return str(self.title)
    
    def get_parent_dir(self):
        return str(self.parent_dir)

    def get_branch(self):
        return str(self.branch)