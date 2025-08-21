#!/usr/bin/env python3
"""
Docker-based Neo4j Setup
Simplified Neo4j setup using Docker
"""

import subprocess
import time
import requests
import os

class DockerNeo4jSetup:
    def __init__(self):
        self.container_name = "sf-metadata-neo4j"
        self.neo4j_password = "salesforce123"
        
    def check_docker(self):
        """Check if Docker is installed and running"""
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Docker is installed")
                
                # Check if Docker is running
                result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ Docker is running")
                    return True
                else:
                    print("❌ Docker is not running. Please start Docker Desktop.")
                    return False
            else:
                print("❌ Docker is not installed")
                return False
        except FileNotFoundError:
            print("❌ Docker is not installed")
            return False
    
    def install_docker_guide(self):
        """Provide Docker installation guide"""
        print("\n📋 DOCKER INSTALLATION REQUIRED")
        print("=" * 40)
        print("🔗 Download Docker Desktop:")
        print("https://www.docker.com/products/docker-desktop/")
        print("\n📝 Installation Steps:")
        print("1. Download Docker Desktop for Windows")
        print("2. Run installer as administrator")
        print("3. Restart computer if prompted")
        print("4. Start Docker Desktop")
        print("5. Wait for Docker to be ready (green icon in system tray)")
        print("6. Run this script again")
    
    def stop_existing_container(self):
        """Stop and remove existing Neo4j container"""
        try:
            # Stop container
            subprocess.run(['docker', 'stop', self.container_name], 
                         capture_output=True, check=False)
            # Remove container
            subprocess.run(['docker', 'rm', self.container_name], 
                         capture_output=True, check=False)
            print("🧹 Cleaned up existing Neo4j container")
        except:
            pass
    
    def start_neo4j_container(self):
        """Start Neo4j in Docker container"""
        print("🚀 Starting Neo4j container...")
        
        # Stop any existing container
        self.stop_existing_container()
        
        # Docker run command
        cmd = [
            'docker', 'run',
            '--name', self.container_name,
            '-p', '7474:7474',
            '-p', '7687:7687',
            '-d',
            '-v', f"{os.getcwd()}/neo4j_data:/data",
            '-v', f"{os.getcwd()}/neo4j_logs:/logs",
            '-v', f"{os.getcwd()}/converted_metadata:/var/lib/neo4j/import",
            '--env', f'NEO4J_AUTH=neo4j/{self.neo4j_password}',
            '--env', 'NEO4J_PLUGINS=["apoc"]',
            '--env', 'NEO4J_server_memory_heap_initial__size=1G',
            '--env', 'NEO4J_server_memory_heap_max__size=2G',
            '--env', 'NEO4J_server_memory_pagecache_size=1G',
            'neo4j:5.15.0'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("✅ Neo4j container started successfully")
            
            # Wait for Neo4j to be ready
            print("⏳ Waiting for Neo4j to be ready...")
            max_attempts = 30
            for attempt in range(max_attempts):
                try:
                    response = requests.get("http://localhost:7474", timeout=2)
                    if response.status_code == 200:
                        print("✅ Neo4j is ready!")
                        return True
                except:
                    pass
                
                time.sleep(2)
                print(f"   Attempt {attempt + 1}/{max_attempts}...")
            
            print("⚠️ Neo4j may still be starting. Please check manually.")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error starting Neo4j container: {e}")
            print(f"Error output: {e.stderr}")
            return False
    
    def update_loader_config(self):
        """Update neo4j_loader.py with Docker configuration"""
        loader_file = "neo4j_loader.py"
        
        if not os.path.exists(loader_file):
            print(f"❌ {loader_file} not found")
            return False
        
        # Read the file
        with open(loader_file, 'r') as f:
            content = f.read()
        
        # Update the configuration section
        old_config = '''    # Configuration - Update these values for your Neo4j instance
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "password"  # Change this to your Neo4j password'''
    
        new_config = f'''    # Configuration - Docker Neo4j instance
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "{self.neo4j_password}"  # Docker Neo4j password'''
        
        if old_config in content:
            content = content.replace(old_config, new_config)
            
            # Write back to file
            with open(loader_file, 'w') as f:
                f.write(content)
            
            print("✅ Updated neo4j_loader.py with Docker configuration")
            return True
        else:
            print("⚠️ Could not automatically update neo4j_loader.py")
            print(f"Please manually set NEO4J_PASSWORD = '{self.neo4j_password}'")
            return False
    
    def show_completion_info(self):
        """Show completion information"""
        print("\n🎉 DOCKER NEO4J SETUP COMPLETE!")
        print("=" * 50)
        print("📋 Connection Details:")
        print("🌐 Neo4j Browser: http://localhost:7474")
        print("🔌 Bolt Protocol: bolt://localhost:7687")
        print(f"👤 Username: neo4j")
        print(f"🔑 Password: {self.neo4j_password}")
        
        print("\n📁 Data Directories:")
        print(f"📊 Database Data: {os.getcwd()}/neo4j_data")
        print(f"📝 Logs: {os.getcwd()}/neo4j_logs")
        print(f"📥 Import: {os.getcwd()}/converted_metadata")
        
        print("\n🚀 Next Steps:")
        print("1. Open Neo4j Browser: http://localhost:7474")
        print(f"2. Login with: neo4j / {self.neo4j_password}")
        print("3. Load Salesforce metadata:")
        print("   python neo4j_loader.py")
        
        print("\n🐳 Docker Commands:")
        print(f"Stop Neo4j:    docker stop {self.container_name}")
        print(f"Start Neo4j:   docker start {self.container_name}")
        print(f"Remove Neo4j:  docker rm {self.container_name}")
        print("View logs:     docker logs sf-metadata-neo4j")


def main():
    """Main setup function"""
    print("🐳 DOCKER NEO4J SETUP FOR SALESFORCE METADATA")
    print("=" * 60)
    
    setup = DockerNeo4jSetup()
    
    # Check Docker
    if not setup.check_docker():
        setup.install_docker_guide()
        return
    
    # Start Neo4j container
    if not setup.start_neo4j_container():
        return
    
    # Update loader configuration
    setup.update_loader_config()
    
    # Show completion info
    setup.show_completion_info()


if __name__ == "__main__":
    main()
