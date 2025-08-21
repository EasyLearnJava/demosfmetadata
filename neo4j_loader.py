#!/usr/bin/env python3
"""
Neo4j Loader for Salesforce Metadata
Loads the converted JSON metadata into Neo4j graph database.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from neo4j import GraphDatabase
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Neo4jMetadataLoader:
    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password"):
        """Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.metadata_dir = Path("converted_metadata")
        
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
    
    def clear_database(self):
        """Clear all nodes and relationships from the database"""
        with self.driver.session() as session:
            logger.info("Clearing existing data from Neo4j database...")
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Database cleared successfully")
    
    def create_constraints(self):
        """Create constraints and indexes for better performance"""
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
            logger.info("Creating constraints and indexes...")
            for constraint in constraints:
                try:
                    session.run(constraint)
                    logger.info(f"Created constraint: {constraint}")
                except Exception as e:
                    logger.warning(f"Constraint may already exist: {e}")
    
    def load_objects(self):
        """Load CustomObject nodes"""
        objects_file = self.metadata_dir / "objects.json"
        if not objects_file.exists():
            logger.warning("objects.json not found")
            return
            
        with open(objects_file, 'r', encoding='utf-8') as f:
            objects = json.load(f)
        
        with self.driver.session() as session:
            logger.info(f"Loading {len(objects)} CustomObject nodes...")
            
            for obj in objects:
                # Create main object node
                session.run("""
                    CREATE (o:CustomObject {
                        id: $id,
                        name: $name,
                        type: $type,
                        enableFeeds: $enableFeeds,
                        enableHistory: $enableHistory,
                        sharingModel: $sharingModel,
                        externalSharingModel: $externalSharingModel
                    })
                """, 
                id=obj['id'],
                name=obj['name'],
                type=obj['type'],
                enableFeeds=obj['metadata'].get('enableFeeds', False),
                enableHistory=obj['metadata'].get('enableHistory', False),
                sharingModel=obj['metadata'].get('sharingModel', ''),
                externalSharingModel=obj['metadata'].get('externalSharingModel', '')
                )
                
                # Create field nodes
                for field in obj.get('fields', []):
                    session.run("""
                        CREATE (f:CustomField {
                            id: $id,
                            name: $name,
                            type: $type,
                            object: $object,
                            fullName: $fullName,
                            trackFeedHistory: $trackFeedHistory
                        })
                    """,
                    id=field['id'],
                    name=field['name'],
                    type=field['type'],
                    object=field['object'],
                    fullName=field['metadata'].get('fullName', ''),
                    trackFeedHistory=field['metadata'].get('trackFeedHistory', False)
                    )
                
                # Create ListView nodes
                for listview in obj.get('listViews', []):
                    session.run("""
                        CREATE (lv:ListView {
                            id: $id,
                            name: $name,
                            type: $type,
                            object: $object
                        })
                    """,
                    id=listview['id'],
                    name=listview['name'],
                    type=listview['type'],
                    object=listview['object']
                    )
                
                # Create WebLink nodes
                for weblink in obj.get('webLinks', []):
                    session.run("""
                        CREATE (wl:WebLink {
                            id: $id,
                            name: $name,
                            type: $type,
                            object: $object
                        })
                    """,
                    id=weblink['id'],
                    name=weblink['name'],
                    type=weblink['type'],
                    object=weblink['object']
                    )
            
            logger.info("CustomObject nodes loaded successfully")
    
    def load_layouts(self):
        """Load Layout nodes"""
        layouts_file = self.metadata_dir / "layouts.json"
        if not layouts_file.exists():
            logger.warning("layouts.json not found")
            return
            
        with open(layouts_file, 'r', encoding='utf-8') as f:
            layouts = json.load(f)
        
        with self.driver.session() as session:
            logger.info(f"Loading {len(layouts)} Layout nodes...")
            
            for layout in layouts:
                session.run("""
                    CREATE (l:Layout {
                        id: $id,
                        name: $name,
                        type: $type,
                        object: $object
                    })
                """,
                id=layout['id'],
                name=layout['name'],
                type=layout['type'],
                object=layout['object']
                )
            
            logger.info("Layout nodes loaded successfully")
    
    def load_classes(self):
        """Load ApexClass nodes"""
        classes_file = self.metadata_dir / "classes.json"
        if not classes_file.exists():
            logger.warning("classes.json not found")
            return
            
        with open(classes_file, 'r', encoding='utf-8') as f:
            classes = json.load(f)
        
        with self.driver.session() as session:
            logger.info(f"Loading {len(classes)} ApexClass nodes...")
            
            for cls in classes:
                session.run("""
                    CREATE (c:ApexClass {
                        id: $id,
                        name: $name,
                        type: $type,
                        apiVersion: $apiVersion,
                        status: $status,
                        sourceCodeLength: $sourceCodeLength
                    })
                """,
                id=cls['id'],
                name=cls['name'],
                type=cls['type'],
                apiVersion=cls['metadata'].get('apiVersion', ''),
                status=cls['metadata'].get('status', ''),
                sourceCodeLength=len(cls.get('source_code', ''))
                )
            
            logger.info("ApexClass nodes loaded successfully")
    
    def load_triggers(self):
        """Load ApexTrigger nodes"""
        triggers_file = self.metadata_dir / "triggers.json"
        if not triggers_file.exists():
            logger.warning("triggers.json not found")
            return
            
        with open(triggers_file, 'r', encoding='utf-8') as f:
            triggers = json.load(f)
        
        with self.driver.session() as session:
            logger.info(f"Loading {len(triggers)} ApexTrigger nodes...")
            
            for trigger in triggers:
                session.run("""
                    CREATE (t:ApexTrigger {
                        id: $id,
                        name: $name,
                        type: $type,
                        object: $object,
                        apiVersion: $apiVersion,
                        status: $status,
                        sourceCodeLength: $sourceCodeLength
                    })
                """,
                id=trigger['id'],
                name=trigger['name'],
                type=trigger['type'],
                object=trigger.get('object', ''),
                apiVersion=trigger['metadata'].get('apiVersion', ''),
                status=trigger['metadata'].get('status', ''),
                sourceCodeLength=len(trigger.get('source_code', ''))
                )
            
            logger.info("ApexTrigger nodes loaded successfully")
    
    def load_workflows(self):
        """Load Workflow nodes"""
        workflows_file = self.metadata_dir / "workflows.json"
        if not workflows_file.exists():
            logger.warning("workflows.json not found")
            return
            
        with open(workflows_file, 'r', encoding='utf-8') as f:
            workflows = json.load(f)
        
        with self.driver.session() as session:
            logger.info(f"Loading {len(workflows)} Workflow nodes...")
            
            for workflow in workflows:
                session.run("""
                    CREATE (w:Workflow {
                        id: $id,
                        name: $name,
                        type: $type,
                        object: $object
                    })
                """,
                id=workflow['id'],
                name=workflow['name'],
                type=workflow['type'],
                object=workflow['object']
                )
            
            logger.info("Workflow nodes loaded successfully")

    def load_relationships(self):
        """Load relationships between nodes"""
        relationships_file = self.metadata_dir / "relationships.json"
        if not relationships_file.exists():
            logger.warning("relationships.json not found")
            return

        with open(relationships_file, 'r', encoding='utf-8') as f:
            relationships = json.load(f)

        with self.driver.session() as session:
            logger.info(f"Loading {len(relationships)} relationships...")

            for rel in relationships:
                # Create relationship based on type
                query = f"""
                    MATCH (from {{id: $from_id}})
                    MATCH (to {{id: $to_id}})
                    CREATE (from)-[:{rel['type']}]->(to)
                """

                try:
                    session.run(query, from_id=rel['from'], to_id=rel['to'])
                except Exception as e:
                    logger.warning(f"Failed to create relationship {rel}: {e}")

            logger.info("Relationships loaded successfully")

    def load_all_metadata(self, clear_existing: bool = True):
        """Load all metadata into Neo4j"""
        try:
            if clear_existing:
                self.clear_database()

            self.create_constraints()
            self.load_objects()
            self.load_layouts()
            self.load_classes()
            self.load_triggers()
            self.load_workflows()
            self.load_relationships()

            logger.info("All metadata loaded successfully into Neo4j!")

        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            raise

    def get_database_stats(self):
        """Get statistics about the loaded data"""
        with self.driver.session() as session:
            stats = {}

            # Count nodes by type
            node_types = ['CustomObject', 'CustomField', 'Layout', 'ApexClass', 'ApexTrigger', 'Workflow', 'ListView', 'WebLink']
            for node_type in node_types:
                result = session.run(f"MATCH (n:{node_type}) RETURN count(n) as count")
                stats[node_type] = result.single()['count']

            # Count relationships
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            stats['Relationships'] = result.single()['count']

            return stats


def main():
    """Main execution function"""
    print("Neo4j Metadata Loader for Salesforce")
    print("=" * 40)

    # Configuration - Update these values for your Neo4j instance
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "salesforce123"  # Updated to match your Neo4j password

    loader = None
    try:
        # Initialize loader
        print(f"Connecting to Neo4j at {NEO4J_URI}...")
        loader = Neo4jMetadataLoader(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

        # Load all metadata
        loader.load_all_metadata(clear_existing=True)

        # Print statistics
        stats = loader.get_database_stats()
        print("\nDatabase Statistics:")
        print("-" * 30)
        for key, value in stats.items():
            print(f"{key}: {value}")

        print("\nNext steps:")
        print("1. Open Neo4j Browser at http://localhost:7474")
        print("2. Run queries to explore your Salesforce metadata graph")
        print("3. Example queries:")
        print("   - MATCH (o:CustomObject)-[:HAS_FIELD]->(f:CustomField) RETURN o, f")
        print("   - MATCH (c:ApexClass)-[:DEPENDS_ON]->(o:CustomObject) RETURN c, o")
        print("   - MATCH (t:ApexTrigger)-[:HAS_TRIGGER]-(o:CustomObject) RETURN t, o")

    except Exception as e:
        logger.error(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Neo4j is running")
        print("2. Check your connection details (URI, username, password)")
        print("3. Ensure the converted_metadata directory exists with JSON files")

    finally:
        if loader:
            loader.close()


if __name__ == "__main__":
    main()
