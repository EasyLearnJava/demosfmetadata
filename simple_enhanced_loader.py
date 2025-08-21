#!/usr/bin/env python3
"""
Simple Enhanced Neo4j Loader
Load comprehensive Salesforce metadata into Neo4j
"""

import json
from pathlib import Path
from neo4j import GraphDatabase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleEnhancedLoader:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.metadata_dir = Path("converted_metadata")
        
        # Test connection
        with self.driver.session() as session:
            session.run("RETURN 1")
        logger.info("✅ Connected to Neo4j")
    
    def close(self):
        if self.driver:
            self.driver.close()
    
    def clear_database(self):
        logger.info("🧹 Clearing database...")
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        logger.info("✅ Database cleared")
    
    def create_constraints(self):
        logger.info("🔧 Creating constraints...")
        constraints = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (o:CustomObject) REQUIRE o.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (f:CustomField) REQUIRE f.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (l:Layout) REQUIRE l.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:ApexClass) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (t:ApexTrigger) REQUIRE t.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (w:Workflow) REQUIRE w.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (lv:ListView) REQUIRE lv.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (wl:WebLink) REQUIRE wl.id IS UNIQUE"
        ]
        
        with self.driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                    logger.info(f"✅ Created constraint")
                except Exception as e:
                    logger.warning(f"⚠️ Constraint exists: {e}")
    
    def load_comprehensive_objects(self):
        logger.info("📋 Loading comprehensive objects...")
        
        objects = ['Contact', 'Opportunity']
        
        for obj_name in objects:
            comp_file = self.metadata_dir / f"{obj_name}_comprehensive.json"
            
            if not comp_file.exists():
                logger.warning(f"⚠️ {obj_name}_comprehensive.json not found")
                continue
            
            with open(comp_file, 'r') as f:
                obj_data = json.load(f)
            
            self._load_single_comprehensive_object(obj_data)
            logger.info(f"✅ Loaded {obj_name}")
    
    def _load_single_comprehensive_object(self, obj_data):
        obj_name = obj_data.get('name', '')
        
        with self.driver.session() as session:
            # Create object node
            session.run("""
                MERGE (o:CustomObject {id: $id})
                SET o.name = $name, o.type = 'CustomObject'
            """, id=f"{obj_name}_object", name=obj_name)
            
            # Create field nodes
            for field in obj_data.get('fields', []):
                field_name = field.get('name', '')
                field_id = f"{obj_name}_{field_name}"
                
                session.run("""
                    MERGE (f:CustomField {id: $id})
                    SET f.name = $name,
                        f.type = $type,
                        f.label = $label,
                        f.object = $object
                """, 
                id=field_id,
                name=field_name,
                type=field.get('type', 'Unknown'),
                label=field.get('label', field_name),
                object=obj_name
                )
                
                # Create HAS_FIELD relationship
                session.run("""
                    MATCH (o:CustomObject {id: $obj_id})
                    MATCH (f:CustomField {id: $field_id})
                    MERGE (o)-[:HAS_FIELD]->(f)
                """, obj_id=f"{obj_name}_object", field_id=field_id)
            
            # Create ListView nodes
            for listview in obj_data.get('listViews', []):
                listview_name = listview.get('name', '')
                listview_id = f"{obj_name}_{listview_name}_listview"
                
                session.run("""
                    MERGE (lv:ListView {id: $id})
                    SET lv.name = $name, lv.object = $object, lv.type = 'ListView'
                """, id=listview_id, name=listview_name, object=obj_name)
                
                # Create HAS_LISTVIEW relationship
                session.run("""
                    MATCH (o:CustomObject {id: $obj_id})
                    MATCH (lv:ListView {id: $listview_id})
                    MERGE (o)-[:HAS_LISTVIEW]->(lv)
                """, obj_id=f"{obj_name}_object", listview_id=listview_id)
            
            # Create WebLink nodes
            for weblink in obj_data.get('webLinks', []):
                weblink_name = weblink.get('name', '')
                weblink_id = f"{obj_name}_{weblink_name}_weblink"
                
                session.run("""
                    MERGE (wl:WebLink {id: $id})
                    SET wl.name = $name, wl.object = $object, wl.type = 'WebLink'
                """, id=weblink_id, name=weblink_name, object=obj_name)
                
                # Create HAS_WEBLINK relationship
                session.run("""
                    MATCH (o:CustomObject {id: $obj_id})
                    MATCH (wl:WebLink {id: $weblink_id})
                    MERGE (o)-[:HAS_WEBLINK]->(wl)
                """, obj_id=f"{obj_name}_object", weblink_id=weblink_id)
    
    def load_comprehensive_relationships(self):
        logger.info("🔗 Loading comprehensive relationships...")
        
        comp_rels_file = self.metadata_dir / "comprehensive_relationships.json"
        
        if not comp_rels_file.exists():
            logger.warning("⚠️ comprehensive_relationships.json not found")
            return
        
        with open(comp_rels_file, 'r') as f:
            data = json.load(f)
        
        relationships = data.get('relationships', [])
        logger.info(f"📊 Loading {len(relationships)} relationships...")
        
        with self.driver.session() as session:
            for rel in relationships:
                try:
                    self._create_relationship(session, rel)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to create relationship: {e}")
        
        logger.info("✅ Comprehensive relationships loaded")
    
    def _create_relationship(self, session, rel):
        from_entity = rel.get('from', '')
        to_entity = rel.get('to', '')
        rel_type = rel.get('type', '')
        context = rel.get('context', '')
        
        if rel_type in ['BELONGS_TO', 'LOOKUP_TO', 'RELATES_TO', 'REFERENCES']:
            # Cross-object relationships
            query = f"""
                MATCH (a:CustomObject {{name: $from}})
                MATCH (b:CustomObject {{name: $to}})
                MERGE (a)-[r:{rel_type}]->(b)
                SET r.context = $context
            """
            session.run(query, from=from_entity, to=to_entity, context=context)
            
        elif rel_type == 'HAS_FIELD':
            # Object to field relationships (already created above)
            pass
            
        elif rel_type == 'HAS_LISTVIEW':
            # Object to listview relationships (already created above)
            pass
            
        elif rel_type == 'HAS_WEBLINK':
            # Object to weblink relationships (already created above)
            pass
            
        elif rel_type == 'DISPLAYS_FIELD':
            # Layout to field relationships
            session.run("""
                MATCH (l:Layout {name: $from})
                MATCH (f:CustomField {name: $to})
                MERGE (l)-[:DISPLAYS_FIELD]->(f)
            """, from=from_entity, to=to_entity)
        
        else:
            # Generic relationship
            query = f"""
                MATCH (a {{name: $from}})
                MATCH (b {{name: $to}})
                MERGE (a)-[r:{rel_type}]->(b)
                SET r.context = $context
            """
            session.run(query, from=from_entity, to=to_entity, context=context)
    
    def get_statistics(self):
        with self.driver.session() as session:
            stats = {}
            
            # Count nodes
            node_types = ['CustomObject', 'CustomField', 'Layout', 'ApexClass', 
                         'ApexTrigger', 'Workflow', 'ListView', 'WebLink']
            
            for node_type in node_types:
                result = session.run(f"MATCH (n:{node_type}) RETURN count(n) as count")
                count = result.single()
                stats[node_type] = count['count'] if count else 0
            
            # Count relationships
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            count = result.single()
            stats['Total_Relationships'] = count['count'] if count else 0
            
            return stats
    
    def print_statistics(self):
        stats = self.get_statistics()
        
        print("\n📊 COMPREHENSIVE DATABASE STATISTICS")
        print("=" * 50)
        
        for node_type, count in stats.items():
            if node_type != 'Total_Relationships':
                print(f"   {node_type:15}: {count:3d}")
        
        print(f"\n🔗 Total Relationships: {stats.get('Total_Relationships', 0)}")
    
    def load_all_comprehensive_metadata(self):
        try:
            self.clear_database()
            self.create_constraints()
            
            # Load existing metadata first
            self._load_existing_metadata()
            
            # Load comprehensive objects
            self.load_comprehensive_objects()
            
            # Load comprehensive relationships
            self.load_comprehensive_relationships()
            
            # Print statistics
            self.print_statistics()
            
            logger.info("🎉 All comprehensive metadata loaded successfully!")
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            raise
    
    def _load_existing_metadata(self):
        logger.info("📋 Loading existing metadata...")
        
        # Use original loader for existing data
        from neo4j_loader import Neo4jMetadataLoader
        
        original_loader = Neo4jMetadataLoader(
            "bolt://localhost:7687", 
            "neo4j", 
            "salesforce123"
        )
        
        # Load without clearing
        original_loader.load_objects()
        original_loader.load_layouts()
        original_loader.load_classes()
        original_loader.load_triggers()
        original_loader.load_workflows()
        
        original_loader.close()
        logger.info("✅ Existing metadata loaded")

def main():
    print("🚀 Simple Enhanced Neo4j Loader")
    print("=" * 50)
    
    loader = None
    try:
        loader = SimpleEnhancedLoader("bolt://localhost:7687", "neo4j", "salesforce123")
        loader.load_all_comprehensive_metadata()
        
        print("\n🎯 SUCCESS! Your enhanced metadata is now in Neo4j!")
        print("🌐 Open Neo4j Browser: http://localhost:7474")
        print("🔑 Login: neo4j / salesforce123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if loader:
            loader.close()

if __name__ == "__main__":
    main()
