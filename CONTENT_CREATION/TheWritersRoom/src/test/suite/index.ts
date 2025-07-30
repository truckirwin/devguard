import * as path from 'path';
import * as fs from 'fs';
import Mocha = require('mocha');

export interface TestConfig {
    timeout: number;
    retries: number;
    reporter: string;
    coverage: {
        enabled: boolean;
        threshold: {
            statements: number;
            branches: number;
            functions: number;
            lines: number;
        };
    };
}

export class WritersRoomTestSuite {
    private mocha: Mocha;
    private config: TestConfig;
    private testsRoot: string;

    constructor(testsRoot: string) {
        this.testsRoot = testsRoot;
        this.config = this.loadTestConfig();
        this.mocha = this.createMochaInstance();
    }

    private loadTestConfig(): TestConfig {
        return {
            timeout: 10000,
            retries: 2,
            reporter: 'spec',
            coverage: {
                enabled: true,
                threshold: {
                    statements: 90,
                    branches: 85,
                    functions: 90,
                    lines: 90
                }
            }
        };
    }

    private createMochaInstance(): Mocha {
        return new Mocha({
            ui: 'tdd',
            color: true,
            timeout: this.config.timeout,
            retries: this.config.retries,
            reporter: this.config.reporter
        });
    }

    public async run(): Promise<void> {
        return new Promise((resolve, reject) => {
            try {
                console.log('🧪 Starting The Writers Room Test Suite...');
                
                // Find and add test files
                const testFiles = this.findTestFiles();
                console.log(`📁 Found ${testFiles.length} test files`);
                
                testFiles.forEach((file: string) => {
                    console.log(`  • ${path.relative(this.testsRoot, file)}`);
                    this.mocha.addFile(file);
                });

                // Run tests
                console.log('\n🚀 Running tests...\n');
                
                this.mocha.run((failures: number) => {
                    if (failures > 0) {
                        console.error(`\n❌ ${failures} test(s) failed`);
                        reject(new Error(`${failures} tests failed.`));
                    } else {
                        console.log('\n✅ All tests passed!');
                        resolve();
                    }
                });
            } catch (err) {
                console.error('Test suite error:', err);
                reject(err);
            }
        });
    }

    private findTestFiles(): string[] {
        const files: string[] = [];
        
        // Manually find test files without glob dependency
        this.walkDirectory(this.testsRoot, files);
        
        // Remove duplicates and sort
        return [...new Set(files)].sort();
    }

    private walkDirectory(dir: string, files: string[]): void {
        try {
            const items = fs.readdirSync(dir);
            
            for (const item of items) {
                const fullPath = path.join(dir, item);
                
                try {
                    const stat = fs.statSync(fullPath);
                    
                    if (stat.isDirectory()) {
                        // Skip node_modules and other common directories
                        if (!['node_modules', '.git', 'out', 'dist', 'build'].includes(item)) {
                            this.walkDirectory(fullPath, files);
                        }
                    } else if (item.endsWith('.test.js') || item.endsWith('.spec.js')) {
                        files.push(fullPath);
                    }
                } catch (statError: any) {
                    console.warn(`Warning: Could not stat ${fullPath}:`, statError?.message || 'Unknown error');
                }
            }
        } catch (readError: any) {
            console.warn(`Warning: Could not read directory ${dir}:`, readError?.message || 'Unknown error');
        }
    }

    public addTestFile(filePath: string): void {
        this.mocha.addFile(filePath);
    }

    public setTimeout(timeout: number): void {
        this.config.timeout = timeout;
        this.mocha.timeout(timeout);
    }

    public setReporter(reporter: string): void {
        this.config.reporter = reporter;
        // Note: Mocha reporter can't be changed after instantiation
        // This would require recreating the Mocha instance
    }
}

// Legacy function for backward compatibility
export function run(): Promise<void> {
    const testsRoot = path.resolve(__dirname, '..');
    const testSuite = new WritersRoomTestSuite(testsRoot);
    return testSuite.run();
}

// Enhanced test discovery with recursive directory walking
function findTestFiles(dir: string): string[] {
    const files: string[] = [];
    
    function walkDir(currentDir: string) {
        try {
            const items = fs.readdirSync(currentDir);
            
            for (const item of items) {
                const fullPath = path.join(currentDir, item);
                
                try {
                    const stat = fs.statSync(fullPath);
                    
                    if (stat.isDirectory()) {
                        // Skip node_modules and other common directories
                        if (!['node_modules', '.git', 'out', 'dist', 'build'].includes(item)) {
                            walkDir(fullPath);
                        }
                    } else if (item.endsWith('.test.js') || item.endsWith('.spec.js')) {
                        files.push(fullPath);
                    }
                } catch (statError: any) {
                    console.warn(`Warning: Could not stat ${fullPath}:`, statError?.message || 'Unknown error');
                }
            }
        } catch (readError: any) {
            console.warn(`Warning: Could not read directory ${currentDir}:`, readError?.message || 'Unknown error');
        }
    }
    
    walkDir(dir);
    return files;
}

// Test utilities for mocking and setup
export class TestUtils {
    public static createMockVSCode() {
        return {
            workspace: {
                getConfiguration: (section?: string) => ({
                    get: (key: string, defaultValue?: any) => defaultValue,
                    update: async (key: string, value: any) => Promise.resolve(),
                    has: (key: string) => false
                }),
                workspaceFolders: []
            },
            window: {
                showInformationMessage: (message: string, ...items: string[]) => Promise.resolve(undefined),
                showWarningMessage: (message: string, ...items: string[]) => Promise.resolve(undefined),
                showErrorMessage: (message: string, ...items: string[]) => Promise.resolve(undefined),
                showInputBox: (options?: any) => Promise.resolve(undefined),
                showQuickPick: (items: any[], options?: any) => Promise.resolve(undefined),
                createStatusBarItem: () => ({
                    text: '',
                    tooltip: '',
                    command: '',
                    show: () => {},
                    hide: () => {},
                    dispose: () => {}
                }),
                registerTreeDataProvider: () => ({ dispose: () => {} }),
                registerWebviewViewProvider: () => ({ dispose: () => {} })
            },
            commands: {
                registerCommand: (command: string, callback: (...args: any[]) => any) => ({
                    dispose: () => {}
                }),
                executeCommand: (command: string, ...args: any[]) => Promise.resolve()
            },
            ConfigurationTarget: {
                Global: 1,
                Workspace: 2,
                WorkspaceFolder: 3
            },
            StatusBarAlignment: {
                Left: 1,
                Right: 2
            }
        };
    }

    public static createMockAWS() {
        // Create mock functions without jest dependency
        const mockFn = () => ({
            mockResolvedValue: (value: any) => Promise.resolve(value),
            mockRejectedValue: (error: any) => Promise.reject(error)
        });

        return {
            bedrock: {
                send: mockFn().mockResolvedValue({
                    body: new TextEncoder().encode(JSON.stringify({
                        content: [{ text: 'Mock AI response' }],
                        usage: { input_tokens: 10, output_tokens: 20 }
                    }))
                })
            },
            dynamodb: {
                put: mockFn().mockResolvedValue({}),
                get: mockFn().mockResolvedValue({ Item: {} }),
                query: mockFn().mockResolvedValue({ Items: [] }),
                scan: mockFn().mockResolvedValue({ Items: [] }),
                update: mockFn().mockResolvedValue({}),
                delete: mockFn().mockResolvedValue({})
            },
            s3: {
                putObject: mockFn().mockResolvedValue({}),
                getObject: mockFn().mockResolvedValue({ Body: 'mock content' }),
                deleteObject: mockFn().mockResolvedValue({}),
                listObjects: mockFn().mockResolvedValue({ Contents: [] })
            }
        };
    }

    public static async createTestProject(projectName: string = 'test-project'): Promise<string> {
        const testDir = path.join(__dirname, '..', '..', '..', 'test-workspace', projectName);
        
        if (!fs.existsSync(testDir)) {
            fs.mkdirSync(testDir, { recursive: true });
        }

        // Create basic project structure
        const projectStructure = {
            'project.json': JSON.stringify({
                name: projectName,
                type: 'screenplay',
                created: new Date().toISOString(),
                version: '1.0.0'
            }, null, 2),
            'screenplay.fountain': `Title: ${projectName}
Author: Test User
Draft date: ${new Date().toLocaleDateString()}

FADE IN:

INT. TEST SCENE - DAY

This is a test screenplay for automated testing.

FADE OUT.`,
            'characters.json': JSON.stringify([
                {
                    name: 'Test Character',
                    description: 'A character for testing purposes',
                    traits: ['brave', 'intelligent']
                }
            ], null, 2)
        };

        for (const [filename, content] of Object.entries(projectStructure)) {
            fs.writeFileSync(path.join(testDir, filename), content);
        }

        return testDir;
    }

    public static async cleanupTestProject(projectPath: string): Promise<void> {
        if (fs.existsSync(projectPath)) {
            fs.rmSync(projectPath, { recursive: true, force: true });
        }
    }

    public static createMockAgent(agentType: string = 'test-agent') {
        return {
            id: agentType,
            name: `Test ${agentType}`,
            description: 'A test agent for automated testing',
            personality: 'helpful and concise',
            specialty: 'testing',
            available: true,
            lastUsed: new Date().toISOString()
        };
    }

    public static async delay(ms: number): Promise<void> {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    public static generateTestData(type: 'dialogue' | 'character' | 'scene' | 'plot') {
        const testData = {
            dialogue: {
                characters: ['ALICE', 'BOB'],
                lines: [
                    'ALICE: This is a test dialogue.',
                    'BOB: Yes, it is for testing purposes.',
                    'ALICE: Perfect for our automated tests.'
                ]
            },
            character: {
                name: 'Test Character',
                age: 30,
                occupation: 'Software Tester',
                personality: ['methodical', 'detail-oriented', 'reliable'],
                backstory: 'A dedicated professional who ensures quality in everything.',
                goals: ['Find all bugs', 'Improve user experience'],
                conflicts: ['Time pressure', 'Perfectionist tendencies']
            },
            scene: {
                location: 'INT. TEST LABORATORY - DAY',
                description: 'A sterile testing environment with computers and monitors.',
                mood: 'focused and productive',
                props: ['computers', 'test scripts', 'coffee cups'],
                characters: ['Test Engineer', 'QA Manager']
            },
            plot: {
                title: 'The Testing Chronicles',
                genre: 'Tech Drama',
                logline: 'A team of testers race against time to ensure software quality.',
                acts: [
                    'Setup: Tests are written and environment prepared',
                    'Execution: Tests run and bugs are discovered',
                    'Resolution: Issues are fixed and quality is achieved'
                ],
                themes: ['Quality', 'Teamwork', 'Precision']
            }
        };

        return testData[type];
    }
}

// Performance testing utilities
export class PerformanceTestUtils {
    public static async measureExecutionTime<T>(
        operation: () => Promise<T>,
        iterations: number = 1
    ): Promise<{ result: T; averageTime: number; totalTime: number }> {
        const times: number[] = [];
        let result: T;

        for (let i = 0; i < iterations; i++) {
            const start = performance.now();
            result = await operation();
            const end = performance.now();
            times.push(end - start);
        }

        const totalTime = times.reduce((sum, time) => sum + time, 0);
        const averageTime = totalTime / iterations;

        return {
            result: result!,
            averageTime,
            totalTime
        };
    }

    public static async loadTest(
        operation: () => Promise<any>,
        concurrency: number = 10,
        duration: number = 5000
    ): Promise<{
        totalRequests: number;
        successfulRequests: number;
        failedRequests: number;
        averageResponseTime: number;
        requestsPerSecond: number;
    }> {
        const startTime = Date.now();
        const endTime = startTime + duration;
        const responseTimes: number[] = [];
        let totalRequests = 0;
        let successfulRequests = 0;
        let failedRequests = 0;

        const workers = Array(concurrency).fill(null).map(async () => {
            while (Date.now() < endTime) {
                const requestStart = Date.now();
                totalRequests++;

                try {
                    await operation();
                    successfulRequests++;
                } catch (error) {
                    failedRequests++;
                }

                const requestEnd = Date.now();
                responseTimes.push(requestEnd - requestStart);
            }
        });

        await Promise.all(workers);

        const actualDuration = Date.now() - startTime;
        const averageResponseTime = responseTimes.reduce((sum, time) => sum + time, 0) / responseTimes.length;
        const requestsPerSecond = (totalRequests / actualDuration) * 1000;

        return {
            totalRequests,
            successfulRequests,
            failedRequests,
            averageResponseTime,
            requestsPerSecond
        };
    }
}

// Export everything for use in tests
export { WritersRoomTestSuite as TestSuite };
export default { run, TestUtils, PerformanceTestUtils }; 