#!/usr/bin/env python3
"""
Neo4j Windows Startup Helper
Find and start Neo4j on Windows
"""

import os
import subprocess
import time
import requests
from pathlib import Path

class Neo4jWindowsStarter:
    def __init__(self):
        self.neo4j_paths = []
        self.neo4j_executable = None
        
    def find_neo4j_installation(self):
        """Find Neo4j installation on Windows"""
        print("🔍 Searching for Neo4j installation...")
        
        # Common Neo4j installation paths
        search_paths = [
            # Neo4j Desktop locations
            Path.home() / "AppData" / "Local" / "Programs" / "Neo4j Desktop",
            Path.home() / "AppData" / "Roaming" / "Neo4j Desktop",
            Path("C:") / "Program Files" / "Neo4j Desktop",
            Path("C:") / "Program Files (x86)" / "Neo4j Desktop",
            
            # Manual installation locations
            Path("C:") / "neo4j",
            Path("C:") / "Program Files" / "neo4j",
            Path("C:") / "Program Files (x86)" / "neo4j",
            Path.cwd() / "neo4j",
            
            # Common download locations
            Path.home() / "Downloads" / "neo4j-community-5.15.0",
            Path.home() / "Downloads" / "neo4j",
            Path.home() / "Desktop" / "neo4j",
        ]
        
        found_installations = []
        
        for path in search_paths:
            if path.exists():
                print(f"   Checking: {path}")
                
                # Look for Neo4j executables
                possible_exes = [
                    path / "bin" / "neo4j.bat",
                    path / "bin" / "neo4j.exe",
                ]
                
                # For Neo4j Desktop, look deeper
                if "Neo4j Desktop" in str(path):
                    # Neo4j Desktop stores databases in a different structure
                    for subdir in path.rglob("*"):
                        if subdir.is_dir() and "neo4j" in subdir.name.lower():
                            possible_exes.extend([
                                subdir / "bin" / "neo4j.bat",
                                subdir / "bin" / "neo4j.exe",
                            ])
                
                for exe in possible_exes:
                    if exe.exists():
                        found_installations.append(exe)
                        print(f"   ✅ Found: {exe}")
        
        if found_installations:
            self.neo4j_executable = found_installations[0]  # Use first found
            print(f"\n✅ Using Neo4j at: {self.neo4j_executable}")
            return True
        else:
            print("❌ No Neo4j installation found")
            return False
    
    def check_neo4j_desktop_running(self):
        """Check if Neo4j Desktop is running"""
        print("\n🖥️ Checking Neo4j Desktop...")
        
        try:
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq Neo4j Desktop.exe'], 
                                  capture_output=True, text=True)
            if 'Neo4j Desktop.exe' in result.stdout:
                print("✅ Neo4j Desktop is running")
                print("💡 Open Neo4j Desktop and start your database")
                return True
            else:
                print("❌ Neo4j Desktop is not running")
                return False
        except:
            return False
    
    def start_neo4j_desktop(self):
        """Try to start Neo4j Desktop"""
        print("\n🚀 Attempting to start Neo4j Desktop...")
        
        desktop_paths = [
            Path.home() / "AppData" / "Local" / "Programs" / "Neo4j Desktop" / "Neo4j Desktop.exe",
            Path("C:") / "Program Files" / "Neo4j Desktop" / "Neo4j Desktop.exe",
            Path("C:") / "Program Files (x86)" / "Neo4j Desktop" / "Neo4j Desktop.exe",
        ]
        
        for desktop_path in desktop_paths:
            if desktop_path.exists():
                try:
                    subprocess.Popen([str(desktop_path)], shell=True)
                    print(f"✅ Started Neo4j Desktop from: {desktop_path}")
                    print("💡 Please create and start a database in Neo4j Desktop")
                    return True
                except Exception as e:
                    print(f"❌ Failed to start: {e}")
        
        print("❌ Could not find or start Neo4j Desktop")
        return False
    
    def start_neo4j_service(self):
        """Try to start Neo4j as a service"""
        print("\n🔧 Attempting to start Neo4j service...")
        
        if not self.neo4j_executable:
            return False
        
        try:
            # Try to start Neo4j
            neo4j_dir = self.neo4j_executable.parent.parent
            print(f"Starting Neo4j from: {neo4j_dir}")
            
            # Change to Neo4j directory and start
            result = subprocess.run([str(self.neo4j_executable), "console"], 
                                  cwd=str(neo4j_dir),
                                  creationflags=subprocess.CREATE_NEW_CONSOLE)
            
            print("✅ Neo4j startup command executed")
            print("⏳ Waiting for Neo4j to start...")
            
            # Wait and test connection
            for i in range(30):
                try:
                    response = requests.get("http://localhost:7474", timeout=2)
                    if response.status_code == 200:
                        print("✅ Neo4j is running!")
                        return True
                except:
                    pass
                
                time.sleep(2)
                print(f"   Attempt {i+1}/30...")
            
            print("⚠️ Neo4j may still be starting. Check manually at http://localhost:7474")
            return True
            
        except Exception as e:
            print(f"❌ Error starting Neo4j: {e}")
            return False
    
    def provide_manual_instructions(self):
        """Provide manual startup instructions"""
        print("\n📋 MANUAL STARTUP INSTRUCTIONS")
        print("=" * 50)
        
        if self.neo4j_executable:
            print(f"1. 🖥️ Open Command Prompt as Administrator")
            print(f"2. 📁 Navigate to: {self.neo4j_executable.parent.parent}")
            print(f"3. 🚀 Run: {self.neo4j_executable.name} console")
            print(f"4. ⏳ Wait for startup messages")
            print(f"5. 🌐 Open: http://localhost:7474")
        else:
            print("1. 🖥️ Open Neo4j Desktop")
            print("2. ➕ Create a new project")
            print("3. 🗄️ Add a local database")
            print("4. 🔑 Set password: salesforce123")
            print("5. ▶️ Click 'Start' on your database")
            print("6. 🌐 Click 'Open' to access browser")
        
        print("\n🔑 Default Login:")
        print("   Username: neo4j")
        print("   Password: neo4j (first time) or salesforce123")
    
    def run_startup_process(self):
        """Run complete startup process"""
        print("🚀 NEO4J WINDOWS STARTUP HELPER")
        print("=" * 50)
        
        # Check if already running
        try:
            response = requests.get("http://localhost:7474", timeout=2)
            if response.status_code == 200:
                print("✅ Neo4j is already running!")
                print("🌐 Open: http://localhost:7474")
                return True
        except:
            pass
        
        # Check if Neo4j Desktop is running
        if self.check_neo4j_desktop_running():
            print("💡 Neo4j Desktop is running. Please start your database in the Desktop app.")
            return True
        
        # Try to start Neo4j Desktop
        if self.start_neo4j_desktop():
            print("✅ Neo4j Desktop started. Please create and start a database.")
            return True
        
        # Find Neo4j installation
        if self.find_neo4j_installation():
            # Try to start Neo4j service
            if self.start_neo4j_service():
                return True
        
        # Provide manual instructions
        self.provide_manual_instructions()
        
        return False


def main():
    """Main startup function"""
    starter = Neo4jWindowsStarter()
    
    success = starter.run_startup_process()
    
    if success:
        print("\n🎯 NEXT STEPS:")
        print("1. 🌐 Open Neo4j Browser: http://localhost:7474")
        print("2. 🔑 Login with: neo4j / neo4j (or salesforce123)")
        print("3. 📊 Load your data: python neo4j_loader.py")
        print("4. 🔍 Run your first query from NEO4J_QUERY_GUIDE.md")
    else:
        print("\n💡 ALTERNATIVE SOLUTIONS:")
        print("1. Use Neo4j Desktop (recommended)")
        print("2. Download Neo4j Community Edition manually")
        print("3. Use Docker: python docker_neo4j_setup.py")
        print("4. Check MANUAL_NEO4J_SETUP.md for detailed instructions")
    
    print("\n✅ Startup process complete!")


if __name__ == "__main__":
    main()
