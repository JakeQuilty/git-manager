# Actions

TODO: write this

## Add File(Static)

## Update Issue Template

## Update License Year

## Merge CODEOWNERS Files

Merges a local CODEOWNERS file with the ones in the repos.

- If a CODEOWNERS does not exist in the repo, it copies the local one in
- Copies in local CODEOWNERS into the repo's CODEOWNERS line by line if they don't exist

`old_codeowners` - path in repo to the CODEOWNERS file
`new_codeowners` - local CODEOWNERS to be merged into old one