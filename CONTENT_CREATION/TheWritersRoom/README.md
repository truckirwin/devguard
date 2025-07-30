# The Writers Room - AI-Powered Creative Writing IDE

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](./package.json)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)
[![VS Code](https://img.shields.io/badge/VS%20Code-1.95+-purple.svg)](https://code.visualstudio.com/)

> **A Cursor-like IDE experience for creative writers with AI-powered collaboration featuring multiple specialized writing agents**

## 🎬 Overview

The Writers Room transforms your VS Code environment into a sophisticated creative writing studio. Collaborate with specialized AI agents including Aaron Sorkin for dialogue, Character Specialists for development, and Creative Visionaries for big-picture storytelling. Built on AWS Bedrock with Claude 4.0 Sonnet for the highest quality creative assistance.

### ✨ Key Features

- **🤖 Multiple AI Writing Agents**: Aaron Sorkin, Coen Brothers, Character Specialist, and more
- **⚡ Hybrid Auto-Max AI**: Intelligent model selection with 100 prompts per session
- **🎯 Claude 4.0 Sonnet Priority**: Advanced dialogue and character development
- **📝 Project Management**: Screenplay, novel, and story project templates
- **🔄 Real-time Assistance**: Instant feedback on dialogue, characters, and scenes
- **🛡️ Security-First**: AWS Well-Architected with enterprise-grade security
- **📊 Session Management**: Cost tracking and usage analytics

## 🚀 Quick Start

### Installation

1. **Install from VS Code Marketplace** (coming soon)
   ```bash
   code --install-extension thewritersroom.the-writers-room
   ```

2. **Or install from VSIX**
   ```bash
   code --install-extension the-writers-room-1.0.0.vsix
   ```

### Setup

1. **Configure AI Provider**
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Run `Writers Room: Configure AI Keys`
   - Choose your preferred provider:
     - **AWS Bedrock** (Recommended) - Best quality with Claude 4.0 Sonnet
     - **Anthropic** - Direct API access
     - **OpenAI** - GPT-4 support

2. **Start Writing**
   - Press `Cmd+Shift+A` to open AI chat
   - Or run `Writers Room: Create New Writing Project`

## 🎭 AI Writing Agents

### 🎬 Script Doctor
*Professional script consultant and story expert*
- Narrative structure analysis
- Pacing and flow optimization
- Story logic validation
- Industry best practices

### ✍️ Aaron Sorkin
*Master of sharp, witty dialogue*
- Rapid-fire conversations
- Character-driven storytelling
- Walk-and-talk scenes
- Intelligent character voices

### 👥 Character Specialist
*Deep character development expert*
- Three-dimensional character creation
- Personality consistency
- Character arc development
- Motivation and conflict analysis

### 🎨 Creative Visionary
*Big picture storytelling and artistic vision*
- High-concept ideation
- Thematic development
- Genre exploration
- Creative problem solving

### 🎭 Coen Brothers
*Quirky, darkly comic storytelling*
- Eccentric character voices
- Regional dialects
- Dark humor and irony
- Unique narrative perspectives

### 🎪 Quentin Tarantino
*Bold, stylized storytelling*
- Non-linear narratives
- Pop culture references
- Distinctive dialogue style
- Genre-blending approaches

### 🏔️ Taylor Sheridan
*Character-driven stories with authentic sense of place*
- Authentic dialogue
- Strong sense of location
- Character-driven plots
- Realistic relationships

### ⚔️ Jack Carr
*Military and thriller expertise*
- Tactical authenticity
- Procedural accuracy
- Action sequences
- Military/law enforcement details

## 🛠️ Core Features

### Project Management

Create structured writing projects with templates:

```bash
# Create new project
Cmd+Shift+N → Writers Room: Create New Writing Project

# Project types:
- 🎬 Screenplay (Fountain format)
- 📖 Novel (Markdown chapters)
- 📝 Short Story
- 🎭 Stage Play
```

### Writing Enhancement

Improve your writing with AI assistance:

```bash
# Improve selected text
Select text → Right-click → Writers Room: Improve Dialogue
Select text → Right-click → Writers Room: Develop Character
Select text → Right-click → Writers Room: Enhance Scene

# Document analysis
Cmd+Shift+P → Writers Room: Analyze Script
```

### AI Chat Interface

Direct conversation with AI agents:

```bash
# Open AI chat
Cmd+Shift+A

# Chat with specific agent
Cmd+Shift+P → Writers Room: Select AI Agent

# Example prompts:
"Help me write a tense confrontation between two former friends"
"Develop a character who's hiding a secret"
"What's a good plot twist for a mystery story?"
```

## 🧠 Hybrid Auto-Max AI System

### Intelligent Model Selection

The system automatically selects the optimal AI model based on your task:

- **Claude 4.0 Sonnet**: Dialogue writing, character development, creative brainstorming
- **Claude 3.5 Haiku**: Quick suggestions, simple tasks, high urgency
- **Claude 3.5 Sonnet**: General writing, moderate complexity tasks

### Session Management

- **100 prompts per session** (Max mode capability)
- **Cost tracking** with real-time estimates
- **Model usage analytics** 
- **Session status** in status bar

### Example Usage

```typescript
// The system analyzes your request
"Write dialogue between a detective and suspect"

// Analysis results:
Task Type: DIALOGUE_WRITING
Complexity: MODERATE
Agent: aaron-sorkin

// Model selection:
Primary Model: Claude 4.0 Sonnet
Reasoning: "Claude 4.0 Sonnet for advanced dialogue and character development"
Estimated Latency: 2-5s
```

## 📋 Commands Reference

### Core Commands

| Command | Shortcut | Description |
|---------|----------|-------------|
| `Writers Room: Open AI Chat` | `Cmd+Shift+A` | Start conversation with AI |
| `Writers Room: Create Project` | `Cmd+Shift+N` | Create new writing project |
| `Writers Room: Select Agent` | - | Choose AI writing agent |
| `Writers Room: Configure AI` | - | Set up API keys |

### Writing Commands

| Command | Description |
|---------|-------------|
| `Writers Room: Improve Dialogue` | Enhance selected dialogue |
| `Writers Room: Develop Character` | Expand character description |
| `Writers Room: Analyze Script` | Get feedback on entire document |
| `Writers Room: Brainstorm Ideas` | Generate creative ideas |

### Project Commands

| Command | Description |
|---------|-------------|
| `Writers Room: New Scene` | Insert scene heading |
| `Writers Room: New Character` | Create character template |

### Session Commands

| Command | Description |
|---------|-------------|
| `Writers Room: Show Session Status` | View prompt usage and cost |
| `Writers Room: Clear Conversation` | Start new session |
| `Writers Room: Test AI Connection` | Verify API connectivity |

## ⚙️ Configuration

### AI Provider Settings

Configure in VS Code Settings (`Cmd+,`):

```json
{
  "theWritersRoom.aiProvider": "aws-bedrock",
  "theWritersRoom.defaultAgent": "aaron-sorkin",
  "theWritersRoom.autoSave": true,
  "theWritersRoom.theme": "auto"
}
```

### AWS Bedrock Setup (Recommended)

1. **Create AWS Account** and enable Bedrock
2. **Request Model Access** for Claude models
3. **Create IAM User** with Bedrock permissions
4. **Configure in Extension**:
   - Access Key ID
   - Secret Access Key
   - Region (us-east-1 recommended)

### Anthropic Setup

1. **Get API Key** from [Anthropic Console](https://console.anthropic.com/)
2. **Configure in Extension** with your API key

### OpenAI Setup

1. **Get API Key** from [OpenAI Platform](https://platform.openai.com/)
2. **Configure in Extension** with your API key

## 🧪 Testing

### Run Core Tests

```bash
# Compile TypeScript
npm run compile

# Run core functionality tests
node test-core.js

# Run full test suite (requires VS Code)
npm test
```

### Test Coverage

Our comprehensive testing includes:

- ✅ **Unit Tests**: AIService, ConfigManager, TestUtils (90%+ coverage)
- ✅ **Integration Tests**: API endpoints, AWS services
- ✅ **Performance Tests**: Load testing, response times
- ✅ **Security Tests**: Input validation, error handling

## 🏗️ Architecture

### Technology Stack

- **Frontend**: TypeScript, VS Code Extension API
- **AI Services**: AWS Bedrock, Anthropic, OpenAI
- **Testing**: Mocha, Custom test framework
- **Build**: TypeScript compiler, npm scripts

### Key Components

```
src/
├── extension.ts           # Main extension entry point
├── services/
│   ├── AIService.ts      # Hybrid AI service with model selection
│   └── ConfigManager.ts  # Configuration and API key management
└── test/
    ├── basic.test.ts     # Comprehensive unit tests
    └── suite/index.ts    # Test framework and utilities
```

### AWS Well-Architected

Built following AWS Well-Architected Framework:

- **Security**: Encryption, IAM, least privilege
- **Reliability**: Multi-region, error handling
- **Performance**: Caching, model optimization
- **Cost Optimization**: Serverless, pay-per-use
- **Operational Excellence**: Monitoring, logging

## 🚦 Status Bar

The status bar shows real-time information:

```
$(zap) Writers Room | $(pulse) 87/100
```

- **Lightning bolt**: Extension active
- **Pulse**: Remaining prompts in session
- **Click**: Open AI chat

## 📊 Session Analytics

Track your AI usage:

```bash
Session Status:
• Prompts used: 13/100
• Remaining: 87
• Estimated cost: $0.0156
• Session ID: session_1751513320806_jqg65uz2z
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/thewritersroom/the-writers-room.git
cd the-writers-room

# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Run tests
npm test

# Package extension
npm run package
```

### Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- **Documentation**: [GitHub Wiki](https://github.com/thewritersroom/the-writers-room/wiki)
- **Issues**: [GitHub Issues](https://github.com/thewritersroom/the-writers-room/issues)
- **Discussions**: [GitHub Discussions](https://github.com/thewritersroom/the-writers-room/discussions)

## 🎯 Roadmap

### Version 1.1 (Coming Soon)
- [ ] Real-time collaboration with other writers
- [ ] Advanced screenplay formatting
- [ ] Export to PDF, Final Draft, and other formats
- [ ] Custom agent creation
- [ ] Voice-to-text integration

### Version 1.2 (Future)
- [ ] Web-based editor
- [ ] Mobile companion app
- [ ] Industry database integration
- [ ] Advanced analytics and insights

---

**Made with ❤️ for writers by writers**

*Transform your creative process with AI-powered collaboration. Start writing your next masterpiece today.* 