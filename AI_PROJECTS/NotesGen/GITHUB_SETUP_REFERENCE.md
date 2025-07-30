# 🐙 GitHub Setup Reference

## Configuration Applied
- Git username and email configured globally
- Default branch set to 'main'
- Push strategy set to 'simple'
- Pull strategy set to merge (not rebase)

## Next Steps

### Push to GitHub
```bash
# If you added a remote origin
git push -u origin main

# If you need to add remote later
git remote add origin https://github.com/USERNAME/REPO.git
git push -u origin main
```

### Cursor GitHub Integration
1. **Command Palette**: `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows)
2. **Search**: "Git: Clone"
3. **Select**: "Clone from GitHub"
4. **Authorize**: Cursor to access GitHub
5. **Access**: Use Cursor's Git panel with `Cmd+Shift+G`

### Useful Git Commands
```bash
# Check status
git status

# Add and commit
git add .
git commit -m "feat: your commit message"

# Push changes
git push

# Pull latest changes
git pull

# Create new branch
git checkout -b feature/new-feature

# Switch branches
git checkout main
```

### GitHub Authentication Options
1. **Personal Access Token** (Recommended for private repos)
   - Go to GitHub Settings > Developer settings > Personal access tokens
   - Generate new token with `repo` scope
   - Use token as password when prompted

2. **SSH Keys** (Most convenient)
   - Generate: `ssh-keygen -t ed25519 -C "your@email.com"`
   - Add to GitHub: Settings > SSH and GPG keys
   - Use SSH URLs: `git@github.com:username/repo.git`

### Troubleshooting
- **Permission denied**: Check GitHub authentication
- **Remote exists**: `git remote remove origin` then re-add
- **Branch conflicts**: `git pull --rebase` or merge manually
