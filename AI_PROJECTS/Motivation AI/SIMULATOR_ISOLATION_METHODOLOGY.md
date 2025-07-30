# iOS Simulator Isolation Methodology for Multiple Cursor Instances

## ⚠️ CRITICAL: Maintaining Separate Simulator Instances

This document provides an ironclad method for keeping iOS simulators completely separate when running multiple Cursor instances simultaneously.

## 📱 Device Assignment Strategy

### Instance A (Motivation AI - This Instance)
- **Simulator Device**: iPhone 16 Pro Max
- **Device UDID**: Use `xcrun simctl list devices | grep "iPhone 16 Pro Max"` to get specific UDID
- **Project Path**: `/Users/truckirwin/Desktop/PROJECTS/Motivation AI`
- **App Bundle**: Uses modified Rise and Grind project showing Motivation AI interface

### Instance B (Rise and Grind - Other Instance)  
- **Simulator Device**: iPhone 16 Pro (different from Instance A)
- **Device UDID**: Use `xcrun simctl list devices | grep "iPhone 16 Pro" | grep -v Max` to get specific UDID
- **Project Path**: `/Users/truckirwin/Desktop/PROJECTS/Rise and Grind`
- **App Bundle**: Original Rise and Grind app with MainTabView

## 🔒 Isolation Commands

### Step 1: Identify Available Devices
```bash
# List all available simulators
xcrun simctl list devices available

# Get specific UDIDs
echo "iPhone 16 Pro Max devices:"
xcrun simctl list devices | grep "iPhone 16 Pro Max"
echo "iPhone 16 Pro devices (not Max):"
xcrun simctl list devices | grep "iPhone 16 Pro" | grep -v Max
```

### Step 2: Set Device Variables
Each Cursor instance MUST set these variables at the start of every session:

#### For Instance A (Motivation AI):
```bash
# Set the device UDID for iPhone 16 Pro Max
export DEVICE_UDID="[INSERT_IPHONE_16_PRO_MAX_UDID_HERE]"
export DEVICE_NAME="iPhone 16 Pro Max"
export PROJECT_PATH="/Users/truckirwin/Desktop/PROJECTS/Motivation AI"
export APP_NAME="RiseAndGrind"  # Note: Still uses RiseAndGrind bundle but shows Motivation AI
```

#### For Instance B (Rise and Grind):
```bash
# Set the device UDID for iPhone 16 Pro
export DEVICE_UDID="[INSERT_IPHONE_16_PRO_UDID_HERE]"
export DEVICE_NAME="iPhone 16 Pro"
export PROJECT_PATH="/Users/truckirwin/Desktop/PROJECTS/Rise and Grind"
export APP_NAME="RiseAndGrind"
```

### Step 3: Device-Specific Operations

#### Boot Specific Device:
```bash
# ALWAYS use the specific UDID
xcrun simctl boot $DEVICE_UDID
```

#### Open Specific Simulator:
```bash
# Open the specific device simulator
open -a Simulator --args -CurrentDeviceUDID $DEVICE_UDID
```

#### Install App on Specific Device:
```bash
# Navigate to project directory first
cd "$PROJECT_PATH"

# Install on the specific device only
xcrun simctl install $DEVICE_UDID "$PROJECT_PATH/Rise and Grind/build/Release-iphonesimulator/$APP_NAME.app"
```

#### Launch App on Specific Device:
```bash
# Launch using bundle identifier on specific device
xcrun simctl launch $DEVICE_UDID com.truckirwin.riseandgrind.app
```

## 🚨 MANDATORY Pre-Session Checklist

### Before ANY simulator operation, EACH Cursor instance MUST:

1. **Verify Current Working Directory:**
   ```bash
   pwd
   # Should show the correct project path for this instance
   ```

2. **Set Device Variables:**
   ```bash
   # Run the appropriate export commands above
   echo "Using device: $DEVICE_NAME ($DEVICE_UDID)"
   ```

3. **Verify Device Status:**
   ```bash
   # Check what's currently running
   xcrun simctl list devices | grep "Booted"
   ```

4. **Shutdown Conflicts (if needed):**
   ```bash
   # Only shutdown the OTHER instance's device if there's a conflict
   # Instance A should NEVER shutdown iPhone 16 Pro
   # Instance B should NEVER shutdown iPhone 16 Pro Max
   ```

## 🛡️ Complete Workflow for Each Instance

### Instance A (Motivation AI) Complete Workflow:
```bash
# 1. Set environment
export DEVICE_UDID="[IPHONE_16_PRO_MAX_UDID]"
export DEVICE_NAME="iPhone 16 Pro Max"
export PROJECT_PATH="/Users/truckirwin/Desktop/PROJECTS/Motivation AI"
export APP_NAME="RiseAndGrind"

# 2. Navigate to project
cd "$PROJECT_PATH"

# 3. Shutdown only our device (if needed)
xcrun simctl shutdown $DEVICE_UDID

# 4. Clean build
cd "/Users/truckirwin/Desktop/PROJECTS/Rise and Grind"
xcodebuild clean -scheme RiseAndGrind

# 5. Boot our specific device
xcrun simctl boot $DEVICE_UDID

# 6. Open our specific simulator
open -a Simulator --args -CurrentDeviceUDID $DEVICE_UDID

# 7. Build the app
xcodebuild -scheme RiseAndGrind -destination "id=$DEVICE_UDID" build

# 8. Install on our device
xcrun simctl install $DEVICE_UDID "build/Release-iphonesimulator/RiseAndGrind.app"

# 9. Launch on our device
xcrun simctl launch $DEVICE_UDID com.truckirwin.riseandgrind.app
```

### Instance B (Rise and Grind) Complete Workflow:
```bash
# 1. Set environment
export DEVICE_UDID="[IPHONE_16_PRO_UDID]"
export DEVICE_NAME="iPhone 16 Pro"
export PROJECT_PATH="/Users/truckirwin/Desktop/PROJECTS/Rise and Grind"
export APP_NAME="RiseAndGrind"

# 2. Navigate to project
cd "$PROJECT_PATH"

# 3. Shutdown only our device (if needed)
xcrun simctl shutdown $DEVICE_UDID

# 4. Clean build
xcodebuild clean -scheme RiseAndGrind

# 5. Boot our specific device
xcrun simctl boot $DEVICE_UDID

# 6. Open our specific simulator
open -a Simulator --args -CurrentDeviceUDID $DEVICE_UDID

# 7. Build the app
xcodebuild -scheme RiseAndGrind -destination "id=$DEVICE_UDID" build

# 8. Install on our device
xcrun simctl install $DEVICE_UDID "build/Release-iphonesimulator/RiseAndGrind.app"

# 9. Launch on our device
xcrun simctl launch $DEVICE_UDID com.truckirwin.riseandgrind.app
```

## 🔍 Verification Commands

### Check Which Device is Running What:
```bash
# See all booted devices
xcrun simctl list devices | grep "Booted"

# See what apps are installed on our device
xcrun simctl listapps $DEVICE_UDID

# Check if our app is running
xcrun simctl list processes $DEVICE_UDID | grep RiseAndGrind
```

## ⚠️ NEVER DO These Commands:

1. **NEVER use `xcrun simctl shutdown all`** - This affects both instances
2. **NEVER use device names without UDID** - Could target wrong device
3. **NEVER assume which device is "running"** - Always specify UDID
4. **NEVER cross-contaminate project paths** - Always verify `pwd`

## 🎯 Quick Setup Script for Each Instance

### For Instance A (save as `setup_motivation_ai.sh`):
```bash
#!/bin/bash
# Get the iPhone 16 Pro Max UDID
DEVICE_UDID=$(xcrun simctl list devices | grep "iPhone 16 Pro Max" | head -1 | grep -o '[A-F0-9-]\{36\}')
export DEVICE_UDID=$DEVICE_UDID
export DEVICE_NAME="iPhone 16 Pro Max"
export PROJECT_PATH="/Users/truckirwin/Desktop/PROJECTS/Motivation AI"
export APP_NAME="RiseAndGrind"

echo "✅ Instance A (Motivation AI) configured:"
echo "   Device: $DEVICE_NAME"
echo "   UDID: $DEVICE_UDID"
echo "   Project: $PROJECT_PATH"
```

### For Instance B (save as `setup_rise_and_grind.sh`):
```bash
#!/bin/bash
# Get the iPhone 16 Pro UDID (not Max)
DEVICE_UDID=$(xcrun simctl list devices | grep "iPhone 16 Pro" | grep -v Max | head -1 | grep -o '[A-F0-9-]\{36\}')
export DEVICE_UDID=$DEVICE_UDID
export DEVICE_NAME="iPhone 16 Pro"
export PROJECT_PATH="/Users/truckirwin/Desktop/PROJECTS/Rise and Grind"
export APP_NAME="RiseAndGrind"

echo "✅ Instance B (Rise and Grind) configured:"
echo "   Device: $DEVICE_NAME"
echo "   UDID: $DEVICE_UDID"
echo "   Project: $PROJECT_PATH"
```

## 🔄 Emergency Reset Commands

If simulators get mixed up:

```bash
# Shutdown all simulators
xcrun simctl shutdown all

# Wait 5 seconds
sleep 5

# Each instance then runs their setup script and workflow
```

---

## 📋 Summary for Other Cursor Instance:

**Share this entire document with the other Cursor instance.** The key principles:

1. **Different Device Types**: iPhone 16 Pro Max vs iPhone 16 Pro
2. **Always Use UDIDs**: Never rely on device names alone
3. **Environment Variables**: Set device-specific variables every session
4. **Verification**: Always check what's running before operations
5. **Isolation**: Never use commands that affect "all" devices

This methodology ensures complete isolation between the two instances. 