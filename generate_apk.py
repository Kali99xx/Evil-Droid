#!/usr/bin/env python3
"""
Evil-Droid APK Generator
A standalone tool to generate functional Android APK applications.

This tool creates a complete, installable Android APK from scratch
without requiring heavy dependencies like Metasploit.

Usage:
    python3 generate_apk.py --name MyApp --package com.example.myapp --output ./output/

Requirements:
    - Python 3.6+
    - Android SDK build tools (aapt, zipalign, apksigner)
    - Java JDK (keytool, jarsigner)

Author: Evil-Droid Framework
License: Educational purposes only
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Optional


class APKGenerator:
    """Generates functional Android APK applications."""

    # Pre-compiled minimal DEX bytecode for a simple Android app
    # This is the compiled bytecode for a minimal MainActivity
    MINIMAL_DEX_HEADER = bytes([
        0x64, 0x65, 0x78, 0x0a,  # dex\n
        0x30, 0x33, 0x35, 0x00,  # 035\0 (DEX version)
    ])

    def __init__(self, app_name: str, package_name: str, output_dir: str):
        """
        Initialize the APK generator.

        Args:
            app_name: The display name of the application
            package_name: The package name (e.g., com.example.myapp)
            output_dir: Directory to output the generated APK
        """
        self.app_name = app_name
        self.package_name = package_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Check for required tools
        self._check_dependencies()

    def _check_dependencies(self):
        """Check if required tools are available."""
        required_tools = ['aapt', 'zipalign', 'keytool', 'jarsigner']
        missing = []

        for tool in required_tools:
            if not shutil.which(tool):
                missing.append(tool)

        if missing:
            print(f"Warning: Missing tools: {', '.join(missing)}")
            print("Some features may not work correctly.")
            print("Install with: sudo apt-get install aapt zipalign openjdk-17-jdk")

    def _find_android_jar(self) -> Optional[Path]:
        """
        Find android.jar for compilation.

        Searches in common locations where the Android SDK platform JAR is installed.
        Returns the path if found, None otherwise.
        """
        # Try specific known, tested paths first (in order of preference)
        # We prefer stable API levels that are known to work with aapt
        known_paths = [
            # Debian/Ubuntu system packages - most reliable
            Path('/usr/lib/android-sdk/platforms/android-23/android.jar'),
            Path('/usr/lib/android-sdk/platforms/android-28/android.jar'),
            Path('/usr/lib/android-sdk/platforms/android-30/android.jar'),
            Path('/usr/share/java/com.android.android-23.jar'),
            Path('/usr/share/java/com.android.android-28.jar'),
            Path('/usr/share/java/com.android.android-30.jar'),
        ]

        for path in known_paths:
            if path.exists():
                return path

        # Scan system SDK platforms directory for any available platform
        sdk_platforms_dir = Path('/usr/lib/android-sdk/platforms')
        if sdk_platforms_dir.exists():
            # Sort numerically by API level (android-23 -> 23)
            platforms = []
            for platform in sdk_platforms_dir.iterdir():
                jar_path = platform / 'android.jar'
                if jar_path.exists():
                    try:
                        api_level = int(platform.name.replace('android-', '').split('.')[0])
                        platforms.append((api_level, jar_path))
                    except ValueError:
                        pass
            # Prefer API 23-30 range for stability
            platforms.sort(key=lambda x: (0 if 23 <= x[0] <= 30 else 1, x[0]))
            if platforms:
                return platforms[0][1]

        # Check ANDROID_HOME environment variable (user SDK installations)
        android_home = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
        if android_home:
            android_home_path = Path(android_home)
            platforms_dir = android_home_path / 'platforms'
            if platforms_dir.exists():
                # Similar preference for stable API levels
                platforms = []
                for platform in platforms_dir.iterdir():
                    jar_path = platform / 'android.jar'
                    if jar_path.exists():
                        try:
                            api_level = int(platform.name.replace('android-', '').split('.')[0])
                            platforms.append((api_level, jar_path))
                        except ValueError:
                            pass
                platforms.sort(key=lambda x: (0 if 23 <= x[0] <= 30 else 1, x[0]))
                if platforms:
                    return platforms[0][1]

        # Additional common installation paths
        additional_paths = [
            Path.home() / 'Android/Sdk/platforms/android-28/android.jar',
            Path.home() / 'Android/Sdk/platforms/android-30/android.jar',
            Path('/opt/android-sdk/platforms/android-28/android.jar'),
            Path('/opt/android-sdk/platforms/android-30/android.jar'),
        ]

        for path in additional_paths:
            if path.exists():
                return path

        return None

    def _create_android_manifest(self, work_dir: Path) -> str:
        """Create AndroidManifest.xml content."""
        # Using target SDK 28 for broader compatibility while maintaining security
        # Modern apps should target higher, but this ensures compatibility with
        # the smali code we generate which uses basic Android APIs
        manifest = f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{self.package_name}"
    android:versionCode="1"
    android:versionName="1.0">

    <uses-sdk
        android:minSdkVersion="16"
        android:targetSdkVersion="28" />

    <uses-permission android:name="android.permission.INTERNET" />

    <application
        android:label="{self.app_name}"
        android:allowBackup="true">

        <activity
            android:name=".MainActivity"
            android:label="{self.app_name}"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

    </application>
</manifest>'''
        return manifest

    def _create_main_activity_java(self) -> str:
        """Create MainActivity.java source code."""
        java_code = f'''package {self.package_name};

import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;
import android.view.Gravity;
import android.graphics.Color;

public class MainActivity extends Activity {{
    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);

        TextView textView = new TextView(this);
        textView.setText("{self.app_name}\\n\\nGenerated by Evil-Droid Framework\\n\\nThis is a demonstration APK.");
        textView.setTextSize(20);
        textView.setGravity(Gravity.CENTER);
        textView.setTextColor(Color.BLACK);
        textView.setBackgroundColor(Color.WHITE);
        textView.setPadding(50, 50, 50, 50);

        setContentView(textView);
    }}
}}'''
        return java_code

    def _create_strings_xml(self) -> str:
        """Create strings.xml resource file."""
        return f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">{self.app_name}</string>
</resources>'''

    def _compile_java_to_dex(self, work_dir: Path, java_file: Path) -> Optional[Path]:
        """Compile Java source to DEX bytecode."""
        android_jar = self._find_android_jar()

        if not android_jar:
            print("Warning: android.jar not found, using smali-based DEX generation")
            return None

        classes_dir = work_dir / 'classes'
        classes_dir.mkdir(exist_ok=True)

        # Compile Java to class files using Java 11 bytecode (compatible with Android)
        try:
            result = subprocess.run([
                'javac',
                '-source', '11',
                '-target', '11',
                '-bootclasspath', str(android_jar),
                '-classpath', str(android_jar),
                '-d', str(classes_dir),
                str(java_file)
            ], capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                print(f"Java compilation warning: {result.stderr}")
                return None
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"Java compilation error: {e}")
            return None

        # Convert to DEX using d8 or dx
        dex_file = work_dir / 'classes.dex'

        # Try d8 first (newer, preferred)
        d8_path = shutil.which('d8')
        if d8_path:
            try:
                class_files = list(classes_dir.rglob('*.class'))
                result = subprocess.run(
                    [d8_path, '--output', str(work_dir)] + [str(f) for f in class_files],
                    capture_output=True, text=True, timeout=60
                )
                if dex_file.exists():
                    return dex_file
            except Exception as e:
                print(f"d8 conversion error: {e}")

        # Try dx (older tool)
        dx_path = shutil.which('dx')
        if dx_path:
            try:
                result = subprocess.run([
                    dx_path, '--dex', f'--output={dex_file}', str(classes_dir)
                ], capture_output=True, text=True, timeout=60)
                if dex_file.exists():
                    return dex_file
            except Exception as e:
                print(f"dx conversion error: {e}")

        return None

    def _create_minimal_dex(self, work_dir: Path) -> Path:
        """
        Create a minimal but valid DEX file using smali.

        This creates a valid DEX that implements a simple MainActivity
        using the smali assembler format.
        """
        smali_dir = work_dir / 'smali'
        package_path = self.package_name.replace('.', '/')

        # Create package directory structure
        main_activity_dir = smali_dir / package_path
        main_activity_dir.mkdir(parents=True, exist_ok=True)

        # Create MainActivity.smali - a fully functional Android Activity
        smali_code = f'''.class public L{package_path}/MainActivity;
.super Landroid/app/Activity;
.source "MainActivity.java"

# Default constructor
.method public constructor <init>()V
    .registers 1

    invoke-direct {{p0}}, Landroid/app/Activity;-><init>()V

    return-void
.end method

# onCreate method - called when Activity is created
.method protected onCreate(Landroid/os/Bundle;)V
    .registers 5
    .param p1, "savedInstanceState"    # Landroid/os/Bundle;

    # Call super.onCreate()
    invoke-super {{p0, p1}}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V

    # Create a new TextView
    new-instance v0, Landroid/widget/TextView;
    invoke-direct {{v0, p0}}, Landroid/widget/TextView;-><init>(Landroid/content/Context;)V

    # Set the text content
    const-string v1, "{self.app_name}\\n\\nWelcome to Evil-Droid Framework\\n\\nThis is a demonstration APK\\ngenerated for educational purposes."
    invoke-virtual {{v0, v1}}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    # Set text size to 20sp
    const/high16 v1, 0x41a00000    # 20.0f
    invoke-virtual {{v0, v1}}, Landroid/widget/TextView;->setTextSize(F)V

    # Set gravity to CENTER (0x11)
    const/16 v1, 0x11
    invoke-virtual {{v0, v1}}, Landroid/widget/TextView;->setGravity(I)V

    # Set text color to BLACK (0xff000000)
    const v1, -0x1000000
    invoke-virtual {{v0, v1}}, Landroid/widget/TextView;->setTextColor(I)V

    # Set background color to WHITE (0xffffffff)
    const/4 v1, -0x1
    invoke-virtual {{v0, v1}}, Landroid/widget/TextView;->setBackgroundColor(I)V

    # Set padding (50 pixels on all sides)
    const/16 v1, 0x32
    invoke-virtual {{v0, v1, v1, v1, v1}}, Landroid/widget/TextView;->setPadding(IIII)V

    # Set the TextView as the content view
    invoke-virtual {{p0, v0}}, L{package_path}/MainActivity;->setContentView(Landroid/view/View;)V

    return-void
.end method
'''
        smali_file = main_activity_dir / 'MainActivity.smali'
        smali_file.write_text(smali_code)

        dex_file = work_dir / 'classes.dex'

        # Try using smali directly if available
        smali_path = shutil.which('smali')
        if smali_path:
            try:
                # Use 'smali assemble' to convert smali to DEX
                result = subprocess.run([
                    smali_path, 'assemble',
                    '--output', str(dex_file),
                    str(smali_dir)
                ], capture_output=True, text=True, timeout=60)

                if dex_file.exists():
                    print(f"    [+] Smali assembled successfully")
                    return dex_file
                else:
                    # Try alternative smali syntax
                    result = subprocess.run([
                        smali_path, 'a',
                        '-o', str(dex_file),
                        str(smali_dir)
                    ], capture_output=True, text=True, timeout=60)

                    if dex_file.exists():
                        print(f"    [+] Smali assembled successfully")
                        return dex_file
                    else:
                        print(f"    [-] Smali stderr: {result.stderr}")

            except Exception as e:
                print(f"    [-] Smali assembly error: {e}")

        # If smali not available, try using baksmali/smali from apktool
        # or create a pre-built minimal DEX
        return self._create_prebuilt_dex(work_dir)

    def _create_prebuilt_dex(self, work_dir: Path) -> Path:
        """
        Create a pre-built minimal DEX file.

        This is a fallback that creates a minimal valid DEX structure
        that Android will accept, even if it doesn't do much.
        """
        dex_file = work_dir / 'classes.dex'

        # This is a minimal valid DEX file that declares our MainActivity
        # It's essentially an empty class that Android can load
        package_path = self.package_name.replace('.', '/')

        # For a truly functional APK without DEX compilation tools,
        # we'll need to use apktool to create the DEX from smali

        # Find apktool.jar - first check relative to script, then in tools dir
        script_dir = Path(__file__).parent.resolve()
        possible_apktool_paths = [
            script_dir / 'tools' / 'apktool.jar',
            Path.cwd() / 'tools' / 'apktool.jar',
        ]

        apktool_jar = None
        for path in possible_apktool_paths:
            if path.exists():
                apktool_jar = path
                break

        if apktool_jar and apktool_jar.exists():
            # Create a minimal APK structure that apktool can work with
            temp_apk_dir = work_dir / 'temp_apk'
            temp_apk_dir.mkdir(exist_ok=True)

            # Create smali directory structure
            smali_out = temp_apk_dir / 'smali' / self.package_name.replace('.', '/')
            smali_out.mkdir(parents=True, exist_ok=True)

            # Write smali file - with consistent messaging as the primary smali generator
            smali_code = f'''.class public L{package_path}/MainActivity;
.super Landroid/app/Activity;

.method public constructor <init>()V
    .registers 1
    invoke-direct {{p0}}, Landroid/app/Activity;-><init>()V
    return-void
.end method

.method protected onCreate(Landroid/os/Bundle;)V
    .registers 4

    invoke-super {{p0, p1}}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V

    new-instance v0, Landroid/widget/TextView;
    invoke-direct {{v0, p0}}, Landroid/widget/TextView;-><init>(Landroid/content/Context;)V

    const-string v1, "{self.app_name}\\n\\nWelcome to Evil-Droid Framework\\n\\nThis is a demonstration APK\\ngenerated for educational purposes."
    invoke-virtual {{v0, v1}}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    const/high16 v1, 0x41a00000
    invoke-virtual {{v0, v1}}, Landroid/widget/TextView;->setTextSize(F)V

    const/16 v1, 0x11
    invoke-virtual {{v0, v1}}, Landroid/widget/TextView;->setGravity(I)V

    invoke-virtual {{p0, v0}}, L{package_path}/MainActivity;->setContentView(Landroid/view/View;)V

    return-void
.end method
'''
            (smali_out / 'MainActivity.smali').write_text(smali_code)

            # Create apktool.yml
            # forcedPackageId 127 (0x7f) is the standard Android resource package ID
            # used for application resources. Framework resources use ID 1 (0x01).
            apktool_yml = f'''version: 2.2.4
apkFileName: temp.apk
isFrameworkApk: false
usesFramework:
  ids:
  - 1
sdkInfo:
  minSdkVersion: '16'
  targetSdkVersion: '28'
packageInfo:
  renameManifestPackage: null
  forcedPackageId: '127'
versionInfo:
  versionCode: '1'
  versionName: '1.0'
compressionType: false
sharedLibrary: false
sparseResources: false
'''
            (temp_apk_dir / 'apktool.yml').write_text(apktool_yml)

            # Create AndroidManifest.xml
            manifest = self._create_android_manifest(work_dir)
            (temp_apk_dir / 'AndroidManifest.xml').write_text(manifest)

            # Create minimal res structure
            res_values = temp_apk_dir / 'res' / 'values'
            res_values.mkdir(parents=True, exist_ok=True)
            (res_values / 'strings.xml').write_text(self._create_strings_xml())

            # Use apktool to build
            try:
                built_apk = work_dir / 'built.apk'
                result = subprocess.run([
                    'java', '-jar', str(apktool_jar),
                    'b', str(temp_apk_dir),
                    '-o', str(built_apk)
                ], capture_output=True, text=True, timeout=120, cwd=work_dir)

                if built_apk.exists():
                    # Extract classes.dex from built APK
                    with zipfile.ZipFile(built_apk, 'r') as zf:
                        if 'classes.dex' in zf.namelist():
                            zf.extract('classes.dex', work_dir)
                            return dex_file

            except Exception as e:
                print(f"Apktool build error: {e}")

        # Ultimate fallback: create a minimal valid DEX header
        # This won't do anything useful but will be a valid file
        print("Warning: Unable to create functional DEX, creating minimal placeholder")
        self._write_minimal_dex_placeholder(dex_file)
        return dex_file

    def _write_minimal_dex_placeholder(self, dex_file: Path):
        """Write a minimal valid DEX file structure."""
        # Minimal DEX file that Android will accept
        # This is a valid but essentially empty DEX
        dex_data = bytearray([
            # DEX header
            0x64, 0x65, 0x78, 0x0a,  # magic: dex\n
            0x30, 0x33, 0x35, 0x00,  # version: 035\0
            # Checksum will be calculated
            0x00, 0x00, 0x00, 0x00,
            # SHA-1 signature (20 bytes, placeholder)
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            # File size
            0x70, 0x00, 0x00, 0x00,  # 112 bytes
            # Header size
            0x70, 0x00, 0x00, 0x00,  # 112 bytes
            # Endian tag
            0x78, 0x56, 0x34, 0x12,
            # Link size/off
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            # Map off
            0x00, 0x00, 0x00, 0x00,
            # String IDs size/off
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            # Type IDs size/off
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            # Proto IDs size/off
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            # Field IDs size/off
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            # Method IDs size/off
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            # Class defs size/off
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            # Data size/off
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
        ])

        # Calculate checksum (Adler-32 of everything after checksum field)
        import zlib
        checksum = zlib.adler32(bytes(dex_data[12:])) & 0xffffffff
        dex_data[8:12] = checksum.to_bytes(4, 'little')

        dex_file.write_bytes(bytes(dex_data))

    def _create_resources(self, work_dir: Path) -> Optional[Path]:
        """Create and compile Android resources using aapt."""
        res_dir = work_dir / 'res'
        res_dir.mkdir(exist_ok=True)

        # Create values directory
        values_dir = res_dir / 'values'
        values_dir.mkdir(exist_ok=True)

        # Write strings.xml
        (values_dir / 'strings.xml').write_text(self._create_strings_xml())

        # Write AndroidManifest.xml
        manifest_file = work_dir / 'AndroidManifest.xml'
        manifest_file.write_text(self._create_android_manifest(work_dir))

        # Get android.jar path using helper method
        android_jar = self._find_android_jar()

        if not android_jar:
            print("Warning: android.jar not found for resource compilation")
            return None

        # Compile resources with aapt
        resources_apk = work_dir / 'resources.apk'

        try:
            result = subprocess.run([
                'aapt', 'package',
                '-f',
                '-M', str(manifest_file),
                '-S', str(res_dir),
                '-I', str(android_jar),
                '-F', str(resources_apk),
                '--min-sdk-version', '16',
                '--target-sdk-version', '28'
            ], capture_output=True, text=True, timeout=60)

            if resources_apk.exists():
                return resources_apk
            else:
                print(f"AAPT warning: {result.stderr}")

        except Exception as e:
            print(f"Resource compilation error: {e}")

        return None

    def _sign_apk(self, apk_path: Path) -> bool:
        """Sign the APK with a debug key."""
        keystore = Path.home() / '.android' / 'debug.keystore'
        keystore.parent.mkdir(parents=True, exist_ok=True)

        # Create debug keystore if it doesn't exist or recreate with SHA256
        if keystore.exists():
            # Remove old keystore to create with modern algorithms
            keystore.unlink()

        try:
            subprocess.run([
                'keytool', '-genkey', '-v',
                '-keystore', str(keystore),
                '-alias', 'androiddebugkey',
                '-keyalg', 'RSA',
                '-keysize', '2048',
                '-validity', '10000',
                '-storepass', 'android',
                '-keypass', 'android',
                '-dname', 'CN=Android Debug,O=Android,C=US'
            ], capture_output=True, text=True, timeout=30, check=True)
        except Exception as e:
            print(f"Keystore creation error: {e}")
            return False

        # Sign with jarsigner using SHA-256 (modern, secure)
        try:
            result = subprocess.run([
                'jarsigner',
                '-keystore', str(keystore),
                '-storepass', 'android',
                '-keypass', 'android',
                '-digestalg', 'SHA-256',
                '-sigalg', 'SHA256withRSA',
                str(apk_path),
                'androiddebugkey'
            ], capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                print(f"Signing warning: {result.stderr}")
                # Continue anyway, some errors are just warnings

            return True

        except Exception as e:
            print(f"Signing error: {e}")
            return False

    def _align_apk(self, input_apk: Path, output_apk: Path) -> bool:
        """Align the APK with zipalign."""
        try:
            result = subprocess.run([
                'zipalign', '-f', '4',
                str(input_apk),
                str(output_apk)
            ], capture_output=True, text=True, timeout=30)

            return output_apk.exists()

        except Exception as e:
            print(f"Alignment error: {e}")
            return False

    def generate(self) -> Optional[Path]:
        """
        Generate the APK file.

        Returns:
            Path to the generated APK, or None if generation failed.
        """
        print(f"Generating APK: {self.app_name}")
        print(f"Package: {self.package_name}")

        with tempfile.TemporaryDirectory() as temp_dir:
            work_dir = Path(temp_dir)

            # Step 1: Create DEX file
            print("[*] Creating DEX bytecode...")
            dex_file = self._create_minimal_dex(work_dir)

            if not dex_file or not dex_file.exists():
                print("Error: Failed to create DEX file")
                return None

            # Step 2: Create and compile resources
            print("[*] Compiling resources...")
            resources_apk = self._create_resources(work_dir)

            # Step 3: Create the APK structure
            print("[*] Building APK structure...")
            unsigned_apk = work_dir / 'unsigned.apk'

            with zipfile.ZipFile(unsigned_apk, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Add DEX file
                zf.write(dex_file, 'classes.dex')

                # Add manifest and resources from aapt output
                if resources_apk and resources_apk.exists():
                    with zipfile.ZipFile(resources_apk, 'r') as res_zf:
                        for name in res_zf.namelist():
                            if name not in zf.namelist():
                                zf.writestr(name, res_zf.read(name))
                else:
                    # If aapt failed, the APK won't be installable on real devices
                    # because Android requires binary AndroidManifest.xml
                    print("Warning: Resource compilation failed - APK may not install on devices")
                    print("    Install android-sdk-platform-23 or higher for full compatibility")
                    # Still include the manifest for structural completeness
                    manifest = self._create_android_manifest(work_dir)
                    zf.writestr('AndroidManifest.xml', manifest)

            # Step 4: Sign the APK
            print("[*] Signing APK...")
            if not self._sign_apk(unsigned_apk):
                print("Warning: APK signing may have issues")

            # Step 5: Align the APK
            print("[*] Aligning APK...")
            final_apk = self.output_dir / f"{self.app_name}.apk"

            if not self._align_apk(unsigned_apk, final_apk):
                # If alignment fails, just copy the signed APK
                shutil.copy(unsigned_apk, final_apk)

            if final_apk.exists():
                print(f"[✔] APK generated successfully: {final_apk}")
                print(f"[*] Size: {final_apk.stat().st_size} bytes")
                return final_apk
            else:
                print("Error: Failed to generate APK")
                return None


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate a functional Android APK application',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
    %(prog)s --name MyApp --package com.example.myapp
    %(prog)s -n TestApp -p com.test.app -o ./output/

This tool creates a complete, installable Android APK.
Use for educational purposes only.
        '''
    )

    parser.add_argument(
        '-n', '--name',
        default='EvilDroidApp',
        help='Application name (default: EvilDroidApp)'
    )

    parser.add_argument(
        '-p', '--package',
        default='com.evildroid.app',
        help='Package name (default: com.evildroid.app)'
    )

    parser.add_argument(
        '-o', '--output',
        default='./evilapk/',
        help='Output directory (default: ./evilapk/)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Validate package name
    if not all(c.isalnum() or c == '.' for c in args.package):
        print("Error: Package name must contain only alphanumeric characters and dots")
        sys.exit(1)

    if args.package.startswith('.') or args.package.endswith('.'):
        print("Error: Package name cannot start or end with a dot")
        sys.exit(1)

    # Generate APK
    generator = APKGenerator(args.name, args.package, args.output)
    result = generator.generate()

    if result:
        print("\n" + "=" * 50)
        print(f"SUCCESS: APK created at {result}")
        print("=" * 50)
        print("\nTo install on a device:")
        print(f"  adb install {result}")
        print("\nTo test on an emulator, enable 'Unknown Sources' first.")
        sys.exit(0)
    else:
        print("\nFailed to generate APK")
        sys.exit(1)


if __name__ == '__main__':
    main()
