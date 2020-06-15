#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import sys
from os import path
import tempfile
from subprocess import check_output
from os import listdir
from os.path import isfile, join
import shutil
import json
import logging

from repo import repo


global LOGGER

FAILED_REPOS = []
SUCCESFUL_REPOS = []
PR_LINKS = []

MANDATORY_GENERAL_PARAMETERS = [
	'pr_name',
	'branch_name',
	'commit_message',
	'git_add',
]

def create_logger():
	# create logger with 'spam_application'
	logger = logging.getLogger('git-manager')
	logger.setLevel(logging.DEBUG)
	# create file handler which logs even debug messages
	fh = logging.FileHandler('git-manager.logs')
	fh.setLevel(logging.DEBUG)
	# create console handler with a higher log level
	ch = logging.StreamHandler()
	ch.setLevel(logging.ERROR)
	# create formatter and add it to the handlers
	formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	fh.setFormatter(formatter)
	ch.setFormatter(formatter)
	# add the handlers to the logger
	logger.addHandler(fh)
	logger.addHandler(ch)
	logger.info("------------------ STARTING ------------------")
	logger.info("Logger initialized")
	return logger

def error_message(message):
	LOGGER.error(message)
	LOGGER.info("------------------ ENDING ------------------")
	exit(1)

# TODO add more coverage
def check_valid_arguments(args):
	if len(args) == 1 or len(args) > 2:
		print("git-manager requires parameter 'action dir'")
		print("Example: `git-manager ./actions/action_dir`")
		LOGGER.debug("ERROR: git-manager requires parameter 'action dir'")
		exit(1)

def get_config(action_dir):
	config_file_path = action_dir + "/config.yml"
	# read the config content
	config_content = open(config_file_path, 'r').read()
	# create the python dictionary of the config, this will throw yaml 
	# exception if the config does not meet yaml standards
	config = yaml.load(config_content)

	# validate mandatory config fields
	#validate_config(config)				################################################
	return config

def validate_config(config):
	LOGGER.info("Starting to validate config")
	if 'orgs' not in config:
		error_message("'orgs' was not provided in the config file")

	if 'general' not in config:
		error_message("'general' was not provided in the config file")

	general = config['general']
	for mandatory_parameter in MANDATORY_GENERAL_PARAMETERS:
		if mandatory_parameter not in general:
			error_message("'{}' was not provided in the config file".format(mandatory_parameter))
	LOGGER.info("Successfully validated config")

def create_working_dir():
	dir_path = tempfile.mkdtemp()
	LOGGER.info("Created a tmp directory for cloning repos: " + dir_path)
	return dir_path

# creates a list of repo objects from the config
def create_repo_list(config, working_dir):
	repo_list = []
	for curr_org, value in config['orgs'].items():
		repos = value['repos']
		for curr_repo in repos:
			repo_list.append(repo(LOGGER, curr_org, curr_repo, working_dir))
	return repo_list

def update_single_repo(config, repo, action_dir):
	LOGGER.info("----- {} -----".format(repo.get_title()))
	# clones the repo to working_dir(or whatever dir was specified on the repo's creation
	LOGGER.info("Cloning repo '{}' to {}".format(repo.get_title(), repo.get_parent_dir()))
	repo.git_clone()

	# change branch
	branch = config['general']['branch']['branch_name']
	if config['general']['branch']['create_branch']:
		LOGGER.info("Creating branch: {}".format(branch))
		repo.git_branch(branch)
	
	LOGGER.info("Checking out branch: {}".format(branch))
	repo.git_checkout(branch)

	# run action file on repo
	# this needs some serious thought and work.
	LOGGER.info("Running action on: {}".format(repo.get_title()))
	run_action(action_dir, repo.get_dir())

	# add files to commit that are specified in config
	for to_add in config['general']['commit']['git_add']:
		repo.git_add(to_add)

	# commit
	repo.git_commit(config['general']['commit']['commit_message'])

	# push
	repo.git_push()

	#pull request
	if config['general']['pull_request']['create_pr']:
		pr_title = config['general']['pull_request']['title']
		pr_body = config['general']['pull_request']['body']
		pr_base = config['general']['pull_request']['base']

		pr_link = repo.git_create_pull_request(pr_title, branch, pr_base, pr_body)

		if pr_link is not None:
			PR_LINKS.append(pr_link)

def run_action(action_dir, repo_dir):
	run_path = path.join(action_dir, "action")
	command = [run_path, str(repo_dir)]
	subprocess_command(command, None)

def subprocess_command(command, working_dir):
	LOGGER.info("Executing: {}".format(" ".join(command)))
	command_output = check_output(command, cwd = working_dir).decode('utf-8')
	if len(command_output) > 0:
            LOGGER.info("Response:\n{}".format(command_output))

def update_all_repos(config, repo_list, action_dir):
	for curr_repo in repo_list:
		try:
			update_single_repo(config, curr_repo, action_dir)
			print("{}: SUCCESS".format(curr_repo.get_title()))
			LOGGER.info("{}: SUCCESS\n".format(curr_repo.get_title()))
			SUCCESFUL_REPOS.append(curr_repo.get_title())
		except:
			LOGGER.error("{}: FAIL\n".format(curr_repo.get_title()))
			FAILED_REPOS.append(curr_repo.get_title())

		if config['general']['remove_repo']:
			LOGGER.info("Removing local repo: {}\n".format(curr_repo.get_dir()))
			shutil.rmtree(curr_repo.get_dir())

def summary_message():
	total_repos = len(SUCCESFUL_REPOS) + len(FAILED_REPOS)

	success_string = "Success({suc}/{tot}):".format(suc = len(SUCCESFUL_REPOS), tot = total_repos)
	for repo in SUCCESFUL_REPOS:
		success_string = success_string + "\n{}".format(repo)

	fail_string = "Fail({fail}/{tot}):".format(fail = len(FAILED_REPOS), tot = total_repos)
	for repo in FAILED_REPOS:
		fail_string = fail_string + "\n{}".format(repo)

	pr_string = "Pull Requests:"
	for link in PR_LINKS:
		pr_string = pr_string + "\n{}".format(link)

	return "SUMMARY:\n\n{success}\n\n{fail}\n\n{pr}".format(success = success_string, fail = fail_string, pr = pr_string)

def main():
	check_valid_arguments(sys.argv)
	action_dir = sys.argv[1]
	config = get_config(action_dir)
	working_dir = create_working_dir()
	repo_list = create_repo_list(config, working_dir)
	update_all_repos(config, repo_list, action_dir)
	
	### clean up tmp dir
	if config['general']['remove_tmp_dir']:
		LOGGER.info("Removing tmp dir: {}".format(working_dir))
		shutil.rmtree(working_dir)

	# show completion message. failed repos and #. success. pr links. whether tmp dir is still present
	summary = summary_message()
	LOGGER.info(summary)
	print("\n"+ summary)

if __name__ == "__main__":
	LOGGER = create_logger()
	main()
	LOGGER.info("------------------ ENDING ------------------")

# shutil.rmtree(dir_path)




