import * as vscode from 'vscode';

export class ConfigurationService {
    private readonly configSection = 'cursorVoice';

    getDeepgramApiKey(): string {
        return this.getConfiguration().get<string>('deepgramApiKey', '');
    }

    getOpenAIApiKey(): string {
        return this.getConfiguration().get<string>('openaiApiKey', '');
    }

    getLanguage(): string {
        return this.getConfiguration().get<string>('language', 'en-US');
    }

    getSensitivity(): number {
        return this.getConfiguration().get<number>('sensitivity', 0.7);
    }

    getContinuousListening(): boolean {
        return this.getConfiguration().get<boolean>('continuousListening', false);
    }

    getCodeContextEnabled(): boolean {
        return this.getConfiguration().get<boolean>('enableCodeContext', true);
    }

    getAIAssistanceEnabled(): boolean {
        return this.getConfiguration().get<boolean>('enableAIAssistance', true);
    }

    getMicrophoneDevice(): string {
        return this.getConfiguration().get<string>('microphoneDevice', 'default');
    }

    getVoiceCommands(): any {
        return this.getConfiguration().get<any>('voiceCommands', {
            "openFile": ["open file", "open document"],
            "saveFile": ["save", "save file"],
            "newFile": ["new file", "create file"],
            "closeFile": ["close", "close file"],
            "goToLine": ["go to line", "goto line"],
            "findInFile": ["find", "search"],
            "replaceInFile": ["replace", "find and replace"],
            "toggleSidebar": ["toggle sidebar", "hide sidebar", "show sidebar"],
            "openTerminal": ["open terminal", "show terminal"],
            "runCode": ["run", "execute", "run code"],
            "formatCode": ["format", "format code"],
            "commentCode": ["comment", "comment out"],
            "copyLine": ["copy line"],
            "deleteLine": ["delete line"],
            "duplicateLine": ["duplicate line"],
            "selectAll": ["select all"]
        });
    }

    async updateConfiguration(key: string, value: any, target: vscode.ConfigurationTarget = vscode.ConfigurationTarget.Global): Promise<void> {
        await this.getConfiguration().update(key, value, target);
    }

    private getConfiguration(): vscode.WorkspaceConfiguration {
        return vscode.workspace.getConfiguration(this.configSection);
    }

    // Validation methods
    validateConfiguration(): { isValid: boolean; errors: string[] } {
        const errors: string[] = [];

        if (!this.getDeepgramApiKey()) {
            errors.push('Deepgram API key is required for speech recognition');
        }

        if (this.getAIAssistanceEnabled() && !this.getOpenAIApiKey()) {
            errors.push('OpenAI API key is required when AI assistance is enabled');
        }

        const sensitivity = this.getSensitivity();
        if (sensitivity < 0.1 || sensitivity > 1.0) {
            errors.push('Voice sensitivity must be between 0.1 and 1.0');
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }

    // Get configuration for display in UI
    getConfigurationSummary(): any {
        return {
            deepgramConfigured: !!this.getDeepgramApiKey(),
            openaiConfigured: !!this.getOpenAIApiKey(),
            language: this.getLanguage(),
            sensitivity: this.getSensitivity(),
            continuousListening: this.getContinuousListening(),
            codeContextEnabled: this.getCodeContextEnabled(),
            aiAssistanceEnabled: this.getAIAssistanceEnabled(),
            microphoneDevice: this.getMicrophoneDevice(),
            voiceCommandCount: Object.keys(this.getVoiceCommands()).length
        };
    }
} 