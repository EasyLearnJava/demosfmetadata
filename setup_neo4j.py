#!/usr/bin/env python3
"""
Neo4j Setup and Installation Guide
Automated setup for Neo4j with Salesforce metadata integration
"""

import os
import sys
import subprocess
import platform
import requests
import zipfile
import shutil
from pathlib import Path
import time

class Neo4jSetup:
    def __init__(self):
        self.system = platform.system().lower()
        self.neo4j_version = "5.15.0"
        self.neo4j_home = Path("neo4j")
        self.neo4j_data = self.neo4j_home / "data"
        self.neo4j_logs = self.neo4j_home / "logs"
        
    def check_java(self):
        """Check if Java is installed"""
        try:
            result = subprocess.run(['java', '-version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Java is installed")
                return True
            else:
                print("❌ Java is not installed")
                return False
        except FileNotFoundError:
            print("❌ Java is not installed")
            return False
    
    def install_java_guide(self):
        """Provide Java installation guide"""
        print("\n📋 JAVA INSTALLATION REQUIRED")
        print("=" * 40)
        print("Neo4j requires Java 17 or later. Please install Java:")
        print("\n🔗 Download Options:")
        print("1. Oracle JDK: https://www.oracle.com/java/technologies/downloads/")
        print("2. OpenJDK: https://adoptium.net/")
        print("3. Amazon Corretto: https://aws.amazon.com/corretto/")
        
        if self.system == "windows":
            print("\n🪟 Windows Installation:")
            print("1. Download Java installer (.msi or .exe)")
            print("2. Run installer as administrator")
            print("3. Add Java to PATH environment variable")
            print("4. Restart command prompt and run this script again")
        
        print("\n✅ Verify installation by running: java -version")
    
    def download_neo4j(self):
        """Download Neo4j Community Edition"""
        if self.neo4j_home.exists():
            print(f"✅ Neo4j directory already exists at {self.neo4j_home}")
            return True
            
        print(f"📥 Downloading Neo4j Community Edition {self.neo4j_version}...")
        
        if self.system == "windows":
            url = f"https://dist.neo4j.org/neo4j-community-{self.neo4j_version}-windows.zip"
            filename = f"neo4j-community-{self.neo4j_version}-windows.zip"
        else:
            url = f"https://dist.neo4j.org/neo4j-community-{self.neo4j_version}-unix.tar.gz"
            filename = f"neo4j-community-{self.neo4j_version}-unix.tar.gz"
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ Downloaded {filename}")
            
            # Extract
            print("📦 Extracting Neo4j...")
            if filename.endswith('.zip'):
                with zipfile.ZipFile(filename, 'r') as zip_ref:
                    zip_ref.extractall('.')
            else:
                subprocess.run(['tar', '-xzf', filename], check=True)
            
            # Rename to standard directory name
            extracted_dir = f"neo4j-community-{self.neo4j_version}"
            if Path(extracted_dir).exists():
                Path(extracted_dir).rename(self.neo4j_home)
            
            # Clean up
            os.remove(filename)
            
            print(f"✅ Neo4j extracted to {self.neo4j_home}")
            return True
            
        except Exception as e:
            print(f"❌ Error downloading Neo4j: {e}")
            return False
    
    def configure_neo4j(self):
        """Configure Neo4j settings"""
        print("⚙️ Configuring Neo4j...")
        
        config_file = self.neo4j_home / "conf" / "neo4j.conf"
        
        if not config_file.exists():
            print(f"❌ Config file not found: {config_file}")
            return False
        
        # Read existing config
        with open(config_file, 'r') as f:
            config = f.read()
        
        # Add/modify settings for better performance and security
        additional_config = """

# Salesforce Metadata Configuration
# Increase memory for large metadata imports
server.memory.heap.initial_size=1G
server.memory.heap.max_size=2G
server.memory.pagecache.size=1G

# Enable APOC procedures (if available)
dbms.security.procedures.unrestricted=apoc.*

# Increase transaction timeout for large imports
dbms.transaction.timeout=300s

# Allow larger result sets
dbms.query.cache_size=1000

# Logging configuration
dbms.logs.query.enabled=true
dbms.logs.query.threshold=1s
"""
        
        # Append configuration
        with open(config_file, 'a') as f:
            f.write(additional_config)
        
        print("✅ Neo4j configured for Salesforce metadata")
        return True
    
    def start_neo4j(self):
        """Start Neo4j server"""
        print("🚀 Starting Neo4j server...")
        
        if self.system == "windows":
            neo4j_cmd = self.neo4j_home / "bin" / "neo4j.bat"
        else:
            neo4j_cmd = self.neo4j_home / "bin" / "neo4j"
        
        if not neo4j_cmd.exists():
            print(f"❌ Neo4j executable not found: {neo4j_cmd}")
            return False
        
        try:
            # Start Neo4j
            if self.system == "windows":
                subprocess.Popen([str(neo4j_cmd), "console"], 
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen([str(neo4j_cmd), "console"])
            
            print("⏳ Waiting for Neo4j to start...")
            time.sleep(10)
            
            # Check if Neo4j is running
            try:
                response = requests.get("http://localhost:7474", timeout=5)
                if response.status_code == 200:
                    print("✅ Neo4j is running!")
                    print("🌐 Neo4j Browser: http://localhost:7474")
                    print("🔌 Bolt Protocol: bolt://localhost:7687")
                    return True
            except:
                pass
            
            print("⚠️ Neo4j may still be starting. Please check manually.")
            return True
            
        except Exception as e:
            print(f"❌ Error starting Neo4j: {e}")
            return False
    
    def setup_complete_guide(self):
        """Provide complete setup instructions"""
        print("\n🎉 NEO4J SETUP COMPLETE!")
        print("=" * 50)
        print("📋 Next Steps:")
        print("1. Open Neo4j Browser: http://localhost:7474")
        print("2. Default credentials:")
        print("   - Username: neo4j")
        print("   - Password: neo4j")
        print("3. You'll be prompted to change the password on first login")
        print("4. Update the password in neo4j_loader.py")
        print("5. Run: python neo4j_loader.py")
        
        print("\n🔧 Configuration Files:")
        print(f"- Neo4j Home: {self.neo4j_home.absolute()}")
        print(f"- Config: {self.neo4j_home / 'conf' / 'neo4j.conf'}")
        print(f"- Data: {self.neo4j_home / 'data'}")
        print(f"- Logs: {self.neo4j_home / 'logs'}")
        
        print("\n🚀 Loading Salesforce Metadata:")
        print("python neo4j_loader.py")


def main():
    """Main setup function"""
    print("🔧 NEO4J SETUP FOR SALESFORCE METADATA")
    print("=" * 50)
    
    setup = Neo4jSetup()
    
    # Check Java
    if not setup.check_java():
        setup.install_java_guide()
        return
    
    # Download and setup Neo4j
    if not setup.download_neo4j():
        return
    
    # Configure Neo4j
    if not setup.configure_neo4j():
        return
    
    # Start Neo4j
    if not setup.start_neo4j():
        return
    
    # Show completion guide
    setup.setup_complete_guide()


if __name__ == "__main__":
    main()
