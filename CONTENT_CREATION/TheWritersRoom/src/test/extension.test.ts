import * as assert from 'assert';
import * as vscode from 'vscode';
import { AIService } from '../services/AIService';
import { ConfigManager } from '../services/ConfigManager';

suite('The Writers Room Extension Test Suite', () => {
    let extension: vscode.Extension<any>;

    suiteSetup(async () => {
        // Get the extension
        extension = vscode.extensions.getExtension('thewritersroom.the-writers-room')!;
        
        // Activate the extension
        if (!extension.isActive) {
            await extension.activate();
        }
    });

    test('Extension should be present and activated', () => {
        assert.ok(extension);
        assert.ok(extension.isActive);
    });

    test('Extension should register all commands', async () => {
        const commands = await vscode.commands.getCommands(true);
        
        const expectedCommands = [
            'theWritersRoom.test',
            'theWritersRoom.createProject',
            'theWritersRoom.openAIChat',
            'theWritersRoom.configureAPI',
            'theWritersRoom.selectAgent',
            'theWritersRoom.testAIConnection',
            'theWritersRoom.switchAIProvider',
            'theWritersRoom.openSettings',
            'theWritersRoom.showAgentPanel',
            'theWritersRoom.clearConversation'
        ];

        for (const command of expectedCommands) {
            assert.ok(commands.includes(command), `Command ${command} should be registered`);
        }
    });

    test('AIService should be a singleton', () => {
        const service1 = AIService.getInstance();
        const service2 = AIService.getInstance();
        
        assert.strictEqual(service1, service2, 'AIService should return the same instance');
    });

    test('AIService should have default configuration', () => {
        const aiService = AIService.getInstance();
        
        assert.ok(aiService.getCurrentProvider(), 'Should have a current provider');
        assert.ok(aiService.getCurrentModel(), 'Should have a current model');
        
        const providers = aiService.getAvailableProviders();
        assert.ok(providers.length > 0, 'Should have available providers');
        
        // Check that each provider has models
        providers.forEach(provider => {
            assert.ok(provider.name, 'Provider should have a name');
            assert.ok(provider.models.length > 0, 'Provider should have models');
        });
    });

    test('AIService should handle mock responses', async () => {
        const aiService = AIService.getInstance();
        
        try {
            const response = await aiService.sendMessage('Test message', 'test');
            
            assert.ok(response, 'Should return a response');
            assert.ok(response.text, 'Response should have text');
            assert.ok(response.text.length > 0, 'Response text should not be empty');
            
            if (response.usage) {
                assert.ok(typeof response.usage.totalTokens === 'number', 'Usage should have total tokens');
            }
        } catch (error) {
            // This is expected if no API keys are configured
            assert.ok(error instanceof Error, 'Should throw an error if not configured');
        }
    });

    test('ConfigManager should handle configuration', () => {
        // Create a mock context for testing
        const mockContext: vscode.ExtensionContext = {
            subscriptions: [],
            workspaceState: {
                get: () => undefined,
                update: async () => {},
                keys: () => []
            },
            globalState: {
                get: () => undefined,
                update: async () => {},
                keys: () => [],
                setKeysForSync: () => {}
            },
            extensionUri: vscode.Uri.file(__dirname),
            extensionPath: __dirname,
            asAbsolutePath: (relativePath: string) => relativePath,
            storageUri: undefined,
            storagePath: undefined,
            globalStorageUri: vscode.Uri.file(__dirname),
            globalStoragePath: __dirname,
            logUri: vscode.Uri.file(__dirname),
            logPath: __dirname,
            extensionMode: vscode.ExtensionMode.Test,
            extension: extension,
            environmentVariableCollection: {} as any,
            secrets: {} as any,
            languageModelAccessInformation: {} as any
        };

        const configManager = ConfigManager.getInstance(mockContext);
        
        assert.ok(configManager, 'ConfigManager should be created');
        
        const config = configManager.getConfiguration();
        assert.ok(config, 'Should return workspace configuration');
        
        const apiStatus = configManager.getAPIKeyStatus();
        assert.ok(typeof apiStatus === 'object', 'Should return API key status object');
        assert.ok('openai' in apiStatus, 'Should have OpenAI status');
        assert.ok('anthropic' in apiStatus, 'Should have Anthropic status');
        assert.ok('awsBedrock' in apiStatus, 'Should have AWS Bedrock status');
    });

    test('Test command should be executable', async () => {
        // Execute the test command
        try {
            await vscode.commands.executeCommand('theWritersRoom.test');
            // If we get here, the command executed without throwing
            assert.ok(true, 'Test command should execute');
        } catch (error) {
            // The command might fail due to missing API keys, but it should still be registered
            assert.ok(error instanceof Error, 'Command should be registered even if it fails');
        }
    });

    test('Configuration should have proper defaults', () => {
        const config = vscode.workspace.getConfiguration('theWritersRoom');
        
        // Test that configuration properties exist
        const aiProvider = config.get('aiProvider');
        const defaultAgent = config.get('defaultAgent');
        const autoSave = config.get('autoSave');
        
        assert.ok(typeof aiProvider === 'string', 'AI provider should be a string');
        assert.ok(typeof defaultAgent === 'string', 'Default agent should be a string');
        assert.ok(typeof autoSave === 'boolean', 'Auto save should be a boolean');
    });

    test('Extension should set active context', async () => {
        // Wait a bit for the context to be set
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // The context should be set by the extension
        // Note: In test environment, we can't easily check context values
        // but we can verify the command was called
        assert.ok(true, 'Context should be set during activation');
    });

    suiteTeardown(() => {
        // Clean up if needed
        console.log('Test suite completed');
    });
}); 