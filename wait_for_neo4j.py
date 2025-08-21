#!/usr/bin/env python3
"""
Wait for Neo4j to become available
Monitor Neo4j startup and notify when ready
"""

import time
import requests
from datetime import datetime

def wait_for_neo4j(max_wait_minutes=10):
    """Wait for Neo4j to become available"""
    print("⏳ Waiting for Neo4j to become available...")
    print("💡 Make sure to create and start a database in Neo4j Desktop")
    print("=" * 60)
    
    max_attempts = max_wait_minutes * 6  # Check every 10 seconds
    
    for attempt in range(1, max_attempts + 1):
        try:
            # Test connection
            response = requests.get("http://localhost:7474", timeout=3)
            
            if response.status_code == 200:
                print(f"\n🎉 SUCCESS! Neo4j is available!")
                print(f"🌐 Neo4j Browser: http://localhost:7474")
                print(f"⏰ Ready after {attempt * 10} seconds")
                
                # Test if we can connect to the database
                print("\n🔍 Testing database connection...")
                try:
                    from neo4j import GraphDatabase
                    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "salesforce123"))
                    with driver.session() as session:
                        result = session.run("RETURN 1 as test")
                        if result.single()["test"] == 1:
                            print("✅ Database connection successful!")
                            print("🚀 Ready to load data: python neo4j_loader.py")
                            driver.close()
                            return True
                    driver.close()
                except Exception as e:
                    print(f"⚠️ Browser available but database not ready: {e}")
                    print("💡 Make sure database is started in Neo4j Desktop")
                    print("🔑 Check password is set to: salesforce123")
                
                return True
                
        except requests.exceptions.ConnectionError:
            # Neo4j not ready yet
            pass
        except Exception as e:
            print(f"⚠️ Error checking Neo4j: {e}")
        
        # Progress indicator
        if attempt % 6 == 0:  # Every minute
            minutes_waited = attempt // 6
            print(f"⏳ Still waiting... ({minutes_waited} minute{'s' if minutes_waited != 1 else ''} elapsed)")
            print("💡 In Neo4j Desktop: Create project → Add database → Start database")
        elif attempt % 2 == 0:  # Every 20 seconds
            print(".", end="", flush=True)
        
        time.sleep(10)
    
    print(f"\n❌ Neo4j did not become available within {max_wait_minutes} minutes")
    print("🔧 Troubleshooting steps:")
    print("1. Check Neo4j Desktop is open")
    print("2. Create and start a database")
    print("3. Verify password is 'salesforce123'")
    print("4. Try accessing http://localhost:7474 manually")
    
    return False

def main():
    """Main monitoring function"""
    print("🔍 NEO4J AVAILABILITY MONITOR")
    print("=" * 40)
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    # Check if already available
    try:
        response = requests.get("http://localhost:7474", timeout=2)
        if response.status_code == 200:
            print("✅ Neo4j is already available!")
            print("🌐 Open: http://localhost:7474")
            return
    except:
        pass
    
    # Wait for Neo4j
    if wait_for_neo4j():
        print("\n🎯 NEXT STEPS:")
        print("1. Open Neo4j Browser: http://localhost:7474")
        print("2. Login: neo4j / salesforce123")
        print("3. Load data: python neo4j_loader.py")
        print("4. Run first query from NEO4J_QUERY_GUIDE.md")
    else:
        print("\n📞 Need help? Check:")
        print("- NEO4J_DESKTOP_SETUP_STEPS.md")
        print("- Run: python troubleshoot_neo4j.py")

if __name__ == "__main__":
    main()
