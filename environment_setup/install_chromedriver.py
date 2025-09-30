#!/usr/bin/env python3
"""
Script to detect Google Chrome version and install matching ChromeDriver.
"""

import os
import platform
import re
import subprocess
import sys
import zipfile
from pathlib import Path
from urllib.request import urlopen, urlretrieve
import json


def get_chrome_version():
    """Detect the installed Chrome version based on the operating system."""
    system = platform.system()
    version = None
    
    try:
        if system == "Darwin":  # macOS
            # Try to get version from Chrome app
            chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            if os.path.exists(chrome_path):
                result = subprocess.check_output([chrome_path, "--version"], stderr=subprocess.STDOUT)
                version_string = result.decode('utf-8').strip()
                # Extract version number (e.g., "Google Chrome 117.0.5938.149")
                match = re.search(r'(\d+\.\d+\.\d+\.\d+)', version_string)
                if match:
                    version = match.group(1)
        
        elif system == "Linux":
            # Try multiple possible Chrome installations
            chrome_commands = [
                "google-chrome --version",
                "google-chrome-stable --version",
                "chromium --version",
                "chromium-browser --version"
            ]
            for cmd in chrome_commands:
                try:
                    result = subprocess.check_output(cmd.split(), stderr=subprocess.STDOUT)
                    version_string = result.decode('utf-8').strip()
                    match = re.search(r'(\d+\.\d+\.\d+\.\d+)', version_string)
                    if match:
                        version = match.group(1)
                        break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
        
        elif system == "Windows":
            # Check Windows registry for Chrome version
            import winreg
            paths = [
                r"SOFTWARE\Google\Chrome\BLBeacon",
                r"SOFTWARE\Wow6432Node\Google\Chrome\BLBeacon"
            ]
            for path in paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                    version, _ = winreg.QueryValueEx(key, "version")
                    winreg.CloseKey(key)
                    if version:
                        break
                except WindowsError:
                    continue
        
        else:
            print(f"Unsupported operating system: {system}")
            return None
    
    except Exception as e:
        print(f"Error detecting Chrome version: {e}")
        return None
    
    if version:
        print(f"Detected Chrome version: {version}")
        return version
    else:
        print("Could not detect Chrome version.")
        return None


def get_major_version(version_string):
    """Extract major version number from full version string."""
    if version_string:
        return version_string.split('.')[0]
    return None


def get_chromedriver_download_url(chrome_version):
    """
    Get the appropriate ChromeDriver download URL for the Chrome version.
    Uses the Chrome for Testing JSON endpoints for Chrome 115+.
    """
    major_version = int(get_major_version(chrome_version))
    system = platform.system()
    machine = platform.machine().lower()
    
    # Determine platform string
    if system == "Darwin":
        if machine == "arm64":
            platform_name = "mac-arm64"
        else:
            platform_name = "mac-x64"
    elif system == "Linux":
        if "64" in machine:
            platform_name = "linux64"
        else:
            print("32-bit Linux is not supported by recent ChromeDriver versions")
            return None
    elif system == "Windows":
        if "64" in machine or "amd64" in machine:
            platform_name = "win64"
        else:
            platform_name = "win32"
    else:
        print(f"Unsupported platform: {system}")
        return None
    
    try:
        if major_version >= 115:
            # Use Chrome for Testing endpoints for version 115+
            # First, get the exact version available
            api_url = f"https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone-with-downloads.json"
            
            print(f"Fetching ChromeDriver info for Chrome {major_version}...")
            with urlopen(api_url) as response:
                data = json.loads(response.read().decode())
                
            if str(major_version) in data.get('milestones', {}):
                milestone_data = data['milestones'][str(major_version)]
                downloads = milestone_data.get('downloads', {}).get('chromedriver', [])
                
                # Find the download for our platform
                for download in downloads:
                    if download['platform'] == platform_name:
                        download_url = download['url']
                        version = milestone_data['version']
                        print(f"Found ChromeDriver {version} for {platform_name}")
                        return download_url
                
                print(f"No ChromeDriver download found for platform: {platform_name}")
                return None
            else:
                print(f"Chrome version {major_version} not found in Chrome for Testing")
                return None
        
        else:
            # Use old ChromeDriver endpoints for versions < 115
            # Get the matching ChromeDriver version
            version_url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}"
            
            print(f"Fetching ChromeDriver version for Chrome {major_version}...")
            with urlopen(version_url) as response:
                chromedriver_version = response.read().decode().strip()
            
            print(f"Found ChromeDriver version: {chromedriver_version}")
            
            # Map platform to old naming convention
            if platform_name == "mac-arm64" or platform_name == "mac-x64":
                old_platform = "mac64"
            elif platform_name == "linux64":
                old_platform = "linux64"
            elif platform_name == "win64":
                old_platform = "win32"  # Old naming
            elif platform_name == "win32":
                old_platform = "win32"
            else:
                old_platform = platform_name
            
            download_url = f"https://chromedriver.storage.googleapis.com/{chromedriver_version}/chromedriver_{old_platform}.zip"
            return download_url
    
    except Exception as e:
        print(f"Error getting ChromeDriver download URL: {e}")
        return None


def download_and_extract_chromedriver(download_url, target_dir):
    """Download and extract ChromeDriver to the target directory."""
    try:
        zip_path = os.path.join(target_dir, "chromedriver.zip")
        
        print(f"Downloading ChromeDriver from: {download_url}")
        urlretrieve(download_url, zip_path)
        print("Download complete!")
        
        print("Extracting ChromeDriver...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extract all contents
            zip_ref.extractall(target_dir)
        
        # Clean up zip file
        os.remove(zip_path)
        
        # Find the chromedriver executable
        system = platform.system()
        chromedriver_name = "chromedriver.exe" if system == "Windows" else "chromedriver"
        
        # Look for chromedriver in extracted directories (new versions may be in subdirectories)
        chromedriver_path = None
        for root, dirs, files in os.walk(target_dir):
            if chromedriver_name in files:
                found_path = os.path.join(root, chromedriver_name)
                # If it's in a subdirectory, move it to the root
                if root != target_dir:
                    target_path = os.path.join(target_dir, chromedriver_name)
                    if os.path.exists(target_path):
                        os.remove(target_path)
                    os.rename(found_path, target_path)
                    chromedriver_path = target_path
                else:
                    chromedriver_path = found_path
                break
        
        if chromedriver_path:
            # Make executable on Unix-like systems
            if system != "Windows":
                os.chmod(chromedriver_path, 0o755)
            
            print(f"ChromeDriver installed successfully at: {chromedriver_path}")
            
            # Clean up any extracted directories
            for item in os.listdir(target_dir):
                item_path = os.path.join(target_dir, item)
                if os.path.isdir(item_path) and "chromedriver" in item.lower():
                    import shutil
                    shutil.rmtree(item_path)
            
            return chromedriver_path
        else:
            print("Error: Could not find chromedriver executable in the extracted files")
            return None
    
    except Exception as e:
        print(f"Error downloading/extracting ChromeDriver: {e}")
        return None


def main():
    """Main function to orchestrate the ChromeDriver installation."""
    print("=" * 60)
    print("ChromeDriver Installation Script")
    print("=" * 60)
    print()
    
    # Get the script's directory (project root)
    script_dir = Path(__file__).parent.parent.absolute()
    print(f"Target installation directory: {script_dir}")
    print()
    
    # Check if chromedriver already exists
    chromedriver_name = "chromedriver.exe" if platform.system() == "Windows" else "chromedriver"
    existing_chromedriver = script_dir / chromedriver_name
    
    if existing_chromedriver.exists():
        response = input(f"ChromeDriver already exists at {existing_chromedriver}. Replace it? (y/n): ")
        if response.lower() != 'y':
            print("Installation cancelled.")
            return
        os.remove(existing_chromedriver)
    
    # Detect Chrome version
    chrome_version = get_chrome_version()
    if not chrome_version:
        print("\nCould not detect Chrome version. Please ensure Google Chrome is installed.")
        sys.exit(1)
    
    print()
    
    # Get ChromeDriver download URL
    download_url = get_chromedriver_download_url(chrome_version)
    if not download_url:
        print("\nCould not find a matching ChromeDriver version.")
        sys.exit(1)
    
    print()
    
    # Download and install ChromeDriver
    installed_path = download_and_extract_chromedriver(download_url, str(script_dir))
    
    if installed_path:
        print()
        print("=" * 60)
        print("Installation complete! ✓")
        print("=" * 60)
        print(f"\nChromeDriver is ready to use at: {installed_path}")
    else:
        print("\nInstallation failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()

