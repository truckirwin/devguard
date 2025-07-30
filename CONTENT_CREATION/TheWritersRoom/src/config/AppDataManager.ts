import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';
import * as os from 'os';

export interface WritersRoomConfig {
    version: string;
    lastUpdated: string;
    userSettings: UserSettings;
    importedScripts: ImportedScript[];
    agentBackstories: AgentBackstory[];
    customAgents: CustomAgent[];
    workspacePreferences: WorkspacePreferences;
}

export interface UserSettings {
    defaultAIProvider: string;
    defaultAgent: string;
    autoSave: boolean;
    enableTelemetry: boolean;
    theme: string;
    fontSize: number;
    fontFamily: string;
    enableSpellCheck: boolean;
    enableAutoComplete: boolean;
    maxRecentProjects: number;
}

export interface ImportedScript {
    id: string;
    name: string;
    filePath: string;
    importDate: string;
    fileSize: number;
    format: 'fountain' | 'fdx' | 'pdf' | 'txt' | 'md';
    metadata: {
        title?: string;
        author?: string;
        genre?: string;
        pages?: number;
        characters?: string[];
        locations?: string[];
    };
    tags: string[];
    notes: string;
}

export interface AgentBackstory {
    agentId: string;
    name: string;
    backstory: string;
    personality: any;
    expertise: any;
    relationships: any;
    customizations: {
        userNotes: string;
        preferredModels: string[];
        customPrompts: string[];
        interactionHistory: InteractionRecord[];
    };
}

export interface CustomAgent {
    id: string;
    name: string;
    title: string;
    description: string;
    personality: any;
    expertise: any;
    createdDate: string;
    isActive: boolean;
    creator: string;
}

export interface InteractionRecord {
    date: string;
    projectId?: string;
    interaction: string;
    rating?: number;
    notes?: string;
}

export interface WorkspacePreferences {
    recentProjects: RecentProject[];
    favoriteAgents: string[];
    customKeyBindings: { [command: string]: string };
    layoutPreferences: {
        sidebarWidth: number;
        panelHeight: number;
        explorerCollapsed: boolean;
    };
}

export interface RecentProject {
    path: string;
    name: string;
    type: string;
    lastOpened: string;
    isPinned: boolean;
}

export class AppDataManager {
    private static instance: AppDataManager;
    private configPath: string;
    private config: WritersRoomConfig;
    private context: vscode.ExtensionContext;

    private constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.configPath = this.getConfigPath();
        this.config = this.loadConfig();
    }

    public static getInstance(context?: vscode.ExtensionContext): AppDataManager {
        if (!AppDataManager.instance && context) {
            AppDataManager.instance = new AppDataManager(context);
        }
        return AppDataManager.instance;
    }

    private getConfigPath(): string {
        // Use OS-specific application data directory
        const homeDir = os.homedir();
        let appDataDir: string;

        switch (process.platform) {
            case 'win32':
                appDataDir = path.join(homeDir, 'AppData', 'Roaming', 'TheWritersRoom');
                break;
            case 'darwin':
                appDataDir = path.join(homeDir, 'Library', 'Application Support', 'TheWritersRoom');
                break;
            default: // Linux and others
                appDataDir = path.join(homeDir, '.config', 'TheWritersRoom');
                break;
        }

        // Ensure directory exists
        if (!fs.existsSync(appDataDir)) {
            fs.mkdirSync(appDataDir, { recursive: true });
        }

        return path.join(appDataDir, 'config.json');
    }

    private loadConfig(): WritersRoomConfig {
        try {
            if (fs.existsSync(this.configPath)) {
                const configData = fs.readFileSync(this.configPath, 'utf8');
                const config = JSON.parse(configData);
                
                // Migrate old config if needed
                return this.migrateConfig(config);
            }
        } catch (error) {
            console.error('Error loading config:', error);
        }

        // Return default config
        return this.getDefaultConfig();
    }

    private getDefaultConfig(): WritersRoomConfig {
        return {
            version: '1.0.0',
            lastUpdated: new Date().toISOString(),
            userSettings: {
                defaultAIProvider: 'openai',
                defaultAgent: 'script_doctor',
                autoSave: true,
                enableTelemetry: false,
                theme: 'auto',
                fontSize: 14,
                fontFamily: 'Courier New, monospace',
                enableSpellCheck: true,
                enableAutoComplete: true,
                maxRecentProjects: 10
            },
            importedScripts: [],
            agentBackstories: [],
            customAgents: [],
            workspacePreferences: {
                recentProjects: [],
                favoriteAgents: ['script_doctor', 'character_specialist'],
                customKeyBindings: {},
                layoutPreferences: {
                    sidebarWidth: 300,
                    panelHeight: 200,
                    explorerCollapsed: false
                }
            }
        };
    }

    private migrateConfig(config: any): WritersRoomConfig {
        // Handle config migration from older versions
        const defaultConfig = this.getDefaultConfig();
        
        return {
            version: config.version || defaultConfig.version,
            lastUpdated: new Date().toISOString(),
            userSettings: { ...defaultConfig.userSettings, ...config.userSettings },
            importedScripts: config.importedScripts || [],
            agentBackstories: config.agentBackstories || [],
            customAgents: config.customAgents || [],
            workspacePreferences: { ...defaultConfig.workspacePreferences, ...config.workspacePreferences }
        };
    }

    public saveConfig(): void {
        try {
            this.config.lastUpdated = new Date().toISOString();
            const configData = JSON.stringify(this.config, null, 2);
            fs.writeFileSync(this.configPath, configData, 'utf8');
            console.log('✅ Configuration saved to:', this.configPath);
        } catch (error) {
            console.error('❌ Error saving config:', error);
            vscode.window.showErrorMessage('Failed to save Writers Room configuration');
        }
    }

    // User Settings
    public getUserSettings(): UserSettings {
        return this.config.userSettings;
    }

    public updateUserSettings(settings: Partial<UserSettings>): void {
        this.config.userSettings = { ...this.config.userSettings, ...settings };
        this.saveConfig();
    }

    // Imported Scripts
    public getImportedScripts(): ImportedScript[] {
        return this.config.importedScripts;
    }

    public addImportedScript(script: ImportedScript): void {
        this.config.importedScripts.push(script);
        this.saveConfig();
    }

    public removeImportedScript(scriptId: string): void {
        this.config.importedScripts = this.config.importedScripts.filter(s => s.id !== scriptId);
        this.saveConfig();
    }

    public updateImportedScript(scriptId: string, updates: Partial<ImportedScript>): void {
        const index = this.config.importedScripts.findIndex(s => s.id === scriptId);
        if (index !== -1) {
            this.config.importedScripts[index] = { ...this.config.importedScripts[index], ...updates };
            this.saveConfig();
        }
    }

    // Agent Backstories
    public getAgentBackstories(): AgentBackstory[] {
        return this.config.agentBackstories;
    }

    public getAgentBackstory(agentId: string): AgentBackstory | undefined {
        return this.config.agentBackstories.find(a => a.agentId === agentId);
    }

    public updateAgentBackstory(agentId: string, backstory: Partial<AgentBackstory>): void {
        const index = this.config.agentBackstories.findIndex(a => a.agentId === agentId);
        if (index !== -1) {
            this.config.agentBackstories[index] = { ...this.config.agentBackstories[index], ...backstory };
        } else {
            this.config.agentBackstories.push({
                agentId,
                name: backstory.name || agentId,
                backstory: backstory.backstory || '',
                personality: backstory.personality || {},
                expertise: backstory.expertise || {},
                relationships: backstory.relationships || {},
                customizations: backstory.customizations || {
                    userNotes: '',
                    preferredModels: [],
                    customPrompts: [],
                    interactionHistory: []
                }
            });
        }
        this.saveConfig();
    }

    public addInteractionRecord(agentId: string, interaction: InteractionRecord): void {
        const backstory = this.getAgentBackstory(agentId);
        if (backstory) {
            backstory.customizations.interactionHistory.push(interaction);
            this.saveConfig();
        }
    }

    // Custom Agents
    public getCustomAgents(): CustomAgent[] {
        return this.config.customAgents;
    }

    public addCustomAgent(agent: CustomAgent): void {
        this.config.customAgents.push(agent);
        this.saveConfig();
    }

    public removeCustomAgent(agentId: string): void {
        this.config.customAgents = this.config.customAgents.filter(a => a.id !== agentId);
        this.saveConfig();
    }

    // Workspace Preferences
    public getWorkspacePreferences(): WorkspacePreferences {
        return this.config.workspacePreferences;
    }

    public updateWorkspacePreferences(preferences: Partial<WorkspacePreferences>): void {
        this.config.workspacePreferences = { ...this.config.workspacePreferences, ...preferences };
        this.saveConfig();
    }

    public addRecentProject(project: RecentProject): void {
        const existing = this.config.workspacePreferences.recentProjects.findIndex(p => p.path === project.path);
        if (existing !== -1) {
            this.config.workspacePreferences.recentProjects[existing] = project;
        } else {
            this.config.workspacePreferences.recentProjects.unshift(project);
        }

        // Limit recent projects
        const maxRecent = this.config.userSettings.maxRecentProjects;
        this.config.workspacePreferences.recentProjects = this.config.workspacePreferences.recentProjects.slice(0, maxRecent);
        this.saveConfig();
    }

    // Utility methods
    public getConfigFilePath(): string {
        return this.configPath;
    }

    public exportConfig(): string {
        return JSON.stringify(this.config, null, 2);
    }

    public importConfig(configData: string): boolean {
        try {
            const newConfig = JSON.parse(configData);
            this.config = this.migrateConfig(newConfig);
            this.saveConfig();
            return true;
        } catch (error) {
            console.error('Error importing config:', error);
            return false;
        }
    }

    public resetToDefaults(): void {
        this.config = this.getDefaultConfig();
        this.saveConfig();
        vscode.window.showInformationMessage('Writers Room configuration reset to defaults');
    }
} 