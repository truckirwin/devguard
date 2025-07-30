const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

async function testExtension() {
    console.log('🚀 Testing The Writers Room Extension...');
    
    // Check if compiled extension exists
    const extensionPath = path.join(__dirname, 'out', 'src', 'extension.js');
    if (!fs.existsSync(extensionPath)) {
        console.error('❌ Extension not compiled! Run: npm run compile');
        process.exit(1);
    }
    
    console.log('✅ Extension compiled successfully');
    
    // Launch VS Code with extension development
    console.log('📂 Starting VS Code Extension Development Host...');
    
    const vscode = spawn('code', [
        '--extensionDevelopmentPath=' + __dirname,
        '--new-window',
        './test-workspace'
    ], {
        stdio: 'inherit',
        detached: true
    });
    
    vscode.on('error', (error) => {
        console.error('❌ Failed to start VS Code:', error.message);
        process.exit(1);
    });
    
    console.log('✅ VS Code Extension Development Host started');
    console.log('📝 To test the extension:');
    console.log('   1. Open Command Palette (Cmd+Shift+P)');
    console.log('   2. Type "Writers Room: Test Extension"');
    console.log('   3. You should see "The Writers Room is working!" message');
    console.log('');
    console.log('🔧 Available commands:');
    console.log('   - Writers Room: Test Extension');
    console.log('   - Writers Room: Create New Writing Project');
    console.log('   - Writers Room: Open AI Chat');
    console.log('   - Writers Room: Settings');
    
    // Don't wait for VS Code to exit
    vscode.unref();
}

testExtension().catch(console.error); 