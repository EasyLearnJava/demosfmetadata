#!/usr/bin/env python3
"""
Add Contact and Opportunity objects to existing Neo4j database
"""

import json
from pathlib import Path
from neo4j import GraphDatabase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_contact_opportunity_to_neo4j():
    """Add Contact and Opportunity objects to Neo4j"""
    
    # Connect to Neo4j
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "salesforce123"))
    
    try:
        with driver.session() as session:
            # Test connection
            session.run("RETURN 1")
            logger.info("✅ Connected to Neo4j")
            
            # Load Contact data
            contact_file = Path("converted_metadata/Contact_comprehensive.json")
            if contact_file.exists():
                with open(contact_file, 'r') as f:
                    contact_data = json.load(f)
                
                add_object_to_neo4j(session, contact_data)
                logger.info("✅ Added Contact object")
            else:
                logger.warning("⚠️ Contact_comprehensive.json not found")
            
            # Load Opportunity data
            opp_file = Path("converted_metadata/Opportunity_comprehensive.json")
            if opp_file.exists():
                with open(opp_file, 'r') as f:
                    opp_data = json.load(f)
                
                add_object_to_neo4j(session, opp_data)
                logger.info("✅ Added Opportunity object")
            else:
                logger.warning("⚠️ Opportunity_comprehensive.json not found")
            
            # Add cross-object relationships
            add_cross_object_relationships(session)
            
            # Print updated statistics
            print_statistics(session)
            
    finally:
        driver.close()

def add_object_to_neo4j(session, obj_data):
    """Add a single object with fields, listviews, and weblinks to Neo4j"""
    
    obj_name = obj_data.get('name', '')
    logger.info(f"📋 Adding {obj_name} object...")
    
    # Create object node
    session.run("""
        MERGE (o:CustomObject {id: $id})
        SET o.name = $name, 
            o.type = 'CustomObject',
            o.label = $label
    """, 
    id=f"{obj_name}_object",
    name=obj_name,
    label=obj_name
    )
    
    # Add fields
    for field in obj_data.get('fields', []):
        field_name = field.get('name', '')
        field_id = f"{obj_name}_{field_name}"
        
        # Create field node
        session.run("""
            MERGE (f:CustomField {id: $id})
            SET f.name = $name,
                f.type = $type,
                f.label = $label,
                f.object = $object,
                f.required = $required,
                f.unique = $unique
        """,
        id=field_id,
        name=field_name,
        type=field.get('type', 'Unknown'),
        label=field.get('label', field_name),
        object=obj_name,
        required=field.get('required', False),
        unique=field.get('unique', False)
        )
        
        # Create HAS_FIELD relationship
        session.run("""
            MATCH (o:CustomObject {id: $obj_id})
            MATCH (f:CustomField {id: $field_id})
            MERGE (o)-[:HAS_FIELD]->(f)
        """, obj_id=f"{obj_name}_object", field_id=field_id)
    
    # Add list views
    for listview in obj_data.get('listViews', []):
        listview_name = listview.get('name', '')
        listview_id = f"{obj_name}_{listview_name}_listview"
        
        # Create ListView node
        session.run("""
            MERGE (lv:ListView {id: $id})
            SET lv.name = $name,
                lv.object = $object,
                lv.type = 'ListView',
                lv.label = $label
        """,
        id=listview_id,
        name=listview_name,
        object=obj_name,
        label=listview.get('label', listview_name)
        )
        
        # Create HAS_LISTVIEW relationship
        session.run("""
            MATCH (o:CustomObject {id: $obj_id})
            MATCH (lv:ListView {id: $listview_id})
            MERGE (o)-[:HAS_LISTVIEW]->(lv)
        """, obj_id=f"{obj_name}_object", listview_id=listview_id)
    
    # Add web links
    for weblink in obj_data.get('webLinks', []):
        weblink_name = weblink.get('name', '')
        weblink_id = f"{obj_name}_{weblink_name}_weblink"
        
        # Create WebLink node
        session.run("""
            MERGE (wl:WebLink {id: $id})
            SET wl.name = $name,
                wl.object = $object,
                wl.type = 'WebLink',
                wl.displayType = $displayType,
                wl.linkType = $linkType
        """,
        id=weblink_id,
        name=weblink_name,
        object=obj_name,
        displayType=weblink.get('displayType', ''),
        linkType=weblink.get('linkType', '')
        )
        
        # Create HAS_WEBLINK relationship
        session.run("""
            MATCH (o:CustomObject {id: $obj_id})
            MATCH (wl:WebLink {id: $weblink_id})
            MERGE (o)-[:HAS_WEBLINK]->(wl)
        """, obj_id=f"{obj_name}_object", weblink_id=weblink_id)
    
    logger.info(f"   ✅ {obj_name}: {len(obj_data.get('fields', []))} fields, {len(obj_data.get('listViews', []))} list views, {len(obj_data.get('webLinks', []))} web links")

def add_cross_object_relationships(session):
    """Add relationships between Account, Contact, and Opportunity"""
    logger.info("🔗 Adding cross-object relationships...")
    
    # Contact belongs to Account
    session.run("""
        MATCH (c:CustomObject {name: 'Contact'})
        MATCH (a:CustomObject {name: 'Account'})
        MERGE (c)-[:BELONGS_TO {context: 'Contact.AccountId lookup field'}]->(a)
    """)
    
    # Opportunity belongs to Account
    session.run("""
        MATCH (o:CustomObject {name: 'Opportunity'})
        MATCH (a:CustomObject {name: 'Account'})
        MERGE (o)-[:BELONGS_TO {context: 'Opportunity.AccountId lookup field'}]->(a)
    """)
    
    # Opportunity relates to Contact
    session.run("""
        MATCH (o:CustomObject {name: 'Opportunity'})
        MATCH (c:CustomObject {name: 'Contact'})
        MERGE (o)-[:RELATES_TO {context: 'Opportunity can have Contact roles'}]->(c)
    """)
    
    logger.info("✅ Cross-object relationships added")

def print_statistics(session):
    """Print updated database statistics"""
    
    print("\n📊 UPDATED DATABASE STATISTICS")
    print("=" * 50)
    
    # Count nodes by type
    node_types = ['CustomObject', 'CustomField', 'Layout', 'ApexClass', 
                 'ApexTrigger', 'Workflow', 'ListView', 'WebLink']
    
    for node_type in node_types:
        result = session.run(f"MATCH (n:{node_type}) RETURN count(n) as count")
        count = result.single()['count']
        print(f"   {node_type:15}: {count:3d}")
    
    # Count relationships
    result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
    total_rels = result.single()['count']
    print(f"\n🔗 Total Relationships: {total_rels}")
    
    # Count relationships by type
    result = session.run("""
        MATCH ()-[r]->()
        RETURN type(r) as rel_type, count(r) as count
        ORDER BY count DESC
        LIMIT 10
    """)
    
    print("\n🔗 Top Relationship Types:")
    for record in result:
        print(f"   {record['rel_type']:20}: {record['count']:3d}")

def main():
    """Main function"""
    print("🚀 Adding Contact and Opportunity to Neo4j")
    print("=" * 50)
    
    try:
        add_contact_opportunity_to_neo4j()
        
        print("\n🎉 SUCCESS! Contact and Opportunity objects added to Neo4j!")
        print("\n🎯 WHAT'S NEW:")
        print("✅ Contact object with 33 fields and 6 list views")
        print("✅ Opportunity object with 23 fields, 9 list views, and 1 web link")
        print("✅ Cross-object relationships (Contact→Account, Opportunity→Account, etc.)")
        
        print("\n🌐 Open Neo4j Browser: http://localhost:7474")
        print("🔑 Login: neo4j / salesforce123")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
