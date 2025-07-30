import * as vscode from 'vscode';
import { BackupManager } from './backupManager';

export class PhraseDetector implements vscode.Disposable {
    private disposables: vscode.Disposable[] = [];
    private lastTextBuffer: string = '';
    private detectionTimeout: NodeJS.Timeout | undefined;
    private isActive: boolean = false;
    private lastTriggerTime: number = 0;
    private readonly TRIGGER_COOLDOWN = 30000; // 30 seconds cooldown

    constructor(private backupManager: BackupManager) {}

    public start(): void {
        if (this.isActive) {
            return;
        }

        this.isActive = true;
        console.log('🛡️ DevGuard: Phrase detection started');

        // Monitor text changes in active editor
        const onDidChangeText = vscode.workspace.onDidChangeTextDocument((event) => {
            if (event.document === vscode.window.activeTextEditor?.document) {
                this.analyzeTextChange(event);
            }
        });

        // Monitor when user stops typing (debounced phrase detection)
        const onDidChangeSelection = vscode.window.onDidChangeTextEditorSelection(() => {
            this.scheduleAnalysis();
        });

        // Monitor typing activity for better detection
        const onDidChangeActiveEditor = vscode.window.onDidChangeActiveTextEditor(() => {
            this.clearBuffer();
        });

        this.disposables.push(onDidChangeText, onDidChangeSelection, onDidChangeActiveEditor);
    }

    public stop(): void {
        this.isActive = false;
        this.clearDetectionTimeout();
        this.clearBuffer();
        this.disposables.forEach(d => d.dispose());
        this.disposables = [];
        console.log('🛡️ DevGuard: Phrase detection stopped');
    }

    private analyzeTextChange(event: vscode.TextDocumentChangeEvent): void {
        if (!this.isActive) {
            return;
        }

        // Build up text buffer from recent changes
        for (const change of event.contentChanges) {
            // Only track insertions (not deletions)
            if (change.text) {
                this.lastTextBuffer += change.text;
            }
        }

        // Keep buffer reasonable size (last 1000 characters)
        if (this.lastTextBuffer.length > 1000) {
            this.lastTextBuffer = this.lastTextBuffer.slice(-1000);
        }

        this.scheduleAnalysis();
    }

    private scheduleAnalysis(): void {
        if (!this.isActive) {
            return;
        }

        // Clear existing timeout
        this.clearDetectionTimeout();

        // Get delay from configuration
        const config = vscode.workspace.getConfiguration('devguard');
        const delay = config.get('phraseDetectionDelay', 2000);

        // Schedule analysis after user stops typing
        this.detectionTimeout = setTimeout(() => {
            this.detectCompletionPhrases();
        }, delay);
    }

    private detectCompletionPhrases(): void {
        if (!this.isActive || !this.lastTextBuffer.trim()) {
            return;
        }

        const config = vscode.workspace.getConfiguration('devguard');
        
        // Check if detection is enabled
        if (!config.get('enabled', true)) {
            return;
        }

        // Check cooldown to prevent spam
        const currentTime = Date.now();
        if (currentTime - this.lastTriggerTime < this.TRIGGER_COOLDOWN) {
            return;
        }

        const phrases: string[] = config.get('completionPhrases', []);
        const recentText = this.lastTextBuffer.toLowerCase().trim();
        
        // Look for completion phrases
        for (const phrase of phrases) {
            const phrasePattern = phrase.toLowerCase();
            
            // Check if the phrase appears at the end of recent text
            if (this.endsWithPhrase(recentText, phrasePattern)) {
                this.triggerAutoSave(phrase);
                this.lastTriggerTime = currentTime;
                break;
            }
        }

        // Clear buffer after analysis
        this.clearBuffer();
    }

    private endsWithPhrase(text: string, phrase: string): boolean {
        // Remove punctuation and extra spaces for better matching
        const cleanText = text.replace(/[.,!?;:]+\s*$/, '').trim();
        const cleanPhrase = phrase.trim();
        
        // Check if text ends with the phrase (with word boundaries)
        const pattern = new RegExp(`\\b${this.escapeRegex(cleanPhrase)}\\s*$`, 'i');
        return pattern.test(cleanText);
    }

    private escapeRegex(text: string): string {
        return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    private async triggerAutoSave(detectedPhrase: string): Promise<void> {
        try {
            console.log(`🛡️ DevGuard: Detected completion phrase: "${detectedPhrase}"`);
            
            // Show notification with action buttons
            const config = vscode.workspace.getConfiguration('devguard');
            if (config.get('showNotifications', true)) {
                const action = await vscode.window.showInformationMessage(
                    `🛡️ DevGuard detected completion: "${detectedPhrase}" - Auto-saving...`,
                    'Cancel',
                    'Settings'
                );

                if (action === 'Settings') {
                    vscode.commands.executeCommand('workbench.action.openSettings', 'devguard');
                    return;
                }
                
                if (action === 'Cancel') {
                    return;
                }
            }

            // Perform backup
            await this.backupManager.performSmartSave(`Auto-save triggered by: "${detectedPhrase}"`);
            
        } catch (error) {
            console.error('🛡️ DevGuard: Auto-save failed:', error);
            vscode.window.showErrorMessage(`DevGuard auto-save failed: ${error}`);
        }
    }

    private clearDetectionTimeout(): void {
        if (this.detectionTimeout) {
            clearTimeout(this.detectionTimeout);
            this.detectionTimeout = undefined;
        }
    }

    private clearBuffer(): void {
        this.lastTextBuffer = '';
    }

    public dispose(): void {
        this.stop();
    }
} 