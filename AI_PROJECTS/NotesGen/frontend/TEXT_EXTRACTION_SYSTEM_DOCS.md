# PPT Text Extraction System Documentation

## Overview

This document provides comprehensive documentation for the PowerPoint text extraction and editing system. This system has been carefully designed and debugged to provide reliable text extraction, intelligent parsing, and seamless editing capabilities.

## System Architecture

### Frontend Components

#### 1. SlideTextEditor.tsx
- **Purpose**: Individual slide text editing with intelligent parsing
- **Key Features**:
  - Smart categorization of speaker notes into predefined fields
  - Real-time text modification tracking
  - Combines fragmented title pieces into coherent titles
  - Handles multiple content shapes separately
- **API Endpoints**: 
  - `GET /api/ppt-text-editor/extract/{pptFileId}/slide/{slideNumber}`

#### 2. PPTTextEditor.tsx
- **Purpose**: Bulk text editing for entire presentations
- **Key Features**:
  - Extract text from all slides at once
  - Validation before saving
  - Bulk editing capabilities
  - Save changes back to new PPT file
- **API Endpoints**:
  - `GET /api/ppt-text-editor/extract/{pptFileId}`
  - `POST /api/ppt-text-editor/validate-changes`
  - `POST /api/ppt-text-editor/save/{pptFileId}`

#### 3. PPTTextExtractor.tsx
- **Purpose**: Testing and debugging utility
- **Key Features**:
  - Extract all slides or individual slides
  - Useful for debugging extraction issues
  - Performance testing and validation
- **API Endpoints**:
  - `GET /api/ppt-text-editor/extract/{pptFileId}`
  - `GET /api/ppt-text-editor/extract/{pptFileId}/slide/{slideNumber}`

#### 4. NotesEditor.tsx
- **Purpose**: Main container organizing all text editing tools
- **Key Features**:
  - Tab-based organization of different tools
  - State preservation between tab switches
  - Centralized workflow management

## Critical Configuration

### API URL Configuration (CRITICAL)

**The most important aspect of this system is the API URL configuration. This configuration prevents major intermittent failures.**

#### Environment Variable Setup
```bash
# frontend/.env
REACT_APP_API_URL=http://localhost:8000
```

#### Code Pattern (Used in ALL components)
```typescript
// CRITICAL: Use environment variable for API URL
const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const response = await fetch(`${apiUrl}/api/ppt-text-editor/extract/${pptFileId}`);
```

#### Why This Pattern is Critical

**Problem**: Previously, components used relative URLs like `/api/ppt-text-editor/extract/...`

**Issue**: These requests went to the React development server (port 3000/3001) instead of the backend API server (port 8000)

**Symptoms**: "Unexpected token '<', '<!DOCTYPE'" errors because the React dev server returned HTML error pages instead of JSON

**Solution**: Use environment variable-based URLs to ensure all API requests go to the correct backend server

### Backend Server Configuration

#### Correct Server Startup
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --log-level info
```

#### Environment Variables
```bash
# backend/.env
SQLALCHEMY_DATABASE_URI=postgresql://postgres:password@localhost/notesgen
```

## Intelligent Text Parsing

### Speaker Notes Categorization

The system automatically categorizes speaker notes into these fields:

1. **Developer Notes**: URLs, technical implementation details, ~developer markers
2. **Alt Text**: Numbered references (*1, *2, etc.), image descriptions
3. **Slide Description**: Flowchart content, process descriptions
4. **Script**: What to say during the slide presentation
5. **Transitional Notes**: Slide navigation, flow between slides
6. **Instructor Notes**: Teaching guidance, emphasis points
7. **Student Notes**: Learning objectives, implementation steps
8. **References**: URLs, citations, documentation links

### Title Combination

The system intelligently combines fragmented title pieces:
- Sorts by position (y-coordinate, then x-coordinate)
- Joins with appropriate spacing
- Handles punctuation correctly
- Filters empty text fragments

## Common Issues and Troubleshooting

### 1. "Unexpected token '<', '<!DOCTYPE'" Error

**Cause**: Frontend making requests to React dev server instead of backend

**Solutions**:
1. Verify backend server is running on port 8000
2. Check `REACT_APP_API_URL` in `frontend/.env`
3. Ensure no conflicting server processes
4. Verify API calls use environment variable pattern

**Verification**:
```bash
curl http://127.0.0.1:8000/health
# Should return: {"status":"healthy"}
```

### 2. Server Port Conflicts

**Symptoms**: `[Errno 48] Address already in use`

**Solutions**:
```bash
# Find conflicting processes
lsof -i :8000

# Kill conflicting processes
kill -9 <PID>

# Start fresh server
cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Text Extraction Returning Empty Results

**Possible Causes**:
- PPT file not properly uploaded
- Database connection issues
- Backend text extraction logic errors

**Debugging Steps**:
1. Check server logs for errors
2. Verify PPT file exists in database
3. Test individual slide extraction
4. Check text cache in database

### 4. Module Import Errors

**Symptoms**: `ModuleNotFoundError: No module named 'app'`

**Solution**: Ensure you're running from the correct directory
```bash
cd backend  # Must be in backend directory
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Performance Considerations

### Text Extraction Caching

- Backend caches extracted text in PostgreSQL database
- Subsequent extractions use cached data for faster response
- Cache invalidation when PPT files are modified

### Frontend State Management

- Components preserve state when switching tabs
- Modification tracking prevents unnecessary API calls
- Efficient re-rendering with React hooks

## Development Guidelines

### When Adding New Features

1. **Always use environment variable for API URLs**
2. **Add comprehensive error handling**
3. **Include loading states for UX**
4. **Test with multiple PPT files**
5. **Verify caching behavior**

### Code Patterns to Follow

```typescript
// ✅ CORRECT: Use environment variable
const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const response = await fetch(`${apiUrl}/api/endpoint`);

// ❌ WRONG: Relative URL
const response = await fetch('/api/endpoint');
```

### Error Handling Pattern

```typescript
try {
  const response = await fetch(apiUrl);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  // Process response...
} catch (error) {
  console.error('Operation failed:', error);
  const errorMessage = error instanceof Error ? error.message : 'Unknown error';
  toast({
    title: "Error Title",
    description: errorMessage,
    status: "error",
    duration: 5000,
    isClosable: true,
  });
}
```

## System Health Monitoring

### Backend Health Check
```bash
curl http://127.0.0.1:8000/health
```

### Database Connection Test
```bash
cd backend
python -c "from app.db.database import SessionLocal; print('✅ Database connection successful'); SessionLocal().close()"
```

### Frontend Development Server
```bash
cd frontend
npm start
# Should start on http://localhost:3000
```

## Conclusion

This text extraction system has been thoroughly debugged and optimized for reliability. The most critical aspect is the API URL configuration pattern that prevents frontend-backend communication issues. Follow the documented patterns and troubleshooting steps to maintain system stability.

For any issues not covered in this documentation, check server logs and follow the systematic debugging approach outlined above. 