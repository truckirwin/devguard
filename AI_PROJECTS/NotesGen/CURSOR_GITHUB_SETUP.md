# 🐙 Cursor + GitHub Configuration Guide

## 🎯 Overview
This guide covers setting up GitHub integration in Cursor editor for seamless version control and collaboration.

## 🔐 Step 1: GitHub Authentication

### Option A: GitHub Authentication (Recommended)
1. **Open Cursor Command Palette**: `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows)
2. **Search for**: `Git: Clone`
3. **Select**: `Clone from GitHub`
4. **Cursor will prompt**: "Sign in to GitHub"
5. **Click**: "Allow" in browser
6. **Authorize**: Cursor to access your GitHub account

### Option B: Personal Access Token
1. **Go to**: [GitHub Settings > Personal Access Tokens](https://github.com/settings/tokens)
2. **Generate new token** with permissions:
   - `repo` (full repository access)
   - `workflow` (GitHub Actions)
   - `user:email` (access email)
3. **Copy token** and store securely
4. **In Cursor**: Settings > Extensions > Git > Authentication

## 🚀 Step 2: Create GitHub Repository

### Via GitHub Web Interface:
```bash
# 1. Go to GitHub.com
# 2. Click "New Repository"
# 3. Repository name: "NotesGen"
# 4. Description: "AI-powered PowerPoint processing and note generation"
# 5. ❌ DON'T initialize with README (we have existing code)
# 6. Click "Create Repository"
```

### Via Cursor (Alternative):
1. **Command Palette**: `Cmd+Shift+P`
2. **Type**: `GitHub: Create Repository`
3. **Fill details** and create

## 🔗 Step 3: Connect Local Repository

### Add Remote Origin:
```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/NotesGen.git

# Verify remote is added
git remote -v
```

### Push to GitHub:
```bash
# Push main branch and set upstream
git push -u origin main

# Verify push successful
git log --oneline
```

## ⚙️ Step 4: Configure Cursor Settings

### Enable GitHub Features:
1. **Open Settings**: `Cmd+,` (Mac) or `Ctrl+,` (Windows)
2. **Search for**: "github"
3. **Enable these features**:
   - ✅ `Git: Enable Smart Commit`
   - ✅ `Git: Auto Fetch`
   - ✅ `Git: Auto Repository Detection`
   - ✅ `GitHub: Git Authentication`

### Git Configuration:
```bash
# Set your GitHub email and name
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Use Cursor as default editor
git config --global core.editor "cursor"
```

## 🎨 Step 5: Cursor GitHub Features

### Source Control Panel:
1. **Open Source Control**: `Ctrl+Shift+G`
2. **View Changes**: See modified files
3. **Stage Changes**: Click `+` next to files
4. **Commit**: Write message and click ✓
5. **Push**: Click "..." → Push

### Command Palette Git Commands:
- **`Git: Clone`** - Clone repository
- **`Git: Add Remote`** - Add remote repository
- **`Git: Push`** - Push to remote
- **`Git: Pull`** - Pull from remote
- **`Git: Create Branch`** - Create new branch
- **`Git: Checkout`** - Switch branches
- **`Git: Merge`** - Merge branches

### GitHub Pull Requests:
1. **Install**: GitHub Pull Requests extension
2. **Command**: `GitHub Pull Requests: Create`
3. **Review**: PRs directly in Cursor
4. **Merge**: Complete workflow in editor

## 🔄 Step 6: Workflow Integration

### Daily Development:
```bash
# 1. Start work - sync with remote
git pull origin main

# 2. Create feature branch
git checkout -b feature/new-feature

# 3. Make changes in Cursor
# 4. Stage and commit via Source Control panel
# 5. Push via Cursor UI or command

# 6. Create PR via GitHub extension
```

### Branch Management in Cursor:
1. **Bottom-left status bar**: Shows current branch
2. **Click branch name**: Switch branches
3. **Command Palette**: `Git: Create Branch`
4. **Source Control panel**: Manage branches

## 📊 Step 7: GitHub Dashboard

### View Repository Status:
1. **Command Palette**: `GitHub: Open Repository`
2. **View**: Issues, PRs, Actions
3. **Quick access**: To GitHub features

### Pull Request Creation:
1. **After pushing branch**: Cursor shows PR option
2. **Click notification**: "Create Pull Request"
3. **Fill details**: Title, description, reviewers
4. **Create**: PR directly from Cursor

## 🛠️ Troubleshooting

### Authentication Issues:
```bash
# Clear credentials and re-authenticate
git config --global --unset credential.helper
# Then retry GitHub operations
```

### Remote Issues:
```bash
# Remove incorrect remote
git remote remove origin

# Add correct remote
git remote add origin https://github.com/USERNAME/REPO.git
```

### Push Rejected:
```bash
# If remote has changes you don't have
git pull origin main --rebase
git push origin main
```

## 🚀 Quick Setup Commands

Run these commands to set up GitHub integration:

```bash
# 1. Configure Git (replace with your details)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 2. Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/NotesGen.git

# 3. Push to GitHub
git push -u origin main

# 4. Create and push feature branch
git checkout -b feature/github-integration
git add CURSOR_GITHUB_SETUP.md
git commit -m "docs: add Cursor GitHub integration guide"
git push origin feature/github-integration
```

## 📝 Best Practices

### Commit Messages:
- Use Cursor's commit message templates
- Follow conventional commits format
- Write clear, descriptive messages

### Branch Protection:
- Set up branch protection rules on GitHub
- Require PR reviews for main branch
- Enable status checks

### Code Reviews:
- Use GitHub Pull Requests extension
- Review code directly in Cursor
- Leave comments and suggestions

---

**🎉 You're Ready!** Your Cursor editor is now fully integrated with GitHub for seamless version control and collaboration.