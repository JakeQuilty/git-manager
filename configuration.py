import logging
import os
import yaml

class configuration:

    MANDATORY_BRANCH_PARAMETERS = [
        'branch_name',
        'create_branch'
    ]
    MANDATORY_COMMIT_PARAMETERS = [
        'git_add',
        'commit_message'
    ]
    MANDATORY_PR_PARAMETERS = [
        'create_pr',
        'title',
        'body',
        'base'
    ]
    MANDATORY_GENERAL_PARAMETERS = [
        ['branch', MANDATORY_BRANCH_PARAMETERS],
        ['commit', MANDATORY_COMMIT_PARAMETERS],
        ['pull_request', MANDATORY_PR_PARAMETERS],
        ['remove_repo', []],
        ['remove_tmp_dir', []]
    ]
    MANDATORY_PARAMETERS = [
        'orgs',
        'general',
        'extra_vars'
    ]

    def __init__(self, logger, path_to_config):
        self.__LOGGER = logger
        self.__config = self.__load_config(path_to_config)
        self.__validate()

        # TODO: Figure out a scalable way to retrive the data from the config without using dict

    def error_message(self, message):
        self.__LOGGER.error(message)
        self.__LOGGER.info("------------------ ENDING ------------------")
        exit(1)

    # Gets `config.yml` from the action directory and returns it as a dictionary object
    def __load_config(self, config_file_path):
        self.__LOGGER.info("Retrieving config: {}".format(config_file_path))
        
        # Read the config content
        try:
            config_content = open(config_file_path, 'r').read()
        except OSError as error:
            self.error_message("Could not find config file:\nPath: {path}\nError: {err}".format(path = config_file_path, err = error))

        # Create a python dictionary of the config
        try:
            config = yaml.load(config_content, Loader=yaml.FullLoader)
        except yaml.YAMLError as error:
            self.error_message("Error in configuration file: {}!".format(error))

        return config

    # Validates this config for required fields
    # Exits with exit code 1 if the config is missing required fields
    def __validate(self):
        self.__LOGGER.info("Validating config...")

        # Validate highest level parameters are present
        for key in self.MANDATORY_PARAMETERS:
            if key not in self.__config:
                self.error_message("Config file missing option: {}".format(key))

        # Make sure 'orgs' isn't empty
        if len(self.__config['orgs']) == 0:
            self.error_message("Config file requires at least 1 organization")

        # Check for required general categories and their subcategories
        general = self.__config['general']
        for category in self.MANDATORY_GENERAL_PARAMETERS:
            if category[0] not in general:
                raise ("Config file missing option: general:{}".format(category[0]))
            for sub_cat in category[1]:
                if sub_cat not in general[category[0]]:
                    self.error_message("Config file missing option: general:{}:{}".format(category[0],sub_cat))

        self.__LOGGER.info("Successfully validated config")

    # Returns the config dict
    def get_config(self):
        return self.__config
        