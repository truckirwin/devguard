import * as path from 'path';
import { runTests } from '@vscode/test-electron';

async function main() {
    try {
        // The folder containing the Extension Manifest package.json
        // Passed to `--extensionDevelopmentPath`
        const extensionDevelopmentPath = path.resolve(__dirname, '../../');

        // The path to test runner
        // Passed to --extensionTestsPath
        const extensionTestsPath = path.resolve(__dirname, './suite/index');

        console.log('🧪 Starting VS Code Extension Tests...');
        console.log(`Extension Development Path: ${extensionDevelopmentPath}`);
        console.log(`Extension Tests Path: ${extensionTestsPath}`);

        // Download VS Code, unzip it and run the integration test
        await runTests({ 
            extensionDevelopmentPath, 
            extensionTestsPath,
            launchArgs: [
                '--disable-extensions',
                '--disable-workspace-trust'
            ]
        });

        console.log('✅ All tests completed successfully!');
    } catch (err) {
        console.error('❌ Failed to run tests:', err);
        process.exit(1);
    }
}

main(); 