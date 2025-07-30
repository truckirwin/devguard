import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';

export interface Agent {
    id: string;
    name: string;
    title: string;
    description?: string;
    personality?: any;
    expertise?: any;
    communication?: any;
    relationships?: any;
    available: boolean;
    lastUsed?: Date;
}

export class AgentManager {
    private agents: Map<string, Agent> = new Map();
    private context: vscode.ExtensionContext;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.loadAgents();
    }

    private loadAgents() {
        const agentsPath = path.join(this.context.extensionPath, 'agents');
        
        if (!fs.existsSync(agentsPath)) {
            console.error('Agents directory not found:', agentsPath);
            return;
        }

        const agentFiles = fs.readdirSync(agentsPath).filter(file => file.endsWith('.json'));
        
        for (const file of agentFiles) {
            try {
                const agentData = JSON.parse(fs.readFileSync(path.join(agentsPath, file), 'utf8'));
                
                const agent: Agent = {
                    id: agentData.agent_id || agentData.id,
                    name: agentData.name,
                    title: agentData.title,
                    description: agentData.description || `${agentData.title} specialist`,
                    personality: agentData.personality,
                    expertise: agentData.expertise,
                    communication: agentData.communication,
                    relationships: agentData.relationships,
                    available: true,
                    lastUsed: undefined
                };
                
                this.agents.set(agent.id, agent);
                console.log(`Loaded agent: ${agent.name} (${agent.title})`);
            } catch (error) {
                console.error(`Error loading agent ${file}:`, error);
            }
        }

        console.log(`AgentManager loaded ${this.agents.size} agents`);
    }

    public getAgent(agentId: string): Agent | undefined {
        return this.agents.get(agentId);
    }

    public getAllAgents(): Agent[] {
        return Array.from(this.agents.values());
    }

    public getAvailableAgents(): Agent[] {
        return Array.from(this.agents.values()).filter(agent => agent.available);
    }

    public getAgentName(agentId: string): string {
        const agent = this.agents.get(agentId);
        return agent ? agent.name : agentId;
    }

    public getAgentTitle(agentId: string): string {
        const agent = this.agents.get(agentId);
        return agent ? agent.title : 'Unknown Agent';
    }

    public updateLastUsed(agentId: string) {
        const agent = this.agents.get(agentId);
        if (agent) {
            agent.lastUsed = new Date();
        }
    }

    public setAgentAvailability(agentId: string, available: boolean) {
        const agent = this.agents.get(agentId);
        if (agent) {
            agent.available = available;
        }
    }

    public getAgentsBySpecialty(specialty: string): Agent[] {
        return Array.from(this.agents.values()).filter(agent => 
            agent.title.toLowerCase().includes(specialty.toLowerCase()) ||
            (agent.expertise?.specialties && agent.expertise.specialties.some((s: string) => 
                s.toLowerCase().includes(specialty.toLowerCase())
            ))
        );
    }

    public getRecommendedAgents(task: string): Agent[] {
        const taskLower = task.toLowerCase();
        const recommended: Agent[] = [];

        // Define task-to-agent mappings
        const taskMappings = {
            'dialogue': ['character_specialist', 'aaron_sorkin_agent'],
            'character': ['character_specialist', 'script_doctor'],
            'structure': ['script_doctor', 'showrunner'],
            'story': ['script_doctor', 'showrunner', 'creative_visionary'],
            'location': ['location_scout', 'director'],
            'budget': ['producer', 'location_scout'],
            'visual': ['director', 'creative_visionary'],
            'continuity': ['continuity_agent', 'script_doctor'],
            'action': ['jack_carr_agent', 'director'],
            'western': ['taylor_sheridan_agent', 'character_specialist'],
            'comedy': ['coen_brothers_agent', 'creative_visionary'],
            'thriller': ['jack_carr_agent', 'script_doctor'],
            'genre': ['quentin_tarantino_agent', 'coen_brothers_agent', 'creative_visionary']
        };

        // Find matching agents based on task keywords
        for (const [keyword, agentIds] of Object.entries(taskMappings)) {
            if (taskLower.includes(keyword)) {
                for (const agentId of agentIds) {
                    const agent = this.agents.get(agentId);
                    if (agent && agent.available && !recommended.find(a => a.id === agent.id)) {
                        recommended.push(agent);
                    }
                }
            }
        }

        // If no specific matches, return some default agents
        if (recommended.length === 0) {
            const defaultAgents = ['script_doctor', 'character_specialist', 'creative_visionary'];
            for (const agentId of defaultAgents) {
                const agent = this.agents.get(agentId);
                if (agent && agent.available) {
                    recommended.push(agent);
                }
            }
        }

        return recommended.slice(0, 5); // Limit to 5 recommendations
    }

    public getAgentsForMultiChat(): Agent[] {
        // Return agents suitable for multi-agent discussions
        const multiChatAgents = [
            'script_doctor',
            'character_specialist', 
            'creative_visionary',
            'producer',
            'director',
            'continuity_agent',
            'location_scout',
            'showrunner',
            'aaron_sorkin_agent',
            'coen_brothers_agent',
            'quentin_tarantino_agent',
            'taylor_sheridan_agent',
            'jack_carr_agent'
        ];

        return multiChatAgents
            .map(id => this.agents.get(id))
            .filter((agent): agent is Agent => agent !== undefined && agent.available);
    }

    public reloadAgents() {
        this.agents.clear();
        this.loadAgents();
    }
} 