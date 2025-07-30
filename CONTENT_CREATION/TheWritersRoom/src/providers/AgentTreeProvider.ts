import * as vscode from 'vscode';
import * as path from 'path';
import { AgentManager, Agent } from '../agents/AgentManager';

export class AgentTreeProvider implements vscode.TreeDataProvider<AgentTreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<AgentTreeItem | undefined | null | void> = new vscode.EventEmitter<AgentTreeItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<AgentTreeItem | undefined | null | void> = this._onDidChangeTreeData.event;

    constructor(
        private context: vscode.ExtensionContext,
        private agentManager: AgentManager,
        private currentAgent: string = 'script_doctor'
    ) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    setCurrentAgent(agentId: string): void {
        this.currentAgent = agentId;
        this.refresh();
    }

    getTreeItem(element: AgentTreeItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: AgentTreeItem): Thenable<AgentTreeItem[]> {
        console.log('🌲 AgentTreeProvider.getChildren called', element ? element.label : 'root');
        
        if (!element) {
            // Root level - show all agents directly
            try {
                const agents = this.agentManager.getAllAgents();
                console.log(`🌲 Found ${agents.length} agents:`, agents.map(a => a.name));
                
                const items = agents.map(agent => {
                    // Create label with star for current agent
                    const label = agent.id === this.currentAgent ? `⭐ ${agent.name}` : agent.name;
                    
                    // Create path to agent's JSON file
                    const agentFilePath = this.getAgentFilePath(agent.id);
                    
                    const item = new AgentTreeItem(
                        label,
                        vscode.TreeItemCollapsibleState.None,
                        'agent',
                        {
                            command: 'vscode.open',
                            title: 'View Agent Backstory',
                            arguments: [vscode.Uri.file(agentFilePath)]
                        }
                    );
                    item.description = agent.title || 'AI Writing Agent';
                    item.iconPath = this.getAgentIcon(agent.id);
                    item.tooltip = `${agent.name} - ${agent.description || 'Click to view backstory'}`;
                    
                    // Mark current agent with star icon
                    if (agent.id === this.currentAgent) {
                        item.iconPath = new vscode.ThemeIcon('star-full');
                    }
                    
                    return item;
                });
                
                console.log(`🌲 Returning ${items.length} agent items`);
                return Promise.resolve(items);
            } catch (error) {
                console.error('❌ Error getting agents:', error);
                return Promise.resolve([
                    new AgentTreeItem('Error loading agents', vscode.TreeItemCollapsibleState.None, 'error')
                ]);
            }
        }

        return Promise.resolve([]);
    }

    private getAgentIcon(agentId: string): vscode.ThemeIcon {
        const iconMap: { [key: string]: string } = {
            'script_doctor': 'file-text',
            'aaron_sorkin_agent': 'comment-discussion',
            'character_specialist': 'person',
            'creative_visionary': 'lightbulb',
            'coen_brothers_agent': 'smiley',
            'quentin_tarantino_agent': 'film',
            'taylor_sheridan_agent': 'location',
            'jack_carr_agent': 'shield',
            'producer': 'briefcase',
            'director': 'video',
            'continuity_agent': 'checklist',
            'location_scout': 'globe',
            'showrunner': 'crown'
        };
        
        return new vscode.ThemeIcon(iconMap[agentId] || 'person');
    }

    private getAgentFilePath(agentId: string): string {
        // Map agent IDs to their JSON filenames
        const fileMap: { [key: string]: string } = {
            'script_doctor': 'script_doctor.json',
            'aaron_sorkin_agent': 'aaron_sorkin_agent.json',
            'character_specialist': 'character_specialist.json',
            'creative_visionary': 'creative_visionary.json',
            'coen_brothers_agent': 'coen_brothers_agent.json',
            'quentin_tarantino_agent': 'quentin_tarantino_agent.json',
            'taylor_sheridan_agent': 'taylor_sheridan_agent.json',
            'jack_carr_agent': 'jack_carr_agent.json',
            'producer': 'producer.json',
            'director': 'director.json',
            'continuity_agent': 'continuity_agent.json',
            'location_scout': 'location_scout.json',
            'showrunner': 'showrunner.json'
        };
        
        const filename = fileMap[agentId] || `${agentId}.json`;
        return path.join(this.context.extensionPath, 'agents', filename);
    }
}

export class AgentTreeItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly contextValue: string,
        public readonly command?: vscode.Command
    ) {
        super(label, collapsibleState);
        this.tooltip = `${this.label}`;
    }
} 