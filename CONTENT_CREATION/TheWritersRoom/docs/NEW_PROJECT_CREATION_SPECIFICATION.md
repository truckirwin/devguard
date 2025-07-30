# New Project Creation Specification

## The Writers Room - Desktop Application

---

## Executive Summary

This document defines the "New Project" creation functionality for The Writers Room desktop application, enabling users to create structured creative writing projects with appropriate templates, folders, and documentation based on project type and genre.

---

## 1. Project Types & Categories

### 1.1 Primary Project Types

```yaml
Project Types:
  Screenplay:
    - Movie (Feature Film)
    - Broadcast Series (Network TV)
    - Streaming Series (Netflix, Hulu, etc.)
    - Web Series
    - Short Film
    - Documentary
  
  Novel:
    - Fiction (Various genres)
    - Non-Fiction
    - Memoir
    - Young Adult
    - Children's Book
  
  Other Creative Writing:
    - Stage Play
    - Radio Drama
    - Podcast Script
    - Graphic Novel
    - Video Game Script
    - Commercial/Advertising
```

### 1.2 Genre-Specific Templates

```yaml
Screenplay Genres:
  - Action/Adventure
  - Comedy
  - Drama
  - Horror/Thriller
  - Sci-Fi/Fantasy
  - Romance
  - Western
  - Documentary
  - Animation
  - Historical
  - War
  - Musical
  - Family
  - Crime/Mystery
  - Superhero
  - Biographical
```

---

## 2. Project Creation Flow

### 2.1 Launch Screen Options

When users click "Create New Project", they see:

1. **Project Type Selection**
   - Large, visual cards for each project type
   - Icons and descriptions for each type
   - "Custom" option for advanced users

2. **Project Details Form**
   - Project name
   - Genre selection (based on project type)
   - Target audience/market
   - Estimated length/duration
   - Collaboration settings

3. **Template Selection**
   - Industry-standard templates
   - Custom templates
   - Blank template option

### 2.2 AI-Guided Setup

```yaml
AI Assistant Integration:
  Project Setup:
    - Suggest genre-appropriate templates
    - Recommend project structure based on type
    - Provide industry insights and best practices
  
  Character Development:
    - Suggest character archetypes for genre
    - Help with character relationships
    - Provide character development prompts
  
  Worldbuilding:
    - Genre-specific worldbuilding questions
    - Research suggestions
    - Setting development guidance
```

---

## 3. Project Structure Templates

### 3.1 Screenplay Project Structure

Based on the existing SCREENTIME structure:

```
PROJECT_NAME/
├── README.md                    # Project overview and guidelines
├── .gitignore                   # Version control exclusions
├── .vscode/                     # VS Code settings and extensions
├── Scripts/                     # All script drafts and versions
│   ├── Drafts/                  # Working drafts
│   ├── 01_first_draft.md        # First draft
│   ├── 02_revisions.md          # Revision notes
│   └── 03_final_draft.md        # Final draft
├── Scenes/                      # Scene organization
│   ├── Individual_Scenes/       # Individual scene files
│   └── Outline/                 # Act structure
│       ├── 01_act_one.md
│       ├── 02_act_two.md
│       └── 03_act_three.md
├── Characters/                  # Character development
│   ├── 01_main_characters.md
│   ├── 02_supporting_characters.md
│   ├── 03_character_arcs.md
│   └── 04_relationships.md
├── Settings/                    # Locations and environment
│   ├── Concept_Art/            # Visual references
│   ├── 01_locations.md
│   └── 02_environment.md
├── Worldbuilding/              # Background and rules
│   ├── Maps/                   # Visual maps and diagrams
│   ├── 01_history.md
│   ├── 02_culture.md
│   └── 03_rules.md
├── Research/                   # Reference materials
│   ├── General/               # General research
│   ├── Specific_Topics/       # Topic-specific research
│   ├── 01_bibliography.md
│   ├── 02_interviews.md
│   └── 03_reference_images.md
├── Development/               # Pitch and development materials
│   ├── Pitch_Deck/           # Presentation materials
│   ├── 01_treatment.md
│   ├── 02_logline.md
│   └── 03_pitch.md
└── Snippets/                  # Text expansion snippets
    ├── TextExpander/
    ├── VS_Code/
    └── Atom/
```

### 3.2 Novel Project Structure

```
PROJECT_NAME/
├── README.md
├── .gitignore
├── .vscode/
├── Manuscript/                # Main manuscript files
│   ├── Drafts/
│   ├── 01_first_draft.md
│   ├── 02_revisions.md
│   └── 03_final_draft.md
├── Chapters/                  # Individual chapter files
│   ├── 01_chapter_one.md
│   ├── 02_chapter_two.md
│   └── chapter_outline.md
├── Characters/               # Character development
│   ├── 01_main_characters.md
│   ├── 02_supporting_characters.md
│   ├── 03_character_arcs.md
│   └── 04_relationships.md
├── Worldbuilding/           # Setting and background
│   ├── 01_setting.md
│   ├── 02_history.md
│   ├── 03_culture.md
│   └── 04_magic_system.md
├── Research/                # Reference materials
│   ├── 01_bibliography.md
│   ├── 02_reference_notes.md
│   └── 03_inspiration.md
├── Development/             # Publishing materials
│   ├── 01_synopsis.md
│   ├── 02_query_letter.md
│   └── 03_author_bio.md
└── Snippets/               # Writing snippets
    ├── VS_Code/
    └── TextExpander/
```

### 3.3 Series Project Structure (TV/Streaming)

```
PROJECT_NAME/
├── README.md
├── .gitignore
├── .vscode/
├── Series_Bible/            # Series overview and rules
│   ├── 01_series_overview.md
│   ├── 02_character_bible.md
│   ├── 03_world_bible.md
│   └── 04_episode_guide.md
├── Episodes/                # Individual episode scripts
│   ├── Season_01/
│   │   ├── 01_pilot.md
│   │   ├── 02_episode_02.md
│   │   └── episode_outline.md
│   └── Season_02/
├── Characters/              # Character development
│   ├── 01_series_regulars.md
│   ├── 02_recurring_characters.md
│   ├── 03_guest_characters.md
│   └── 04_character_arcs.md
├── Settings/                # Locations and sets
│   ├── 01_primary_locations.md
│   ├── 02_recurring_locations.md
│   └── 03_set_designs.md
├── Development/             # Pitch materials
│   ├── 01_series_pitch.md
│   ├── 02_pilot_script.md
│   └── 03_show_bible.md
└── Snippets/               # TV writing snippets
    ├── VS_Code/
    └── TextExpander/
```

---

## 4. Template Content

### 4.1 README.md Template

```markdown
# [PROJECT_NAME] - [PROJECT_TYPE]

## Project Overview
- **Type**: [Screenplay/Novel/Series/etc.]
- **Genre**: [Genre]
- **Target Audience**: [Audience]
- **Estimated Length**: [Length/Duration]
- **Created**: [Date]
- **Last Updated**: [Date]

## Project Structure
[Description of folder structure and purpose]

## Getting Started
1. Review the README files in each directory
2. Start with the Development folder to outline your story
3. Use the Characters folder to develop your characters
4. Build your world in the Worldbuilding folder
5. Write scenes/chapters in the appropriate folders
6. Assemble your final work in the main Scripts/Manuscript folder

## AI Agent Integration
This project is configured to work with The Writers Room AI agents:
- [List of relevant agents for this project type]

## Version Control
This project uses Git for version control. Make regular commits to track your changes.

## Export Options
- [List of export formats available for this project type]
```

### 4.2 Genre-Specific Templates

Each genre includes:
- **Industry-standard formatting**
- **Genre-specific character archetypes**
- **Common plot structures**
- **Market research and trends**
- **Industry contacts and resources**

---

## 5. AI Integration

### 5.1 Project Setup Assistant

```yaml
AI Setup Flow:
  Project Type Selection:
    - Explain differences between project types
    - Provide industry insights
    - Suggest best practices
  
  Genre Selection:
    - Genre-specific conventions
    - Market analysis
    - Target audience insights
  
  Template Customization:
    - Suggest modifications based on project details
    - Recommend additional folders/files
    - Provide industry-standard structures
```

### 5.2 Agent Recommendations

```yaml
Agent Assignment by Project Type:
  Screenplay:
    - Script Doctor (Structure and pacing)
    - Character Specialist (Character development)
    - Creative Visionary (Big picture ideas)
    - Market Analyst (Industry insights)
  
  Novel:
    - Creative Visionary (Story development)
    - Character Specialist (Character arcs)
    - Structure Specialist (Plot development)
    - Market Analyst (Publishing insights)
  
  Series:
    - Script Doctor (Episode structure)
    - Character Specialist (Series character development)
    - Creative Visionary (Season arcs)
    - Market Analyst (TV industry insights)
```

---

## 6. Implementation Requirements

### 6.1 User Interface

```yaml
UI Components:
  Project Type Selection:
    - Visual cards with icons
    - Hover effects and descriptions
    - Search/filter functionality
  
  Project Details Form:
    - Step-by-step wizard interface
    - Form validation
    - Auto-save progress
  
  Template Preview:
    - Preview of folder structure
    - Sample file contents
    - Customization options
```

### 6.2 File System Integration

```yaml
File Operations:
  Directory Creation:
    - Create all required folders
    - Set appropriate permissions
    - Handle existing files gracefully
  
  Template File Generation:
    - Create all template files
    - Populate with project-specific content
    - Set up version control
  
  VS Code Integration:
    - Configure workspace settings
    - Install recommended extensions
    - Set up snippets and shortcuts
```

### 6.3 Error Handling

```yaml
Error Scenarios:
  Invalid Project Name:
    - Check for special characters
    - Validate length limits
    - Handle reserved names
  
  Insufficient Permissions:
    - Check write permissions
    - Provide helpful error messages
    - Suggest alternative locations
  
  Template Generation Failures:
    - Partial creation handling
    - Rollback capabilities
    - User notification and recovery options
```

---

## 7. Future Enhancements

### 7.1 Advanced Features

```yaml
Future Capabilities:
  Custom Templates:
    - User-defined project structures
    - Template sharing and marketplace
    - Industry-specific templates
  
  Project Migration:
    - Import existing projects
    - Convert between project types
    - Merge multiple projects
  
  Collaboration Setup:
    - Team member invitations
    - Role assignment
    - Permission management
```

---

## Conclusion

This specification provides a comprehensive framework for creating new projects in The Writers Room, ensuring users have the right structure, templates, and AI assistance for their creative writing projects. The system is designed to be flexible, user-friendly, and industry-standard compliant. 