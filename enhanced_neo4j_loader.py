#!/usr/bin/env python3
"""
Enhanced Neo4j Metadata Loader for Salesforce
Loads additional metadata including Contact, Opportunity, and cross-object relationships
"""

import json
import os
from pathlib import Path
from neo4j import GraphDatabase
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedNeo4jMetadataLoader:
    def __init__(self, uri: str, user: str, password: str):
        """Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.metadata_dir = Path("converted_metadata")
        
        # Test connection
        try:
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("✅ Connected to Neo4j successfully")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Neo4j: {e}")
            raise
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
    
    def clear_database(self):
        """Clear all existing data"""
        logger.info("🧹 Clearing existing data from Neo4j database...")
        
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        
        logger.info("✅ Database cleared successfully")
    
    def create_enhanced_constraints(self):
        """Create constraints and indexes for enhanced metadata"""
        logger.info("🔧 Creating enhanced constraints and indexes...")
        
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
                    logger.info(f"✅ Created constraint: {constraint}")
                except Exception as e:
                    logger.warning(f"⚠️ Constraint may already exist: {e}")
    
    def load_enhanced_objects(self):
        """Load Contact and Opportunity objects"""
        logger.info("📋 Loading enhanced objects (Contact, Opportunity)...")

        enhanced_objects = ['Contact', 'Opportunity']

        for obj_name in enhanced_objects:
            # Try comprehensive file first, then regular file
            comprehensive_file = self.metadata_dir / f"{obj_name}_comprehensive.json"
            regular_file = self.metadata_dir / f"{obj_name}.json"

            obj_file = comprehensive_file if comprehensive_file.exists() else regular_file
            
            if not obj_file.exists():
                logger.warning(f"⚠️ {obj_name}.json not found, skipping...")
                continue
            
            try:
                with open(obj_file, 'r') as f:
                    obj_data = json.load(f)
                
                self._load_single_object(obj_data)
                logger.info(f"✅ Loaded {obj_name} object")
                
            except Exception as e:
                logger.error(f"❌ Error loading {obj_name}: {e}")
    
    def _load_single_object(self, obj_data: Dict):
        """Load a single object with its fields"""
        obj_name = obj_data.get('name', '')
        
        with self.driver.session() as session:
            # Create object node
            session.run("""
                MERGE (o:CustomObject {id: $id})
                SET o.name = $name,
                    o.type = $type,
                    o.label = $label,
                    o.description = $description
            """, 
            id=f"{obj_name}_object",
            name=obj_name,
            type="CustomObject",
            label=obj_data.get('label', obj_name),
            description=obj_data.get('description', f"{obj_name} standard object")
            )
            
            # Create field nodes and relationships
            for field in obj_data.get('fields', []):
                field_name = field.get('name', '')
                field_id = f"{obj_name}_{field_name}"
                
                # Create field node
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
                """,
                obj_id=f"{obj_name}_object",
                field_id=field_id
                )
            
            # Create ListView nodes and relationships
            for listview in obj_data.get('listViews', []):
                listview_name = listview.get('name', '')
                listview_id = f"{obj_name}_{listview_name}_listview"
                
                # Create ListView node
                session.run("""
                    MERGE (lv:ListView {id: $id})
                    SET lv.name = $name,
                        lv.object = $object,
                        lv.type = 'ListView'
                """,
                id=listview_id,
                name=listview_name,
                object=obj_name
                )
                
                # Create HAS_LISTVIEW relationship
                session.run("""
                    MATCH (o:CustomObject {id: $obj_id})
                    MATCH (lv:ListView {id: $listview_id})
                    MERGE (o)-[:HAS_LISTVIEW]->(lv)
                """,
                obj_id=f"{obj_name}_object",
                listview_id=listview_id
                )
    
    def load_enhanced_relationships(self):
        """Load enhanced relationships including cross-object relationships"""
        logger.info("🔗 Loading enhanced relationships...")

        # Try comprehensive relationships first, then enhanced, then standard
        comprehensive_rels_file = self.metadata_dir / "comprehensive_relationships.json"
        enhanced_rels_file = self.metadata_dir / "enhanced_relationships.json"

        # Try comprehensive relationships first
        if comprehensive_rels_file.exists():
            rels_file = comprehensive_rels_file
            logger.info("📊 Loading comprehensive relationships...")
        elif enhanced_rels_file.exists():
            rels_file = enhanced_rels_file
            logger.info("📊 Loading enhanced relationships...")
        else:
            logger.warning("⚠️ No enhanced relationships found, loading standard relationships...")
            self.load_standard_relationships()
            return
        
        try:
            with open(rels_file, 'r') as f:
                data = json.load(f)
            
            relationships = data.get('relationships', [])
            logger.info(f"📊 Loading {len(relationships)} enhanced relationships...")
            
            with self.driver.session() as session:
                for rel in relationships:
                    try:
                        self._create_enhanced_relationship(session, rel)
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to create relationship {rel}: {e}")
            
            logger.info("✅ Enhanced relationships loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Error loading enhanced relationships: {e}")
    
    def _create_enhanced_relationship(self, session, rel: Dict):
        """Create a single enhanced relationship"""
        from_entity = rel.get('from', '')
        to_entity = rel.get('to', '')
        rel_type = rel.get('type', '')
        context = rel.get('context', '')
        
        # Handle different relationship types
        if rel_type in ['BELONGS_TO', 'LOOKUP_TO', 'RELATES_TO']:
            # Cross-object relationships
            query = f"""
                MATCH (a:CustomObject {{name: $from}})
                MATCH (b:CustomObject {{name: $to}})
                MERGE (a)-[r:{rel_type}]->(b)
                SET r.context = $context
            """
            session.run(query, from=from_entity, to=to_entity, context=context)
            
        elif rel_type == 'HAS_FIELD':
            # Object to field relationships
            session.run("""
                MATCH (o:CustomObject {name: $from})
                MATCH (f:CustomField {name: $to})
                WHERE f.object = $from
                MERGE (o)-[:HAS_FIELD]->(f)
            """, from=from_entity, to=to_entity)
            
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
    
    def load_standard_relationships(self):
        """Load standard relationships as fallback"""
        logger.info("🔗 Loading standard relationships...")
        
        rels_file = self.metadata_dir / "relationships.json"
        
        if not rels_file.exists():
            logger.warning("⚠️ No relationships file found")
            return
        
        try:
            with open(rels_file, 'r') as f:
                data = json.load(f)
            
            relationships = data.get('relationships', [])
            
            with self.driver.session() as session:
                for rel in relationships:
                    try:
                        self._create_enhanced_relationship(session, rel)
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to create relationship {rel}: {e}")
            
            logger.info("✅ Standard relationships loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Error loading standard relationships: {e}")
    
    def get_enhanced_statistics(self) -> Dict[str, int]:
        """Get comprehensive database statistics"""
        logger.info("📊 Generating enhanced statistics...")
        
        with self.driver.session() as session:
            stats = {}
            
            # Count nodes by type
            node_types = ['CustomObject', 'CustomField', 'Layout', 'ApexClass', 
                         'ApexTrigger', 'Workflow', 'ListView', 'WebLink']
            
            for node_type in node_types:
                result = session.run(f"MATCH (n:{node_type}) RETURN count(n) as count")
                count = result.single()
                stats[node_type] = count['count'] if count else 0
            
            # Count relationships by type
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as rel_type, count(r) as count
                ORDER BY count DESC
            """)
            
            rel_stats = {}
            total_rels = 0
            for record in result:
                rel_type = record['rel_type']
                count = record['count']
                rel_stats[rel_type] = count
                total_rels += count
            
            stats['Total_Relationships'] = total_rels
            stats['Relationship_Types'] = rel_stats
            
            return stats
    
    def print_enhanced_statistics(self):
        """Print comprehensive statistics"""
        stats = self.get_enhanced_statistics()
        
        print("\n📊 ENHANCED DATABASE STATISTICS")
        print("=" * 50)
        
        print("\n🏗️ Node Counts:")
        for node_type, count in stats.items():
            if node_type not in ['Total_Relationships', 'Relationship_Types']:
                print(f"   {node_type:15}: {count:3d}")
        
        print(f"\n🔗 Total Relationships: {stats.get('Total_Relationships', 0)}")
        
        print("\n🔗 Relationship Types:")
        rel_types = stats.get('Relationship_Types', {})
        for rel_type, count in sorted(rel_types.items(), key=lambda x: x[1], reverse=True):
            print(f"   {rel_type:20}: {count:3d}")
    
    def load_all_enhanced_metadata(self, clear_existing: bool = True):
        """Load all enhanced metadata into Neo4j"""
        try:
            if clear_existing:
                self.clear_database()
            
            # Create constraints
            self.create_enhanced_constraints()
            
            # Load existing metadata (from original loader)
            self._load_existing_metadata()
            
            # Load enhanced objects
            self.load_enhanced_objects()
            
            # Load enhanced relationships
            self.load_enhanced_relationships()
            
            # Print statistics
            self.print_enhanced_statistics()
            
            logger.info("🎉 All enhanced metadata loaded successfully into Neo4j!")
            
        except Exception as e:
            logger.error(f"❌ Error loading enhanced metadata: {e}")
            raise
    
    def _load_existing_metadata(self):
        """Load existing metadata using original loader logic"""
        logger.info("📋 Loading existing metadata...")
        
        # Import and use original loader
        from neo4j_loader import Neo4jMetadataLoader
        
        original_loader = Neo4jMetadataLoader(
            self.driver.uri, 
            self.driver._auth[0], 
            self.driver._auth[1]
        )
        
        # Load without clearing (we already cleared)
        original_loader.load_objects()
        original_loader.load_layouts() 
        original_loader.load_classes()
        original_loader.load_triggers()
        original_loader.load_workflows()
        
        original_loader.close()
        logger.info("✅ Existing metadata loaded")

def main():
    """Main execution function"""
    print("🚀 Enhanced Neo4j Metadata Loader for Salesforce")
    print("=" * 60)
    
    # Configuration
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "salesforce123"
    
    loader = None
    try:
        # Initialize enhanced loader
        print(f"🔌 Connecting to Neo4j at {NEO4J_URI}...")
        loader = EnhancedNeo4jMetadataLoader(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
        
        # Load all enhanced metadata
        loader.load_all_enhanced_metadata(clear_existing=True)
        
        print("\n🎯 NEXT STEPS:")
        print("1. 🌐 Open Neo4j Browser: http://localhost:7474")
        print("2. 🔑 Login: neo4j / salesforce123")
        print("3. 🔍 Try the enhanced queries below!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if loader:
            loader.close()

if __name__ == "__main__":
    main()
