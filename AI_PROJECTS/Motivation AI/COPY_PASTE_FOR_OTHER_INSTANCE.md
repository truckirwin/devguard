# 🔥 ONE-COMMAND SETUP FOR RISE AND GRIND INSTANCE

## 🚨 **URGENT: Copy-Paste This Into Your Terminal**

```bash
cd "/Users/truckirwin/Desktop/PROJECTS/Rise and Grind" && curl -s -o setup_rise_and_grind.sh "https://raw.githubusercontent.com/your-repo/main/setup_rise_and_grind.sh" 2>/dev/null || cat > setup_rise_and_grind.sh << 'EOF'
#!/bin/bash
echo "🚀 Setting up Rise and Grind Instance (Instance B)"
echo "================================================"
DEVICE_UDID=$(xcrun simctl list devices | grep "iPhone 16 Pro" | grep -v Max | head -1 | grep -o '[A-F0-9-]\{36\}')
if [ -z "$DEVICE_UDID" ]; then
    echo "❌ ERROR: iPhone 16 Pro not found!"
    xcrun simctl list devices available
    exit 1
fi
export DEVICE_UDID=$DEVICE_UDID
export DEVICE_NAME="iPhone 16 Pro"
export PROJECT_PATH="/Users/truckirwin/Desktop/PROJECTS/Rise and Grind"
export APP_NAME="RiseAndGrind"
echo "✅ Instance B (Rise and Grind) configured:"
echo "   Device: $DEVICE_NAME"
echo "   UDID: $DEVICE_UDID" 
echo "   Project: $PROJECT_PATH"
echo ""
echo "🔒 ISOLATION ACTIVE: This instance will ONLY use iPhone 16 Pro"
echo "⚠️  NEVER shutdown iPhone 16 Pro Max (that's for Motivation AI)"
echo ""
echo "🎯 Ready! Now run your simulator workflow."
EOF
chmod +x setup_rise_and_grind.sh && source setup_rise_and_grind.sh
```

## ✅ **Then Test the Isolation:**

```bash
echo "My device: $DEVICE_NAME ($DEVICE_UDID)" && xcrun simctl list devices | grep "Booted"
```

## 🎯 **Your Workflow (After Setup):**

```bash
# Run this every time you start working:
source setup_rise_and_grind.sh && xcrun simctl shutdown $DEVICE_UDID && xcodebuild clean -scheme RiseAndGrind && xcrun simctl boot $DEVICE_UDID && open -a Simulator --args -CurrentDeviceUDID $DEVICE_UDID && xcodebuild -scheme RiseAndGrind -destination "id=$DEVICE_UDID" build && xcrun simctl install $DEVICE_UDID "build/Release-iphonesimulator/RiseAndGrind.app" && xcrun simctl launch $DEVICE_UDID com.truckirwin.riseandgrind.app
```

---

## 🚨 **KEY RULES:**
- **YOU = iPhone 16 Pro ONLY**
- **Motivation AI = iPhone 16 Pro Max ONLY**  
- **NEVER use `xcrun simctl shutdown all`**
- **ALWAYS run `source setup_rise_and_grind.sh` first**

**That's it! This prevents all conflicts between our instances.** 🚀 