#!/usr/bin/env python3
"""

                                                                                                          
   █████╗ ██████╗ ██╗  ██╗     ██████╗██████╗ ██╗   ██╗                 
  ██╔══██╗██╔══██╗██║ ██╔╝    ██╔════╝██╔══██╗╚██╗ ██╔╝                 
  ███████║██████╔╝█████╔╝     ██║     ██████╔╝ ╚████╔╝                  
  ██╔══██║██╔═══╝ ██╔═██╗     ██║     ██╔══██╗  ╚██╔╝                   
  ██║  ██║██║     ██║  ██╗    ╚██████╗██║  ██║   ██║                    
  ╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝     ╚═════╝╚═╝  ╚═╝   ╚═╝                                                                
"""

import os
import sys
import subprocess
import platform
import shutil
import time
import urllib.request
import zipfile
import tempfile
import json
import hashlib
import socket
from pathlib import Path
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================
APP_NAME = "APK CRYPTER PRO"
APP_VERSION = "2.0"
APP_CODENAME = "BASIC"
MAIN_SCRIPT = "src/apk-cry.py"

# ============================================================================
# COLOR SYSTEM
# ============================================================================
class Colors:
    """ANSI color codes for terminal output"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    HIDDEN = "\033[8m"
    
    # Regular Colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"
    
    # Bright Colors
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Background Colors
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    BG_BLACK = "\033[40m"

C = Colors()

# ============================================================================
# ASCII ART & ANIMATIONS
# ============================================================================
class Banners:
    """ASCII art banners and animations"""
    
    @staticmethod
    def print_nexus_banner():
        """Print the main Nexus banner"""
        banner = f"""
{C.BRIGHT_RED}{C.BOLD}
    
                                                                          
   █████╗ ██████╗ ██╗  ██╗     ██████╗██████╗ ██╗   ██╗                 
  ██╔══██╗██╔══██╗██║ ██╔╝    ██╔════╝██╔══██╗╚██╗ ██╔╝                 
  ███████║██████╔╝█████╔╝     ██║     ██████╔╝ ╚████╔╝                  
  ██╔══██║██╔═══╝ ██╔═██╗     ██║     ██╔══██╗  ╚██╔╝                   
  ██║  ██║██║     ██║  ██╗    ╚██████╗██║  ██║   ██║                    
  ╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝     ╚═════╝╚═╝  ╚═╝   ╚═╝               
                                                                         
    {C.BRIGHT_YELLOW}APK CRYPTER v{APP_VERSION}{C.BRIGHT_RED}                        
    {C.BRIGHT_CYAN}{APP_CODENAME} PROTOCOL{C.BRIGHT_RED}                                  

    {C.RESET}"""
        print(banner)
    
    @staticmethod
    def print_installer_header():
        """Print installer header"""
        header = f"""
{C.BRIGHT_CYAN}{C.BOLD}

                                                                         
       ██╗███╗   ██╗███████╗████████╗ █████╗ ██╗     ██╗                   
       ██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██║     ██║                   
       ██║██╔██╗ ██║███████╗   ██║   ███████║██║     ██║                   
       ██║██║╚██╗██║╚════██║   ██║   ██╔══██║██║     ██║                  
       ██║██║ ╚████║███████║   ██║   ██║  ██║███████╗███████╗              
       ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝              
                                                                          
                  {C.BRIGHT_YELLOW}SMART AUTO-INSTALLER v2.0{C.BRIGHT_CYAN}                           
                                                                          
   
    {C.RESET}"""
        print(header)
    
    @staticmethod
    def print_completion_banner():
        """Print completion banner"""
        banner = f"""
{C.BRIGHT_GREEN}{C.BOLD}

███████╗███████╗████████╗██╗   ██╗██████╗                         
██╔════╝██╔════╝╚══██╔══╝██║   ██║██╔══██╗                        
███████╗█████╗     ██║   ██║   ██║██████╔╝                        
╚════██║██╔══╝     ██║   ██║   ██║██╔═══╝                         
███████║███████╗   ██║   ╚██████╔╝██║                             
╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝                             
                                                                         
        {C.BRIGHT_YELLOW}ALL DEPENDENCIES INSTALLED SUCCESSFULLY!{C.BRIGHT_GREEN}            
        {C.BRIGHT_WHITE}READY TO LAUNCH APK CRY{C.BRIGHT_GREEN}                     

    {C.RESET}"""
        print(banner)

# ============================================================================
# ANIMATIONS
# ============================================================================
class Animations:
    """Terminal animations"""
    
    @staticmethod
    def loading_animation(message: str, duration: float = 2.0):
        """Show loading animation"""
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        end_time = time.time() + duration
        i = 0
        
        while time.time() < end_time:
            sys.stdout.write(f"\r{C.BRIGHT_CYAN}{frames[i % len(frames)]} {message}{C.RESET}")
            sys.stdout.flush()
            time.sleep(0.08)
            i += 1
        
        sys.stdout.write(f"\r{C.BRIGHT_GREEN}✓ {message}{' ' * 20}{C.RESET}\n")
        sys.stdout.flush()
    
    @staticmethod
    def progress_bar(current: int, total: int, message: str = "", width: int = 40):
        """Display progress bar"""
        percentage = int((current / total) * 100)
        filled = int((current / total) * width)
        bar = f"{C.BRIGHT_RED}{'█' * filled}{C.GRAY}{'░' * (width - filled)}{C.RESET}"
        
        sys.stdout.write(f"\r{C.BRIGHT_CYAN}{message} {bar} {C.BRIGHT_WHITE}{percentage}%{C.RESET}")
        sys.stdout.flush()
        
        if current == total:
            sys.stdout.write("\n")
    
    @staticmethod
    def spinning_animation(message: str, stop_event):
        """Show spinning animation until stop_event is set"""
        frames = ["◜", "◠", "◝", "◞", "◡", "◟"]
        i = 0
        
        while not stop_event.is_set():
            sys.stdout.write(f"\r{C.BRIGHT_YELLOW}{frames[i % len(frames)]} {message}{C.RESET}")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        
        sys.stdout.write(f"\r{C.BRIGHT_GREEN}✓ {message}{' ' * 20}{C.RESET}\n")
        sys.stdout.flush()
    
    @staticmethod
    def type_effect(text: str, color: str = C.BRIGHT_WHITE, delay: float = 0.02):
        """Type text with typewriter effect"""
        for char in text:
            sys.stdout.write(f"{color}{char}{C.RESET}")
            sys.stdout.flush()
            time.sleep(delay)
        print()

# ============================================================================
# SYSTEM DETECTION
# ============================================================================
class SystemDetector:
    """Detect system information"""
    
    @staticmethod
    def get_os_info() -> dict:
        """Get detailed OS information"""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'python_implementation': platform.python_implementation(),
            'hostname': socket.gethostname(),
            'is_64bit': platform.machine().endswith('64'),
        }
    
    @staticmethod
    def get_python_info() -> dict:
        """Get Python installation info"""
        return {
            'executable': sys.executable,
            'version': sys.version,
            'version_info': sys.version_info,
            'path': sys.path,
            'pip_available': shutil.which('pip') is not None or shutil.which('pip3') is not None,
        }
    
    @staticmethod
    def check_command(command: str) -> bool:
        """Check if a command is available"""
        return shutil.which(command) is not None

# ============================================================================
# DEPENDENCY MANAGER
# ============================================================================
class DependencyManager:
    """Manage and install all dependencies"""
    
    def __init__(self):
        self.os_info = SystemDetector.get_os_info()
        self.python_info = SystemDetector.get_python_info()
        self.pip_cmd = self._get_pip_command()
        self.python_cmd = sys.executable
        
        # Define requirements
        self.python_packages = {
            'customtkinter': 'customtkinter>=5.2.0',
            'Pillow': 'Pillow>=9.0.0',
            'cryptography': 'cryptography>=41.0.0',
            'requests': 'requests>=2.28.0',
        }
        
        self.system_tools = {
            'java': {
                'name': 'Java JDK',
                'min_version': '11',
                'check_cmd': ['java', '-version'],
                'windows_download': 'https://www.oracle.com/java/technologies/downloads/',
                'linux_install': 'sudo apt install openjdk-17-jdk',
                'macos_install': 'brew install openjdk@17',
            },
            'apktool': {
                'name': 'APKTool',
                'min_version': '2.9.0',
                'check_cmd': ['apktool', '--version'],
                'windows_download': 'https://ibotpeaches.github.io/Apktool/install/',
                'linux_install': 'sudo apt install apktool',
                'macos_install': 'brew install apktool',
            },
        }
        
        self.optional_tools = {
            'zipalign': {
                'name': 'ZipAlign',
                'check_cmd': ['zipalign'],
                'part_of': 'Android SDK Build Tools',
            },
            'apksigner': {
                'name': 'APK Signer',
                'check_cmd': ['apksigner', 'version'],
                'part_of': 'Android SDK Build Tools',
            },
            'adb': {
                'name': 'Android Debug Bridge',
                'check_cmd': ['adb', 'version'],
                'part_of': 'Android SDK Platform Tools',
            },
        }
    
    def _get_pip_command(self) -> str:
        """Get the correct pip command"""
        if shutil.which('pip3'):
            return 'pip3'
        elif shutil.which('pip'):
            return 'pip'
        return 'pip'
    
    def check_python_packages(self) -> dict:
        """Check which Python packages are installed"""
        results = {}
        for package, pip_name in self.python_packages.items():
            try:
                __import__(package.replace('-', '_'))
                results[package] = True
            except ImportError:
                results[package] = False
        return results
    
    def install_python_package(self, package: str) -> bool:
        """Install a Python package"""
        try:
            pip_name = self.python_packages.get(package, package)
            cmd = [self.python_cmd, '-m', 'pip', 'install', pip_name, '--quiet', '--disable-pip-version-check']
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def check_system_tool(self, tool_name: str) -> bool:
        """Check if a system tool is available"""
        if tool_name in self.system_tools:
            check_cmd = self.system_tools[tool_name]['check_cmd']
            try:
                result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=10)
                return result.returncode == 0
            except:
                return False
        return False
    
    def check_optional_tool(self, tool_name: str) -> bool:
        """Check if an optional tool is available"""
        if tool_name in self.optional_tools:
            check_cmd = self.optional_tools[tool_name]['check_cmd']
            try:
                result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=10)
                return result.returncode == 0
            except:
                return False
        return False
    
    def download_apktool(self) -> bool:
        """Download APKTool if not installed"""
        try:
            apktool_url = "https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.9.3.jar"
            tools_dir = Path.home() / '.apk_crypter' / 'tools'
            tools_dir.mkdir(parents=True, exist_ok=True)
            
            apktool_path = tools_dir / 'apktool.jar'
            
            print(f"{C.BRIGHT_CYAN}  ⬇️  Downloading APKTool...{C.RESET}")
            urllib.request.urlretrieve(apktool_url, apktool_path)
            
            # Create wrapper script
            if platform.system() == 'Windows':
                wrapper_path = tools_dir / 'apktool.bat'
                with open(wrapper_path, 'w') as f:
                    f.write(f'@echo off\njava -jar "{apktool_path}" %*\n')
            else:
                wrapper_path = tools_dir / 'apktool'
                with open(wrapper_path, 'w') as f:
                    f.write(f'#!/bin/bash\njava -jar "{apktool_path}" "$@"\n')
                os.chmod(wrapper_path, 0o755)
            
            print(f"{C.BRIGHT_GREEN}  ✓ APKTool downloaded to: {apktool_path}{C.RESET}")
            return True
        except Exception as e:
            print(f"{C.BRIGHT_RED}  ✗ Failed to download APKTool: {e}{C.RESET}")
            return False
    
    def download_android_sdk_tools(self) -> bool:
        """Download Android SDK command line tools"""
        try:
            system = platform.system().lower()
            if system == 'windows':
                url = "https://dl.google.com/android/repository/commandlinetools-win-latest.zip"
            elif system == 'darwin':
                url = "https://dl.google.com/android/repository/commandlinetools-mac-latest.zip"
            else:
                url = "https://dl.google.com/android/repository/commandlinetools-linux-latest.zip"
            
            tools_dir = Path.home() / '.apk_crypter' / 'android-sdk'
            tools_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"{C.BRIGHT_CYAN}  ⬇️  Downloading Android SDK Tools...{C.RESET}")
            
            # Download
            zip_path = tools_dir / 'cmdline-tools.zip'
            urllib.request.urlretrieve(url, zip_path)
            
            # Extract
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(tools_dir)
            
            os.remove(zip_path)
            
            print(f"{C.BRIGHT_GREEN}  ✓ Android SDK Tools installed{C.RESET}")
            return True
        except Exception as e:
            print(f"{C.BRIGHT_RED}  ✗ Failed to download Android SDK: {e}{C.RESET}")
            return False

# ============================================================================
# MAIN INSTALLER
# ============================================================================
class Installer:
    """Main installer class"""
    
    def __init__(self):
        self.dep_manager = DependencyManager()
        self.os_info = SystemDetector.get_os_info()
        self.total_steps = 6
        self.current_step = 0
        
        # Create necessary directories
        self.app_dir = Path.home() / '.apk_crypter'
        self.app_dir.mkdir(parents=True, exist_ok=True)
        
        # Log file
        self.log_file = self.app_dir / 'install.log'
    
    def _log(self, message: str):
        """Write to log file"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def _step(self, message: str):
        """Print step header"""
        self.current_step += 1
        print(f"\n{C.BRIGHT_YELLOW}{C.BOLD}[{self.current_step}/{self.total_steps}]{C.RESET} {C.BRIGHT_CYAN}{message}{C.RESET}")
        print(f"{C.GRAY}{'─' * 60}{C.RESET}")
        self._log(f"STEP {self.current_step}: {message}")
    
    def install(self):
        """Run the complete installation"""
        self._clear_screen()
        Banners.print_nexus_banner()
        
        print(f"\n{C.BRIGHT_WHITE}{C.BOLD}  🚀 Starting Smart Installation...{C.RESET}\n")
        
        # Step 1: System Check
        self._step("System Compatibility Check")
        self._check_system()
        
        # Step 2: Python Packages
        self._step("Python Dependencies")
        self._install_python_packages()
        
        # Step 3: System Tools
        self._step("System Tools & SDK")
        self._check_system_tools()
        
        # Step 4: Optional Tools
        self._step("Optional Development Tools")
        self._check_optional_tools()
        
        # Step 5: Configuration
        self._step("Configuration Setup")
        self._setup_config()
        
        # Step 6: Launch
        self._step("Launch Application")
        self._launch_app()
    
    def _clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if platform.system() == 'Windows' else 'clear')
    
    def _check_system(self):
        """Check system compatibility"""
        print(f"\n{C.BRIGHT_WHITE}  System Information:{C.RESET}")
        print(f"  ├─ OS: {C.BRIGHT_CYAN}{self.os_info['system']} {self.os_info['release']}{C.RESET}")
        print(f"  ├─ Architecture: {C.BRIGHT_CYAN}{self.os_info['machine']}{C.RESET}")
        print(f"  ├─ Python: {C.BRIGHT_CYAN}{self.os_info['python_version']}{C.RESET}")
        print(f"  ├─ Hostname: {C.BRIGHT_CYAN}{self.os_info['hostname']}{C.RESET}")
        print(f"  └─ 64-bit: {C.BRIGHT_GREEN if self.os_info['is_64bit'] else C.BRIGHT_RED}{self.os_info['is_64bit']}{C.RESET}")
        
        # Check Python version
        if sys.version_info < (3, 9):
            print(f"\n{C.BRIGHT_RED}  ✗ Python 3.9+ required! Found: {sys.version_info.major}.{sys.version_info.minor}{C.RESET}")
            print(f"{C.BRIGHT_YELLOW}  Please upgrade Python and try again.{C.RESET}")
            sys.exit(1)
        else:
            print(f"\n{C.BRIGHT_GREEN}  ✓ System compatible{C.RESET}")
        
        self._log(f"System check: {json.dumps(self.os_info)}")
    
    def _install_python_packages(self):
        """Install required Python packages"""
        packages = self.dep_manager.check_python_packages()
        
        total = len(packages)
        installed = 0
        
        for package, is_installed in packages.items():
            if is_installed:
                print(f"{C.BRIGHT_GREEN}  ✓ {package} already installed{C.RESET}")
                installed += 1
            else:
                print(f"{C.BRIGHT_YELLOW}  ⬇️  Installing {package}...{C.RESET}")
                if self.dep_manager.install_python_package(package):
                    print(f"{C.BRIGHT_GREEN}  ✓ {package} installed successfully{C.RESET}")
                    installed += 1
                else:
                    print(f"{C.BRIGHT_RED}  ✗ Failed to install {package}{C.RESET}")
                    print(f"{C.BRIGHT_YELLOW}  Try manually: pip install {package}{C.RESET}")
            
            self._log(f"Package {package}: {'installed' if is_installed else 'failed'}")
        
        print(f"\n{C.BRIGHT_WHITE}  Packages: {installed}/{total} installed{C.RESET}")
    
    def _check_system_tools(self):
        """Check and install system tools"""
        # Check Java
        if self.dep_manager.check_system_tool('java'):
            print(f"{C.BRIGHT_GREEN}  ✓ Java JDK found{C.RESET}")
        else:
            print(f"{C.BRIGHT_RED}  ✗ Java JDK not found{C.RESET}")
            print(f"{C.BRIGHT_YELLOW}  ⚠ Java is required for APK signing{C.RESET}")
            if platform.system() == 'Windows':
                print(f"{C.BRIGHT_CYAN}  Download: {self.dep_manager.system_tools['java']['windows_download']}{C.RESET}")
            elif platform.system() == 'Darwin':
                print(f"{C.BRIGHT_CYAN}  Install: {self.dep_manager.system_tools['java']['macos_install']}{C.RESET}")
            else:
                print(f"{C.BRIGHT_CYAN}  Install: {self.dep_manager.system_tools['java']['linux_install']}{C.RESET}")
        
        # Check APKTool
        if self.dep_manager.check_system_tool('apktool'):
            print(f"{C.BRIGHT_GREEN}  ✓ APKTool found{C.RESET}")
        else:
            print(f"{C.BRIGHT_YELLOW}  ⬇️  APKTool not found - downloading...{C.RESET}")
            if self.dep_manager.download_apktool():
                print(f"{C.BRIGHT_GREEN}  ✓ APKTool installed{C.RESET}")
            else:
                print(f"{C.BRIGHT_RED}  ✗ Failed to install APKTool{C.RESET}")
        
        self._log("System tools check completed")
    
    def _check_optional_tools(self):
        """Check optional tools"""
        for tool_name, tool_info in self.dep_manager.optional_tools.items():
            if self.dep_manager.check_optional_tool(tool_name):
                print(f"{C.BRIGHT_GREEN}  ✓ {tool_info['name']} found{C.RESET}")
            else:
                print(f"{C.GRAY}  ○ {tool_info['name']} not found (optional - {tool_info['part_of']}){C.RESET}")
        
        # Check Android SDK
        android_home = os.environ.get('ANDROID_HOME', '')
        if android_home and os.path.exists(android_home):
            print(f"{C.BRIGHT_GREEN}  ✓ Android SDK found at: {android_home}{C.RESET}")
        else:
            print(f"{C.GRAY}  ○ Android SDK not found (optional){C.RESET}")
            
            # Offer to download
            if platform.system() != 'Darwin':  # macOS users should use brew
                response = input(f"\n{C.BRIGHT_YELLOW}  Download Android SDK tools? (y/n): {C.RESET}")
                if response.lower() == 'y':
                    self.dep_manager.download_android_sdk_tools()
        
        self._log("Optional tools check completed")
    
    def _setup_config(self):
        """Setup configuration"""
        config = {
            'app_name': APP_NAME,
            'version': APP_VERSION,
            'codename': APP_CODENAME,
            'installed_at': datetime.now().isoformat(),
            'python_path': sys.executable,
            'os_info': self.os_info,
            'paths': {
                'app_dir': str(self.app_dir),
                'tools_dir': str(self.app_dir / 'tools'),
                'keys_dir': str(self.app_dir / 'keys'),
            },
            'tools': {
                'java': shutil.which('java') or 'java',
                'apktool': str(self.app_dir / 'tools' / 'apktool.jar'),
            }
        }
        
        config_path = self.app_dir / 'config.json'
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"{C.BRIGHT_GREEN}  ✓ Configuration saved to: {config_path}{C.RESET}")
        self._log(f"Configuration saved")
    
    def _launch_app(self):
        """Launch the main application"""
        # Check if main script exists
        main_script = Path(MAIN_SCRIPT)
        if not main_script.exists():
            print(f"\n{C.BRIGHT_RED}  ✗ Main script not found: {MAIN_SCRIPT}{C.RESET}")
            print(f"{C.BRIGHT_YELLOW}  Please ensure the project structure is correct.{C.RESET}")
            print(f"{C.BRIGHT_YELLOW}  Expected: {main_script.absolute()}{C.RESET}")
            return
        
        Banners.print_completion_banner()
        
        print(f"\n{C.BRIGHT_WHITE}{C.BOLD}  🚀 Launching APK Crypter Pro...{C.RESET}\n")
        
        Animations.loading_animation("Initializing engine", 1.5)
        Animations.loading_animation("Loading protection modules", 1.0)
        Animations.loading_animation("Starting GUI", 0.5)
        
        print(f"\n{C.BRIGHT_GREEN}{C.BOLD}  ╔{'═' * 58}╗{C.RESET}")
        print(f"{C.BRIGHT_GREEN}{C.BOLD}  ║  {C.BRIGHT_WHITE}Launching {APP_NAME} {APP_CODENAME} Protocol...{C.BRIGHT_GREEN}     ║{C.RESET}")
        print(f"{C.BRIGHT_GREEN}{C.BOLD}  ╚{'═' * 58}╝{C.RESET}")
        print()
        
        time.sleep(1)
        
        # Launch the main application
        try:
            subprocess.run([sys.executable, str(main_script)])
        except KeyboardInterrupt:
            print(f"\n{C.BRIGHT_YELLOW}  Application closed by user{C.RESET}")
        except Exception as e:
            print(f"\n{C.BRIGHT_RED}  Error launching application: {e}{C.RESET}")
            print(f"{C.BRIGHT_YELLOW}  Try running manually: python {MAIN_SCRIPT}{C.RESET}")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================
def main():
    """Main entry point"""
    try:
        installer = Installer()
        installer.install()
    except KeyboardInterrupt:
        print(f"\n\n{C.BRIGHT_YELLOW}  ⚠ Installation cancelled by user{C.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{C.BRIGHT_RED}  ✗ Installation failed: {e}{C.RESET}")
        print(f"{C.BRIGHT_YELLOW}  Check install.log for details{C.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()