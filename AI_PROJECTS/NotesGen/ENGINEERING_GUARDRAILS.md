# ENGINEERING GUARDRAILS & IMPLEMENTATION RULES

## **MANDATORY PRE-IMPLEMENTATION ANALYSIS**

### **Rule 1: NO "TRY AND SEE" CODING**
- ❌ **FORBIDDEN**: Making code changes without understanding root cause
- ❌ **FORBIDDEN**: "Let's try this approach" without verification
- ✅ **REQUIRED**: Complete analysis before any code modification

### **Rule 2: COMPREHENSIVE SYSTEM UNDERSTANDING**
- **BEFORE** any changes, must document:
  - Complete data flow from frontend → backend → database
  - Every API endpoint and its expected behavior  
  - All React hooks and their dependencies
  - Database schema and data relationships
  - Error propagation paths

### **Rule 3: VIRTUAL VERIFICATION PROCESS**
1. **Virtual Code Review**: Mentally trace through proposed changes
2. **Logic Simulation**: Verify the fix addresses the actual root cause
3. **Dependency Analysis**: Ensure changes don't break existing functionality
4. **Integration Testing**: Mentally verify frontend-backend compatibility

### **Rule 4: EVIDENCE-BASED DIAGNOSIS**
- Collect ALL relevant logs, errors, and system state
- Map each error to its root cause in the codebase
- Verify assumptions with code inspection
- Document the complete problem chain

### **Rule 5: IMPLEMENTATION PLAN REQUIREMENT**
- Create detailed MD documentation BEFORE coding
- Include step-by-step verification process
- Define success criteria for each fix
- Plan rollback strategy if changes fail

## **ANALYSIS METHODOLOGY**

### **Phase 1: System State Assessment**
1. **Frontend Analysis**
   - React component hierarchy and data flow
   - State management (Zustand store) examination
   - API call patterns and error handling
   - Console errors and network requests

2. **Backend Analysis**  
   - Server startup and initialization
   - Database connection and schema
   - API endpoint implementation
   - Request/response patterns

3. **Integration Analysis**
   - CORS configuration
   - API endpoint availability  
   - Data serialization/deserialization
   - Error response formats

### **Phase 2: Root Cause Identification**
1. **Error Chain Mapping**
   - Primary failure point identification
   - Secondary failure cascade analysis
   - Missing dependency identification

2. **Code Flow Verification**
   - Trace data from user action → database
   - Verify each transformation step
   - Identify broken links in the chain

### **Phase 3: Solution Design**
1. **Fix Strategy Development**
   - Address root cause, not symptoms
   - Minimal impact approach
   - Backward compatibility preservation

2. **Implementation Planning**
   - Step-by-step execution plan
   - Testing strategy for each step
   - Success/failure criteria definition

## **IMPLEMENTATION EXECUTION RULES**

### **Rule 6: ONE ISSUE AT A TIME**
- Focus on single, well-defined problem
- Complete full resolution before moving to next issue
- Document resolution and verification

### **Rule 7: INCREMENTAL VERIFICATION**
- Test each change immediately after implementation
- Verify success criteria before proceeding
- Document actual vs expected behavior

### **Rule 8: FAILURE PROTOCOL**
- If any step fails, STOP immediately
- Analyze why the planned fix didn't work
- Return to analysis phase, don't attempt new "quick fixes"

### **Rule 9: DOCUMENTATION REQUIREMENT**
- Update implementation plan with actual results
- Document any deviations from planned approach
- Record lessons learned for future reference

## **QUALITY GATES**

### **Before Implementation:**
- [ ] Complete system understanding documented
- [ ] Root cause identified and verified
- [ ] Solution approach validated virtually
- [ ] Implementation plan created and reviewed
- [ ] Success criteria defined

### **During Implementation:**
- [ ] Each step verified before proceeding
- [ ] Changes logged and documented
- [ ] Rollback plan ready if needed

### **After Implementation:**
- [ ] Success criteria met and verified
- [ ] System integration tested
- [ ] Documentation updated
- [ ] Lessons learned recorded

---

**VIOLATION CONSEQUENCES:**
Any violation of these rules requires:
1. Immediate STOP of implementation
2. Return to analysis phase
3. Documentation of what went wrong
4. Revised approach following proper methodology 