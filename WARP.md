# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Evil-Droid is a bash-based Android penetration testing framework (v0.3) that creates, generates, and embeds APK payloads for Android platform security testing. This is an educational security research tool.

**Author:** Mascerano Bachir (dev-labs.co)

## System Requirements

This framework requires:
- Root privileges to run
- Active internet connection (checked at startup)
- Linux environment (designed for Kali/Debian-based systems)

## Dependencies

The following tools are automatically checked and installed if missing:
1. **metasploit-framework** - Payload generation and listener
2. **xterm** - Terminal emulator for separate processes
3. **zenity** - GUI dialog boxes for user input
4. **aapt** - Android Asset Packaging Tool
5. **apktool** - APK decompilation/recompilation (also included in `tools/apktool.jar`)
6. **zipalign** - APK optimization tool

## Running the Framework

```bash
# Make script executable (first time only)
chmod +x evil-droid

# Run the framework (requires root)
sudo ./evil-droid
```

The framework will:
1. Check internet connectivity
2. Verify/install all dependencies
3. Start Apache and PostgreSQL services
4. Present an interactive menu

## Core Architecture

### Main Script Structure

The `evil-droid` bash script (872 lines) is organized as follows:

1. **Initialization (lines 1-220)**
   - Color definitions for terminal output
   - Root privilege check
   - Internet connectivity verification
   - Dependency checking and auto-installation
   - Path and variable setup

2. **Core Functions (lines 221-710)**
   - `gen_payload()` - Generate standalone MSF payload APKs
   - `embed_payload()` - Embed payload into original APK (old method)
   - `apk_decomp()` / `apk_comp()` - Decompile/recompile payload APKs
   - `apk_decomp1()` / `apk_comp1()` - Decompile/recompile original APKs
   - `perms()` - Add Android permissions to AndroidManifest.xml
   - `hook_smalies()` - Inject payload execution into original APK smali code
   - `flagg()` / `flagg_original()` - Obfuscate payload to bypass AV detection
   - `sign()` - Sign APK with Android debug keystore
   - `listener()` - Launch Metasploit multi/handler
   - Service management functions for Apache and PostgreSQL

3. **Main Menu (lines 731-872)**
   - Option 1: Generate MSF payload APK
   - Option 2: Backdoor original APK (old method using msfvenom -x)
   - Option 3: Backdoor original APK (new method with smali injection)
   - Option 4: Bypass AV with obfuscation and custom icons
   - Option 5: Start Metasploit listener
   - c: Clean output directory
   - q: Quit

### Key Technical Workflows

**Backdoor Injection Process (Option 3 - NEW method):**
1. Generate MSF payload APK with msfvenom
2. Decompile original APK using apktool
3. Decompile payload APK
4. Inject permissions into original AndroidManifest.xml
5. Copy payload smali files into original APK structure
6. Hook payload execution into launcher activity's smali code
7. Recompile backdoored APK
8. Sign with debug keystore
9. Align APK with zipalign

**AV Bypass Obfuscation (Option 4):**
- Renames smali directories and files with random 10-char strings (VAR1-VAR8)
- Obfuscates package names: `com.metasploit.stage` → `com.$VAR1.$VAR2`
- Renames key classes: `Payload.smali` → `$VAR3.smali`
- Supports custom icon replacement to change APK appearance

### Output Directory

Generated APKs are stored in: `./evilapk/`

### Services Management

The framework manages system services:
- **Apache2** - Used for hosting APKs via attack vector feature
- **PostgreSQL** - Required by Metasploit Framework
- Both are started at initialization and stopped on exit/error

### Error Handling

- `error()` - Handles APK rebuild failures, stops services and exits
- `error0()` - General error handler for other operations
- `ctrl_c()` - Graceful shutdown on Ctrl+C interrupt

## Development Notes

### Smali Injection Mechanism

The framework locates the main launcher activity by:
1. Finding `android.intent.category.LAUNCHER` in AndroidManifest.xml
2. Extracting the associated activity name or application name
3. Locating the corresponding `.smali` file
4. Injecting `invoke-static` call to `MainService;->start()V` at first `return-void` instruction
5. Falls back to alternative activities if primary injection fails

### Random Variable Generation

Obfuscation uses `/dev/urandom` to generate random strings:
```bash
VAR1=$(cat /dev/urandom | tr -cd 'a-z' | head -c 10)
```
These replace predictable strings like "metasploit", "payload", "stage" in smali code.

### Android Permissions

The framework injects comprehensive permissions for full device access:
- Network (INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE)
- Location (ACCESS_COARSE_LOCATION, ACCESS_FINE_LOCATION)
- Phone (READ_PHONE_STATE, CALL_PHONE, READ_CALL_LOG, WRITE_CALL_LOG)
- SMS (SEND_SMS, RECEIVE_SMS, READ_SMS)
- Storage (WRITE_EXTERNAL_STORAGE, CAMERA)
- Other (RECORD_AUDIO, READ_CONTACTS, WRITE_CONTACTS, RECEIVE_BOOT_COMPLETED)

### Attack Vector Feature

The clone website feature:
1. Downloads target website with wget
2. Injects invisible iframe pointing to APK
3. Auto-redirects after 15 seconds
4. Hosts via Apache at `/var/www/html/`

## Security and Ethics

This is an educational security research tool. The framework includes disclaimers about ethical use and VirusTotal submission warnings. Use only on systems you own or have explicit permission to test.
