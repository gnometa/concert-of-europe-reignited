#!/usr/bin/env python3
"""
Build script for V2LocKit
=========================

Creates a standalone executable using PyInstaller.

Usage:
    python scripts/build.py
"""

import subprocess
import sys
from pathlib import Path


def main():
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    print("=" * 60)
    print("V2LocKit Build Script")
    print("=" * 60)
    
    # Check PyInstaller is installed
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Build command
    spec_file = script_dir / "v2lockit.spec"
    
    if spec_file.exists():
        print(f"Using spec file: {spec_file}")
        cmd = [sys.executable, "-m", "PyInstaller", str(spec_file), "--clean"]
    else:
        print("No spec file found, using default settings...")
        main_py = project_root / "src" / "v2lockit" / "main.py"
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            "--name", "V2LocKit",
            "--clean",
            str(main_py)
        ]
    
    print(f"Running: {' '.join(cmd)}")
    print()
    
    # Run PyInstaller
    result = subprocess.run(cmd, cwd=project_root)
    
    if result.returncode == 0:
        print()
        print("=" * 60)
        print("BUILD SUCCESSFUL!")
        print("=" * 60)
        dist_dir = project_root / "dist"
        exe_file = dist_dir / "V2LocKit.exe"
        if exe_file.exists():
            print(f"Executable: {exe_file}")
            print(f"Size: {exe_file.stat().st_size / 1024 / 1024:.1f} MB")
    else:
        print()
        print("BUILD FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    main()
