#!/usr/bin/env python3
"""
Neo4j Connection Test
Test Neo4j connection and run sample queries
"""

from neo4j import GraphDatabase
import json
import sys
from pathlib import Path

class Neo4jTester:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="salesforce123"):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
    
    def test_connection(self):
        """Test basic Neo4j connection"""
        print("🔌 Testing Neo4j Connection...")
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                record = result.single()
                if record and record["test"] == 1:
                    print("✅ Neo4j connection successful!")
                    return True
                else:
                    print("❌ Unexpected response from Neo4j")
                    return False
                    
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("\n🔧 Troubleshooting:")
            print("1. Check if Neo4j is running: http://localhost:7474")
            print("2. Verify credentials (username/password)")
            print("3. Ensure port 7687 is not blocked")
            return False
    
    def test_database_content(self):
        """Test if Salesforce metadata is loaded"""
        print("\n📊 Testing Database Content...")
        
        if not self.driver:
            print("❌ No database connection")
            return False
        
        try:
            with self.driver.session() as session:
                # Count all nodes
                result = session.run("MATCH (n) RETURN count(n) as total")
                total_nodes = result.single()["total"]
                
                if total_nodes == 0:
                    print("⚠️ Database is empty - run 'python neo4j_loader.py' to load data")
                    return False
                
                print(f"✅ Found {total_nodes} nodes in database")
                
                # Count by node type
                result = session.run("""
                    MATCH (n) 
                    RETURN labels(n) as nodeType, count(n) as count
                    ORDER BY count DESC
                """)
                
                print("\n📋 Node Distribution:")
                for record in result:
                    node_type = record["nodeType"][0] if record["nodeType"] else "Unknown"
                    count = record["count"]
                    print(f"  {node_type:15}: {count:3d} nodes")
                
                # Count relationships
                result = session.run("MATCH ()-[r]->() RETURN count(r) as total")
                total_rels = result.single()["total"]
                print(f"\n🔗 Total Relationships: {total_rels}")
                
                return True
                
        except Exception as e:
            print(f"❌ Error querying database: {e}")
            return False
    
    def run_sample_queries(self):
        """Run sample queries to demonstrate functionality"""
        print("\n🔍 Running Sample Queries...")
        
        if not self.driver:
            return False
        
        queries = [
            {
                "name": "Account Object Fields",
                "query": """
                    MATCH (o:CustomObject {name: 'Account'})-[:HAS_FIELD]->(f:CustomField)
                    RETURN o.name as object, collect(f.name)[0..5] as sample_fields, count(f) as total_fields
                """,
                "description": "Show Account object and its fields"
            },
            {
                "name": "Class Dependencies",
                "query": """
                    MATCH (c:ApexClass)-[r:DEPENDS_ON_CLASS]->(dep:ApexClass)
                    RETURN c.name as class, dep.name as depends_on
                    LIMIT 5
                """,
                "description": "Show class dependencies"
            },
            {
                "name": "Trigger Relationships",
                "query": """
                    MATCH (o:CustomObject)-[:HAS_TRIGGER]->(t:ApexTrigger)
                    RETURN o.name as object, t.name as trigger
                """,
                "description": "Show object-trigger relationships"
            },
            {
                "name": "Layout Field Count",
                "query": """
                    MATCH (l:Layout)-[:DISPLAYS_FIELD]->(f:CustomField)
                    RETURN l.name as layout, count(f) as field_count
                    ORDER BY field_count DESC
                    LIMIT 3
                """,
                "description": "Show layouts with most fields"
            }
        ]
        
        try:
            with self.driver.session() as session:
                for query_info in queries:
                    print(f"\n📝 {query_info['name']}:")
                    print(f"   {query_info['description']}")
                    
                    result = session.run(query_info['query'])
                    records = list(result)
                    
                    if records:
                        for record in records:
                            print(f"   → {dict(record)}")
                    else:
                        print("   → No results found")
            
            return True
            
        except Exception as e:
            print(f"❌ Error running sample queries: {e}")
            return False
    
    def show_next_steps(self):
        """Show next steps for exploration"""
        print("\n🎯 NEXT STEPS FOR EXPLORATION")
        print("=" * 50)
        print("1. 🌐 Open Neo4j Browser: http://localhost:7474")
        print(f"2. 🔑 Login: {self.user} / {self.password}")
        print("3. 📖 Use queries from NEO4J_QUERY_GUIDE.md")
        print("4. 🔍 Start with this query:")
        print("""
   MATCH (o:CustomObject {name: 'Account'})-[r]-(connected)
   RETURN o, r, connected
   LIMIT 25
        """)
        print("5. 📊 Explore relationships and dependencies")
        print("6. 🎨 Build custom visualizations")
        
        print("\n📚 Key Files:")
        print("- NEO4J_QUERY_GUIDE.md: 25+ ready-to-use queries")
        print("- MANUAL_NEO4J_SETUP.md: Setup instructions")
        print("- converted_metadata/: Original JSON data")
        print("- relationships_analysis.csv: Relationship data")
    
    def close(self):
        """Close database connection"""
        if self.driver:
            self.driver.close()


def main():
    """Main test function"""
    print("🧪 NEO4J CONNECTION & DATA TEST")
    print("=" * 40)
    
    # Test with default credentials
    tester = Neo4jTester()
    
    # Test connection
    if not tester.test_connection():
        print("\n💡 Try different credentials:")
        print("python test_neo4j_connection.py")
        return
    
    # Test database content
    if not tester.test_database_content():
        print("\n🚀 To load Salesforce metadata:")
        print("python neo4j_loader.py")
        tester.close()
        return
    
    # Run sample queries
    if not tester.run_sample_queries():
        tester.close()
        return
    
    # Show next steps
    tester.show_next_steps()
    
    # Close connection
    tester.close()
    
    print("\n✅ Neo4j test completed successfully!")


if __name__ == "__main__":
    main()
