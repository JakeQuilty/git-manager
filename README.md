# git-manager

Manage a large amount of GitHub repositories at once.

## Requirements

- python >= 3.0.0
- [requests](https://requests.readthedocs.io/en/master/)
    - `python3 -m pip install requests`

## How To Use

1. Pick an action from `actions/`
1. Fill out `config.yml`. See [Config Files](#config-files) for details.
1. Set up how you're [authenticating with GitHub](#github-authentication)
1.  Run
    `./git-manager {ACTION DIR}`

    Example:
    ```
    pwd -> /path/to/git-manager
    ./git-manager ./action/add-file-static
    ```

## Config Files

### Empty Config:
```
# List orgs and repos here
orgs:
    your_org1:
        repos:
            - repo1
            - repo2
    your_org2:
        repos: [repo1, repo2]
  
# General required configs here
general:
    branch:
        branch_name:
        create_branch:
    commit:
        git_add:
        commit_message: 
    pull_request:
        create_pr:
        title:
        body:
        base:
    remove_repo:
    remove_tmp_dir:

# Variables needed in action file
extra_vars:
```

### Details


**orgs** - List of GitHub organizations or users that own the repositories

- `repos`
   - List of repositories to be managed

**general** - General configuration details

- `branch`
   - `branch_name`
     - The name of the branch to be worked on during runtime
   - `create_branch`
     - `yes` or `no` to create a branch with `branch_name`
     - **Use if the branch doesn't already exist.**

- `commit`
    - `git_add`
        - List of files to `git add` to the commit
        - Example:
        ```
        git_add:
            - CONTRIBUTING.md
            - .github/ISSUE_TEMPLATE/bug.md
        ```
    - `commit_message`
        - The title of the commit

- `pull_request`
    - `create_pr`
        - `yes` or `no` to create a pull request from `branch_name` to `base` on each repo
        - Requires [GitHub Authentication](#github-authentication)
        - Auth Token requires correct privileges
    - `title`
        - Title of the pull request
    - `body`
        - Body description of the pull request
        - Not a required parameter
    - `base`
        - Base branch to make the pull request point towards
        - `master` in *most* cases

- `remove_repo`
    - `yes` or `no` to remove each repo locally, after pusing the changes
    - Helpful if changing a ***lot*** of repos and storage space is an issue
- `remove_tmp_dir`
    - `yes` or `no` to remove the temporary directory after completion

**extra_vars** - List of action specific variables

## GitHub Authentication

There are two ways to set up your local environment to run the script, but
either way you'll need a GitHub account and a
[personal access token](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line).

### Running using environment variables

1. Set the following environment variables:
  `GITHUB_USERNAME`
  `GITHUB_AUTH_TOKEN`

1. To start, run
   ```
   ./git-manager {ACTION DIR}
   ```

### Running using Summon

1. You can store your GitHub auth token in your OSX keyring and run this script using
   [Summon](https://github.com/cyberark/summon) and the [keyring provider](https://github.com/cyberark/summon-keyring/).

   To do this, add your auth token to your keyring by running:
   ```
   security add-generic-password \
     -s "summon" \
     -a "github/api_token" \
     -w "[ACCESS TOKEN]"
   ```

1. Update [`secrets.yml`](secrets.yml) to include your github username.

1. To start, run
   ```
   summon -p keyring.py ./git-manager {ACTION DIR}
   ```

## Action Directory

The script requires an action directory to be specified on startup. An action directory consists of, at the very minimum, a `config.yml` and an `action` script. Any other files necessary to the specific action should be kept in this directory.

The `action` script must be able to be executed with `./path/action`.

The `action` script is passed the path to the current repo as a parameter. 

- Ex `./actions/update-issue-template/action /tmp/path/to/tmpvgxmpptn/current-repo`
 