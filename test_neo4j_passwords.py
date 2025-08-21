#!/usr/bin/env python3
"""
Test common Neo4j passwords
"""

from neo4j import GraphDatabase
import sys

def test_password(password):
    """Test a specific password"""
    try:
        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", password))
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            if result.single()["test"] == 1:
                driver.close()
                return True
        driver.close()
    except Exception as e:
        pass
    return False

def main():
    print("🔑 TESTING COMMON NEO4J PASSWORDS")
    print("=" * 40)
    
    # Common passwords to try
    passwords = [
        "neo4j",
        "password", 
        "admin",
        "salesforce123",
        "",  # empty password
        "123456",
        "demo"
    ]
    
    for password in passwords:
        print(f"Testing password: '{password}'", end="")
        if test_password(password):
            print(" ✅ SUCCESS!")
            print(f"\n🎉 WORKING CREDENTIALS:")
            print(f"   Username: neo4j")
            print(f"   Password: {password}")
            print(f"\n🌐 Login at: http://localhost:7474")
            print(f"🚀 Then run: python neo4j_loader.py")
            return
        else:
            print(" ❌")
    
    print(f"\n❌ None of the common passwords worked")
    print(f"\n💡 SOLUTIONS:")
    print(f"1. Create new database in Neo4j Desktop with password 'salesforce123'")
    print(f"2. Reset password for existing database")
    print(f"3. Check Neo4j Desktop settings for password hint")

if __name__ == "__main__":
    main()
