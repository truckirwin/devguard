import * as assert from 'assert';
import * as vscode from 'vscode';
import { AIService, TaskRequest, TaskType, TaskComplexity } from '../services/AIService';
import { ConfigManager } from '../services/ConfigManager';
import { TestUtils } from './suite/index';

// Mock VS Code API
const mockVSCode = TestUtils.createMockVSCode();
Object.assign(vscode, mockVSCode);

suite('The Writers Room - Core Tests', () => {
    
    suite('AIService Tests', () => {
        let aiService: AIService;
        
        setup(() => {
            aiService = AIService.getInstance();
        });
        
        test('Should initialize with correct default values', () => {
            assert.strictEqual(aiService.getCurrentProvider(), 'aws-bedrock');
            assert.strictEqual(aiService.getCurrentModel(), 'anthropic.claude-4-sonnet-20241022-v1:0');
        });
        
        test('Should return available providers', () => {
            const providers = aiService.getAvailableProviders();
            assert.strictEqual(providers.length, 3);
            assert.strictEqual(providers[0].name, 'AWS Bedrock (Recommended)');
            assert.ok(providers[0].models.includes('anthropic.claude-4-sonnet-20241022-v1:0'));
        });
        
        test('Should create session successfully', async () => {
            const session = await aiService.createSession('test-user');
            assert.ok(session.sessionId);
            assert.strictEqual(session.userId, 'test-user');
            assert.strictEqual(session.promptCount, 0);
            assert.strictEqual(session.maxPrompts, 100);
            assert.strictEqual(session.active, true);
        });
        
        test('Should analyze task correctly for dialogue writing', async () => {
            const mockService = aiService as any;
            const task: TaskRequest = {
                message: 'Help me write dialogue between two characters',
                agentType: 'aaron-sorkin',
                userId: 'test-user',
                sessionId: 'test-session'
            };
            
            const analysis = await mockService.analyzeTask(task);
            assert.strictEqual(analysis.type, TaskType.DIALOGUE_WRITING);
            assert.ok(analysis.estimatedTokens > 0);
        });
        
        test('Should analyze task correctly for character development', async () => {
            const mockService = aiService as any;
            const task: TaskRequest = {
                message: 'Help me develop a character with complex motivations',
                agentType: 'character-specialist',
                userId: 'test-user',
                sessionId: 'test-session'
            };
            
            const analysis = await mockService.analyzeTask(task);
            assert.strictEqual(analysis.type, TaskType.CHARACTER_DEVELOPMENT);
            assert.strictEqual(analysis.complexity, TaskComplexity.ADVANCED);
        });
        
        test('Should select Claude 4.0 Sonnet for dialogue tasks', async () => {
            const mockService = aiService as any;
            const analysis = {
                complexity: TaskComplexity.MODERATE,
                type: TaskType.DIALOGUE_WRITING,
                urgency: 'normal',
                estimatedTokens: 1000
            };
            
            const selection = await mockService.hybridSelectModel(analysis);
            assert.strictEqual(selection.primaryModel, 'anthropic.claude-4-sonnet-20241022-v1:0');
            assert.strictEqual(selection.reasoning, 'Claude 4.0 Sonnet for advanced dialogue and character development');
        });
        
        test('Should select Haiku for simple urgent tasks', async () => {
            const mockService = aiService as any;
            const analysis = {
                complexity: TaskComplexity.SIMPLE,
                type: TaskType.GENERAL_WRITING,
                urgency: 'high',
                estimatedTokens: 200
            };
            
            const selection = await mockService.hybridSelectModel(analysis);
            assert.strictEqual(selection.primaryModel, 'anthropic.claude-3-haiku-20240307-v1:0');
            assert.strictEqual(selection.reasoning, 'Speed-optimized for simple/urgent tasks');
        });
        
        test('Should build dialogue prompt correctly', () => {
            const mockService = aiService as any;
            const task: TaskRequest = {
                message: 'Write a dramatic confrontation scene',
                agentType: 'aaron-sorkin',
                userId: 'test-user',
                sessionId: 'test-session'
            };
            
            const prompt = mockService.buildDialoguePrompt(task);
            assert.ok(prompt.includes('expert dialogue writer'));
            assert.ok(prompt.includes('Write a dramatic confrontation scene'));
            assert.ok(prompt.includes('Enhanced dialogue'));
        });
        
        test('Should get correct agent context', () => {
            const mockService = aiService as any;
            
            const sorkinContext = mockService.getAgentContext('aaron-sorkin');
            assert.ok(sorkinContext.includes('Aaron Sorkin'));
            assert.ok(sorkinContext.includes('rapid-fire'));
            
            const characterContext = mockService.getAgentContext('character-specialist');
            assert.ok(characterContext.includes('character development'));
            assert.ok(characterContext.includes('three-dimensional'));
        });
        
        test('Should calculate cost correctly', () => {
            const mockService = aiService as any;
            const analysis = {
                complexity: TaskComplexity.MODERATE,
                type: TaskType.DIALOGUE_WRITING,
                urgency: 'normal',
                estimatedTokens: 1000
            };
            
            const cost = mockService.calculateCost('anthropic.claude-4-sonnet-20241022-v1:0', analysis);
            assert.strictEqual(cost, 0.003); // 0.003 * (1000/1000)
        });
        
        test('Should handle session limit correctly', async () => {
            const session = await aiService.createSession('test-user');
            const mockService = aiService as any;
            
            // Simulate reaching limit
            session.promptCount = 99;
            const updatedSession = await mockService.incrementPromptCount(
                session.sessionId, 
                'test-model', 
                0.001
            );
            
            assert.strictEqual(updatedSession.promptCount, 100);
            assert.strictEqual(updatedSession.active, false);
        });
    });
    
    suite('ConfigManager Tests', () => {
        let configManager: ConfigManager;
        
        setup(() => {
            // Create a mock context for ConfigManager
            const mockContext = {
                subscriptions: [],
                workspaceState: {
                    get: () => undefined,
                    update: () => Promise.resolve()
                },
                globalState: {
                    get: () => undefined,
                    update: () => Promise.resolve()
                }
            } as any;
            
            configManager = ConfigManager.getInstance(mockContext);
        });
        
        test('Should get configuration', () => {
            const config = configManager.getConfiguration();
            assert.ok(config);
            assert.ok(typeof config.get === 'function');
        });
        
        test('Should check API key status', () => {
            const status = configManager.getAPIKeyStatus();
            assert.ok(typeof status === 'object');
            assert.ok('openai' in status);
            assert.ok('anthropic' in status);
            assert.ok('awsBedrock' in status);
        });
    });
    
    suite('Test Utilities Tests', () => {
        test('Should create mock VS Code API', () => {
            const mock = TestUtils.createMockVSCode();
            assert.ok(mock.workspace);
            assert.ok(mock.window);
            assert.ok(mock.commands);
            assert.ok(typeof mock.workspace.getConfiguration === 'function');
        });
        
        test('Should create mock AWS services', () => {
            const mock = TestUtils.createMockAWS();
            assert.ok(mock.bedrock);
            assert.ok(mock.dynamodb);
            assert.ok(mock.s3);
        });
        
        test('Should create test project', async () => {
            const projectPath = await TestUtils.createTestProject('test-screenplay');
            assert.ok(projectPath);
            assert.ok(projectPath.includes('test-screenplay'));
            
            // Cleanup
            await TestUtils.cleanupTestProject(projectPath);
        });
        
        test('Should create mock agent', () => {
            const agent = TestUtils.createMockAgent('test-agent');
            assert.strictEqual(agent.id, 'test-agent');
            assert.strictEqual(agent.name, 'Test test-agent');
            assert.strictEqual(agent.specialty, 'testing');
            assert.strictEqual(agent.available, true);
        });
        
        test('Should generate test data', () => {
            const dialogueData = TestUtils.generateTestData('dialogue') as any;
            assert.ok(dialogueData.characters);
            assert.ok(dialogueData.lines);
            assert.strictEqual(dialogueData.characters.length, 2);
            
            const characterData = TestUtils.generateTestData('character') as any;
            assert.ok(characterData.name);
            assert.ok(characterData.personality);
            assert.ok(Array.isArray(characterData.personality));
            
            const sceneData = TestUtils.generateTestData('scene') as any;
            assert.ok(sceneData.location);
            assert.ok(sceneData.description);
            
            const plotData = TestUtils.generateTestData('plot') as any;
            assert.ok(plotData.title);
            assert.ok(plotData.genre);
            assert.ok(plotData.acts);
        });
        
        test('Should provide delay utility', async () => {
            const start = Date.now();
            await TestUtils.delay(100);
            const end = Date.now();
            assert.ok(end - start >= 100);
        });
    });
    
    suite('Agent Context Tests', () => {
        let aiService: AIService;
        
        setup(() => {
            aiService = AIService.getInstance();
        });
        
        test('Should provide Aaron Sorkin context', () => {
            const mockService = aiService as any;
            const context = mockService.getAgentContext('aaron-sorkin');
            
            assert.ok(context.includes('Aaron Sorkin'));
            assert.ok(context.includes('rapid-fire'));
            assert.ok(context.includes('character-driven'));
        });
        
        test('Should provide Coen Brothers context', () => {
            const mockService = aiService as any;
            const context = mockService.getAgentContext('coen-brothers');
            
            assert.ok(context.includes('Coen Brothers'));
            assert.ok(context.includes('quirky'));
            assert.ok(context.includes('darkly comic'));
        });
        
        test('Should provide Character Specialist context', () => {
            const mockService = aiService as any;
            const context = mockService.getAgentContext('character-specialist');
            
            assert.ok(context.includes('character development'));
            assert.ok(context.includes('three-dimensional'));
            assert.ok(context.includes('distinct voices'));
        });
        
        test('Should provide default context for unknown agent', () => {
            const mockService = aiService as any;
            const context = mockService.getAgentContext('unknown-agent');
            
            assert.ok(context.includes('script doctor'));
            assert.ok(context.includes('story consultant'));
        });
    });
    
    suite('Session Management Tests', () => {
        let aiService: AIService;
        
        setup(() => {
            aiService = AIService.getInstance();
        });
        
        test('Should create unique session IDs', async () => {
            const session1 = await aiService.createSession('user1');
            const session2 = await aiService.createSession('user2');
            
            assert.notStrictEqual(session1.sessionId, session2.sessionId);
        });
        
        test('Should track model usage in session', async () => {
            const session = await aiService.createSession('test-user');
            const mockService = aiService as any;
            
            await mockService.incrementPromptCount(session.sessionId, 'model1', 0.001);
            await mockService.incrementPromptCount(session.sessionId, 'model1', 0.001);
            await mockService.incrementPromptCount(session.sessionId, 'model2', 0.002);
            
            const updatedSession = mockService.sessions.get(session.sessionId);
            assert.strictEqual(updatedSession.modelUsage.get('model1'), 2);
            assert.strictEqual(updatedSession.modelUsage.get('model2'), 1);
            assert.strictEqual(updatedSession.costAccumulated, 0.004);
        });
        
        test('Should generate valid session ID format', () => {
            const mockService = aiService as any;
            const sessionId = mockService.generateSessionId();
            
            assert.ok(sessionId.startsWith('session_'));
            assert.ok(sessionId.length > 20);
        });
    });
    
    suite('Error Handling Tests', () => {
        let aiService: AIService;
        
        setup(() => {
            aiService = AIService.getInstance();
        });
        
        test('Should handle invalid session ID', async () => {
            const mockService = aiService as any;
            
            try {
                await mockService.incrementPromptCount('invalid-session', 'model', 0.001);
                assert.fail('Should have thrown error');
            } catch (error: any) {
                assert.ok(error.message.includes('Session not found'));
            }
        });
        
        test('Should handle missing AWS client', async () => {
            const mockService = aiService as any;
            mockService.bedrockClient = undefined;
            
            try {
                await mockService.callClaude4SonnetBedrock('test prompt', 'test-agent');
                assert.fail('Should have thrown error');
            } catch (error: any) {
                assert.ok(error.message.includes('AWS Bedrock client not initialized'));
            }
        });
        
        test('Should handle missing Anthropic client', async () => {
            const mockService = aiService as any;
            mockService.anthropicClient = undefined;
            
            try {
                await mockService.callClaude4SonnetDirect('test prompt', 'test-agent');
                assert.fail('Should have thrown error');
            } catch (error: any) {
                assert.ok(error.message.includes('Anthropic client not initialized'));
            }
        });
    });
    
    suite('Integration Tests', () => {
        test('Should integrate AI service with config manager', () => {
            const aiService = AIService.getInstance();
            const providers = aiService.getAvailableProviders();
            
            // Verify that the providers match what ConfigManager would expect
            assert.ok(providers.some(p => p.name.includes('AWS Bedrock')));
            assert.ok(providers.some(p => p.name.includes('Anthropic')));
            assert.ok(providers.some(p => p.name.includes('OpenAI')));
        });
        
        test('Should maintain singleton pattern', () => {
            const instance1 = AIService.getInstance();
            const instance2 = AIService.getInstance();
            
            assert.strictEqual(instance1, instance2);
        });
    });
}); 