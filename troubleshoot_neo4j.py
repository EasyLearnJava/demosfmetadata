#!/usr/bin/env python3
"""
Neo4j Troubleshooting Tool
Diagnose and fix Neo4j connection issues
"""

import subprocess
import requests
import socket
import time
import os
import platform
from pathlib import Path

class Neo4jTroubleshooter:
    def __init__(self):
        self.system = platform.system().lower()
        self.neo4j_ports = [7474, 7687]
        
    def check_port_availability(self, port):
        """Check if a port is available or in use"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                if result == 0:
                    return "IN_USE"
                else:
                    return "AVAILABLE"
        except Exception:
            return "ERROR"
    
    def check_neo4j_processes(self):
        """Check if Neo4j processes are running"""
        print("🔍 Checking for Neo4j processes...")
        
        try:
            if self.system == "windows":
                result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq java.exe'], 
                                      capture_output=True, text=True)
                if 'java.exe' in result.stdout:
                    print("✅ Java processes found (Neo4j might be running)")
                    # Look for Neo4j specific processes
                    if 'neo4j' in result.stdout.lower():
                        print("✅ Neo4j process detected")
                        return True
                    else:
                        print("⚠️ Java running but no Neo4j process detected")
                else:
                    print("❌ No Java processes found")
            else:
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                if 'neo4j' in result.stdout.lower():
                    print("✅ Neo4j process detected")
                    return True
                else:
                    print("❌ No Neo4j processes found")
            
            return False
            
        except Exception as e:
            print(f"❌ Error checking processes: {e}")
            return False
    
    def check_ports(self):
        """Check Neo4j port status"""
        print("\n🔌 Checking Neo4j ports...")
        
        port_status = {}
        for port in self.neo4j_ports:
            status = self.check_port_availability(port)
            port_status[port] = status
            
            if status == "IN_USE":
                print(f"✅ Port {port}: In use (Good - Neo4j might be running)")
            elif status == "AVAILABLE":
                print(f"❌ Port {port}: Available (Neo4j not running)")
            else:
                print(f"⚠️ Port {port}: Error checking")
        
        return port_status
    
    def test_http_connection(self):
        """Test HTTP connection to Neo4j"""
        print("\n🌐 Testing HTTP connection...")
        
        urls_to_test = [
            "http://localhost:7474",
            "http://127.0.0.1:7474",
            "http://localhost:7474/browser/",
        ]
        
        for url in urls_to_test:
            try:
                print(f"   Testing: {url}")
                response = requests.get(url, timeout=5)
                print(f"   ✅ Response: {response.status_code}")
                if response.status_code == 200:
                    print(f"   🎉 Neo4j is accessible at: {url}")
                    return True
            except requests.exceptions.ConnectionError:
                print(f"   ❌ Connection refused")
            except requests.exceptions.Timeout:
                print(f"   ❌ Connection timeout")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        return False
    
    def check_docker_neo4j(self):
        """Check if Neo4j is running in Docker"""
        print("\n🐳 Checking Docker Neo4j...")
        
        try:
            # Check if Docker is running
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Docker is not running")
                return False
            
            # Check for Neo4j containers
            if 'neo4j' in result.stdout:
                print("✅ Neo4j Docker container found")
                
                # Get container details
                result = subprocess.run(['docker', 'ps', '--filter', 'ancestor=neo4j', '--format', 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'], 
                                      capture_output=True, text=True)
                print("Container details:")
                print(result.stdout)
                return True
            else:
                print("❌ No Neo4j Docker containers running")
                return False
                
        except FileNotFoundError:
            print("❌ Docker not installed")
            return False
        except Exception as e:
            print(f"❌ Error checking Docker: {e}")
            return False
    
    def check_neo4j_desktop(self):
        """Check for Neo4j Desktop installation"""
        print("\n🖥️ Checking Neo4j Desktop...")
        
        if self.system == "windows":
            # Common Neo4j Desktop locations
            desktop_paths = [
                Path.home() / "AppData" / "Local" / "Programs" / "Neo4j Desktop",
                Path("C:") / "Program Files" / "Neo4j Desktop",
                Path("C:") / "Users" / os.getenv('USERNAME', '') / "AppData" / "Local" / "Programs" / "Neo4j Desktop"
            ]
            
            for path in desktop_paths:
                if path.exists():
                    print(f"✅ Neo4j Desktop found at: {path}")
                    return True
            
            print("❌ Neo4j Desktop not found in common locations")
        else:
            print("⚠️ Neo4j Desktop check not implemented for this OS")
        
        return False
    
    def provide_solutions(self, port_status, processes_running, docker_running):
        """Provide specific solutions based on diagnosis"""
        print("\n🔧 TROUBLESHOOTING SOLUTIONS")
        print("=" * 50)
        
        if not processes_running and not docker_running:
            print("❌ PROBLEM: Neo4j is not running")
            print("\n💡 SOLUTIONS:")
            print("1. 🖥️ Neo4j Desktop:")
            print("   - Download from: https://neo4j.com/download/")
            print("   - Install and create a new database")
            print("   - Click 'Start' on your database")
            
            print("\n2. 🐳 Docker Neo4j:")
            print("   - Start Docker Desktop")
            print("   - Run: python docker_neo4j_setup.py")
            
            print("\n3. 📦 Manual Installation:")
            print("   - Follow MANUAL_NEO4J_SETUP.md")
            print("   - Download Neo4j Community Edition")
            print("   - Start with: neo4j\\bin\\neo4j.bat console")
        
        elif processes_running and port_status.get(7474) != "IN_USE":
            print("❌ PROBLEM: Neo4j process running but port 7474 not accessible")
            print("\n💡 SOLUTIONS:")
            print("1. Check Neo4j configuration:")
            print("   - Look for neo4j.conf file")
            print("   - Ensure server.default_listen_address=0.0.0.0")
            print("   - Restart Neo4j")
            
            print("\n2. Firewall/Antivirus:")
            print("   - Check Windows Firewall settings")
            print("   - Allow Neo4j through firewall")
            print("   - Temporarily disable antivirus")
        
        elif docker_running:
            print("✅ Docker Neo4j detected")
            print("\n🔧 Try these URLs:")
            print("   - http://localhost:7474")
            print("   - http://127.0.0.1:7474")
            print("\n🐳 Docker commands:")
            print("   - Check logs: docker logs sf-metadata-neo4j")
            print("   - Restart: docker restart sf-metadata-neo4j")
        
        else:
            print("⚠️ UNCLEAR SITUATION")
            print("\n💡 GENERAL SOLUTIONS:")
            print("1. Restart your computer")
            print("2. Try a different port")
            print("3. Check for conflicting software")
            print("4. Use Neo4j Desktop (easiest option)")
    
    def quick_fix_attempts(self):
        """Attempt quick fixes"""
        print("\n🚀 ATTEMPTING QUICK FIXES...")
        
        # Try to start Docker Neo4j if Docker is available
        try:
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
            if result.returncode == 0:
                print("🐳 Attempting to start Docker Neo4j...")
                
                # Try to start existing container
                start_result = subprocess.run(['docker', 'start', 'sf-metadata-neo4j'], 
                                            capture_output=True, text=True)
                if start_result.returncode == 0:
                    print("✅ Started existing Neo4j container")
                    time.sleep(5)
                    if self.test_http_connection():
                        return True
                else:
                    print("⚠️ No existing container found")
                    print("💡 Run: python docker_neo4j_setup.py")
        except:
            pass
        
        return False
    
    def run_full_diagnosis(self):
        """Run complete diagnosis"""
        print("🔍 NEO4J CONNECTION TROUBLESHOOTER")
        print("=" * 50)
        
        # Check processes
        processes_running = self.check_neo4j_processes()
        
        # Check ports
        port_status = self.check_ports()
        
        # Test HTTP connection
        http_working = self.test_http_connection()
        
        if http_working:
            print("\n🎉 SUCCESS: Neo4j is accessible!")
            print("🌐 Open: http://localhost:7474")
            return True
        
        # Check Docker
        docker_running = self.check_docker_neo4j()
        
        # Check Neo4j Desktop
        self.check_neo4j_desktop()
        
        # Try quick fixes
        if self.quick_fix_attempts():
            print("\n🎉 QUICK FIX SUCCESSFUL!")
            return True
        
        # Provide solutions
        self.provide_solutions(port_status, processes_running, docker_running)
        
        return False


def main():
    """Main troubleshooting function"""
    troubleshooter = Neo4jTroubleshooter()
    
    success = troubleshooter.run_full_diagnosis()
    
    if not success:
        print("\n📞 NEED MORE HELP?")
        print("1. Check the detailed guides:")
        print("   - MANUAL_NEO4J_SETUP.md")
        print("   - NEO4J_SETUP_GUIDE.md")
        print("2. Try Neo4j Desktop (easiest option)")
        print("3. Ensure Java is working: java -version")
        print("4. Check system requirements")
    
    print("\n✅ Troubleshooting complete!")


if __name__ == "__main__":
    main()
