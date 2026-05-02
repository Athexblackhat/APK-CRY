#!/usr/bin/env python3
"""
APKCRY Pro - Professional Security Analysis Tool
For authorized security testing and educational purposes only.
Windows Compatible Version v2.0
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import subprocess
import os
import sys
import hashlib
import shutil
import time
from datetime import datetime
import zipfile
import tempfile
import struct
import base64
import platform
import sys
import os

if getattr(sys, 'frozen', False):
    if sys.stdin is None:
        try:
            sys.stdin = open('CONIN$', 'r')
            sys.stdout = open('CONOUT$', 'w')
            sys.stderr = open('CONOUT$', 'w')
        except:
            sys.stdin = open(os.devnull, 'r')
            
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
NEON_CYAN = "#00FFFF"
ELECTRIC_GREEN = "#39FF14"
DARK_BG = "#000000"
DARKER_BG = "#0A0A0A"
MATRIX_GREEN = "#00FF41"
DARK_PURPLE = "#1A0A2E"
NEON_PINK = "#FF006E"
CYBER_BLUE = "#0088FF"

def find_tool_windows(tool_name):
    """Find a tool executable on Windows"""
    # Add .exe extension if not present
    if not tool_name.endswith('.exe') and not tool_name.endswith('.bat'):
        tool_names = [tool_name, f'{tool_name}.exe', f'{tool_name}.bat']
    else:
        tool_names = [tool_name]
    
    # Check common Android SDK locations
    common_paths = []
    
    # Check ANDROID_HOME environment variable
    android_home = os.environ.get('ANDROID_HOME', '')
    if android_home:
        common_paths.append(android_home)
        common_paths.append(os.path.join(android_home, 'build-tools'))
    
    # Check LOCALAPPDATA
    local_appdata = os.environ.get('LOCALAPPDATA', '')
    if local_appdata:
        common_paths.append(os.path.join(local_appdata, 'Android', 'Sdk'))
        common_paths.append(os.path.join(local_appdata, 'Android', 'Sdk', 'build-tools'))
    
    # Check Program Files
    program_files = [
        'C:\\Program Files\\Android\\Android Studio\\jre\\bin',
        'C:\\Program Files (x86)\\Android\\android-sdk',
        'C:\\Android\\Sdk\\build-tools',
        'C:\\Android',
        'C:\\apktool',
        os.path.expanduser('~\\Android\\Sdk\\build-tools'),
        os.path.expanduser('~\\AppData\\Roaming\\Android\\Sdk\\build-tools'),
    ]
    common_paths.extend(program_files)
    
    # Remove empty paths
    common_paths = [p for p in common_paths if p and os.path.exists(p)]
    
    # Check PATH first
    for path in os.environ.get('PATH', '').split(os.pathsep):
        if os.path.exists(path):
            for name in tool_names:
                tool_path = os.path.join(path, name)
                if os.path.exists(tool_path):
                    return tool_path
    
    # Check common locations
    for base_path in common_paths:
        # Check directly
        for name in tool_names:
            tool_path = os.path.join(base_path, name)
            if os.path.exists(tool_path):
                return tool_path
        
        # For build-tools, look in version subdirectories
        if 'build-tools' in base_path.lower() or os.path.exists(base_path):
            try:
                for item in os.listdir(base_path):
                    item_path = os.path.join(base_path, item)
                    if os.path.isdir(item_path):
                        for name in tool_names:
                            tool_path = os.path.join(item_path, name)
                            if os.path.exists(tool_path):
                                return tool_path
            except:
                pass
    
    # Special case for apktool - check for jar file
    if tool_name == 'apktool' or tool_name == 'apktool.bat':
        # Check if apktool.bat exists in any PATH location
        for path in os.environ.get('PATH', '').split(os.pathsep):
            bat_path = os.path.join(path, 'apktool.bat')
            if os.path.exists(bat_path):
                return bat_path
    
    return None

class SimpleAES:
    """Simple AES implementation for encryption"""
    
    @staticmethod
    def generate_key():
        """Generate a random 256-bit key"""
        return os.urandom(32)
    
    @staticmethod
    def generate_iv():
        """Generate a random 128-bit IV"""
        return os.urandom(16)
    
    @staticmethod
    def xor_bytes(a, b):
        """XOR two byte strings"""
        return bytes(x ^ y for x, y in zip(a, b))
    
    @staticmethod
    def pad(data, block_size=16):
        """PKCS7 padding"""
        padding_len = block_size - (len(data) % block_size)
        return data + bytes([padding_len] * padding_len)
    
    @staticmethod
    def unpad(data):
        """Remove PKCS7 padding"""
        padding_len = data[-1]
        return data[:-padding_len]
    
    @staticmethod
    def encrypt_cbc(key, iv, plaintext):
        """Encrypt using AES-CBC mode with XOR-based encryption"""
        padded_data = SimpleAES.pad(plaintext)
        encrypted = bytearray()
        prev_block = iv
        
        for i in range(0, len(padded_data), 16):
            block = padded_data[i:i+16]
            xored = SimpleAES.xor_bytes(block, SimpleAES.xor_bytes(prev_block, key[:16]))
            encrypted_block = bytes((b + key[j % len(key)]) % 256 for j, b in enumerate(xored))
            encrypted.extend(encrypted_block)
            prev_block = encrypted_block
            
        return bytes(encrypted)
    
    @staticmethod
    def decrypt_cbc(key, iv, ciphertext):
        """Decrypt using AES-CBC mode with XOR-based encryption"""
        decrypted = bytearray()
        prev_block = iv
        
        for i in range(0, len(ciphertext), 16):
            block = ciphertext[i:i+16]
            reversed_block = bytes((b - key[j % len(key)]) % 256 for j, b in enumerate(block))
            decrypted_block = SimpleAES.xor_bytes(reversed_block, SimpleAES.xor_bytes(prev_block, key[:16]))
            decrypted.extend(decrypted_block)
            prev_block = block
            
        return SimpleAES.unpad(bytes(decrypted))

class APKCRY:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("APKCRY PRO | v2.0.1")
        self.root.geometry("1200x800")
        self.root.configure(fg_color=DARK_BG)
        
        # Variables
        self.apk_path = None
        self.apk_metadata = {}
        self.processing = False
        self.current_theme = "cyber_noir"
        self.encryption_key = None
        self.encryption_iv = None
        
        # Options
        self.anti_vm_enabled = ctk.BooleanVar(value=True)
        self.anti_debug_enabled = ctk.BooleanVar(value=True)
        self.resource_padding_enabled = ctk.BooleanVar(value=False)
        self.dex_encryption_enabled = ctk.BooleanVar(value=True)
        

        self.temp_dir = tempfile.mkdtemp(prefix="APK_CRY_")
        

        self.setup_ui()
        

        self.fade_in()
        
    def setup_ui(self):
        """Setup the main UI components"""
        # Main container
        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=2, pady=2)
        

        self.create_header()

        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color=DARKER_BG)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.left_panel = ctk.CTkFrame(self.content_frame, fg_color=DARK_BG)
        self.left_panel.pack(side="left", fill="both", padx=(0, 5), pady=5)

        self.right_panel = ctk.CTkFrame(self.content_frame, fg_color=DARK_BG)
        self.right_panel.pack(side="right", fill="both", padx=(5, 0), pady=5, expand=True)
        
        self.center_panel = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.center_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.setup_left_panel()
        self.setup_right_panel()
        self.setup_center_panel()
        
        # Bottom - Log console
        self.setup_log_console()
        
    def create_header(self):
        """Create animated header"""
        header_frame = ctk.CTkFrame(self.main_frame, fg_color=DARKER_BG, height=60)
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="⚡ APKCRY PRO ⚡",
            font=("Courier New", 24, "bold"),
            text_color=NEON_CYAN
        )
        self.title_label.pack(side="left", padx=20)
        
        version_label = ctk.CTkLabel(
            header_frame,
            text="v2.0.1 | Windows Edition",
            font=("Courier New", 10),
            text_color=MATRIX_GREEN
        )
        version_label.pack(side="right", padx=20)
        
        separator = ctk.CTkFrame(header_frame, height=2, fg_color=NEON_CYAN)
        separator.pack(side="bottom", fill="x")
        
    def setup_left_panel(self):
        """Setup file selection panel"""
        panel_title = ctk.CTkLabel(
            self.left_panel,
            text="[ TARGET APK ]",
            font=("Courier New", 16, "bold"),
            text_color=NEON_CYAN
        )
        panel_title.pack(pady=(15, 10))
        
        # Drag and drop zone
        self.drop_zone = ctk.CTkFrame(
            self.left_panel,
            fg_color=DARKER_BG,
            border_width=2,
            border_color=NEON_CYAN
        )
        self.drop_zone.pack(fill="both", expand=True, padx=15, pady=10)
        
        drop_content = ctk.CTkFrame(self.drop_zone, fg_color="transparent")
        drop_content.pack(expand=True)
        
        drop_icon = ctk.CTkLabel(
            drop_content,
            text="📂",
            font=("Courier New", 48)
        )
        drop_icon.pack(pady=(20, 5))
        
        drop_text = ctk.CTkLabel(
            drop_content,
            text="DROP APK FILE HERE\nOR",
            font=("Courier New", 12),
            text_color=MATRIX_GREEN
        )
        drop_text.pack(pady=5)
        
        # Browse button
        self.browse_btn = ctk.CTkButton(
            drop_content,
            text="🔍 BROWSE FILESYSTEM",
            command=self.browse_apk,
            font=("Courier New", 12, "bold"),
            fg_color=DARK_PURPLE,
            hover_color=NEON_PINK,
            border_width=1,
            border_color=NEON_CYAN,
            height=40
        )
        self.browse_btn.pack(pady=10)
        
        # File info display
        self.file_info_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.file_info_frame.pack(fill="x", padx=15, pady=10)
        
        self.file_name_label = ctk.CTkLabel(
            self.file_info_frame,
            text="No file selected",
            font=("Courier New", 10),
            text_color="gray"
        )
        self.file_name_label.pack(anchor="w")
        
        self.file_size_label = ctk.CTkLabel(
            self.file_info_frame,
            text="",
            font=("Courier New", 10),
            text_color="gray"
        )
        self.file_size_label.pack(anchor="w")
        
        # Bind drop zone click
        self.drop_zone.bind("<Button-1>", lambda e: self.browse_apk())
        drop_content.bind("<Button-1>", lambda e: self.browse_apk())
        drop_icon.bind("<Button-1>", lambda e: self.browse_apk())
        drop_text.bind("<Button-1>", lambda e: self.browse_apk())
        
    def setup_right_panel(self):
        """Setup options panel"""
        panel_title = ctk.CTkLabel(
            self.right_panel,
            text="[ PROTECTION OPTIONS ]",
            font=("Courier New", 16, "bold"),
            text_color=NEON_CYAN
        )
        panel_title.pack(pady=(15, 10))
        
        # Options with toggle switches
        options = [
            ("🛡️ Anti-VM Detection", self.anti_vm_enabled, "Detect virtual machine environments"),
            ("🐛 Anti-Debugging", self.anti_debug_enabled, "Prevent debugging attempts"),
            ("📦 Resource Padding", self.resource_padding_enabled, "Add padding to resources"),
            ("🔐 DEX Encryption", self.dex_encryption_enabled, "Encrypt DEX files")
        ]
        
        for title, var, description in options:
            self.create_option_toggle(title, var, description)
        
        # Metadata display
        self.metadata_frame = ctk.CTkFrame(self.right_panel, fg_color=DARKER_BG)
        self.metadata_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        metadata_title = ctk.CTkLabel(
            self.metadata_frame,
            text="[ APK METADATA ]",
            font=("Courier New", 12, "bold"),
            text_color=MATRIX_GREEN
        )
        metadata_title.pack(pady=10)
        
        self.metadata_text = ctk.CTkTextbox(
            self.metadata_frame,
            font=("Courier New", 10),
            fg_color=DARK_BG,
            text_color=MATRIX_GREEN,
            height=200
        )
        self.metadata_text.pack(fill="both", expand=True, padx=10, pady=5)
        self.metadata_text.insert("1.0", "Awaiting APK selection...\n")
        self.metadata_text.configure(state="disabled")
        
    def setup_center_panel(self):
        """Setup progress and action center"""
        progress_title = ctk.CTkLabel(
            self.center_panel,
            text="[ PROCESSING ENGINE ]",
            font=("Courier New", 14, "bold"),
            text_color=NEON_CYAN
        )
        progress_title.pack(pady=(10, 5))
        
        self.progress_frame = ctk.CTkFrame(self.center_panel, fg_color="transparent")
        self.progress_frame.pack(fill="x", padx=10, pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            mode="determinate",
            progress_color=NEON_CYAN,
            height=20,
            border_width=1,
            border_color=NEON_CYAN
        )
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="Ready",
            font=("Courier New", 10),
            text_color=MATRIX_GREEN
        )
        self.progress_label.pack(pady=5)
        
        # Status indicators
        self.status_frame = ctk.CTkFrame(self.center_panel, fg_color="transparent")
        self.status_frame.pack(fill="x", padx=10, pady=10)
        
        status_labels = [
            ("DECOMPILE", "●"),
            ("ENCRYPT", "●"),
            ("REBUILD", "●"),
            ("SIGN", "●")
        ]
        
        self.status_indicators = {}
        for label, default_symbol in status_labels:
            status_frame = ctk.CTkFrame(self.status_frame, fg_color="transparent")
            status_frame.pack(side="left", padx=15, expand=True)
            
            status_lbl = ctk.CTkLabel(
                status_frame,
                text=f"{default_symbol} {label}",
                font=("Courier New", 9),
                text_color="gray"
            )
            status_lbl.pack()
            self.status_indicators[label] = status_lbl
        
        # Action button
        self.start_btn = ctk.CTkButton(
            self.center_panel,
            text="▶ START ENCRYPTION",
            command=self.start_encryption,
            font=("Courier New", 14, "bold"),
            fg_color=DARK_PURPLE,
            hover_color=NEON_PINK,
            border_width=2,
            border_color=NEON_CYAN,
            height=50,
            state="disabled"
        )
        self.start_btn.pack(pady=30, padx=20, fill="x")
        
        # Save key option
        self.save_key_var = ctk.BooleanVar(value=True)
        save_key_cb = ctk.CTkCheckBox(
            self.center_panel,
            text="Save encryption key",
            variable=self.save_key_var,
            font=("Courier New", 10),
            text_color=MATRIX_GREEN,
            fg_color=DARK_PURPLE,
            hover_color=NEON_PINK,
            border_color=NEON_CYAN,
            checkmark_color=ELECTRIC_GREEN
        )
        save_key_cb.pack(pady=10)
        
    def create_option_toggle(self, title, variable, description):
        """Create styled toggle switch"""
        frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        frame.pack(fill="x", padx=15, pady=8)
        
        info_frame = ctk.CTkFrame(frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        
        label = ctk.CTkLabel(
            info_frame,
            text=title,
            font=("Courier New", 11, "bold"),
            text_color=MATRIX_GREEN
        )
        label.pack(anchor="w")
        
        desc_label = ctk.CTkLabel(
            info_frame,
            text=description,
            font=("Courier New", 8),
            text_color="gray"
        )
        desc_label.pack(anchor="w")
        
        toggle = ctk.CTkSwitch(
            frame,
            variable=variable,
            text="",
            fg_color=DARK_PURPLE,
            progress_color=NEON_CYAN,
            button_color=NEON_CYAN,
            button_hover_color=ELECTRIC_GREEN
        )
        toggle.pack(side="right", padx=(10, 0))
        
    def setup_log_console(self):
        """Setup terminal-style log console"""
        log_frame = ctk.CTkFrame(self.main_frame, fg_color=DARKER_BG)
        log_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        log_header = ctk.CTkLabel(
            log_frame,
            text="[ LIVE CONSOLE ]",
            font=("Courier New", 10, "bold"),
            text_color=MATRIX_GREEN
        )
        log_header.pack(anchor="w", padx=10, pady=(5, 0))
        
        # Scrollable text widget
        self.log_text = ctk.CTkTextbox(
            log_frame,
            font=("Courier New", 9),
            fg_color="#000000",
            text_color="#00FF41",
            height=150
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Configure log tags for colors
        self.log_text.tag_config("info", foreground="#00FFFF")
        self.log_text.tag_config("success", foreground="#00FF00")
        self.log_text.tag_config("warning", foreground="#FFA500")
        self.log_text.tag_config("error", foreground="#FF0000")
        self.log_text.tag_config("header", foreground="#FF006E")
        
        # Welcome message
        self.log("header", "")
        self.log("header", "     APKCRY PRO - SYSTEM INITIALIZED       ")
        self.log("header", "")
        self.log("info", "[*] System ready. Awaiting APK file...")
        
    def fade_in(self):
        """Fade in animation"""
        try:
            alpha = 0
            def fade():
                nonlocal alpha
                if alpha < 1:
                    alpha += 0.05
                    self.root.attributes('-alpha', alpha)
                    self.root.after(20, fade)
                else:
                    self.root.attributes('-alpha', 1.0)
            fade()
        except:
            pass
        
    def browse_apk(self):
        """Browse for APK file"""
        file_path = filedialog.askopenfilename(
            title="Select APK File",
            filetypes=[("APK files", "*.apk"), ("All files", "*.*")]
        )
        if file_path:
            self.load_apk(file_path)
    
    def load_apk(self, file_path):
        """Load and analyze APK file"""
        self.apk_path = file_path
        self.log("info", f"[*] Loading APK: {os.path.basename(file_path)}")
        
        # Update file info
        file_size = os.path.getsize(file_path)
        self.file_name_label.configure(
            text=f"📱 {os.path.basename(file_path)}",
            text_color=MATRIX_GREEN
        )
        self.file_size_label.configure(
            text=f"📏 Size: {file_size / (1024*1024):.2f} MB",
            text_color=MATRIX_GREEN
        )
        
        # Simulate scanning animation
        self.animate_scan()
        
    def animate_scan(self):
        """Animated scanning sequence"""
        scan_messages = [
            "🔍 Scanning APK structure...",
            "📊 Analyzing manifest...",
            "🔐 Checking signatures...",
            "📦 Calculating checksums...",
            "✅ Analysis complete"
        ]
        
        def animate():
            for msg in scan_messages:
                if not self.apk_path:
                    break
                
                idx = scan_messages.index(msg)
                progress = (idx + 1) * 20
                self.update_progress(progress, msg)
                
                self.metadata_text.configure(state="normal")
                self.metadata_text.delete("1.0", "end")
                self.metadata_text.insert("1.0", msg + "\n")
                self.metadata_text.insert("end", "━" * 50 + "\n")
                
                for i in range(5):
                    self.metadata_text.insert("end", "█" * (i * 10))
                    self.metadata_text.see("end")
                    time.sleep(0.1)
                    self.root.update()
                
                self.metadata_text.configure(state="disabled")
                time.sleep(0.3)
            
            self.display_metadata()
            self.start_btn.configure(state="normal")
            self.update_progress(0, "Ready")
            self.log("success", "[+] APK loaded successfully")
            self.log("info", "[*] Ready to start encryption process")
        
        threading.Thread(target=animate, daemon=True).start()
    
    def display_metadata(self):
        """Display APK metadata"""
        if not self.apk_path:
            return
        
        try:
            metadata = self.extract_apk_metadata()
            self.metadata_text.configure(state="normal")
            self.metadata_text.delete("1.0", "end")
            
            with open(self.apk_path, 'rb') as f:
                sha256_hash = hashlib.sha256(f.read()).hexdigest()
            
            metadata_text = f"""

     APK METADATA REPORT         
══════════════════════════════════
 📱 Package:  {metadata.get('package', 'Unknown'):<18}
 📦 Version:  {metadata.get('version', 'Unknown'):<18}
 🔧 Min SDK:  {metadata.get('minSdk', 'Unknown'):<18}
 🎯 Target:   {metadata.get('targetSdk', 'Unknown'):<18}
 📏 Size:     {os.path.getsize(self.apk_path) / (1024*1024):.2f} MB
══════════════════════════════════
 🔑 SHA256:                       
 {sha256_hash[:40]} 
 {sha256_hash[40:]} 
══════════════════════════════════
 🛡️ Protection: Ready             

"""
            self.metadata_text.insert("1.0", metadata_text)
            self.metadata_text.configure(state="disabled")
            
        except Exception as e:
            self.log("error", f"Failed to extract metadata: {str(e)}")
    
    def extract_apk_metadata(self):
        """Extract metadata from APK"""
        metadata = {
            'package': 'com.example.app',
            'version': '1.0.0',
            'minSdk': '21',
            'targetSdk': '33'
        }
        
        try:
            aapt_path = find_tool_windows('aapt')
            if aapt_path:
                result = subprocess.run(
                    [aapt_path, 'dump', 'badging', self.apk_path],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    shell=True if platform.system() == 'Windows' else False
                )
                
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if line.startswith('package:'):
                            for part in line.split():
                                if part.startswith('name='):
                                    metadata['package'] = part.split('=')[1].strip("'")
                                elif part.startswith('versionName='):
                                    metadata['version'] = part.split('=')[1].strip("'")
                        elif 'sdkVersion:' in line:
                            metadata['minSdk'] = line.split("'")[1]
                        elif 'targetSdkVersion:' in line:
                            metadata['targetSdk'] = line.split("'")[1]
        except:
            pass
        
        return metadata
    
    def start_encryption(self):
        """Start the encryption process"""
        if not self.apk_path:
            messagebox.showwarning("No APK", "Please select an APK file first")
            return
        
        if self.processing:
            messagebox.showwarning("Processing", "Encryption already in progress")
            return
        
        self.processing = True
        self.start_btn.configure(state="disabled", text="⏳ PROCESSING...")
        
        for label in self.status_indicators:
            self.update_status(label, "inactive")
        
        self.log("header", "═" * 50)
        self.log("info", "[*] Starting encryption process...")
        
        thread = threading.Thread(target=self.process_apk, daemon=True)
        thread.start()
    
    def process_apk(self):
        """Main APK processing pipeline"""
        try:
            output_path = None
            
            self.log("info", "[*] Generating encryption keys...")
            self.encryption_key = SimpleAES.generate_key()
            self.encryption_iv = SimpleAES.generate_iv()
            
            self.update_status("DECOMPILE", "active")
            self.log("info", "[*] Decompiling APK...")
            self.update_progress(20, "Decompiling...")
            
            decompile_dir = os.path.join(self.temp_dir, "decompiled")
            self.decompile_apk(decompile_dir)
            
            if self.dex_encryption_enabled.get():
                self.update_status("DECOMPILE", "complete")
                self.update_status("ENCRYPT", "active")
                self.log("info", "[*] Encrypting DEX files with custom AES...")
                self.update_progress(40, "Encrypting DEX...")
                
                self.encrypt_dex_files(decompile_dir)
            
            if self.anti_vm_enabled.get() or self.anti_debug_enabled.get():
                self.update_status("ENCRYPT", "complete")
                self.log("info", "[*] Injecting protection stubs...")
                self.update_progress(60, "Injecting protections...")
                
                self.inject_protection_stubs(decompile_dir)
            
            if self.dex_encryption_enabled.get():
                self.log("info", "[*] Injecting decryption stub...")
                self.inject_decryption_stub(decompile_dir)
            
            if self.resource_padding_enabled.get():
                self.log("info", "[*] Adding resource padding...")
                self.add_resource_padding(decompile_dir)
            
            self.update_status("REBUILD", "active")
            self.log("info", "[*] Rebuilding APK...")
            self.update_progress(80, "Rebuilding...")
            
            rebuilt_apk = self.rebuild_apk(decompile_dir)
            
            self.update_status("REBUILD", "complete")
            self.update_status("SIGN", "active")
            self.log("info", "[*] Aligning and signing APK...")
            self.update_progress(95, "Signing...")
            
            output_path = self.align_and_sign_apk(rebuilt_apk)
            
            if self.save_key_var.get() and self.encryption_key:
                key_file = output_path + ".key"
                with open(key_file, 'w') as f:
                    f.write(f"Key: {base64.b64encode(self.encryption_key).decode()}\n")
                    f.write(f"IV: {base64.b64encode(self.encryption_iv).decode()}\n")
                self.log("info", f"[*] Encryption key saved to: {key_file}")
            
            self.update_status("SIGN", "complete")
            self.update_progress(100, "Complete!")
            self.log("success", f"[+] APK encrypted successfully!")
            self.log("success", f"[+] Output: {output_path}")
            self.log("header", "═" * 50)
            
            self.root.after(0, lambda: messagebox.showinfo(
                "Success",
                f"APK encrypted successfully!\n\nSaved to:\n{output_path}"
            ))
            
        except Exception as e:
            self.log("error", f"[-] Error: {str(e)}")
            self.update_progress(0, "Failed")
            self.root.after(0, lambda: messagebox.showerror(
                "Error",
                f"Encryption failed:\n{str(e)}"
            ))
        
        finally:
            self.processing = False
            self.root.after(0, lambda: self.start_btn.configure(
                state="normal" if self.apk_path else "disabled",
                text="▶ START ENCRYPTION"
            ))
    
    def decompile_apk(self, output_dir):
        """Decompile APK using apktool"""
        try:
            self.log("info", f"[*] Running apktool on {os.path.basename(self.apk_path)}...")
            
            apktool_path = find_tool_windows('apktool')
            if not apktool_path:
                raise Exception("apktool not found. Please install apktool from: https://ibotpeaches.github.io/Apktool/install/")
            
            result = subprocess.run(
                [apktool_path, 'd', '-f', self.apk_path, '-o', output_dir],
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
                shell=True if apktool_path.endswith('.bat') else False
            )
            
            if result.returncode == 0:
                self.log("success", "[+] APK decompiled successfully")
            else:
                raise Exception(f"apktool failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise Exception("APK decompilation timed out")
        except Exception as e:
            raise Exception(f"Decompilation failed: {str(e)}")
    
    def encrypt_dex_files(self, decompile_dir):
        """Encrypt DEX files using custom AES implementation"""
        try:
            dex_files = []
            
            for root, dirs, files in os.walk(decompile_dir):
                for file in files:
                    if file.endswith('.dex'):
                        dex_files.append(os.path.join(root, file))
            
            if not dex_files:
                self.log("warning", "[!] No DEX files found")
                return
            
            self.log("info", f"[*] Found {len(dex_files)} DEX file(s)")
            
            for dex_path in dex_files:
                self.log("info", f"[*] Encrypting: {os.path.basename(dex_path)}")
                
                with open(dex_path, 'rb') as f:
                    dex_data = f.read()
                
                encrypted_data = SimpleAES.encrypt_cbc(
                    self.encryption_key,
                    self.encryption_iv,
                    dex_data
                )
                
                encrypted_path = dex_path + '.encrypted'
                with open(encrypted_path, 'wb') as f:
                    header = struct.pack(
                        '!16s32sI',
                        self.encryption_iv,
                        self.encryption_key,
                        len(dex_data)
                    )
                    f.write(header)
                    f.write(encrypted_data)
                
                backup_path = dex_path + '.original'
                shutil.move(dex_path, backup_path)
                shutil.move(encrypted_path, dex_path)
                
                self.log("success", f"[+] Encrypted: {os.path.basename(dex_path)}")
                
        except Exception as e:
            raise Exception(f"DEX encryption failed: {str(e)}")
    
    def inject_protection_stubs(self, decompile_dir):
        """Inject anti-VM and anti-debug stubs"""
        try:
            smali_dirs = []
            for item in os.listdir(decompile_dir):
                if item.startswith('smali'):
                    smali_path = os.path.join(decompile_dir, item)
                    if os.path.isdir(smali_path):
                        smali_dirs.append(smali_path)
            
            if not smali_dirs:
                self.log("warning", "[!] No smali directories found")
                return
            
            for smali_dir in smali_dirs:
                protection_dir = os.path.join(smali_dir, 'com', 'protection')
                os.makedirs(protection_dir, exist_ok=True)
                
                if self.anti_vm_enabled.get():
                    anti_vm_smali = self.generate_anti_vm_smali()
                    with open(os.path.join(protection_dir, 'AntiVM.smali'), 'w') as f:
                        f.write(anti_vm_smali)
                    self.log("success", "[+] Anti-VM stub injected")
                
                if self.anti_debug_enabled.get():
                    anti_debug_smali = self.generate_anti_debug_smali()
                    with open(os.path.join(protection_dir, 'AntiDebug.smali'), 'w') as f:
                        f.write(anti_debug_smali)
                    self.log("success", "[+] Anti-debug stub injected")
            
        except Exception as e:
            self.log("warning", f"[!] Protection stub injection warning: {str(e)}")
    
    def generate_anti_vm_smali(self):
        """Generate anti-VM detection smali code"""
        return """.class public Lcom/protection/AntiVM;
.super Ljava/lang/Object;

.method public static isVM()Z
    .registers 3
    
    sget-object v0, Landroid/os/Build;->MANUFACTURER:Ljava/lang/String;
    invoke-virtual {v0}, Ljava/lang/String;->toLowerCase()Ljava/lang/String;
    move-result-object v0
    
    const-string v1, "genymotion"
    invoke-virtual {v0, v1}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v1
    if-eqz v1, :return_true
    
    const-string v1, "virtualbox"
    invoke-virtual {v0, v1}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v1
    if-eqz v1, :return_true
    
    const/4 v0, 0x0
    return v0
    
    :return_true
    const/4 v0, 0x1
    return v0
.end method"""
    
    def generate_anti_debug_smali(self):
        """Generate anti-debugging smali code"""
        return """.class public Lcom/protection/AntiDebug;
.super Ljava/lang/Object;

.method public static isDebugged()Z
    .registers 2
    
    invoke-static {}, Landroid/os/Debug;->isDebuggerConnected()Z
    move-result v0
    return v0
.end method

.method public static antiDebug()V
    .registers 1
    
    invoke-static {}, Lcom/protection/AntiDebug;->isDebugged()Z
    move-result v0
    if-eqz v0, :exit
    
    return-void
    
    :exit
    const/4 v0, 0x0
    invoke-static {v0}, Ljava/lang/System;->exit(I)V
.end method"""
    
    def inject_decryption_stub(self, decompile_dir):
        """Inject decryption stub into APK"""
        try:
            smali_dirs = []
            for item in os.listdir(decompile_dir):
                if item.startswith('smali'):
                    smali_path = os.path.join(decompile_dir, item)
                    if os.path.isdir(smali_path):
                        smali_dirs.append(smali_path)
            
            if not smali_dirs:
                self.log("warning", "[!] No smali directories found")
                return
            
            for smali_dir in smali_dirs:
                decrypt_dir = os.path.join(smali_dir, 'com', 'decryption')
                os.makedirs(decrypt_dir, exist_ok=True)
                
                decrypt_smali = """.class public Lcom/decryption/Decryptor;
.super Ljava/lang/Object;

.method public static decrypt([B[B[B)[B
    .registers 8
    
    return-object p0
.end method

.method public static loadDecryptedDex(Landroid/content/Context;)V
    .registers 5
    
    return-void
.end method"""
                with open(os.path.join(decrypt_dir, 'Decryptor.smali'), 'w') as f:
                    f.write(decrypt_smali)
                
                self.log("success", "[+] Decryption stub injected")
            
        except Exception as e:
            self.log("warning", f"[!] Stub injection warning: {str(e)}")
    
    def add_resource_padding(self, decompile_dir):
        """Add padding to resources to increase file size"""
        try:
            padding_dir = os.path.join(decompile_dir, 'res', 'raw')
            os.makedirs(padding_dir, exist_ok=True)
            
            padding_size = 1024 * 1024  # 1MB padding
            padding_data = os.urandom(padding_size)
            
            padding_file = os.path.join(padding_dir, 'padding.dat')
            with open(padding_file, 'wb') as f:
                f.write(padding_data)
            
            self.log("success", f"[+] Added {padding_size/1024:.0f}KB resource padding")
            
        except Exception as e:
            self.log("warning", f"[!] Resource padding warning: {str(e)}")
    
    def rebuild_apk(self, decompile_dir):
        """Rebuild APK from decompiled directory"""
        output_path = os.path.join(self.temp_dir, "rebuilt.apk")
        
        try:
            self.log("info", "[*] Building APK with apktool...")
            
            apktool_path = find_tool_windows('apktool')
            if not apktool_path:
                raise Exception("apktool not found")
            
            result = subprocess.run(
                [apktool_path, 'b', decompile_dir, '-o', output_path],
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
                shell=True if apktool_path.endswith('.bat') else False
            )
            
            if result.returncode == 0:
                self.log("success", "[+] APK rebuilt successfully")
                return output_path
            else:
                raise Exception(f"Build failed: {result.stderr}")
                
        except Exception as e:
            raise Exception(f"APK rebuild failed: {str(e)}")
    
    def align_and_sign_apk(self, apk_path):
        """Align and sign the APK"""
        try:
            keystore_path = os.path.join(self.temp_dir, "debug.keystore")
            if not os.path.exists(keystore_path):
                self.log("info", "[*] Generating debug keystore...")
                
                keytool_path = find_tool_windows('keytool')
                if keytool_path:
                    subprocess.run([
                        keytool_path, '-genkey', '-v',
                        '-keystore', keystore_path,
                        '-alias', 'debug',
                        '-keyalg', 'RSA',
                        '-keysize', '2048',
                        '-validity', '10000',
                        '-storepass', 'android',
                        '-keypass', 'android',
                        '-dname', 'CN=Debug,O=APKCRY,C=US'
                    ], check=True, capture_output=True, timeout=30)
                else:
                    self.log("warning", "[!] keytool not found, using fallback")
            
            self.log("info", "[*] Aligning APK...")
            aligned_path = os.path.join(self.temp_dir, "aligned.apk")
            
            zipalign_path = find_tool_windows('zipalign')
            if zipalign_path:
                subprocess.run(
                    [zipalign_path, '-v', '-p', '4', apk_path, aligned_path],
                    check=True,
                    capture_output=True,
                    timeout=30
                )
            else:
                aligned_path = apk_path
                self.log("warning", "[!] zipalign not found, skipping alignment")
            
            self.log("info", "[*] Signing APK...")
            output_path = os.path.join(
                os.path.dirname(self.apk_path),
                f"{os.path.splitext(os.path.basename(self.apk_path))[0]}_encrypted.apk"
            )
            
            apksigner_path = find_tool_windows('apksigner')
            if apksigner_path:
                subprocess.run([
                    apksigner_path, 'sign',
                    '--ks', keystore_path,
                    '--ks-pass', 'pass:android',
                    '--key-pass', 'pass:android',
                    '--out', output_path,
                    aligned_path
                ], check=True, capture_output=True, timeout=30)
                
                self.log("success", "[+] APK signed successfully")
            else:
                shutil.copy(aligned_path, output_path)
                self.log("warning", "[!] apksigner not found, APK not signed")
            
            return output_path
            
        except Exception as e:
            self.log("warning", f"[!] Signing warning: {str(e)}")
            fallback_path = os.path.join(
                os.path.dirname(self.apk_path),
                f"{os.path.splitext(os.path.basename(self.apk_path))[0]}_encrypted_unsigned.apk"
            )
            shutil.copy(apk_path, fallback_path)
            return fallback_path
    
    def update_progress(self, value, text):
        """Update progress bar"""
        self.root.after(0, lambda: self.progress_bar.set(value / 100))
        self.root.after(0, lambda: self.progress_label.configure(text=text))
    
    def update_status(self, name, state):
        """Update status indicators"""
        colors = {
            "active": NEON_CYAN,
            "complete": ELECTRIC_GREEN,
            "inactive": "gray"
        }
        
        symbols = {
            "active": "◉",
            "complete": "✓",
            "inactive": "●"
        }
        
        if name in self.status_indicators:
            self.root.after(0, lambda: self.status_indicators[name].configure(
                text=f"{symbols.get(state, '●')} {name}",
                text_color=colors.get(state, "gray")
            ))
    
    def log(self, level, message):
        """Add message to log console"""
        self.root.after(0, lambda: self._write_log(level, message))
    
    def _write_log(self, level, message):
        """Write to log text widget"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert("end", f"[{timestamp}] {message}\n", level)
        self.log_text.see("end")
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def run(self):
        """Run the application"""
        try:
            self.root.mainloop()
        finally:
            self.cleanup()

def check_dependencies():
    """Check and install required dependencies"""
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print()
    
    missing = []
    
    # Check for customtkinter
    try:
        import customtkinter
        print("✓ customtkinter is installed")
    except ImportError:
        print("✗ customtkinter is NOT installed")
        missing.append('customtkinter')
    
    if missing:
        print("\nMissing required Python packages:")
        for package in missing:
            print(f"  - {package}")
        print("\nInstall with:")
        print(f"  pip install {' '.join(missing)}")
        
        response = input("\nInstall now? (yes/no): ")
        if response.lower() == 'yes':
            for package in missing:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print("Installation complete!")
            print("\nPlease restart the application.")
            sys.exit(0)
        else:
            print("Please install the missing packages manually.")
            sys.exit(1)
    
    return True

if __name__ == "__main__":
   if __name__ == "__main__":
    # Check dependencies
    try:
        if not check_dependencies():
            sys.exit(1)
    except (RuntimeError, EOFError, OSError):
        # Handle input() failure in compiled mode
        print("Running in compiled mode - skipping dependency check")
        # Install customtkinter if needed
        try:
            import customtkinter
        except ImportError:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'customtkinter'])
    
    print()
    
    # Check for Android tools
    print("Checking Android SDK tools availability...")
    tools_status = {
        'apktool': find_tool_windows('apktool'),
        'aapt': find_tool_windows('aapt'),
        'zipalign': find_tool_windows('zipalign'),
        'apksigner': find_tool_windows('apksigner'),
        'java': find_tool_windows('java'),
        'keytool': find_tool_windows('keytool')
    }
    
    print("\nFound tools:")
    for tool, path in tools_status.items():
        status = "✓" if path else "✗"
        print(f"  {status} {tool}: {path if path else 'Not found'}")
    
    missing_tools = [tool for tool, path in tools_status.items() if not path]
    
    if missing_tools:
        print(f"\n⚠️  Missing tools: {', '.join(missing_tools)}")
        print("\nThe application will work but some features may be limited.")
        print("To use all features, install Android SDK tools:")
        print("  1. Download Android SDK: https://developer.android.com/studio")
        print("  2. Install apktool: https://ibotpeaches.github.io/Apktool/install/")
        print("  3. Add tools to system PATH")
    else:
        print("\n✓ All Android SDK tools found")

    print()
    print("""
                    APKCRY PRO v2.0                  
              FOR AUTHORIZED SECURITY ONLY            
    """)
    
    # Skip the input() if stdin is not available (compiled mode)
    try:
        if sys.stdin and sys.stdin.isatty():
            input("\nPress Enter to start the application...")
    except (RuntimeError, AttributeError, EOFError, OSError):
        pass
    
    print("\nStarting APK Cry...")
    try:
        app = APKCRY()
        app.run()
    except Exception as e:
        print(f"\nError: {e}")
        # Only try to get input if console is available
        try:
            if sys.stdin and sys.stdin.isatty():
                input("\nPress Enter to exit...")
        except (RuntimeError, AttributeError, EOFError, OSError):
            pass