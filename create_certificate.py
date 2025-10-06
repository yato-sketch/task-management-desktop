#!/usr/bin/env python3
"""
Create a self-signed certificate for code signing the Windows executable
This helps reduce security warnings on Windows
"""

import os
import subprocess
import sys
from pathlib import Path

def create_self_signed_certificate():
    """Create a self-signed certificate for code signing"""
    
    print("🔐 Creating Self-Signed Certificate for Code Signing")
    print("=" * 55)
    
    cert_file = "taskmanager_cert.pfx"
    cert_name = "TaskManager Code Signing Certificate"
    
    # Check if OpenSSL is available
    try:
        result = subprocess.run(["openssl", "version"], capture_output=True, text=True)
        print(f"✓ OpenSSL found: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ OpenSSL not found. Installing...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyopenssl"], check=True)
            print("✓ PyOpenSSL installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyOpenSSL")
            return False
    
    # Create private key and certificate
    print("🔑 Generating private key and certificate...")
    
    # Create a simple certificate using OpenSSL
    openssl_cmd = [
        "openssl", "req", "-x509", "-newkey", "rsa:4096", "-keyout", "private.key",
        "-out", "certificate.crt", "-days", "365", "-nodes",
        "-subj", f"/C=US/ST=State/L=City/O=TaskManager/OU=Development/CN={cert_name}"
    ]
    
    try:
        subprocess.run(openssl_cmd, check=True, capture_output=True)
        print("✓ Certificate and private key created")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create certificate: {e}")
        return False
    
    # Convert to PFX format
    print("🔄 Converting to PFX format...")
    pfx_cmd = [
        "openssl", "pkcs12", "-export", "-out", cert_file,
        "-inkey", "private.key", "-in", "certificate.crt",
        "-passout", "pass:taskmanager123"
    ]
    
    try:
        subprocess.run(pfx_cmd, check=True, capture_output=True)
        print("✓ PFX certificate created")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create PFX: {e}")
        return False
    
    # Clean up temporary files
    for temp_file in ["private.key", "certificate.crt"]:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    print(f"✅ Certificate created: {cert_file}")
    print("🔐 Password: taskmanager123")
    print("\n📋 Next steps:")
    print("1. Import the certificate into Windows Certificate Store")
    print("2. Use it to sign the executable")
    print("3. Or use the unsigned version with manifest file")
    
    return True

def create_signing_script():
    """Create a script to sign the executable"""
    
    sign_script = """@echo off
echo Signing TaskManager.exe with certificate...
echo.

REM Check if certificate exists
if not exist "taskmanager_cert.pfx" (
    echo Error: Certificate file not found!
    echo Run create_certificate.py first.
    pause
    exit /b 1
)

REM Sign the executable
signtool sign /f taskmanager_cert.pfx /p taskmanager123 /t http://timestamp.digicert.com TaskManager.exe

if %errorLevel% == 0 (
    echo.
    echo ✅ Executable signed successfully!
    echo The security warning should be reduced.
) else (
    echo.
    echo ❌ Signing failed. Make sure signtool is available.
    echo You can also use the unsigned version with the manifest file.
)

echo.
pause
"""
    
    with open("sign_executable.bat", "w") as f:
        f.write(sign_script)
    
    print("📝 Created sign_executable.bat")

if __name__ == "__main__":
    if create_self_signed_certificate():
        create_signing_script()
        print("\n🎯 Certificate creation completed!")
    else:
        print("\n❌ Certificate creation failed.")
        sys.exit(1)
