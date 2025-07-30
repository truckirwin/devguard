# 🔒 Work Protection Guide - Never Lose Development Work Again

## **Critical Work Loss Prevention Rules**

### **1. Commit Early, Commit Often**
```bash
# After EVERY meaningful change (15-30 minutes of work):
git add .
git commit -m "Brief description of what was changed"
git push origin [branch-name]
```

### **2. Create Feature Branches for Each Task**
```bash
# Before starting ANY new work:
git checkout -b feature/descriptive-name
# Work on single issue
# Test and verify
git push origin feature/descriptive-name
```

### **3. Save Points Before Major Changes**
```bash
# Before attempting any complex change:
git add .
git commit -m "SAVEPOINT: Before attempting [describe change]"
```

## **Daily Protection Routine**

### **Start of Day Checklist**
- [ ] `git status` - Check what branch you're on
- [ ] `git pull origin main` - Get latest changes  
- [ ] Create new feature branch for today's work
- [ ] Verify both frontend and backend are running

### **Every 20-30 Minutes**
- [ ] `git add .` and `git commit -m "Descriptive message"`
- [ ] Test the specific change you just made
- [ ] Push to remote if change is stable

### **End of Day Checklist**  
- [ ] Commit all work: `git add . && git commit -m "End of day: [summary]"`
- [ ] Push to remote: `git push origin [current-branch]`
- [ ] Update project status in `PROJECT_STATUS.md`
- [ ] Note tomorrow's priorities

## **Emergency Recovery Commands**

### **If You Accidentally Lose Changes**
```bash
# Check for uncommitted changes
git stash list

# Recover stashed work
git stash pop

# Find recent commits
git reflog

# Recover specific commit
git cherry-pick [commit-hash]
```

### **If Branch Gets Corrupted**
```bash
# Create new branch from last good commit
git checkout -b recovery/[date] [last-good-commit]

# Or reset to known good state
git reset --hard [commit-hash]
```

## **Backup Strategy**

### **Local Backups**
- Use Time Machine (macOS) or equivalent
- `.git` folder contains full history - ensure it's backed up
- Keep copies of critical files in separate locations

### **Remote Backups**
- Always have GitHub/GitLab remote repository
- Push changes multiple times per day
- Use multiple remotes if working on critical features

## **File-Level Protection**

### **For Critical Files, Use Multiple Saves**
```bash
# Before editing important files:
cp important-file.tsx important-file.tsx.backup-$(date +%Y%m%d_%H%M%S)
```

### **IDE/Editor Settings**
- Enable auto-save in your editor
- Set up automatic git commits in IDE
- Use file watchers for automatic backups

## **Project-Specific Safeguards**

### **NotesGen Specific**
```bash
# Always verify services are running before starting work
curl -s http://127.0.0.1:8000/health
curl -s http://localhost:3001

# Commit after fixing each linting error (not all at once)
git add [specific-file] && git commit -m "Fix: [specific linting issue]"

# Test each component change in browser immediately
# Take screenshots of working features before changing them
```

## **Communication & Documentation**

### **Document Everything**
- Update `PROJECT_STATUS.md` with each major change
- Create `DAILY_LOG.md` to track what was accomplished
- Note any issues encountered and their solutions

### **Recovery Documentation**
- Keep notes of what you were working on
- Document reproduction steps for bugs
- Save screenshots of working states

## **Scripts for Automation**

### **Enhanced Backup Scripts**

**smart-save.sh** - Main backup script with external protection:
- Creates timestamped .zip backup outside project folder
- Saves git diff and status to separate .txt file
- Excludes large directories (node_modules, .git, venv, etc.)
- Commits and pushes to remote repository

**quick-save.sh** - Calls smart-save.sh for quick sessions

**daily-backup.sh** - Enhanced daily backup with special daily .zip file

### **External Backup Structure**
```
../ProjectName_BACKUPS/
├── ProjectName_backup_20250606_065429.zip    # Timestamped backups
├── ProjectName_diff_20250606_065429.txt      # Git diff and context
├── DAILY_ProjectName_20250606.zip            # Daily backups
└── [Multiple timestamped files...]
```

### **Backup Features**
✅ **Full project zip** (excludes large dirs)  
✅ **Git diff tracking** with context  
✅ **Automatic timestamping**  
✅ **External storage** (outside project)  
✅ **Size monitoring** (shows total backup size)  
✅ **Git operations** (commit + push)
✅ **Smart deduplication** (prevents backup proliferation)
✅ **Automatic cleanup** (keeps last 10 backups)

### **🧠 Intelligent Backup Logic**
- **Recent backup exists** (< 30 min): Only git operations, skip zip creation
- **No recent backup**: Create new timestamped backup
- **Significant keywords** detected: Force new backup regardless of timing
  - Keywords: `major`, `complete`, `finished`, `milestone`, `release`, `Daily backup`
- **Auto-cleanup**: Maintains only last 10 regular backups (excludes daily backups)

## **🤖 Automated Protection Triggers**

### **AI Assistant Auto-Save Triggers**
When you indicate task completion with phrases like:
- "Good, that works"
- "That's working now"
- "Perfect, that's done"
- "This section is complete"
- "That fixes it"

**→ AI will automatically run `./quick-save.sh`**

### **Daily Commit Prompts**
- **Morning Prompt (9-11 AM)**: "Ready to commit this morning's work to git?"
- **Afternoon Prompt (2-4 PM)**: "Time for an afternoon git commit?"
- **End of Day**: AI automatically runs `./daily-backup.sh`

### **Session Completion Detection**
After 8+ rounds of focused development work, AI will:
1. Auto-save the progress
2. Suggest a descriptive commit message
3. Ask if you want to push to remote

## **🚨 Manual Red Flags - Stop and Save Immediately**

- About to attempt major refactoring
- Switching between multiple issues
- Experimenting with new approaches
- Working on complex merge conflicts
- Before running any destructive commands
- When feeling tired or rushed

## **Recovery Test**

### **Monthly Recovery Drill**
1. Create test branch with some dummy changes
2. Practice recovering from various scenarios
3. Verify your backup systems work
4. Update this guide based on lessons learned

---

**Remember**: It's better to have 50 small commits that work than to lose 8 hours of changes due to one mistake.

**Next Steps**: Run `chmod +x quick-save.sh daily-backup.sh` to make scripts executable. 