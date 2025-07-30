# 🚨 CRITICAL CONFIGURATION NOTES - READ FIRST 🚨

**⚠️ EXPENSIVE MISTAKE PREVENTION ⚠️**

This file documents critical configuration requirements that MUST be checked FIRST before debugging AI/Nova model issues.

## 🔴 STEP 1: AWS CREDENTIALS & REGION (CHECK FIRST!)

### Nova Model Access Requirements
- **CRITICAL**: Nova models require specific AWS credentials with proper permissions
- **CRITICAL**: Nova models are REGION-SPECIFIC - must use correct region
- **LOCATION**: Credentials are in `../APPSEC/NotesGenSec.txt` (outside project directory)

### Correct Configuration for Nova Models
```bash
# ✅ CORRECT - Nova-enabled credentials from APPSEC directory
export AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_HERE
export AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY_HERE
export AWS_DEFAULT_REGION=us-east-1  # ⚠️ CRITICAL: us-east-1 NOT us-west-2!
```

### ❌ Common Mistakes That Cause Circuit Breaker Failures
1. **Wrong Region**: Using `us-west-2` instead of `us-east-1`
2. **Wrong Credentials**: Using demo/test credentials instead of Nova-enabled ones
3. **IAM Permissions**: Using credentials that only allow Claude, not Nova

## 🔴 STEP 2: DEBUGGING CIRCUIT BREAKER FAILURES

### If You See These Errors:
```
🚫 Circuit breaker OPEN for amazon.nova-lite-v1:0
🚫 Circuit breaker OPEN for amazon.nova-micro-v1:0
```

### DO THIS FIRST (Before touching code):
1. **Check AWS region**: `curl http://localhost:8000/api/v1/ai/debug`
2. **Verify credentials**: Check if using APPSEC credentials
3. **Test basic AWS access**: Try a simple Bedrock API call
4. **Check IAM permissions**: Ensure Nova model access in IAM policy

### DON'T DO THIS (Waste of time):
- ❌ Modify model configurations
- ❌ Change circuit breaker settings  
- ❌ Debug application code
- ❌ Update AI service logic

## 🔴 STEP 3: STARTUP CHECKLIST

### Before Starting Development:
- [ ] Check `../APPSEC/NotesGenSec.txt` for latest credentials
- [ ] Verify AWS region is `us-east-1`
- [ ] Test `/health` endpoint works
- [ ] Test `/api/v1/ai/debug` shows correct region
- [ ] Run a single AI generation test first

### Startup Commands (Copy-Paste Ready):
```bash
# Navigate to backend
cd backend

# Set Nova-enabled environment (from APPSEC)
export DATABASE_URL=postgresql://notesgen:notesgen_password@localhost:5432/notesgen_db
export AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_HERE
export AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY_HERE  
export AWS_DEFAULT_REGION=us-east-1  # ⚠️ CRITICAL: NOT us-west-2
export SECRET_KEY=your-secret-key-here-change-in-production

# Start with verification
echo "🔧 Starting with Nova-enabled credentials:"
echo "   Region: us-east-1 (CORRECTED from us-west-2)"
echo "   Access Key: YOUR_AWS_ACCESS_KEY_HERE"

# Start server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## 🔴 STEP 4: DEPRECATED WARNINGS

### If You See:
```
⚠️ DEPRECATED: Using dangerous numeric ID 15 - should use tracking_id
```

### Root Cause:
Frontend components still sending numeric IDs instead of tracking_ids to:
- `/api/slide-images/ppt/{id}/slides`  
- `/api/v1/bulk-generate-notes/{id}`

### Fix Locations:
- `frontend/src/features/ppt/components/FileBrowser.tsx` - Line 849 monitoring function
- `frontend/src/components/SlidePreview.tsx` - slide image URLs
- Any component using `selectedPPT.id` instead of `selectedPPT.tracking_id`

## 🔴 STEP 5: COST-SAVING VERIFICATION

### Quick Health Check (30 seconds):
```bash
# 1. Backend health
curl http://localhost:8000/health

# 2. AWS configuration  
curl http://localhost:8000/api/v1/ai/debug

# 3. Expected response:
# {"aws_region":"us-east-1","credentials_look_real":true}
```

### If region shows `us-west-2` → STOP AND FIX IMMEDIATELY

## 🔴 EMERGENCY CHECKLIST

When AI features fail, check in this order:

1. **AWS Region** (5 seconds) - `/api/v1/ai/debug`
2. **Credentials** (10 seconds) - Check APPSEC directory  
3. **Basic connectivity** (10 seconds) - `/health` endpoint
4. **Model permissions** (30 seconds) - Try single AI call
5. **Application code** (only after above passes)

---

**💰 COST REMINDER**: Debugging application code when the issue is credentials/region wastes hours. Always check configuration first.

**🔄 UPDATE THIS FILE**: When you discover new configuration issues, document them here immediately. 