## Evil-Droid Framework . version 0.3 
    Author: Mascerano Bachir [ dev-labs ]

## Legal Disclamer:
    The author does not hold any responsibility for the bad use of this tool,
    remember this is only for educational purpose.

## Description:
    Evil-Droid is a framework that create & generate & embed apk payload to penetrate android platforms
 
## Screenshot:
![pic1](https://i.imgur.com/LczO636.png)

![pic2](https://i.imgur.com/mhXxb5Q.png)

<br /><br />

## Dependencies :
    1 - metasploit-framework
	2 - xterm
	3 - Zenity
	4 - Aapt
	5 - Apktool
	6 - Zipalign

## Download/Config/Usage:
    1? - Download the tool from github
         git clone https://github.com/M4sc3r4n0/Evil-Droid.git

    2? - Set script execution permission
         cd Evil-Droid
         chmod +x evil-droid


    4?- Run Evil-Droid Framework :
       ./evil-droid
         see options bellow	   

## Standalone APK Generator

A new Python-based standalone APK generator is now available. This tool creates functional Android APK applications without requiring the full Metasploit framework.

### Quick Start

```bash
# Install dependencies (Ubuntu/Debian)
sudo apt-get install -y aapt zipalign smali openjdk-17-jdk

# Generate an APK
python3 generate_apk.py --name MyApp --package com.example.myapp

# The APK will be created in ./evilapk/MyApp.apk
```

### Usage Options

```
python3 generate_apk.py [options]

Options:
  -n, --name NAME        Application name (default: EvilDroidApp)
  -p, --package PACKAGE  Package name (default: com.evildroid.app)
  -o, --output OUTPUT    Output directory (default: ./evilapk/)
  -v, --verbose          Verbose output
  -h, --help             Show help message
```

### Examples

```bash
# Generate with custom name and package
python3 generate_apk.py -n TestApp -p com.test.app

# Specify output directory
python3 generate_apk.py -n MyApp -p com.mycompany.app -o ./output/

# Install on connected Android device
adb install ./evilapk/MyApp.apk
```

### Requirements for Standalone Generator

- Python 3.6+
- Android SDK build tools (aapt, zipalign)
- Smali assembler
- Java JDK (keytool, jarsigner)

## video tutorial: 
https://www.youtube.com/watch?v=8u-NHeTdPRE&feature=share old version
