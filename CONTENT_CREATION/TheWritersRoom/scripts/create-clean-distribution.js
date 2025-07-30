#!/usr/bin/env node

/**
 * The Writers Room - Clean Distribution Builder
 * Creates a properly engineered VS Code portable distribution
 * 
 * Engineering Principles:
 * - Don't modify VS Code's original bundle (prevents signing issues)
 * - Use VS Code's official portable mode
 * - Proper extension installation via VS Code CLI
 * - Clean separation of concerns
 */

const fs = require('fs-extra');
const path = require('path');
const { execSync } = require('child_process');

class CleanDistributionBuilder {
    constructor() {
        this.projectRoot = path.join(__dirname, '..');
        this.buildDir = path.join(this.projectRoot, 'build');
        this.distDir = path.join(this.projectRoot, 'dist-clean');
        this.tempDir = path.join(this.projectRoot, 'temp-clean');
        this.version = require('../package.json').version;
    }

    async build() {
        console.log('🏗️  Starting Clean Distribution Build');
        console.log('=====================================\n');

        try {
            await this.cleanup();
            await this.createDirectories();
            await this.buildExtension();
            await this.downloadVSCode();
            await this.extractVSCode();
            await this.setupPortableMode();
            await this.installExtension();
            await this.createConfiguration();
            await this.createSampleProject();
            await this.createLauncher();
            await this.packageDistribution();
            await this.createInstaller();
            
            console.log('\n✅ Clean distribution build completed!');
            console.log(`📦 Output: ${this.distDir}`);
            console.log(`🚀 Test with: open "${this.distDir}/The Writers Room.app"`);
        } catch (error) {
            console.error('\n❌ Build failed:', error.message);
            console.error(error.stack);
            process.exit(1);
        }
    }

    async cleanup() {
        console.log('🧹 Cleaning previous builds...');
        await fs.remove(this.tempDir);
        await fs.remove(this.distDir);
        await fs.remove(this.buildDir);
    }

    async createDirectories() {
        console.log('📁 Creating build directories...');
        await fs.ensureDir(this.tempDir);
        await fs.ensureDir(this.distDir);
        await fs.ensureDir(this.buildDir);
    }

    async downloadVSCode() {
        console.log('⬇️  Downloading VS Code for macOS...');
        
        // Detect architecture and download appropriate version
        const { execSync: execSyncSync } = require('child_process');
        const arch = execSyncSync('uname -m', { encoding: 'utf8' }).trim();
        
        let vscodeUrl;
        if (arch === 'arm64') {
            // Apple Silicon version
            vscodeUrl = 'https://update.code.visualstudio.com/latest/darwin-arm64/stable';
            console.log('   Detected Apple Silicon (ARM64) - downloading ARM64 version');
        } else {
            // Intel version
            vscodeUrl = 'https://update.code.visualstudio.com/latest/darwin/stable';
            console.log('   Detected Intel (x86_64) - downloading Intel version');
        }
        
        const downloadPath = path.join(this.tempDir, 'vscode.zip');
        
        execSync(`curl -L "${vscodeUrl}" -o "${downloadPath}"`, { 
            stdio: 'inherit',
            cwd: this.tempDir 
        });
        
        console.log('✅ VS Code downloaded');
    }

    async extractVSCode() {
        console.log('📦 Extracting VS Code...');
        
        const zipPath = path.join(this.tempDir, 'vscode.zip');
        const extractPath = path.join(this.tempDir, 'vscode-extracted');
        
        await fs.ensureDir(extractPath);
        execSync(`unzip -q "${zipPath}" -d "${extractPath}"`, { stdio: 'inherit' });
        
        // Move VS Code.app to a standard location
        const vscodeApp = path.join(extractPath, 'Visual Studio Code.app');
        const vscodeDestination = path.join(this.buildDir, 'VSCode.app');
        
        await fs.move(vscodeApp, vscodeDestination);
        console.log('✅ VS Code extracted');
    }

    async setupPortableMode() {
        console.log('⚙️  Setting up VS Code portable mode...');
        
        const vscodeApp = path.join(this.buildDir, 'VSCode.app');
        const dataDir = path.join(vscodeApp, 'Contents', 'Resources', 'app', 'data');
        
        // Create portable data structure
        await fs.ensureDir(path.join(dataDir, 'user-data'));
        await fs.ensureDir(path.join(dataDir, 'extensions'));
        await fs.ensureDir(path.join(dataDir, 'tmp'));
        
        console.log('✅ Portable mode configured');
    }

    async buildExtension() {
        console.log('🔨 Building The Writers Room extension...');
        
        // Ensure extension is compiled (compile before downloading VS Code to avoid conflicts)
        execSync('npm run compile', { 
            stdio: 'inherit', 
            cwd: this.projectRoot 
        });
        
        // Ensure build directory exists for output
        await fs.ensureDir(this.buildDir);
        
        // Package extension as .vsix
        const vsixOutput = path.join(this.buildDir, 'the-writers-room.vsix');
        execSync(`npx vsce package --out "${vsixOutput}"`, { 
            stdio: 'inherit', 
            cwd: this.projectRoot 
        });
        
        console.log('✅ Extension built and packaged');
    }

    async installExtension() {
        console.log('📦 Installing extension to portable VS Code...');
        
        const vscodeApp = path.join(this.buildDir, 'VSCode.app');
        const dataDir = path.join(vscodeApp, 'Contents', 'Resources', 'app', 'data');
        const vsixPath = path.join(this.buildDir, 'the-writers-room.vsix');
        
        // Manual extension installation (more reliable than CLI)
        await this.manualExtensionInstall(vsixPath, dataDir);
        
        console.log('✅ Extension installed');
    }

    async manualExtensionInstall(vsixPath, dataDir) {
        const extensionsDir = path.join(dataDir, 'extensions');
        
        // Extract VSIX file (it's just a ZIP)
        const tempExtractDir = path.join(this.tempDir, 'extension-extract');
        await fs.ensureDir(tempExtractDir);
        
        execSync(`unzip -q "${vsixPath}" -d "${tempExtractDir}"`, { stdio: 'inherit' });
        
        // Read package.json to get extension info
        const packageJson = await fs.readJSON(path.join(tempExtractDir, 'extension', 'package.json'));
        const extensionId = `${packageJson.publisher}.${packageJson.name}-${packageJson.version}`;
        
        // Create extension directory
        const extensionInstallDir = path.join(extensionsDir, extensionId);
        await fs.ensureDir(extensionInstallDir);
        
        // Copy extension files
        await fs.copy(path.join(tempExtractDir, 'extension'), extensionInstallDir);
        
        console.log(`   Extension installed as: ${extensionId}`);
    }

    async createConfiguration() {
        console.log('⚙️  Creating Writers Room configuration...');
        
        const vscodeApp = path.join(this.buildDir, 'VSCode.app');
        const dataDir = path.join(vscodeApp, 'Contents', 'Resources', 'app', 'data');
        const userDir = path.join(dataDir, 'user-data', 'User');
        
        await fs.ensureDir(userDir);
        
        // Create optimized settings for writing
        const settings = {
            "workbench.startupEditor": "none",
            "workbench.colorTheme": "Default Dark+",
            "workbench.iconTheme": "vs-seti",
            "window.title": "The Writers Room - ${activeEditorShort}${separator}${rootName}",
            "editor.fontSize": 16,
            "editor.lineHeight": 1.6,
            "editor.fontFamily": "'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, monospace",
            "editor.wordWrap": "on",
            "editor.lineNumbers": "off",
            "editor.minimap.enabled": false,
            "workbench.activityBar.visible": true,
            "workbench.statusBar.visible": true,
            "files.autoSave": "afterDelay",
            "files.autoSaveDelay": 2000,
            "theWritersRoom.autoSave": true,
            "theWritersRoom.defaultAgent": "script-doctor",
            "theWritersRoom.theme": "dark",
            "explorer.confirmDelete": false,
            "git.enabled": false,
            "telemetry.telemetryLevel": "off",
            "update.mode": "none"
        };
        
        await fs.writeJSON(path.join(userDir, 'settings.json'), settings, { spaces: 2 });
        
        // Create default keybindings for Writers Room
        const keybindings = [
            {
                "key": "cmd+shift+a",
                "command": "theWritersRoom.openAIChat"
            },
            {
                "key": "cmd+shift+n",
                "command": "theWritersRoom.createProject"
            }
        ];
        
        await fs.writeJSON(path.join(userDir, 'keybindings.json'), keybindings, { spaces: 2 });
        
        console.log('✅ Configuration created');
    }

    async createSampleProject() {
        console.log('📝 Creating sample project...');
        
        const vscodeApp = path.join(this.buildDir, 'VSCode.app');
        const dataDir = path.join(vscodeApp, 'Contents', 'Resources', 'app', 'data');
        const sampleProjectDir = path.join(dataDir, 'sample-project');
        
        await fs.ensureDir(sampleProjectDir);
        
        // Create sample project structure
        const projectStructure = {
            'README.md': `# Welcome to The Writers Room

This is your sample writing project to get you started.

## Features Available:
- AI Writing Agents in the sidebar
- Project structure templates
- Collaborative writing tools
- Export capabilities

## Getting Started:
1. Open the AI agents panel (click the Writers Room icon in the activity bar)
2. Create a new project: Cmd+Shift+N
3. Start writing in any .md file
4. Use Cmd+Shift+A to open AI chat

Happy writing! 🎬✍️`,
            
            'scenes/act1.md': `# Act 1

## Opening Scene

Your story begins here...

*Remember: Every great story starts with a character who wants something and faces obstacles getting it.*`,
            
            'scenes/act2.md': `# Act 2

## Rising Action

The conflict develops and complications arise...

*Keep raising the stakes for your protagonist.*`,
            
            'scenes/act3.md': `# Act 3

## Climax and Resolution

Everything comes together in the final act...

*Deliver on the promises you made to your audience.*`,
            
            'characters/main.md': `# Main Characters

## Protagonist
- **Name:** 
- **Age:** 
- **Occupation:** 
- **Goal:** 
- **Obstacle:** 
- **Stakes:** 

## Antagonist
- **Name:** 
- **Motivation:** 
- **Connection to protagonist:** `,
            
            'characters/supporting.md': `# Supporting Characters

These characters help or hinder your protagonist's journey.

## Character Template
- **Name:** 
- **Role:** 
- **Relationship to protagonist:** 
- **Key trait:** `,
            
            'worldbuilding/settings.md': `# Settings and Locations

## Primary Location

**Where:** 
**When:** 
**Atmosphere:** 
**Significance to story:** 

## Secondary Locations

Add as needed for your story.`,
            
            'research/notes.md': `# Research Notes

Keep track of important research for authenticity.

## Sources
- [ ] Books
- [ ] Articles  
- [ ] Interviews
- [ ] Documentaries

## Key Facts
- 
- 
- `
        };
        
        for (const [filePath, content] of Object.entries(projectStructure)) {
            const fullPath = path.join(sampleProjectDir, filePath);
            await fs.ensureDir(path.dirname(fullPath));
            await fs.writeFile(fullPath, content);
        }
        
        // Create workspace file
        const workspace = {
            "folders": [
                {
                    "name": "Sample Writing Project",
                    "path": "./sample-project"
                }
            ],
            "settings": {
                "theWritersRoom.isActive": true
            }
        };
        
        await fs.writeJSON(path.join(dataDir, 'sample-project.code-workspace'), workspace, { spaces: 2 });
        
        console.log('✅ Sample project created');
    }

    async createLauncher() {
        console.log('🚀 Creating application launcher...');
        
        const writerRoomApp = path.join(this.distDir, 'The Writers Room.app');
        const contentsDir = path.join(writerRoomApp, 'Contents');
        const macosDir = path.join(contentsDir, 'MacOS');
        const resourcesDir = path.join(contentsDir, 'Resources');
        
        await fs.ensureDir(macosDir);
        await fs.ensureDir(resourcesDir);
        
        // Copy the entire VS Code app as our base
        const vscodeApp = path.join(this.buildDir, 'VSCode.app');
        await fs.copy(vscodeApp, writerRoomApp);
        
        // Create custom Info.plist that preserves executable info
        const infoPlist = `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Electron</string>
    <key>CFBundleIdentifier</key>
    <string>com.thewritersroom.app</string>
    <key>CFBundleName</key>
    <string>The Writers Room</string>
    <key>CFBundleDisplayName</key>
    <string>The Writers Room</string>
    <key>CFBundleVersion</key>
    <string>${this.version}</string>
    <key>CFBundleShortVersionString</key>
    <string>${this.version}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>WRTR</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSRequiresAquaSystemAppearance</key>
    <false/>
</dict>
</plist>`;
        
        await fs.writeFile(path.join(contentsDir, 'Info.plist'), infoPlist);
        
        // Create launch script that opens the sample project
        const launchScript = `#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
DATA_DIR="$APP_DIR/Contents/Resources/app/data"

# Launch VS Code with Writers Room configuration
exec "$APP_DIR/Contents/MacOS/Electron" \\
    --extensions-dir="$DATA_DIR/extensions" \\
    --user-data-dir="$DATA_DIR/user-data" \\
    "$DATA_DIR/sample-project.code-workspace"
`;
        
        const launchScriptPath = path.join(macosDir, 'launch-writers-room');
        await fs.writeFile(launchScriptPath, launchScript);
        await fs.chmod(launchScriptPath, '755');
        
        console.log('✅ Launcher created');
    }

    async packageDistribution() {
        console.log('📦 Finalizing distribution package...');
        
        // The app is already in dist-clean directory
        // Remove VS Code's signature to avoid conflicts
        const appPath = path.join(this.distDir, 'The Writers Room.app');
        
        try {
            execSync(`codesign --remove-signature "${appPath}"`, { stdio: 'pipe' });
            execSync(`codesign --remove-signature "${appPath}"/Contents/Frameworks/*/`, { stdio: 'pipe' });
        } catch (error) {
            console.log('Note: Could not remove code signatures (may not be needed)');
        }
        
        console.log('✅ Distribution package ready');
    }

    async createInstaller() {
        console.log('💿 Creating DMG installer...');
        
        const dmgPath = path.join(this.projectRoot, `TheWritersRoom-${this.version}.dmg`);
        const tempDmgDir = path.join(this.tempDir, 'dmg-contents');
        
        await fs.ensureDir(tempDmgDir);
        
        // Copy app to DMG staging area
        await fs.copy(
            path.join(this.distDir, 'The Writers Room.app'),
            path.join(tempDmgDir, 'The Writers Room.app')
        );
        
        // Create Applications alias for easy installation
        try {
            execSync(`ln -s /Applications "${tempDmgDir}/Applications"`, { stdio: 'pipe' });
        } catch (error) {
            console.log('Note: Could not create Applications alias');
        }
        
        // Create DMG
        const dmgCommand = `hdiutil create -volname "The Writers Room" -srcfolder "${tempDmgDir}" -ov -format UDZO "${dmgPath}"`;
        execSync(dmgCommand, { stdio: 'inherit' });
        
        console.log(`✅ DMG installer created: ${dmgPath}`);
    }
}

// Run if called directly
if (require.main === module) {
    const builder = new CleanDistributionBuilder();
    builder.build();
}

module.exports = CleanDistributionBuilder; 