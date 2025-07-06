# Claude Instructions

## Command Execution Policy
- Run all read-only commands without asking for permission
- NEVER run `sudo` or any commands that require password authentication without explicit user permission
- Examples of commands to run freely: `ls`, `cat`, `grep`, `find`, `git status`, `git log`, `python --version`, etc.
- Examples of commands to ask permission for: `sudo`, `rm`, `mv` (when moving to different directories), `git commit`, `git push`, etc.

## Git Attribution Policy
When creating commits or pull requests, ALWAYS include attribution to Claude:

### For Commits
All commits must end with:
```
🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### For Pull Requests
All pull request descriptions must end with:
```
🤖 Generated with [Claude Code](https://claude.ai/code)
```

### For Pull Request Merges
ALWAYS use squash merge when merging pull requests. Use the `gh pr merge --squash` command.

## Git Workflow Policy
**NEVER push directly to the main branch.** ALWAYS use pull requests for any changes to main.

- Create a feature branch for all changes
- Commit changes to the feature branch
- Create a pull request to merge into main
- Use squash merge to merge the pull request
- Delete the feature branch after merging

This ensures proper code review and maintains a clean commit history on main.

### "Submit to GitHub" Command
When the user says "submit to GitHub", perform the complete workflow:

1. **Create and push feature branch**: Create branch, commit changes, push to remote
2. **Create pull request**: Use `gh pr create` with appropriate title and description
3. **Merge pull request**: Use `gh pr merge --squash` to merge the PR
4. **Clean up branches**: 
   - Switch back to main branch (`git checkout main`)
   - Pull latest changes (`git pull origin main`)
   - Delete local feature branch (`git branch -d <branch-name>`)
   - Remote branch will be auto-deleted by GitHub after merge

This complete workflow ensures changes are properly reviewed, merged, and cleaned up without manual intervention.

### For Branch Naming
When creating local branches, use the following naming convention:
`{type}/{YYYYMMDD}/{description}`

Examples:
- `feature/20250625/add-test-generator`
- `bug/20250625/fix-edge-case`
- `refactor/20250625/improve-performance`

Where:
- `{type}`: feature, bug, refactor, docs, etc.
- `{YYYYMMDD}`: today's date in macbook's local time in YYYYMMDD format. For example, June 25, 2025 becomes "20250625"
- `{description}`: brief description using kebab-case

This ensures proper attribution when Claude creates commits or pull requests for the leetcode-testgen project.