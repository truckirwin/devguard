#!/usr/bin/env node

/**
 * Development Setup Script for The Writers Room
 * This script helps set up the development environment
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🎬 Setting up The Writers Room development environment...\n');

// Check Node.js version
function checkNodeVersion() {
    const version = process.version;
    const major = parseInt(version.slice(1).split('.')[0]);
    
    if (major < 18) {
        console.error('❌ Node.js 18+ is required. Current version:', version);
        process.exit(1);
    }
    
    console.log('✅ Node.js version:', version);
}

// Check if npm is available
function checkNpm() {
    try {
        const npmVersion = execSync('npm --version', { encoding: 'utf8' }).trim();
        console.log('✅ npm version:', npmVersion);
    } catch (error) {
        console.error('❌ npm is not available');
        process.exit(1);
    }
}

// Install dependencies
function installDependencies() {
    console.log('\n📦 Installing dependencies...');
    
    try {
        execSync('npm install', { stdio: 'inherit' });
        console.log('✅ Dependencies installed successfully');
    } catch (error) {
        console.error('❌ Failed to install dependencies');
        process.exit(1);
    }
}

// Create sample project for testing
function createSampleProject() {
    console.log('\n📝 Creating sample project for testing...');
    
    const sampleProjectPath = path.join(process.cwd(), 'sample-project');
    
    if (!fs.existsSync(sampleProjectPath)) {
        try {
            // Use the existing create_new_project.js script
            const { createProject } = require('../scripts/create_new_project.js');
            
            // Create a sample screenplay project
            createProject(
                'Sample Screenplay',
                'screenplay',
                'Feature Film',
                'Drama',
                sampleProjectPath
            );
            
            console.log('✅ Sample project created at:', sampleProjectPath);
        } catch (error) {
            console.log('⚠️  Could not create sample project:', error.message);
        }
    } else {
        console.log('✅ Sample project already exists');
    }
}

// Create development configuration
function createDevConfig() {
    console.log('\n⚙️  Creating development configuration...');
    
    const configDir = path.join(process.cwd(), 'config');
    const devConfigPath = path.join(configDir, 'dev.json');
    
    if (!fs.existsSync(configDir)) {
        fs.mkdirSync(configDir, { recursive: true });
    }
    
    if (!fs.existsSync(devConfigPath)) {
        const devConfig = {
            development: true,
            debug: true,
            logLevel: 'debug',
            features: {
                aiAgents: true,
                fileExplorer: true,
                projectCreation: true
            }
        };
        
        fs.writeFileSync(devConfigPath, JSON.stringify(devConfig, null, 2));
        console.log('✅ Development config created');
    } else {
        console.log('✅ Development config already exists');
    }
}

// Display next steps
function displayNextSteps() {
    console.log('\n🎉 Setup complete! Here are your next steps:\n');
    
    console.log('1. Start the development server:');
    console.log('   npm run dev\n');
    
    console.log('2. Create a new project:');
    console.log('   - Click "Create New Project" in the app');
    console.log('   - Or use the command line: npm run new-project\n');
    
    console.log('3. Explore the codebase:');
    console.log('   - src/main.js - Main Electron process');
    console.log('   - src/renderer/ - Frontend code');
    console.log('   - scripts/ - Utility scripts');
    console.log('   - agents/ - AI agent configurations\n');
    
    console.log('4. Build for production:');
    console.log('   npm run build\n');
    
    console.log('📚 For more information, see the README.md file');
    console.log('🐛 Report issues on GitHub: https://github.com/thewritersroom/desktop-app/issues\n');
}

// Main setup function
function main() {
    try {
        checkNodeVersion();
        checkNpm();
        installDependencies();
        createSampleProject();
        createDevConfig();
        displayNextSteps();
    } catch (error) {
        console.error('❌ Setup failed:', error.message);
        process.exit(1);
    }
}

// Run setup if this script is executed directly
if (require.main === module) {
    main();
}

module.exports = {
    checkNodeVersion,
    checkNpm,
    installDependencies,
    createSampleProject,
    createDevConfig,
    displayNextSteps
}; 