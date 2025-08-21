#!/usr/bin/env python3
"""
Explore the loaded Salesforce metadata in Neo4j
"""

from neo4j import GraphDatabase

def explore_neo4j_data():
    """Explore what's loaded in Neo4j"""
    
    # Connect to Neo4j
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "salesforce123"))
    
    print("🔍 EXPLORING YOUR SALESFORCE METADATA IN NEO4J")
    print("=" * 60)
    
    with driver.session() as session:
        
        # 1. Node counts
        print("\n📊 NODE COUNTS:")
        print("-" * 20)
        
        node_types = ["CustomObject", "CustomField", "Layout", "ApexClass", 
                     "ApexTrigger", "Workflow", "ListView", "WebLink"]
        
        for node_type in node_types:
            result = session.run(f"MATCH (n:{node_type}) RETURN count(n) as count")
            count = result.single()["count"]
            print(f"{node_type:15}: {count:3d}")
        
        # 2. Relationship counts
        print("\n🔗 RELATIONSHIP COUNTS:")
        print("-" * 25)
        
        result = session.run("MATCH ()-[r]->() RETURN type(r) as rel_type, count(r) as count ORDER BY count DESC")
        for record in result:
            print(f"{record['rel_type']:20}: {record['count']:3d}")
        
        # 3. Account object details
        print("\n🏢 ACCOUNT OBJECT DETAILS:")
        print("-" * 30)
        
        result = session.run("""
            MATCH (o:CustomObject {name: 'Account'})
            RETURN o.name as name, o.label as label, o.description as description
        """)
        
        for record in result:
            print(f"Name: {record['name']}")
            print(f"Label: {record['label']}")
            print(f"Description: {record['description'][:100]}..." if record['description'] else "No description")
        
        # 4. Sample fields
        print("\n📝 SAMPLE ACCOUNT FIELDS:")
        print("-" * 30)
        
        result = session.run("""
            MATCH (o:CustomObject {name: 'Account'})-[:HAS_FIELD]->(f:CustomField)
            RETURN f.name as field_name, f.type as field_type, f.label as field_label
            ORDER BY f.name
            LIMIT 10
        """)
        
        for record in result:
            print(f"{record['field_name']:20} | {record['field_type']:15} | {record['field_label']}")
        
        # 5. Apex classes
        print("\n💻 APEX CLASSES:")
        print("-" * 20)
        
        result = session.run("""
            MATCH (c:ApexClass)
            RETURN c.name as class_name, c.status as status
            ORDER BY c.name
        """)
        
        for record in result:
            print(f"{record['class_name']:30} | Status: {record['status']}")
        
        # 6. Layouts
        print("\n📋 LAYOUTS:")
        print("-" * 15)
        
        result = session.run("""
            MATCH (l:Layout)
            RETURN l.name as layout_name
            ORDER BY l.name
        """)
        
        for record in result:
            print(f"• {record['layout_name']}")
        
        # 7. Sample relationships
        print("\n🔗 SAMPLE RELATIONSHIPS:")
        print("-" * 25)
        
        result = session.run("""
            MATCH (a)-[r]->(b)
            RETURN labels(a)[0] as from_type, a.name as from_name, 
                   type(r) as relationship, 
                   labels(b)[0] as to_type, b.name as to_name
            LIMIT 10
        """)
        
        for record in result:
            print(f"{record['from_type']}({record['from_name']}) --{record['relationship']}--> {record['to_type']}({record['to_name']})")
    
    driver.close()
    
    print("\n🎯 READY TO EXPLORE!")
    print("=" * 30)
    print("1. Open Neo4j Browser: http://localhost:7474")
    print("2. Login: neo4j / salesforce123")
    print("3. Try these queries:")
    print("   • MATCH (n) RETURN n LIMIT 25")
    print("   • MATCH (o:CustomObject)-[r]-(f) RETURN o, r, f LIMIT 25")
    print("   • MATCH (c:ApexClass)-[:DEPENDS_ON]->(o) RETURN c, o")
    print("\n📚 More queries available in: NEO4J_QUERY_GUIDE.md")

if __name__ == "__main__":
    explore_neo4j_data()
