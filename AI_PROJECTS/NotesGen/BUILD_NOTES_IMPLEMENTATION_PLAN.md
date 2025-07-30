# Build Notes Implementation Plan

## 📋 **Project Overview**

**Objective**: Implement bulk AI generation for all slides in a PowerPoint deck with optimized performance, progress tracking, and version control.

**Performance Target**: 25-slide deck processed in ~10-15 seconds with 10 parallel workers.

## 🚨 **CRITICAL: PRESERVATION OF CURRENT FUNCTIONALITY**

**ABSOLUTE REQUIREMENTS - NO EXCEPTIONS:**

### **Zero Breaking Changes Policy**
- ✅ **Current UI must remain 100% functional** - no layout changes, no button removals, no workflow disruptions
- ✅ **Existing Generate button must work exactly as before** - same 3-second performance, same output quality
- ✅ **All current backend APIs must remain unchanged** - no modifications to existing endpoints
- ✅ **Database schema additions ONLY** - no modifications to existing tables or columns
- ✅ **No changes to existing AI service logic** - bulk functionality must be completely separate

### **Incremental Development Strategy**
1. **STAGE-GATE APPROACH**: Each phase must be fully tested and confirmed working before proceeding
2. **BACKWARDS COMPATIBILITY**: All new code must coexist with existing systems
3. **FEATURE FLAGS**: New functionality behind toggles that can be disabled if issues arise
4. **ROLLBACK CAPABILITY**: Each commit must be easily reversible without data loss
5. **CONTINUOUS VALIDATION**: Existing functionality tested after every change

### **Testing Requirements Per Stage**
- ✅ **Existing Generate button works** (3-second test)
- ✅ **UI layout unchanged** (visual regression test)
- ✅ **All current workflows functional** (end-to-end test)
- ✅ **No performance degradation** (baseline comparison)
- ✅ **Database queries unchanged** (query performance test)

---

## ✅ **FINAL DESIGN DECISIONS**

### **1. Build Notes Button Behavior**
**DECIDED:** Process ALL slides in the deck automatically (no confirmation)
- **Rationale**: Fastest UX, matches "bulk" operation expectations
- **Implementation**: Single click triggers processing of entire deck

### **2. Handling Existing AI Content**
**DECIDED:** Overwrite existing AI content with new generation
- **Rationale**: Simpler version management, users expect "refresh" behavior
- **Implementation**: Store previous version before overwriting

### **3. User Experience During Processing**
**DECIDED:** User can continue using the app normally (non-blocking)
- **Rationale**: 10-15 second processing time shouldn't freeze interface
- **Implementation**: Background processing with status updates

### **4. Status Bar Layout** 
**DECIDED:** 3-column layout in blue bottom status bar ✅
- **Column 1**: File name and slide count
- **Column 2**: Current slide indicator (centered)
- **Column 3**: Build Notes progress (right-aligned, when active)

### **5. Error Handling Strategy**
**DECIDED:** Save successful results, show error summary for failures
- **Rationale**: Better user experience, don't lose partial work
- **Implementation**: Atomic per-slide operations with rollback capability

### **6. Database Architecture**
**DECIDED:** Amazon RDS PostgreSQL + S3 file storage ✅
- **Primary DB**: PostgreSQL for JSONB support and ACID compliance
- **File Storage**: S3 for PPT files and slide images
- **Deployment**: Optimized for AWS infrastructure

---

## 🏗️ **System Architecture**

### **High-Level Flow**
```
Frontend (Build Notes Button) 
    ↓
Backend API Endpoint (/api/bulk-generate-notes)
    ↓
Worker Pool Manager (10 workers)
    ↓
Batch Processor (Sequential batches of 10 slides)
    ↓
Nova AI Services (3 models per slide in parallel)
    ↓
Version Storage + Progress Tracking
    ↓
Real-time Progress Updates (WebSocket/SSE)
```

### **Performance Model**
- **Single Slide**: 3 seconds (current reality)
- **10 Workers Parallel**: 10 slides in 3 seconds
- **25-Slide Deck**: ~9-12 seconds total (3 batches)
- **Batch Optimization**: Potential 10-20% improvement

---

## 🔧 **1. Backend Implementation**

### **New API Endpoint**
```python
# /backend/app/api/api_v1/endpoints/bulk_notes.py
@router.post("/bulk-generate-notes/{ppt_file_id}")
async def bulk_generate_notes(
    ppt_file_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # 1. Validate PPT file exists
    # 2. Get all slides for deck
    # 3. Create job_id for tracking
    # 4. Start background task
    # 5. Return job_id for progress tracking
```

### **Worker Pool Manager**
```python
# /backend/app/services/bulk_notes_service.py
class BulkNotesService:
    def __init__(self):
        self.max_workers = 10
        self.batch_size = 10
        
    async def process_deck(self, ppt_file_id: int, job_id: str):
        slides = get_all_slides(ppt_file_id)
        batches = create_sequential_batches(slides, self.batch_size)
        
        for batch_num, batch in enumerate(batches):
            await self.process_batch(batch, job_id, batch_num)
```

### **Sequential Batch Processing**
```python
async def process_batch(self, slides: List[Slide], job_id: str, batch_num: int):
    """Process slides 1-10, then 11-20, etc."""
    with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
        futures = []
        for slide in slides:
            future = executor.submit(self.process_single_slide, slide, job_id)
            futures.append(future)
        
        # Wait for all slides in this batch to complete
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            await self.update_progress(job_id, result)
```

### **Version Storage System**
```python
# New database table: slide_versions
class SlideVersion(Base):
    __tablename__ = "slide_versions"
    
    id = Column(Integer, primary_key=True)
    slide_id = Column(Integer, ForeignKey("slides.id"))
    version_type = Column(String)  # 'original', 'ai_generated', 'edited', 'final'
    content = Column(JSON)  # All field content
    created_at = Column(DateTime)
    is_active = Column(Boolean, default=False)
```

---

## 🎨 **2. Frontend Implementation**

### **Build Notes Button Handler**
```typescript
// /frontend/src/features/ppt/components/NotesEditor.tsx
const handleBuildNotesClick = async () => {
  try {
    setIsBuildingNotes(true);
    
    const response = await fetch(`/api/v1/bulk-generate-notes/${pptFileId}`, {
      method: 'POST'
    });
    
    const { job_id } = await response.json();
    
    // Start progress tracking
    startProgressTracking(job_id);
    
  } catch (error) {
    console.error('Build Notes failed:', error);
  }
};
```

### **Status Bar Integration (3-Column Layout)**
**DECIDED:** Integrate Build Notes progress into the blue bottom status bar:

**Current Status Bar** (in `PPTViewer.tsx`):
```tsx
<Box bg="#007ACC" h="22px" px={3} display="flex" justifyContent="space-between">
  <Text color="#FFFFFF">{selectedPPT.name} - Processing...</Text>
  <Text color="#FFFFFF">Slide {current} of {total}</Text>
</Box>
```

**New 3-Column Status Bar**:
```tsx
<Box bg="#007ACC" h="22px" px={3} display="flex" justifyContent="space-between">
  {/* Column 1: File Info */}
  <Text color="#FFFFFF" flex="1">
    {selectedPPT.name} - {slides.length} slides
  </Text>
  
  {/* Column 2: Current Slide */}
  <Text color="#FFFFFF" flex="1" textAlign="center">
    Slide {selectedSlideIndex + 1} of {slides.length}
  </Text>
  
  {/* Column 3: Build Notes Progress (when active) */}
  <Box flex="1" textAlign="right">
    {isBuildingNotes ? (
      <HStack spacing={2} justify="flex-end">
        <Spinner size="xs" color="white" />
        <Text color="#FFFFFF" fontSize="12px">
          Building {completedSlides}/{totalSlides}
        </Text>
      </HStack>
    ) : (
      <Text color="#FFFFFF" fontSize="12px">Ready</Text>
    )}
  </Box>
</Box>
```

### **Version Comparison Modal**
```typescript
// /frontend/src/components/VersionComparisonModal.tsx
interface VersionComparisonModalProps {
  slideId: number;
  isOpen: boolean;
  onClose: () => void;
}

const VersionComparisonModal: React.FC<VersionComparisonModalProps> = ({
  slideId, isOpen, onClose
}) => {
  const [versions, setVersions] = useState<SlideVersion[]>([]);
  const [selectedVersions, setSelectedVersions] = useState<string[]>(['original', 'ai_generated']);
  
  // Fetch all versions for this slide
  // Display side-by-side comparison
  // Allow selecting which version to make active
  
  return (
    <Modal isOpen={isOpen} onClose={onClose} size="6xl">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Version Comparison - Slide {slideId}</ModalHeader>
        <ModalBody>
          <SimpleGrid columns={2} spacing={4}>
            {selectedVersions.map(versionType => (
              <Box key={versionType}>
                <Heading size="sm">{versionType}</Heading>
                <VersionContent version={getVersion(versionType)} />
              </Box>
            ))}
          </SimpleGrid>
        </ModalBody>
      </ModalContent>
    </Modal>
  );
};
```

---

## 📊 **3. Progress Tracking System**

### **Real-time Updates (Server-Sent Events)**
```python
# /backend/app/api/api_v1/endpoints/progress.py
@router.get("/progress/{job_id}")
async def get_progress_stream(job_id: str):
    async def event_stream():
        while True:
            progress_data = get_job_progress(job_id)
            if progress_data:
                yield f"data: {json.dumps(progress_data)}\n\n"
                
                if progress_data['progress'] >= 100:
                    break
                    
            await asyncio.sleep(1)  # Update every second
    
    return StreamingResponse(
        event_stream(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache"}
    )
```

### **Progress Storage (Redis/Memory)**
```python
# Progress tracking in Redis or in-memory store
class ProgressTracker:
    def __init__(self):
        self.jobs = {}  # In production: use Redis
    
    def update_progress(self, job_id: str, completed_slides: int, total_slides: int):
        progress = (completed_slides / total_slides) * 100
        self.jobs[job_id] = {
            'progress': progress,
            'current_slide': completed_slides,
            'total_slides': total_slides,
            'status': 'processing' if progress < 100 else 'completed'
        }
```

---

## 🗄️ **4. Database Schema Updates**

## 🏗️ **AWS Database Architecture**

### **Primary Database: Amazon RDS PostgreSQL**
**Chosen for AWS deployment requirements:**
- ✅ **JSONB support** - Perfect for version storage and complex slide content
- ✅ **ACID compliance** - Critical for bulk operation integrity  
- ✅ **High concurrency** - Multiple users generating notes simultaneously
- ✅ **AWS integration** - Automated backups, monitoring, scaling
- ✅ **Performance** - Optimized for read/write operations on structured data

### **File Storage: Amazon S3**
```
S3 Bucket Structure:
├── /ppt-files/{ppt_id}/original.pptx
├── /slide-images/{ppt_id}/slide-{n}.png
├── /exports/{job_id}/bulk-results.json
└── /cache/{ppt_id}/processed-content.json
```

### **New Database Tables (PostgreSQL)**
```sql
-- Slide versions for comparison (JSONB for flexibility)
CREATE TABLE slide_versions (
    id SERIAL PRIMARY KEY,
    slide_id INTEGER REFERENCES slides(id),
    version_type VARCHAR(50) NOT NULL, -- 'original', 'ai_generated', 'edited', 'final'
    content JSONB NOT NULL, -- All field content with full structure
    s3_backup_url VARCHAR(500), -- Optional S3 backup for large content
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT FALSE,
    created_by_job_id UUID REFERENCES bulk_generation_jobs(job_id)
);

-- Bulk generation jobs with AWS-optimized fields
CREATE TABLE bulk_generation_jobs (
    id SERIAL PRIMARY KEY,
    job_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    ppt_file_id INTEGER REFERENCES ppt_files(id),
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed', 'cancelled'
    total_slides INTEGER NOT NULL,
    completed_slides INTEGER DEFAULT 0,
    failed_slides INTEGER DEFAULT 0,
    processing_config JSONB, -- Worker count, batch size, AI model preferences
    error_log JSONB, -- Structured error information
    s3_result_url VARCHAR(500), -- S3 location of full results
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    estimated_completion_at TIMESTAMP
);

-- Performance indexes for AWS RDS
CREATE INDEX idx_slide_versions_slide_id ON slide_versions(slide_id);
CREATE INDEX idx_slide_versions_active ON slide_versions(is_active) WHERE is_active = true;
CREATE INDEX idx_slide_versions_type ON slide_versions(version_type);
CREATE INDEX idx_bulk_jobs_status ON bulk_generation_jobs(status);
CREATE INDEX idx_bulk_jobs_ppt_file ON bulk_generation_jobs(ppt_file_id);
CREATE INDEX idx_bulk_jobs_created ON bulk_generation_jobs(created_at);
```

### **Migration Script**
```python
# /backend/migrations/versions/add_bulk_notes_tables.py
def upgrade():
    op.create_table('slide_versions', ...)
    op.create_table('bulk_generation_jobs', ...)
    
    # Create indexes for performance
    op.create_index('idx_slide_versions_slide_id', 'slide_versions', ['slide_id'])
    op.create_index('idx_slide_versions_active', 'slide_versions', ['is_active'])
```

---

## 🚀 **5. Performance Optimizations**

### **Batch Optimization Strategies**
1. **Image Pre-loading**: Load all slide images into memory before processing
2. **Model Warm-up**: Pre-initialize Nova models to reduce cold start time
3. **Connection Pooling**: Reuse HTTP connections to AWS Bedrock
4. **Caching**: Cache common prompt responses

### **Memory Management**
```python
class OptimizedBatchProcessor:
    def __init__(self):
        self.image_cache = {}  # Pre-load all images
        self.model_pool = {}   # Keep models warm
    
    async def preload_images(self, ppt_file_id: int):
        """Load all slide images into memory before processing"""
        slides = get_all_slides(ppt_file_id)
        for slide in slides:
            image_data = load_slide_image(slide.id)
            self.image_cache[slide.id] = image_data
```

---

## 📝 **6. Implementation Phases** 

### **STAGE 1: Database Foundation (Non-Breaking)**
**Goal**: Add new tables without touching existing schema
- [ ] **1A**: Create migration script for new tables only
- [ ] **1B**: Test migration on dev database
- [ ] **1C**: Verify existing queries still work (performance baseline)
- [ ] **1D**: Deploy migration to staging
- [ ] **🔒 GATE**: Confirm existing Generate button works (3-second test)

### **STAGE 2: Isolated Backend Service (Non-Breaking)**  
**Goal**: Build bulk service that doesn't interfere with existing code
- [ ] **2A**: Create separate `bulk_notes_service.py` (new file only)
- [ ] **2B**: Add new API endpoint in separate file (`bulk_notes.py`)
- [ ] **2C**: Test new endpoint in isolation (no UI integration yet)
- [ ] **2D**: Verify existing AI service unchanged
- [ ] **🔒 GATE**: Confirm existing Generate button works (performance test)

### **STAGE 3: Progress Tracking Infrastructure (Non-Breaking)**
**Goal**: Add progress system without affecting current UI
- [ ] **3A**: Create progress tracking service (new file)
- [ ] **3B**: Add progress API endpoint (separate from existing APIs)
- [ ] **3C**: Test progress system independently
- [ ] **3D**: Mock progress updates without UI changes
- [ ] **🔒 GATE**: Confirm UI layout unchanged, Generate button works

### **STAGE 4: Minimal UI Integration (Additive Only)**
**Goal**: Add Build Notes button without changing existing layout
- [ ] **4A**: Add Build Notes button (placeholder handler only)
- [ ] **4B**: Test UI layout - confirm no spacing/alignment changes
- [ ] **4C**: Verify all existing buttons work unchanged
- [ ] **4D**: Add basic loading state (no progress bar yet)
- [ ] **🔒 GATE**: Full UI functionality test, Generate button performance test

### **STAGE 5: Core Bulk Processing (Behind Feature Flag)**
**Goal**: Connect Build Notes to backend with safety controls
- [ ] **5A**: Implement Build Notes click handler with feature flag
- [ ] **5B**: Test with single slide first (verify no existing data affected)
- [ ] **5C**: Test with 2-3 slides, confirm isolation from existing workflow
- [ ] **5D**: Add error boundaries to prevent UI crashes
- [ ] **🔒 GATE**: Existing workflow completely unaffected, Generate button unchanged

### **STAGE 6: Progress Visualization (Additive Only)**
**Goal**: Add progress bar without disrupting status bar
- [ ] **6A**: Add progress component to status bar (hidden by default)
- [ ] **6B**: Test status bar layout with/without progress
- [ ] **6C**: Integrate progress updates with bulk processing
- [ ] **6D**: Verify connection status and other status elements unchanged
- [ ] **🔒 GATE**: Status bar functionality preserved, no layout shifts

### **STAGE 7: Version System (Isolated)**
**Goal**: Add version storage without affecting current data flow
- [ ] **7A**: Implement version storage (separate from current slide updates)
- [ ] **7B**: Test version storage with existing data (read-only first)
- [ ] **7C**: Add version comparison modal (accessible but separate)
- [ ] **7D**: Verify current slide editing workflow unchanged
- [ ] **🔒 GATE**: Existing slide editing/saving works exactly as before

### **STAGE 8: Performance Optimization (Non-Intrusive)**
**Goal**: Optimize bulk processing without affecting single slide performance
- [ ] **8A**: Add image pre-loading (only for bulk operations)
- [ ] **8B**: Implement connection pooling (backward compatible)
- [ ] **8C**: Add batch optimizations (bulk-only)
- [ ] **8D**: Performance test both single slide and bulk operations
- [ ] **🔒 GATE**: Single slide performance maintained (3-second baseline)

### **STAGE 9: Final Integration & Polish (Safety First)**
**Goal**: Complete feature with full rollback capability
- [ ] **9A**: End-to-end testing (bulk + existing workflows)
- [ ] **9B**: Error handling and user feedback
- [ ] **9C**: Feature flag removal (only after extensive testing)
- [ ] **9D**: Performance validation and monitoring
- [ ] **🔒 GATE**: Production readiness checklist, rollback plan confirmed

---

## 🧪 **7. Testing Strategy**

### **Performance Testing**
```python
# Test with various deck sizes
test_cases = [
    {"slides": 5, "expected_time": "3-4 seconds"},
    {"slides": 10, "expected_time": "3-4 seconds"},
    {"slides": 25, "expected_time": "9-12 seconds"},
    {"slides": 50, "expected_time": "15-20 seconds"}
]
```

### **Error Scenarios**
- Network timeouts
- AWS rate limiting
- Invalid slide data
- Concurrent user requests
- Memory constraints

---

## 🚨 **8. Risk Mitigation & Safety Protocols**

### **System Stability Protection**
- **Feature Flags**: All new functionality behind runtime toggles
- **Circuit Breakers**: Automatic fallback if bulk processing fails
- **Resource Isolation**: Bulk operations in separate process/thread pools
- **Graceful Degradation**: Disable Build Notes if issues detected
- **Monitoring**: Real-time alerts for performance degradation

### **Rollback Procedures**
- **Database**: Migration rollback scripts tested before deployment
- **Code**: Each stage commits tagged for easy reversion
- **Feature Flags**: Instant disable capability for problematic features
- **Cache Invalidation**: Clear any cached data on rollback
- **User Communication**: Clear messaging if features temporarily disabled

### **AWS Rate Limiting**
- Implement exponential backoff
- Monitor request quotas
- Graceful degradation to sequential processing
- **No impact on existing single-slide generation**

### **Memory Management**
- Limit concurrent workers based on available memory
- Clear image cache after each batch
- Monitor memory usage during processing
- **Separate memory pools for bulk vs. single operations**

### **User Experience Protection**
- Allow cancellation of bulk operations
- Provide clear error messages
- Save partial progress on failures
- **Never block or slow down existing Generate button**
- **Preserve all current keyboard shortcuts and workflows**

### **Data Integrity**
- **Read-only operations initially** - no modifications to existing slide data
- **Version storage separate** from current slide storage
- **Atomic operations** - all or nothing for bulk updates
- **Backup verification** before any schema changes

---

## ✅ **9. Success Metrics**

### **Performance Targets**
- 25-slide deck: < 15 seconds
- 50-slide deck: < 25 seconds  
- Memory usage: < 2GB peak
- Success rate: > 95%

### **User Experience**
- Progress updates every second
- Ability to continue using app during processing
- Clear version comparison interface
- One-click version switching

---

## 📋 **10. Implementation Checklist**

**Backend:**
- [ ] Database schema and migrations
- [ ] Bulk notes service with worker pool
- [ ] API endpoints (bulk generation, progress tracking)
- [ ] Version storage system
- [ ] Error handling and logging

**Frontend:**
- [ ] Build Notes button integration
- [ ] Progress bar component
- [ ] Version comparison modal
- [ ] Status updates and error handling

**Testing:**
- [ ] Unit tests for core services
- [ ] Integration tests for full workflow
- [ ] Performance testing with various deck sizes
- [ ] Error scenario testing

**Documentation:**
- [ ] API documentation
- [ ] User guide for version comparison
- [ ] Performance benchmarks
- [ ] Troubleshooting guide

---

## 🔍 **STAGE VALIDATION CHECKLIST**

**Use this checklist after EVERY stage to ensure no regression:**

### **Critical Functionality Tests** 
- [ ] **Generate Button**: Click Generate, verify 3-second response time
- [ ] **UI Layout**: No button movement, spacing changes, or visual regression
- [ ] **Slide Navigation**: Left/right arrows work, slide numbers correct
- [ ] **Text Editing**: All fields editable, Save button works
- [ ] **Status Bar**: Connection status, theme toggle work
- [ ] **File Browser**: PPT file selection and loading unchanged

### **Performance Baselines**
- [ ] **Single Slide Generation**: ≤ 3 seconds (current baseline)
- [ ] **UI Responsiveness**: No lag in button clicks or navigation
- [ ] **Memory Usage**: No increase in baseline memory consumption
- [ ] **Database Queries**: Existing query performance unchanged

### **Data Integrity Verification**
- [ ] **Existing Slides**: All current slide data intact
- [ ] **Speaker Notes**: No loss or corruption of existing notes
- [ ] **File Uploads**: PPT processing works as before
- [ ] **User Settings**: Theme, preferences preserved

### **Error Scenarios**
- [ ] **Network Issues**: Graceful handling, no UI crashes
- [ ] **Invalid Data**: Error messages clear, system stable
- [ ] **Concurrent Users**: No conflicts with existing workflows

### **Rollback Verification** 
- [ ] **Migration Rollback**: Database can revert cleanly
- [ ] **Code Reversion**: Previous commit restores full functionality
- [ ] **Feature Disable**: Feature flags successfully disable new features
- [ ] **Cache Clearing**: System works with cleared caches

**🚨 STOP RULE: If ANY item fails, halt development and fix before proceeding**

---

## 🛠️ **DEVELOPMENT APPROACH**

### **File Organization Strategy**
- **New Files Only**: Create separate files for all bulk functionality
- **No Existing File Modification**: Only add imports or minimal integration hooks
- **Namespace Isolation**: Use clear prefixes (bulk_, version_, progress_) for new code
- **Separate API Routes**: New endpoints in dedicated router files

### **Code Integration Rules**
```python
# ✅ GOOD - Adding new functionality
from app.services.bulk_notes_service import BulkNotesService  # New import only

# ❌ BAD - Modifying existing function
def existing_generate_notes():
    # Don't modify this function
    pass

# ✅ GOOD - New separate function
def bulk_generate_notes():
    # Completely separate implementation
    pass
```

### **Database Changes Protocol**
- **Additive Only**: New tables, new columns with defaults only
- **No Foreign Key Changes**: Don't modify existing relationships
- **Backward Compatible**: Existing queries must work unchanged
- **Migration Testing**: Test rollback before applying

### **Frontend Integration Strategy**
```typescript
// ✅ GOOD - Adding new component
const BuildNotesButton = () => {
    // New isolated component
};

// ✅ GOOD - Adding to existing component (additive only)
const ExistingComponent = () => {
    // ... existing code unchanged ...
    
    // New addition at end
    {isFeatureEnabled && <BuildNotesButton />}
};

// ❌ BAD - Modifying existing component logic
```

### **Conflict Resolution**
1. **If UI Breaks**: Immediately revert to last working commit
2. **If Performance Degrades**: Disable new features via feature flag
3. **If Database Issues**: Run rollback migration immediately
4. **If Integration Conflicts**: Isolate new code further, reduce integration points
5. **If Uncertain**: Ask for guidance rather than risking existing functionality

### **Commit Strategy**
- **Atomic Commits**: Each stage in single commit with clear rollback tags
- **Descriptive Messages**: Include stage number and validation status
- **Feature Branch**: All development in separate branch until proven stable
- **Quick Rollback**: Each commit should be easily revertible

**Example Commit Messages:**
```
STAGE-1A: Add bulk_generation_jobs table (VALIDATED ✅)
STAGE-2A: Create bulk_notes_service.py (VALIDATED ✅)  
STAGE-4A: Add Build Notes button (UI-TESTED ✅)
``` 