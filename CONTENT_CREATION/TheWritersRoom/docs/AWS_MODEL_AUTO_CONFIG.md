# AWS Model Auto-Configuration System - Hybrid Approach

## Overview

The Writers Room implements a hybrid "Auto-Max" configuration system that combines the intelligent model selection of Auto mode with the enhanced prompt limits of Max mode. This system automatically selects the optimal AWS model based on task complexity while providing up to 100 prompts per session, with Claude 4.0 Sonnet specifically enabled for dialogue writing challenges.

## Hybrid Auto-Max Configuration

### Core Philosophy
```yaml
Hybrid Approach:
  Auto Intelligence:
    - Smart model selection based on task complexity
    - Cost optimization and performance balancing
    - Real-time model switching for different tasks
  
  Max Capabilities:
    - 100 prompt limit per session
    - Enhanced context window utilization
    - Premium model access for critical tasks
  
  Claude 4.0 Sonnet Priority:
    - Primary choice for dialogue writing
    - Character development and storytelling
    - Creative collaboration tasks
    - Advanced screenplay analysis
```

### Model Selection Strategy

```typescript
class HybridModelSelectionEngine {
  private readonly PROMPT_LIMIT = 100; // Max mode prompt limit
  private readonly CLAUDE_4_SONNET_ID = 'anthropic.claude-4-sonnet-20241022-v1:0';

  async selectOptimalModel(task: TaskRequest): Promise<ModelSelection> {
    const taskAnalysis = await this.taskAnalyzer.analyze(task);
    const userContext = await this.getUserContext(task.userId);
    
    // Hybrid logic: Auto intelligence with Max capabilities
    return this.hybridSelectModel(taskAnalysis, userContext);
  }

  private async hybridSelectModel(analysis: TaskAnalysis, context: UserContext): Promise<ModelSelection> {
    const { complexity, type, urgency } = analysis;
    
    // Priority 1: Dialogue writing gets Claude 4.0 Sonnet
    if (type === TaskType.DIALOGUE_WRITING || 
        type === TaskType.CHARACTER_DEVELOPMENT ||
        type === TaskType.CREATIVE_BRAINSTORMING) {
      return {
        primaryModel: this.CLAUDE_4_SONNET_ID,
        fallbackModel: 'anthropic.claude-3-sonnet-20240229-v1:0',
        reasoning: 'Claude 4.0 Sonnet for advanced dialogue and character development',
        estimatedCost: this.calculateCost(this.CLAUDE_4_SONNET_ID, analysis),
        estimatedLatency: '2-5s',
        promptLimit: this.PROMPT_LIMIT,
        enhancedContext: true
      };
    }

    // Priority 2: Complex creative tasks get Claude 4.0 Sonnet
    if (complexity === TaskComplexity.ADVANCED || 
        type === TaskType.MULTI_AGENT_COLLABORATION ||
        type === TaskType.STORY_STRUCTURE) {
      return {
        primaryModel: this.CLAUDE_4_SONNET_ID,
        fallbackModel: 'anthropic.claude-3-opus-20240229-v1:0',
        reasoning: 'Claude 4.0 Sonnet for complex creative tasks and collaboration',
        estimatedCost: this.calculateCost(this.CLAUDE_4_SONNET_ID, analysis),
        estimatedLatency: '2-5s',
        promptLimit: this.PROMPT_LIMIT,
        enhancedContext: true
      };
    }

    // Priority 3: Speed-optimized for simple, urgent tasks
    if (complexity === TaskComplexity.SIMPLE || urgency === 'high') {
      return {
        primaryModel: 'anthropic.claude-3-haiku-20240307-v1:0',
        fallbackModel: 'amazon.titan-text-express-v1',
        reasoning: 'Speed-optimized for simple/urgent tasks',
        estimatedCost: this.calculateCost('haiku', analysis),
        estimatedLatency: '100-300ms',
        promptLimit: this.PROMPT_LIMIT,
        enhancedContext: false
      };
    }

    // Priority 4: Balanced for moderate complexity
    return {
      primaryModel: 'anthropic.claude-3-sonnet-20240229-v1:0',
      fallbackModel: 'amazon.titan-text-v1',
      reasoning: 'Balanced performance for moderate complexity',
      estimatedCost: this.calculateCost('sonnet', analysis),
      estimatedLatency: '500ms-2s',
      promptLimit: this.PROMPT_LIMIT,
      enhancedContext: true
    };
  }
}
```

### Claude 4.0 Sonnet Specialization

```typescript
class Claude4SonnetSpecialist {
  private readonly MODEL_ID = 'anthropic.claude-4-sonnet-20241022-v1:0';
  private readonly MAX_TOKENS = 200000;
  private readonly PROMPT_LIMIT = 100;

  async processDialogueTask(task: DialogueTaskRequest): Promise<DialogueResponse> {
    const prompt = this.buildDialoguePrompt(task);
    
    const response = await this.callClaude4Sonnet({
      prompt,
      maxTokens: this.MAX_TOKENS,
      temperature: this.getOptimalTemperature(task),
      systemPrompt: this.getDialogueSystemPrompt(task)
    });

    return {
      dialogue: response.content,
      suggestions: this.extractDialogueSuggestions(response),
      characterInsights: this.extractCharacterInsights(response),
      emotionalAnalysis: this.analyzeEmotionalContent(response),
      modelUsed: this.MODEL_ID,
      promptCount: this.incrementPromptCount(task.sessionId)
    };
  }

  private buildDialoguePrompt(task: DialogueTaskRequest): string {
    const { content, context, characterProfiles, sceneDescription } = task;
    
    return `
You are an expert dialogue writer specializing in screenplay dialogue. 

SCENE CONTEXT:
${sceneDescription}

CHARACTER PROFILES:
${this.formatCharacterProfiles(characterProfiles)}

CURRENT DIALOGUE:
${content}

TASK: ${task.specificTask}

Please provide:
1. Enhanced dialogue that feels natural and character-specific
2. Emotional depth and subtext
3. Character voice consistency
4. Pacing and rhythm suggestions
5. Potential dialogue alternatives

Focus on making each character's voice distinct and authentic to their personality and background.
    `;
  }

  private getDialogueSystemPrompt(task: DialogueTaskRequest): string {
    return `You are Claude 4.0 Sonnet, an expert in creative writing and dialogue development. 
    
Your strengths include:
- Natural, character-specific dialogue
- Emotional depth and subtext
- Understanding of human psychology
- Screenplay formatting and structure
- Character voice consistency
- Pacing and dramatic timing

For dialogue tasks, focus on:
- Making each character's voice unique and authentic
- Creating emotional resonance
- Advancing the plot through dialogue
- Maintaining character consistency
- Adding subtext and layers of meaning

Always consider the character's background, personality, and current emotional state when crafting dialogue.`;
  }
}
```

### Session Management with 100 Prompt Limit

```typescript
class SessionManager {
  private sessions = new Map<string, SessionData>();

  async createSession(userId: string): Promise<SessionData> {
    const sessionId = generateSessionId();
    const session: SessionData = {
      sessionId,
      userId,
      promptCount: 0,
      maxPrompts: 100,
      startTime: new Date(),
      modelUsage: new Map(),
      costAccumulated: 0,
      active: true
    };

    this.sessions.set(sessionId, session);
    return session;
  }

  async incrementPromptCount(sessionId: string, modelId: string, cost: number): Promise<SessionData> {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error('Session not found');
    }

    session.promptCount++;
    session.costAccumulated += cost;
    
    // Track model usage
    const modelUsage = session.modelUsage.get(modelId) || 0;
    session.modelUsage.set(modelId, modelUsage + 1);

    // Check if session limit reached
    if (session.promptCount >= session.maxPrompts) {
      session.active = false;
      await this.notifySessionLimitReached(session);
    }

    return session;
  }

  async getSessionStatus(sessionId: string): Promise<SessionStatus> {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error('Session not found');
    }

    return {
      sessionId: session.sessionId,
      promptCount: session.promptCount,
      maxPrompts: session.maxPrompts,
      remainingPrompts: session.maxPrompts - session.promptCount,
      costAccumulated: session.costAccumulated,
      active: session.active,
      modelUsage: Object.fromEntries(session.modelUsage),
      sessionDuration: Date.now() - session.startTime.getTime()
    };
  }
}
```

### User Interface Integration

```typescript
class HybridModeManager {
  private currentMode: 'hybrid-auto-max' = 'hybrid-auto-max';
  private sessionManager: SessionManager;
  private claude4Specialist: Claude4SonnetSpecialist;

  async processTask(task: TaskRequest, sessionId: string): Promise<TaskResponse> {
    // Get session status
    const sessionStatus = await this.sessionManager.getSessionStatus(sessionId);
    
    if (!sessionStatus.active) {
      throw new Error('Session limit reached. Please start a new session.');
    }

    // Select optimal model using hybrid logic
    const modelSelection = await this.hybridSelectModel(task);
    
    // Process with selected model
    let response: TaskResponse;
    
    if (modelSelection.primaryModel === 'anthropic.claude-4-sonnet-20241022-v1:0') {
      // Use Claude 4.0 Sonnet specialist
      response = await this.claude4Specialist.processDialogueTask({
        ...task,
        sessionId
      });
    } else {
      // Use standard processing
      response = await this.processWithStandardModel(task, modelSelection);
    }

    // Update session
    await this.sessionManager.incrementPromptCount(
      sessionId, 
      modelSelection.primaryModel, 
      modelSelection.estimatedCost
    );

    return {
      ...response,
      sessionStatus: await this.sessionManager.getSessionStatus(sessionId),
      modelUsed: modelSelection.primaryModel,
      reasoning: modelSelection.reasoning
    };
  }

  private async updateUI(sessionStatus: SessionStatus, modelSelection: ModelSelection): Promise<void> {
    // Update status bar with hybrid mode info
    const statusBarItem = vscode.window.createStatusBarItem();
    statusBarItem.text = `$(zap) Hybrid Mode | $(brain) ${this.getModelDisplayName(modelSelection.primaryModel)} | $(pulse) ${sessionStatus.remainingPrompts}/100`;
    statusBarItem.tooltip = `Hybrid Auto-Max Mode
Model: ${this.getModelDisplayName(modelSelection.primaryModel)}
Reasoning: ${modelSelection.reasoning}
Remaining Prompts: ${sessionStatus.remainingPrompts}
Session Cost: $${sessionStatus.costAccumulated.toFixed(4)}`;
    statusBarItem.show();

    // Show Claude 4.0 Sonnet indicator for dialogue tasks
    if (modelSelection.primaryModel === 'anthropic.claude-4-sonnet-20241022-v1:0') {
      vscode.window.showInformationMessage(
        `Using Claude 4.0 Sonnet for enhanced dialogue writing - ${sessionStatus.remainingPrompts} prompts remaining`
      );
    }
  }
}
```

### Configuration Examples

```yaml
Hybrid Auto-Max Configuration:
  Mode: hybrid-auto-max
  Prompt Limit: 100 per session
  Enhanced Context: Enabled for all models
  
  Model Selection Priority:
    1. Claude 4.0 Sonnet:
       - Dialogue writing tasks
       - Character development
       - Creative brainstorming
       - Multi-agent collaboration
       - Complex storytelling
    
    2. Claude 3.5 Haiku:
       - Real-time suggestions
       - Basic formatting
       - Simple tasks
       - High urgency tasks
    
    3. Claude 3.5 Sonnet:
       - General writing
       - Plot analysis
       - Moderate complexity tasks
       - Balanced performance needs
  
  Claude 4.0 Sonnet Features:
    - Enhanced dialogue understanding
    - Character voice consistency
    - Emotional depth analysis
    - Subtext recognition
    - Advanced storytelling capabilities
    - Multi-character interaction handling
  
  Session Management:
    - 100 prompts per session
    - Cost tracking and limits
    - Model usage analytics
    - Session extension options
    - Automatic session cleanup
```

## Conclusion

The Hybrid Auto-Max configuration provides the best of both worlds:

1. **Intelligent Model Selection**: Automatically chooses the optimal model for each task
2. **Enhanced Capabilities**: 100 prompt limit with premium model access
3. **Claude 4.0 Sonnet Priority**: Specifically enabled for dialogue writing and creative tasks
4. **Cost Optimization**: Balances quality with cost efficiency
5. **Session Management**: Tracks usage and provides clear feedback

This approach ensures that users get the enhanced capabilities they need for creative writing while maintaining cost efficiency and intelligent model selection. Claude 4.0 Sonnet is specifically prioritized for the most important dialogue writing challenges, providing superior creative capabilities when they matter most.
