import * as vscode from 'vscode';
import { SpeechService } from './SpeechService';
import { CommandService } from './CommandService';
import { ConfigurationService } from './ConfigurationService';

export type VoiceControlState = 'idle' | 'listening' | 'processing' | 'error';

export class VoiceControlManager {
    private state: VoiceControlState = 'idle';
    private isListening = false;
    private isDictationMode = false;
    private continuousListening = false;
    private stateChangeEmitter = new vscode.EventEmitter<VoiceControlState>();
    private disposables: vscode.Disposable[] = [];

    constructor(
        private speechService: SpeechService,
        private commandService: CommandService,
        private configurationService: ConfigurationService
    ) {
        this.setupEventHandlers();
    }

    public readonly onStateChange = this.stateChangeEmitter.event;

    private setupEventHandlers() {
        // Listen for speech recognition results
        this.speechService.onTranscriptReceived((transcript) => {
            this.handleVoiceInput(transcript);
        });

        // Listen for speech service state changes
        this.speechService.onStateChange((state) => {
            switch (state) {
                case 'listening':
                    this.setState('listening');
                    break;
                case 'processing':
                    this.setState('processing');
                    break;
                case 'idle':
                    this.setState('idle');
                    break;
                case 'error':
                    this.setState('error');
                    break;
            }
        });

        // Listen for configuration changes
        vscode.workspace.onDidChangeConfiguration((e) => {
            if (e.affectsConfiguration('cursorVoice')) {
                this.handleConfigurationChange();
            }
        });
    }

    async initialize(): Promise<void> {
        try {
            await this.speechService.initialize();
            await this.commandService.initialize();
            console.log('Voice Control Manager initialized successfully');
        } catch (error) {
            console.error('Failed to initialize Voice Control Manager:', error);
            this.setState('error');
            throw error;
        }
    }

    async startVoiceAgent(): Promise<void> {
        if (!await this.checkConfiguration()) {
            throw new Error('Voice control not properly configured. Please set up API keys.');
        }

        this.isDictationMode = false;
        this.continuousListening = true;
        await this.speechService.startListening();
        this.isListening = true;
        
        vscode.window.showInformationMessage('Voice Agent activated. Say commands or "Hey Cursor" for assistance.');
    }

    async toggleDictation(): Promise<void> {
        if (!await this.checkConfiguration()) {
            throw new Error('Voice control not properly configured. Please set up API keys.');
        }

        if (this.isDictationMode && this.isListening) {
            await this.stopDictation();
        } else {
            await this.startDictation();
        }
    }

    private async startDictation(): Promise<void> {
        this.isDictationMode = true;
        this.continuousListening = false;
        await this.speechService.startListening();
        this.isListening = true;
        
        vscode.window.showInformationMessage('Dictation mode started. Speak to input text.');
    }

    private async stopDictation(): Promise<void> {
        await this.speechService.stopListening();
        this.isListening = false;
        this.isDictationMode = false;
        
        vscode.window.showInformationMessage('Dictation stopped.');
    }

    async executeVoiceCommand(): Promise<void> {
        if (!await this.checkConfiguration()) {
            throw new Error('Voice control not properly configured. Please set up API keys.');
        }

        // Start listening for a single command
        this.isDictationMode = false;
        this.continuousListening = false;
        await this.speechService.startListening();
        this.isListening = true;
        
        vscode.window.showInformationMessage('Listening for voice command...');
    }

    async startContinuousListening(): Promise<void> {
        if (!await this.checkConfiguration()) {
            throw new Error('Voice control not properly configured. Please set up API keys.');
        }

        this.continuousListening = !this.continuousListening;
        
        if (this.continuousListening) {
            this.isDictationMode = false;
            await this.speechService.startListening();
            this.isListening = true;
        } else {
            await this.speechService.stopListening();
            this.isListening = false;
        }
    }

    stopListening(): void {
        this.speechService.stopListening();
        this.isListening = false;
        this.isDictationMode = false;
        this.continuousListening = false;
        this.setState('idle');
    }

    private async handleVoiceInput(transcript: string): Promise<void> {
        if (!transcript || transcript.trim().length === 0) {
            return;
        }

        console.log('Voice input received:', transcript);

        try {
            this.setState('processing');

            if (this.isDictationMode) {
                await this.handleDictation(transcript);
            } else {
                await this.handleCommand(transcript);
            }

            // Continue listening if in continuous mode or dictation mode
            if (this.continuousListening || this.isDictationMode) {
                setTimeout(async () => {
                    if (this.isListening) {
                        await this.speechService.startListening();
                    }
                }, 500);
            } else {
                this.stopListening();
            }

        } catch (error) {
            console.error('Error handling voice input:', error);
            vscode.window.showErrorMessage(`Voice command error: ${error}`);
            this.setState('error');
        }
    }

    private async handleDictation(transcript: string): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor for dictation');
            return;
        }

        // Use AI to improve the transcript if enabled
        let processedText = transcript;
        if (this.configurationService.getAIAssistanceEnabled()) {
            processedText = await this.commandService.improveText(transcript, this.getCodeContext());
        }

        // Insert text at cursor position
        const position = editor.selection.active;
        await editor.edit(editBuilder => {
            editBuilder.insert(position, processedText);
        });
    }

    private async handleCommand(transcript: string): Promise<void> {
        // Try to match against configured voice commands first
        const commandMapping = this.configurationService.getVoiceCommands();
        const matchedCommand = this.findMatchingCommand(transcript, commandMapping);
        
        if (matchedCommand) {
            await this.commandService.executeCommand(matchedCommand, transcript);
            return;
        }

        // If no direct command match, use AI to interpret the command
        if (this.configurationService.getAIAssistanceEnabled()) {
            const command = await this.commandService.interpretCommand(transcript, this.getCodeContext());
            if (command) {
                await this.commandService.executeCommand(command.action, transcript, command.parameters);
                return;
            }
        }

        // If still no match, treat as general text input
        vscode.window.showInformationMessage(`No command recognized for: "${transcript}"`);
    }

    private findMatchingCommand(transcript: string, commandMapping: any): string | null {
        const lowerTranscript = transcript.toLowerCase();
        
        for (const [command, phrases] of Object.entries(commandMapping)) {
            const phraseArray = Array.isArray(phrases) ? phrases : [phrases];
            for (const phrase of phraseArray) {
                if (lowerTranscript.includes(phrase.toLowerCase())) {
                    return command;
                }
            }
        }
        
        return null;
    }

    private getCodeContext(): any {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            return null;
        }

        return {
            language: editor.document.languageId,
            fileName: editor.document.fileName,
            selection: editor.selection,
            currentLine: editor.document.lineAt(editor.selection.active.line).text,
            nearbyLines: this.getNearbyLines(editor, 5)
        };
    }

    private getNearbyLines(editor: vscode.TextEditor, radius: number): string[] {
        const currentLine = editor.selection.active.line;
        const start = Math.max(0, currentLine - radius);
        const end = Math.min(editor.document.lineCount - 1, currentLine + radius);
        
        const lines: string[] = [];
        for (let i = start; i <= end; i++) {
            lines.push(editor.document.lineAt(i).text);
        }
        
        return lines;
    }

    private async checkConfiguration(): Promise<boolean> {
        const deepgramKey = this.configurationService.getDeepgramApiKey();
        if (!deepgramKey) {
            const result = await vscode.window.showErrorMessage(
                'Deepgram API key not configured',
                'Configure Now'
            );
            if (result === 'Configure Now') {
                await vscode.commands.executeCommand('cursorVoice.configureAPI');
            }
            return false;
        }

        return true;
    }

    private handleConfigurationChange(): void {
        // Reinitialize services with new configuration
        this.speechService.updateConfiguration();
        this.commandService.updateConfiguration();
    }

    private setState(newState: VoiceControlState): void {
        if (this.state !== newState) {
            this.state = newState;
            this.stateChangeEmitter.fire(newState);
        }
    }

    dispose(): void {
        this.stopListening();
        this.stateChangeEmitter.dispose();
        this.disposables.forEach(d => d.dispose());
    }
} 