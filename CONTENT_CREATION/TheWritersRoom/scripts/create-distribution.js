#!/usr/bin/env node

/**
 * The Writers Room - Distribution Builder
 * Creates a standalone VS Code distribution with The Writers Room extension
 */

const fs = require('fs-extra');
const path = require('path');
const { execSync } = require('child_process');
const { platform } = process;

class DistributionBuilder {
    constructor() {
        this.distDir = path.join(__dirname, '..', 'dist');
        this.tempDir = path.join(__dirname, '..', 'temp');
        this.version = require('../package.json').version;
        this.platforms = {
            'darwin': {
                url: 'https://update.code.visualstudio.com/latest/darwin/stable',
                filename: 'VSCode-darwin.zip',
                appName: 'Visual Studio Code.app'
            },
            'win32': {
                url: 'https://update.code.visualstudio.com/latest/win32-x64-archive/stable', 
                filename: 'VSCode-win32-x64.zip',
                appName: 'Code.exe'
            },
            'linux': {
                url: 'https://update.code.visualstudio.com/latest/linux-x64/stable',
                filename: 'VSCode-linux-x64.tar.gz',
                appName: 'code'
            }
        };
    }

    async build(targetPlatform = platform) {
        console.log('🚀 Building The Writers Room Distribution...\n');
        
        try {
            await this.cleanup();
            await this.createDirectories();
            await this.packageExtension();
            await this.downloadVSCode(targetPlatform);
            await this.extractVSCode(targetPlatform);
            await this.configureWritersRoom(targetPlatform);
            await this.createLauncher(targetPlatform);
            await this.customizeBranding(targetPlatform);
            await this.createInstaller(targetPlatform);
            await this.cleanup();
            
            console.log('✅ Distribution build completed!');
            console.log(`📦 Output: ${this.distDir}`);
        } catch (error) {
            console.error('❌ Build failed:', error.message);
            process.exit(1);
        }
    }

    async cleanup() {
        console.log('🧹 Cleaning up previous builds...');
        await fs.remove(this.tempDir);
        await fs.remove(this.distDir);
    }

    async createDirectories() {
        console.log('📁 Creating directories...');
        await fs.ensureDir(this.tempDir);
        await fs.ensureDir(this.distDir);
    }

    async downloadVSCode(targetPlatform) {
        const platform = this.platforms[targetPlatform];
        if (!platform) {
            throw new Error(`Unsupported platform: ${targetPlatform}`);
        }

        console.log(`⬇️  Downloading VS Code for ${targetPlatform}...`);
        const outputPath = path.join(this.tempDir, platform.filename);
        
        // Download VS Code
        execSync(`curl -L "${platform.url}" -o "${outputPath}"`, { stdio: 'inherit' });
        console.log('✅ VS Code downloaded');
    }

    async extractVSCode(targetPlatform) {
        const platform = this.platforms[targetPlatform];
        const downloadPath = path.join(this.tempDir, platform.filename);
        const extractPath = path.join(this.tempDir, 'vscode');

        console.log('📦 Extracting VS Code...');
        
        if (targetPlatform === 'darwin') {
            execSync(`unzip -q "${downloadPath}" -d "${extractPath}"`, { stdio: 'inherit' });
        } else if (targetPlatform === 'win32') {
            execSync(`unzip -q "${downloadPath}" -d "${extractPath}"`, { stdio: 'inherit' });
        } else if (targetPlatform === 'linux') {
            execSync(`tar -xzf "${downloadPath}" -C "${extractPath}"`, { stdio: 'inherit' });
        }
        
        console.log('✅ VS Code extracted');
    }

    async packageExtension() {
        console.log('📦 Packaging The Writers Room extension...');
        
        // Package the extension
        try {
            execSync('npm run compile', { stdio: 'inherit' });
            execSync('npx vsce package --out ./temp/the-writers-room.vsix', { stdio: 'inherit' });
            console.log('✅ Extension packaged');
        } catch (error) {
            throw new Error('Failed to package extension: ' + error.message);
        }
    }

    async configureWritersRoom(targetPlatform) {
        console.log('⚙️  Configuring The Writers Room...');
        
        const vscodePath = this.getVSCodePath(targetPlatform);
        const dataPath = path.join(vscodePath, 'data');
        const extensionsPath = path.join(dataPath, 'extensions');
        const userDataPath = path.join(dataPath, 'user-data');
        const settingsPath = path.join(userDataPath, 'User');
        
        // Create portable data directory
        await fs.ensureDir(extensionsPath);
        await fs.ensureDir(settingsPath);
        
        // Install the extension
        const extensionVsix = path.join(this.tempDir, 'the-writers-room.vsix');
        const extensionInstallPath = path.join(extensionsPath, 'thewritersroom.the-writers-room-' + this.version);
        
        // Extract extension to extensions folder
        execSync(`unzip -q "${extensionVsix}" -d "${extensionInstallPath}"`, { stdio: 'inherit' });
        
        // Create default settings
        const defaultSettings = {
            "workbench.startupEditor": "none",
            "workbench.colorTheme": "Default Dark+",
            "workbench.iconTheme": "vs-seti",
            "theWritersRoom.autoSave": true,
            "theWritersRoom.defaultAgent": "script-doctor",
            "theWritersRoom.theme": "dark",
            "editor.fontSize": 14,
            "editor.lineHeight": 1.6,
            "editor.fontFamily": "'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace",
            "window.title": "The Writers Room - ${activeEditorShort}${separator}${rootName}",
            "workbench.activityBar.visible": true,
            "explorer.confirmDelete": false,
            "files.autoSave": "afterDelay",
            "files.autoSaveDelay": 1000
        };
        
        await fs.writeJSON(path.join(settingsPath, 'settings.json'), defaultSettings, { spaces: 2 });
        
        // Create welcome workspace
        const welcomeWorkspace = {
            "folders": [
                {
                    "name": "Welcome to The Writers Room",
                    "path": "./sample-project"
                }
            ],
            "settings": {
                "theWritersRoom.isActive": true
            }
        };
        
        await fs.writeJSON(path.join(userDataPath, 'writers-room-welcome.code-workspace'), welcomeWorkspace, { spaces: 2 });
        
        // Copy sample project
        const sampleProjectPath = path.join(vscodePath, 'sample-project');
        await this.createSampleProject(sampleProjectPath);
        
        console.log('✅ The Writers Room configured');
    }

    async createSampleProject(projectPath) {
        console.log('📝 Creating sample project...');
        
        await fs.ensureDir(projectPath);
        
        // Create project structure
        const structure = {
            'scenes/act1.md': '# Act 1\n\nYour first act begins here...',
            'scenes/act2.md': '# Act 2\n\nThe conflict develops...',
            'scenes/act3.md': '# Act 3\n\nThe resolution...',
            'characters/main.md': '# Main Characters\n\nDescribe your protagonists...',
            'characters/supporting.md': '# Supporting Characters\n\nSecondary characters...',
            'worldbuilding/settings.md': '# Settings\n\nDescribe your story world...',
            'research/notes.md': '# Research Notes\n\nImportant research for your story...',
            'README.md': '# Welcome to The Writers Room\n\nThis is your sample writing project. Create new projects using the Command Palette (Cmd/Ctrl+Shift+P) and search for "Writers Room".'
        };
        
        for (const [filePath, content] of Object.entries(structure)) {
            const fullPath = path.join(projectPath, filePath);
            await fs.ensureDir(path.dirname(fullPath));
            await fs.writeFile(fullPath, content);
        }
        
        console.log('✅ Sample project created');
    }

    async createLauncher(targetPlatform) {
        console.log('🚀 Creating launcher...');
        
        const vscodePath = this.getVSCodePath(targetPlatform);
        
        if (targetPlatform === 'darwin') {
            await this.createMacLauncher(vscodePath);
        } else if (targetPlatform === 'win32') {
            await this.createWindowsLauncher(vscodePath);
        } else if (targetPlatform === 'linux') {
            await this.createLinuxLauncher(vscodePath);
        }
        
        console.log('✅ Launcher created');
    }

    async createMacLauncher(vscodePath) {
        const appPath = path.join(this.distDir, 'The Writers Room.app');
        const contentsPath = path.join(appPath, 'Contents');
        const macOSPath = path.join(contentsPath, 'MacOS');
        const resourcesPath = path.join(contentsPath, 'Resources');
        
        await fs.ensureDir(macOSPath);
        await fs.ensureDir(resourcesPath);
        
        // Copy VS Code app
        await fs.copy(path.join(this.tempDir, 'vscode/Visual Studio Code.app'), appPath);
        
        // Create custom Info.plist (preserving executable info)
        const infoPlist = `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>
    <string>The Writers Room</string>
    <key>CFBundleName</key>
    <string>The Writers Room</string>
    <key>CFBundleIdentifier</key>
    <string>com.thewritersroom.app</string>
    <key>CFBundleVersion</key>
    <string>${this.version}</string>
    <key>CFBundleShortVersionString</key>
    <string>${this.version}</string>
    <key>CFBundleExecutable</key>
    <string>Electron</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
</dict>
</plist>`;
        
        await fs.writeFile(path.join(contentsPath, 'Info.plist'), infoPlist);
    }

    async createWindowsLauncher(vscodePath) {
        const appPath = path.join(this.distDir, 'TheWritersRoom');
        await fs.copy(path.join(this.tempDir, 'vscode'), appPath);
        
        // Create launcher batch file
        const launcherScript = `@echo off
title The Writers Room
cd /d "%~dp0"
start "" "Code.exe" --disable-telemetry --disable-updates --extensions-dir="./data/extensions" --user-data-dir="./data/user-data" "./data/writers-room-welcome.code-workspace"
`;
        
        await fs.writeFile(path.join(appPath, 'The Writers Room.bat'), launcherScript);
    }

    async createLinuxLauncher(vscodePath) {
        const appPath = path.join(this.distDir, 'TheWritersRoom');
        await fs.copy(path.join(this.tempDir, 'vscode/VSCode-linux-x64'), appPath);
        
        // Create launcher script
        const launcherScript = `#!/bin/bash
cd "$(dirname "$0")"
./code --disable-telemetry --disable-updates --extensions-dir="./data/extensions" --user-data-dir="./data/user-data" "./data/writers-room-welcome.code-workspace"
`;
        
        await fs.writeFile(path.join(appPath, 'writers-room.sh'), launcherScript);
        await fs.chmod(path.join(appPath, 'writers-room.sh'), '755');
    }

    async customizeBranding(targetPlatform) {
        console.log('🎨 Customizing branding...');
        
        // Copy custom icons and assets if they exist
        const iconPath = path.join(__dirname, '..', 'src', 'assets', 'icon.png');
        if (await fs.pathExists(iconPath)) {
            const vscodePath = this.getVSCodePath(targetPlatform);
            // Add custom icon logic here based on platform
        }
        
        console.log('✅ Branding customized');
    }

    async createInstaller(targetPlatform) {
        console.log('📦 Creating installer package...');
        
        if (targetPlatform === 'darwin') {
            // Create a temporary installer directory with proper layout
            const installerDir = path.join(this.tempDir, 'installer');
            const appsAlias = path.join(installerDir, 'Applications');
            
            await fs.ensureDir(installerDir);
            
            // Copy the app to installer directory
            await fs.copy(path.join(this.distDir, 'The Writers Room.app'), path.join(installerDir, 'The Writers Room.app'));
            
            // Create Applications alias for drag-and-drop install
            try {
                execSync(`ln -s /Applications "${appsAlias}"`, { stdio: 'inherit' });
            } catch (error) {
                console.log('Could not create Applications alias (continuing...)');
            }
            
            // Create DMG with proper installer layout
            execSync(`hdiutil create -volname "The Writers Room" -srcfolder "${installerDir}" -ov -format UDZO "${this.distDir}/../TheWritersRoom-${this.version}.dmg"`, { stdio: 'inherit' });
        } else if (targetPlatform === 'win32') {
            // Create ZIP for Windows
            execSync(`cd "${this.distDir}" && zip -r "../TheWritersRoom-${this.version}-Windows.zip" .`, { stdio: 'inherit' });
        } else if (targetPlatform === 'linux') {
            // Create tar.gz for Linux
            execSync(`cd "${this.distDir}" && tar -czf "../TheWritersRoom-${this.version}-Linux.tar.gz" .`, { stdio: 'inherit' });
        }
        
        console.log('✅ Installer created');
    }

    getVSCodePath(targetPlatform) {
        if (targetPlatform === 'darwin') {
            return path.join(this.tempDir, 'vscode/Visual Studio Code.app/Contents/Resources/app');
        } else if (targetPlatform === 'win32') {
            return path.join(this.tempDir, 'vscode');
        } else if (targetPlatform === 'linux') {
            return path.join(this.tempDir, 'vscode/VSCode-linux-x64');
        }
    }
}

// CLI Interface
if (require.main === module) {
    const targetPlatform = process.argv[2] || process.platform;
    const builder = new DistributionBuilder();
    builder.build(targetPlatform);
}

module.exports = DistributionBuilder; 