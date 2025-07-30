# Quick Start: Testing The Writers Room Distribution

## 🚀 Test Your Standalone Product

This guide helps you quickly test your VS Code-based Writers Room distribution locally.

## Prerequisites

```bash
# Install dependencies
npm install

# Ensure your extension works
npm run compile
npm run package
```

## Step 1: Build Your First Distribution

```bash
# Build for your current platform (macOS)
npm run build:dist
```

This will:
1. ✅ Download the latest VS Code
2. ✅ Package your Writers Room extension
3. ✅ Create a portable VS Code with your extension pre-installed
4. ✅ Set up writer-friendly defaults
5. ✅ Create platform-specific launcher

## Step 2: Test the Distribution

### macOS
```bash
# Your app will be at:
open dist/"The Writers Room.app"
```

### Windows (if cross-building)
```bash
# Your app will be at:
dist/TheWritersRoom/The\ Writers\ Room.bat
```

### Linux (if cross-building)
```bash
# Your app will be at:
dist/TheWritersRoom/writers-room.sh
```

## What You Should See

1. **VS Code opens** with "The Writers Room" branding
2. **Your extension is active** - see the Writers Room icon in the activity bar
3. **Sample project loads** automatically
4. **AI agents are visible** in the sidebar
5. **Chat interface works** on the right side

## Testing Checklist

- [ ] Application launches without errors
- [ ] Writers Room extension is active (activity bar icon visible)
- [ ] Sample project structure appears in explorer
- [ ] AI agents panel shows your configured agents
- [ ] Chat interface opens and is functional
- [ ] Can create new writing projects
- [ ] File editing works normally
- [ ] All Writers Room commands work (Cmd+Shift+P → "Writers Room")

## Customization Quick Wins

### 1. Change App Name
Edit `scripts/create-distribution.js`:
```javascript
// Line ~240
CFBundleDisplayName: "Your Custom Name"
```

### 2. Custom Welcome Message
Edit `scripts/create-distribution.js`:
```javascript
// Line ~170
'README.md': '# Welcome to Your Writing App\n\nStart writing amazing stories!'
```

### 3. Different Default Theme
Edit `scripts/create-distribution.js`:
```javascript
// Line ~130
"workbench.colorTheme": "Default Light+", // or any theme
```

## Distribution Output

After successful build, you'll have:

```
dist/
├── The Writers Room.app/     # Ready to distribute
└── ...

# Plus installer (if on macOS):
TheWritersRoom-1.0.0.dmg     # Professional installer
```

## Common Issues & Solutions

### Issue: "Permission denied" on macOS
```bash
# Make the distribution executable
chmod +x dist/"The Writers Room.app"/Contents/MacOS/*
```

### Issue: Extension not loading
```bash
# Rebuild extension first
npm run compile
npm run package
npm run build:dist
```

### Issue: VS Code download fails
```bash
# Check internet connection and try again
# Or manually download and place in temp/ folder
```

## Next Steps

Once your distribution works locally:

1. **Customize Branding**: Add your logo, change colors, update messages
2. **Test on Target Platforms**: Build for Windows/Linux if needed
3. **Create Professional Installers**: DMG for macOS, MSI for Windows
4. **Set Up Distribution**: Website, app stores, or direct download

## Professional Distribution

For a commercial product:

```bash
# Build all platforms
npm run build:all

# You'll get:
TheWritersRoom-1.0.0.dmg           # macOS installer
TheWritersRoom-1.0.0-Windows.zip   # Windows portable
TheWritersRoom-1.0.0-Linux.tar.gz  # Linux portable
```

## Development vs Distribution

Keep them separate:

```bash
# Development (your Cursor environment)
cd /Users/truckirwin/Desktop/TheWritersRoom
cursor .

# Distribution testing  
cd /Users/truckirwin/Desktop/TheWritersRoom
npm run build:dist
open dist/"The Writers Room.app"
```

Your Cursor environment stays clean! 🎉

## Success! 

You now have:
- ✅ A professional standalone writing application
- ✅ VS Code + your extension pre-configured
- ✅ No interference with your development environment
- ✅ Ready-to-distribute product

**Your Writers Room is ready for the world!** 🚀 