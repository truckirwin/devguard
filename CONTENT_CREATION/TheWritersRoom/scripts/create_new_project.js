#!/usr/bin/env node

/**
 * The Writers Room - New Project Creation Script
 * Creates structured creative writing projects with appropriate templates
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

// Project type definitions
const PROJECT_TYPES = {
  screenplay: {
    name: 'Screenplay',
    description: 'Movie, TV series, or other visual media scripts',
    subtypes: ['Movie', 'Broadcast Series', 'Streaming Series', 'Web Series', 'Short Film', 'Documentary'],
    structure: 'screenplay'
  },
  novel: {
    name: 'Novel',
    description: 'Long-form fiction or non-fiction books',
    subtypes: ['Fiction', 'Non-Fiction', 'Memoir', 'Young Adult', 'Children\'s Book'],
    structure: 'novel'
  },
  stageplay: {
    name: 'Stage Play',
    description: 'Theater scripts and plays',
    subtypes: ['Drama', 'Comedy', 'Musical', 'One-Act', 'Full-Length'],
    structure: 'stageplay'
  },
  podcast: {
    name: 'Podcast Script',
    description: 'Audio content and podcast episodes',
    subtypes: ['Interview', 'Narrative', 'Educational', 'Entertainment'],
    structure: 'podcast'
  }
};

// Genre definitions
const GENRES = {
  screenplay: [
    'Action/Adventure', 'Comedy', 'Drama', 'Horror/Thriller', 'Sci-Fi/Fantasy',
    'Romance', 'Western', 'Documentary', 'Animation', 'Historical',
    'War', 'Musical', 'Family', 'Crime/Mystery', 'Superhero', 'Biographical'
  ],
  novel: [
    'Literary Fiction', 'Commercial Fiction', 'Mystery/Thriller', 'Romance',
    'Science Fiction', 'Fantasy', 'Historical Fiction', 'Young Adult',
    'Children\'s', 'Non-Fiction', 'Memoir', 'Biography', 'Self-Help'
  ]
};

// Project structure templates
const PROJECT_STRUCTURES = {
  screenplay: {
    folders: [
      'Scripts/Drafts',
      'Scenes/Individual_Scenes',
      'Scenes/Outline',
      'Characters',
      'Settings/Concept_Art',
      'Worldbuilding/Maps',
      'Research/General',
      'Research/Specific_Topics',
      'Development/Pitch_Deck',
      'Snippets/TextExpander',
      'Snippets/VS_Code',
      'Snippets/Atom'
    ],
    files: [
      'Scripts/01_first_draft.md',
      'Scripts/02_revisions.md',
      'Scripts/03_final_draft.md',
      'Scenes/Outline/01_act_one.md',
      'Scenes/Outline/02_act_two.md',
      'Scenes/Outline/03_act_three.md',
      'Scenes/Individual_Scenes/README.md',
      'Characters/01_main_characters.md',
      'Characters/02_supporting_characters.md',
      'Characters/03_character_arcs.md',
      'Characters/04_relationships.md',
      'Settings/01_locations.md',
      'Settings/02_environment.md',
      'Worldbuilding/01_history.md',
      'Worldbuilding/02_culture.md',
      'Worldbuilding/03_rules.md',
      'Research/01_bibliography.md',
      'Research/02_interviews.md',
      'Research/03_reference_images.md',
      'Development/01_treatment.md',
      'Development/02_logline.md',
      'Development/03_pitch.md'
    ]
  },
  novel: {
    folders: [
      'Manuscript/Drafts',
      'Chapters',
      'Characters',
      'Worldbuilding',
      'Research',
      'Development',
      'Snippets/VS_Code',
      'Snippets/TextExpander'
    ],
    files: [
      'Manuscript/01_first_draft.md',
      'Manuscript/02_revisions.md',
      'Manuscript/03_final_draft.md',
      'Chapters/01_chapter_one.md',
      'Chapters/02_chapter_two.md',
      'Chapters/chapter_outline.md',
      'Characters/01_main_characters.md',
      'Characters/02_supporting_characters.md',
      'Characters/03_character_arcs.md',
      'Characters/04_relationships.md',
      'Worldbuilding/01_setting.md',
      'Worldbuilding/02_history.md',
      'Worldbuilding/03_culture.md',
      'Worldbuilding/04_magic_system.md',
      'Research/01_bibliography.md',
      'Research/02_reference_notes.md',
      'Research/03_inspiration.md',
      'Development/01_synopsis.md',
      'Development/02_query_letter.md',
      'Development/03_author_bio.md'
    ]
  }
};

// Template content generators
const TEMPLATES = {
  readme: (projectName, projectType, genre, subtype) => `# ${projectName} - ${projectType.name}

## Project Overview
- **Type**: ${projectType.name}
- **Subtype**: ${subtype}
- **Genre**: ${genre}
- **Created**: ${new Date().toLocaleDateString()}
- **Last Updated**: ${new Date().toLocaleDateString()}

## Project Structure
This project follows the standard ${(projectType.name || 'project').toLowerCase()} structure with organized folders for:
- **Scripts/Manuscript**: All drafts and versions
- **Scenes/Chapters**: Organized content structure
- **Characters**: Character development and profiles
- **Settings/Worldbuilding**: Locations and background
- **Research**: Reference materials and notes
- **Development**: Pitch and development materials
- **Snippets**: Text expansion snippets for various editors

## Getting Started
1. Review the README files in each directory
2. Start with the Development folder to outline your story
3. Use the Characters folder to develop your characters
4. Build your world in the Worldbuilding folder
5. Write scenes/chapters in the appropriate folders
6. Assemble your final work in the main Scripts/Manuscript folder

## AI Agent Integration
This project is configured to work with The Writers Room AI agents:
- Script Doctor (Structure and pacing)
- Character Specialist (Character development)
- Creative Visionary (Big picture ideas)
- Market Analyst (Industry insights)

## Version Control
This project uses Git for version control. Make regular commits to track your changes.

## Export Options
- PDF (Final Draft format)
- FDX (Final Draft XML)
- Fountain (Plain text screenplay format)
- Markdown (For documentation)
`,

  gitignore: `# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Editor files
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
*.log
*.tmp
*.bak

# Media files
*.pdf
*.doc
*.docx
*.xls
*.xlsx
*.jpg
*.jpeg
*.png
*.gif
*.mp4
*.mov
*.wav
*.mp3

# Backup files
*.backup
*.old
`,

  vscodeSettings: `{
  "files.associations": {
    "*.md": "markdown",
    "*.fdx": "xml"
  },
  "markdown.preview.fontSize": 14,
  "markdown.preview.lineHeight": 1.6,
  "editor.wordWrap": "on",
  "editor.lineNumbers": "on",
  "editor.minimap.enabled": false,
  "workbench.colorTheme": "Default Dark+",
  "files.autoSave": "afterDelay",
  "files.autoSaveDelay": 1000
}`,

  vscodeExtensions: `{
  "recommendations": [
    "yzhang.markdown-all-in-one",
    "shd101wyy.markdown-preview-enhanced",
    "davidanson.vscode-markdownlint",
    "ms-vscode.wordcount",
    "streetsidesoftware.code-spell-checker"
  ]
}`
};

// Utility functions
function sanitizeProjectName(name) {
  return name.replace(/[^a-zA-Z0-9\s-_]/g, '').replace(/\s+/g, '_');
}

function createDirectory(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
    console.log(`✓ Created directory: ${dirPath}`);
  }
}

function createFile(filePath, content = '') {
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  
  if (!fs.existsSync(filePath)) {
    fs.writeFileSync(filePath, content);
    console.log(`✓ Created file: ${filePath}`);
  }
}

function initializeGit(projectPath) {
  const gitPath = path.join(projectPath, '.git');
  if (!fs.existsSync(gitPath)) {
    // Note: In a real implementation, you'd use a Git library or spawn git commands
    console.log(`✓ Git repository initialized (manual step required)`);
  }
}

// Main project creation function
async function createProject(projectName, projectType, subtype, genre, projectPath) {
  const sanitizedName = sanitizeProjectName(projectName);
  
  // If no projectPath provided, use current working directory (for CLI usage)
  if (!projectPath) {
    projectPath = path.join(process.cwd(), sanitizedName);
  }
  
  console.log(`\n🚀 Creating new ${projectType.name} project: ${projectName}`);
  console.log(`📍 Location: ${projectPath}\n`);
  
  // Create main project directory
  createDirectory(projectPath);
  
  // Create .vscode directory and settings
  const vscodePath = path.join(projectPath, '.vscode');
  createDirectory(vscodePath);
  createFile(path.join(vscodePath, 'settings.json'), TEMPLATES.vscodeSettings);
  createFile(path.join(vscodePath, 'extensions.json'), TEMPLATES.vscodeExtensions);
  
  // Create project structure based on type
  const structure = PROJECT_STRUCTURES[projectType.structure];
  if (structure) {
    // Create folders
    structure.folders.forEach(folder => {
      createDirectory(path.join(projectPath, folder));
    });
    
    // Create files
    structure.files.forEach(file => {
      createFile(path.join(projectPath, file));
    });
  }
  
  // Create README.md
  const readmeContent = TEMPLATES.readme(projectName, projectType, genre, subtype);
  createFile(path.join(projectPath, 'README.md'), readmeContent);
  
  // Create .gitignore
  createFile(path.join(projectPath, '.gitignore'), TEMPLATES.gitignore);
  
  // Initialize Git (placeholder)
  initializeGit(projectPath);
  
  console.log(`\n✅ Project "${projectName}" created successfully!`);
  console.log(`📁 Navigate to: ${projectPath}`);
  console.log(`🔧 Open in The Writers Room to begin writing!\n`);
}

// Interactive CLI
async function interactiveSetup() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  
  const question = (query) => new Promise((resolve) => rl.question(query, resolve));
  
  try {
    console.log('🎬 The Writers Room - New Project Creator\n');
    
    // Get project name
    const projectName = await question('Enter your project name: ');
    if (!projectName.trim()) {
      console.log('❌ Project name is required');
      return;
    }
    
    // Show project types
    console.log('\n📝 Available project types:');
    Object.entries(PROJECT_TYPES).forEach(([key, type], index) => {
      console.log(`${index + 1}. ${type.name} - ${type.description}`);
    });
    
    const typeChoice = await question('\nSelect project type (1-4): ');
    const typeKeys = Object.keys(PROJECT_TYPES);
    const selectedTypeKey = typeKeys[parseInt(typeChoice) - 1];
    
    if (!selectedTypeKey || !PROJECT_TYPES[selectedTypeKey]) {
      console.log('❌ Invalid project type selection');
      return;
    }
    
    const projectType = PROJECT_TYPES[selectedTypeKey];
    
    // Show subtypes
    console.log(`\n📋 Available ${projectType.name} subtypes:`);
    projectType.subtypes.forEach((subtype, index) => {
      console.log(`${index + 1}. ${subtype}`);
    });
    
    const subtypeChoice = await question(`\nSelect ${projectType.name.toLowerCase()} subtype (1-${projectType.subtypes.length}): `);
    const selectedSubtype = projectType.subtypes[parseInt(subtypeChoice) - 1];
    
    if (!selectedSubtype) {
      console.log('❌ Invalid subtype selection');
      return;
    }
    
    // Show genres
    const availableGenres = GENRES[selectedTypeKey] || [];
    if (availableGenres.length > 0) {
      console.log(`\n🎭 Available genres:`);
      availableGenres.forEach((genre, index) => {
        console.log(`${index + 1}. ${genre}`);
      });
      
      const genreChoice = await question(`\nSelect genre (1-${availableGenres.length}): `);
      const selectedGenre = availableGenres[parseInt(genreChoice) - 1];
      
      if (!selectedGenre) {
        console.log('❌ Invalid genre selection');
        return;
      }
      
              // Create the project
        await createProject(projectName, projectType, selectedSubtype, selectedGenre);
      } else {
        // Create the project without genre
        await createProject(projectName, projectType, selectedSubtype, 'General');
    }
    
  } catch (error) {
    console.error('❌ Error creating project:', error.message);
  } finally {
    rl.close();
  }
}

// Command line interface
function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    // Interactive mode
    interactiveSetup();
  } else if (args.length >= 3) {
    // Command line mode: node create_new_project.js <name> <type> <subtype> [genre]
    const [projectName, typeKey, subtype, genre = 'General'] = args;
    
    const projectType = PROJECT_TYPES[typeKey];
    if (!projectType) {
      console.error('❌ Invalid project type. Available types:', Object.keys(PROJECT_TYPES).join(', '));
      process.exit(1);
    }
    
    if (!projectType.subtypes.includes(subtype)) {
      console.error('❌ Invalid subtype. Available subtypes:', projectType.subtypes.join(', '));
      process.exit(1);
    }
    
    createProject(projectName, projectType, subtype, genre);
  } else {
    console.log('Usage:');
    console.log('  Interactive mode: node create_new_project.js');
    console.log('  Command line: node create_new_project.js <name> <type> <subtype> [genre]');
    console.log('\nAvailable types:', Object.keys(PROJECT_TYPES).join(', '));
  }
}

// Run the script
if (require.main === module) {
  main();
}

module.exports = {
  createProject,
  PROJECT_TYPES,
  GENRES,
  PROJECT_STRUCTURES,
  TEMPLATES
}; 