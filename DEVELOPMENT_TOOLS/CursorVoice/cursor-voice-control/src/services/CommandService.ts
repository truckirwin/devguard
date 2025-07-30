import * as vscode from 'vscode';
import { ConfigurationService } from './ConfigurationService';

export interface InterpretedCommand {
    action: string;
    parameters?: any;
    confidence: number;
}

export class CommandService {
    private openaiClient: any;
    private isInitialized = false;

    constructor(private configurationService?: ConfigurationService) {}

    async initialize(): Promise<void> {
        if (this.configurationService?.getAIAssistanceEnabled()) {
            const apiKey = this.configurationService.getOpenAIApiKey();
            if (apiKey) {
                try {
                    // Initialize OpenAI client
                    const { OpenAI } = await import('openai');
                    this.openaiClient = new OpenAI({ apiKey });
                    console.log('OpenAI client initialized');
                } catch (error) {
                    console.warn('Failed to initialize OpenAI client:', error);
                }
            }
        }
        this.isInitialized = true;
    }

    async executeCommand(command: string, transcript: string, parameters?: any): Promise<void> {
        console.log(`Executing command: ${command} with transcript: "${transcript}"`);

        try {
            switch (command) {
                case 'openFile':
                    await this.openFile(parameters);
                    break;
                case 'saveFile':
                    await this.saveFile();
                    break;
                case 'newFile':
                    await this.newFile();
                    break;
                case 'closeFile':
                    await this.closeFile();
                    break;
                case 'goToLine':
                    await this.goToLine(transcript, parameters);
                    break;
                case 'findInFile':
                    await this.findInFile(transcript, parameters);
                    break;
                case 'replaceInFile':
                    await this.replaceInFile(transcript, parameters);
                    break;
                case 'toggleSidebar':
                    await this.toggleSidebar();
                    break;
                case 'openTerminal':
                    await this.openTerminal();
                    break;
                case 'runCode':
                    await this.runCode();
                    break;
                case 'formatCode':
                    await this.formatCode();
                    break;
                case 'commentCode':
                    await this.commentCode();
                    break;
                case 'copyLine':
                    await this.copyLine();
                    break;
                case 'deleteLine':
                    await this.deleteLine();
                    break;
                case 'duplicateLine':
                    await this.duplicateLine();
                    break;
                case 'selectAll':
                    await this.selectAll();
                    break;
                default:
                    vscode.window.showWarningMessage(`Unknown command: ${command}`);
            }
        } catch (error) {
            console.error(`Error executing command ${command}:`, error);
            vscode.window.showErrorMessage(`Failed to execute command: ${error}`);
        }
    }

    async interpretCommand(transcript: string, context: any): Promise<InterpretedCommand | null> {
        if (!this.openaiClient) {
            return null;
        }

        try {
            const prompt = this.buildCommandInterpretationPrompt(transcript, context);
            
            const response = await this.openaiClient.chat.completions.create({
                model: 'gpt-3.5-turbo',
                messages: [{ role: 'user', content: prompt }],
                max_tokens: 200,
                temperature: 0.1
            });

            const content = response.choices[0]?.message?.content;
            if (content) {
                try {
                    const parsed = JSON.parse(content);
                    return parsed;
                } catch (parseError) {
                    console.error('Failed to parse AI response:', parseError);
                }
            }
        } catch (error) {
            console.error('AI command interpretation error:', error);
        }

        return null;
    }

    async improveText(transcript: string, context: any): Promise<string> {
        if (!this.openaiClient) {
            return transcript;
        }

        try {
            const prompt = this.buildTextImprovementPrompt(transcript, context);
            
            const response = await this.openaiClient.chat.completions.create({
                model: 'gpt-3.5-turbo',
                messages: [{ role: 'user', content: prompt }],
                max_tokens: 300,
                temperature: 0.2
            });

            const improvedText = response.choices[0]?.message?.content;
            return improvedText || transcript;
        } catch (error) {
            console.error('Text improvement error:', error);
            return transcript;
        }
    }

    updateConfiguration(): void {
        // Reinitialize if needed when configuration changes
        if (this.configurationService?.getAIAssistanceEnabled()) {
            this.initialize();
        }
    }

    // Command implementations
    private async openFile(parameters?: any): Promise<void> {
        const uri = await vscode.window.showOpenDialog({
            canSelectFiles: true,
            canSelectFolders: false,
            canSelectMany: false
        });
        if (uri && uri[0]) {
            await vscode.window.showTextDocument(uri[0]);
        }
    }

    private async saveFile(): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (editor) {
            await editor.document.save();
            vscode.window.showInformationMessage('File saved');
        }
    }

    private async newFile(): Promise<void> {
        await vscode.commands.executeCommand('workbench.action.files.newUntitledFile');
    }

    private async closeFile(): Promise<void> {
        await vscode.commands.executeCommand('workbench.action.closeActiveEditor');
    }

    private async goToLine(transcript: string, parameters?: any): Promise<void> {
        const lineMatch = transcript.match(/(\d+)/);
        if (lineMatch) {
            const lineNumber = parseInt(lineMatch[1]);
            await vscode.commands.executeCommand('workbench.action.gotoLine', { lineNumber });
        } else {
            await vscode.commands.executeCommand('workbench.action.gotoLine');
        }
    }

    private async findInFile(transcript: string, parameters?: any): Promise<void> {
        // Extract search term from transcript
        const searchMatch = transcript.match(/find\s+(.+)$/i);
        if (searchMatch) {
            const searchTerm = searchMatch[1];
            await vscode.commands.executeCommand('actions.find', { searchString: searchTerm });
        } else {
            await vscode.commands.executeCommand('actions.find');
        }
    }

    private async replaceInFile(transcript: string, parameters?: any): Promise<void> {
        await vscode.commands.executeCommand('editor.action.startFindReplaceAction');
    }

    private async toggleSidebar(): Promise<void> {
        await vscode.commands.executeCommand('workbench.action.toggleSidebarVisibility');
    }

    private async openTerminal(): Promise<void> {
        await vscode.commands.executeCommand('workbench.action.terminal.toggleTerminal');
    }

    private async runCode(): Promise<void> {
        // Try to run the current file based on language
        const editor = vscode.window.activeTextEditor;
        if (editor) {
            const language = editor.document.languageId;
            switch (language) {
                case 'python':
                    await vscode.commands.executeCommand('python.execInTerminal');
                    break;
                case 'javascript':
                case 'typescript':
                    await vscode.commands.executeCommand('workbench.action.debug.start');
                    break;
                default:
                    await vscode.commands.executeCommand('workbench.action.debug.start');
            }
        }
    }

    private async formatCode(): Promise<void> {
        await vscode.commands.executeCommand('editor.action.formatDocument');
    }

    private async commentCode(): Promise<void> {
        await vscode.commands.executeCommand('editor.action.commentLine');
    }

    private async copyLine(): Promise<void> {
        await vscode.commands.executeCommand('editor.action.copyLinesDownAction');
    }

    private async deleteLine(): Promise<void> {
        await vscode.commands.executeCommand('editor.action.deleteLines');
    }

    private async duplicateLine(): Promise<void> {
        await vscode.commands.executeCommand('editor.action.copyLinesDownAction');
    }

    private async selectAll(): Promise<void> {
        await vscode.commands.executeCommand('editor.action.selectAll');
    }

    // AI prompt builders
    private buildCommandInterpretationPrompt(transcript: string, context: any): string {
        return `You are a voice command interpreter for a code editor. Given the voice transcript and code context, determine what action the user wants to perform.

Voice transcript: "${transcript}"
Context: ${JSON.stringify(context, null, 2)}

Available commands: openFile, saveFile, newFile, closeFile, goToLine, findInFile, replaceInFile, toggleSidebar, openTerminal, runCode, formatCode, commentCode, copyLine, deleteLine, duplicateLine, selectAll

Respond with JSON in this format:
{
    "action": "commandName",
    "parameters": {},
    "confidence": 0.8
}

If you cannot determine a clear command, respond with null.`;
    }

    private buildTextImprovementPrompt(transcript: string, context: any): string {
        const language = context?.language || 'text';
        
        return `You are a voice-to-text processor for a code editor. Clean up and improve the following voice transcript for insertion into a ${language} file.

Original transcript: "${transcript}"
File language: ${language}
Context: ${context?.currentLine || 'N/A'}

Rules:
1. Fix obvious speech recognition errors
2. Apply proper formatting for the target language
3. Add appropriate punctuation
4. Convert spoken programming terms to proper syntax
5. Maintain the original intent

Return only the cleaned text, no explanations.`;
    }
} 