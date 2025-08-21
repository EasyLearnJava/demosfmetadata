#!/usr/bin/env python3
"""
Enhanced Salesforce Metadata Parser
Parse package.xml and discover additional metadata components
"""

import xml.etree.ElementTree as ET
import os
import json
from pathlib import Path
from typing import Dict, List, Set
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedMetadataParser:
    def __init__(self, metadata_dir: str = "."):
        self.metadata_dir = Path(metadata_dir)
        self.package_components = {}
        self.discovered_metadata = {}
        self.relationships = []
        
    def parse_package_xml(self, package_path: str = "manifest/package.xml") -> Dict[str, List[str]]:
        """Parse package.xml to discover all metadata components"""
        logger.info(f"📦 Parsing package.xml: {package_path}")
        
        try:
            tree = ET.parse(package_path)
            root = tree.getroot()
            
            # Handle namespace
            namespace = {'sf': 'http://soap.sforce.com/2006/04/metadata'}
            
            components = {}
            
            # Parse each metadata type
            for types_elem in root.findall('sf:types', namespace):
                name_elem = types_elem.find('sf:name', namespace)
                if name_elem is not None:
                    metadata_type = name_elem.text
                    members = []
                    
                    for member_elem in types_elem.findall('sf:members', namespace):
                        if member_elem.text:
                            members.append(member_elem.text)
                    
                    components[metadata_type] = members
                    logger.info(f"   📋 {metadata_type}: {len(members)} components")
            
            self.package_components = components
            return components
            
        except Exception as e:
            logger.error(f"❌ Error parsing package.xml: {e}")
            return {}
    
    def discover_additional_metadata(self) -> Dict[str, any]:
        """Discover metadata files that might not be in our current processing"""
        logger.info("🔍 Discovering additional metadata files...")
        
        discovered = {
            'objects': [],
            'layouts': [],
            'classes': [],
            'triggers': [],
            'workflows': [],
            'flows': [],
            'reports': [],
            'dashboards': [],
            'profiles': [],
            'permissionsets': []
        }
        
        # Search for object files
        objects_dir = self.metadata_dir / "force-app" / "main" / "default" / "objects"
        if objects_dir.exists():
            for obj_dir in objects_dir.iterdir():
                if obj_dir.is_dir():
                    obj_file = obj_dir / f"{obj_dir.name}.object-meta.xml"
                    if obj_file.exists():
                        discovered['objects'].append(obj_dir.name)
                        logger.info(f"   📋 Found object: {obj_dir.name}")
        
        # Search for layout files
        layouts_dir = self.metadata_dir / "force-app" / "main" / "default" / "layouts"
        if layouts_dir.exists():
            for layout_file in layouts_dir.glob("*.layout-meta.xml"):
                layout_name = layout_file.stem.replace('.layout-meta', '')
                discovered['layouts'].append(layout_name)
                logger.info(f"   📄 Found layout: {layout_name}")
        
        # Search for class files
        classes_dir = self.metadata_dir / "classes"
        if classes_dir.exists():
            for class_file in classes_dir.glob("*.cls-meta.xml"):
                class_name = class_file.stem.replace('.cls-meta', '')
                discovered['classes'].append(class_name)
                logger.info(f"   💻 Found class: {class_name}")
        
        # Search for trigger files
        triggers_dir = self.metadata_dir / "triggers"
        if triggers_dir.exists():
            for trigger_file in triggers_dir.glob("*.trigger-meta.xml"):
                trigger_name = trigger_file.stem.replace('.trigger-meta', '')
                discovered['triggers'].append(trigger_name)
                logger.info(f"   ⚡ Found trigger: {trigger_name}")
        
        # Search for workflow files
        workflows_dir = self.metadata_dir / "workflows"
        if workflows_dir.exists():
            for workflow_file in workflows_dir.glob("*.workflow-meta.xml"):
                workflow_name = workflow_file.stem.replace('.workflow-meta', '')
                discovered['workflows'].append(workflow_name)
                logger.info(f"   🔄 Found workflow: {workflow_name}")
        
        self.discovered_metadata = discovered
        return discovered
    
    def parse_contact_object(self) -> Dict:
        """Parse Contact object metadata"""
        contact_file = self.metadata_dir / "force-app" / "main" / "default" / "objects" / "Contact" / "Contact.object-meta.xml"
        
        if not contact_file.exists():
            logger.warning("❌ Contact.object-meta.xml not found")
            return {}
        
        logger.info("📋 Parsing Contact object...")
        
        try:
            tree = ET.parse(contact_file)
            root = tree.getroot()
            
            contact_data = {
                'name': 'Contact',
                'type': 'CustomObject',
                'fields': [],
                'listViews': [],
                'webLinks': []
            }
            
            # Parse fields
            for field in root.findall('.//{http://soap.sforce.com/2006/04/metadata}fields'):
                field_name = field.find('.//{http://soap.sforce.com/2006/04/metadata}fullName')
                field_type = field.find('.//{http://soap.sforce.com/2006/04/metadata}type')
                field_label = field.find('.//{http://soap.sforce.com/2006/04/metadata}label')
                
                if field_name is not None:
                    contact_data['fields'].append({
                        'name': field_name.text,
                        'type': field_type.text if field_type is not None else 'Unknown',
                        'label': field_label.text if field_label is not None else field_name.text
                    })
            
            # Parse list views
            for listview in root.findall('.//{http://soap.sforce.com/2006/04/metadata}listViews'):
                listview_name = listview.find('.//{http://soap.sforce.com/2006/04/metadata}fullName')
                if listview_name is not None:
                    contact_data['listViews'].append({
                        'name': listview_name.text,
                        'type': 'ListView'
                    })
            
            logger.info(f"   ✅ Contact: {len(contact_data['fields'])} fields, {len(contact_data['listViews'])} list views")
            return contact_data
            
        except Exception as e:
            logger.error(f"❌ Error parsing Contact object: {e}")
            return {}
    
    def parse_opportunity_object(self) -> Dict:
        """Parse Opportunity object metadata"""
        opp_file = self.metadata_dir / "force-app" / "main" / "default" / "objects" / "Opportunity" / "Opportunity.object-meta.xml"
        
        if not opp_file.exists():
            logger.warning("❌ Opportunity.object-meta.xml not found")
            return {}
        
        logger.info("📋 Parsing Opportunity object...")
        
        try:
            tree = ET.parse(opp_file)
            root = tree.getroot()
            
            opp_data = {
                'name': 'Opportunity',
                'type': 'CustomObject',
                'fields': [],
                'listViews': [],
                'webLinks': []
            }
            
            # Parse fields
            for field in root.findall('.//{http://soap.sforce.com/2006/04/metadata}fields'):
                field_name = field.find('.//{http://soap.sforce.com/2006/04/metadata}fullName')
                field_type = field.find('.//{http://soap.sforce.com/2006/04/metadata}type')
                field_label = field.find('.//{http://soap.sforce.com/2006/04/metadata}label')
                
                if field_name is not None:
                    opp_data['fields'].append({
                        'name': field_name.text,
                        'type': field_type.text if field_type is not None else 'Unknown',
                        'label': field_label.text if field_label is not None else field_name.text
                    })
            
            # Parse list views
            for listview in root.findall('.//{http://soap.sforce.com/2006/04/metadata}listViews'):
                listview_name = listview.find('.//{http://soap.sforce.com/2006/04/metadata}fullName')
                if listview_name is not None:
                    opp_data['listViews'].append({
                        'name': listview_name.text,
                        'type': 'ListView'
                    })
            
            logger.info(f"   ✅ Opportunity: {len(opp_data['fields'])} fields, {len(opp_data['listViews'])} list views")
            return opp_data
            
        except Exception as e:
            logger.error(f"❌ Error parsing Opportunity object: {e}")
            return {}
    
    def analyze_cross_object_relationships(self, objects_data: List[Dict]) -> List[Dict]:
        """Analyze relationships between objects"""
        logger.info("🔗 Analyzing cross-object relationships...")
        
        relationships = []
        
        # Standard Salesforce relationships
        standard_relationships = [
            {
                'from': 'Contact',
                'to': 'Account',
                'type': 'BELONGS_TO',
                'context': 'Contact.AccountId lookup field'
            },
            {
                'from': 'Opportunity',
                'to': 'Account', 
                'type': 'BELONGS_TO',
                'context': 'Opportunity.AccountId lookup field'
            },
            {
                'from': 'Opportunity',
                'to': 'Contact',
                'type': 'RELATES_TO',
                'context': 'Opportunity can have Contact roles'
            }
        ]
        
        relationships.extend(standard_relationships)
        
        # Look for lookup/master-detail fields
        for obj_data in objects_data:
            obj_name = obj_data.get('name', '')
            
            for field in obj_data.get('fields', []):
                field_name = field.get('name', '')
                field_type = field.get('type', '')
                
                # Check for lookup fields
                if field_type in ['Lookup', 'MasterDetail'] or field_name.endswith('Id'):
                    # Try to determine target object
                    if field_name == 'AccountId':
                        relationships.append({
                            'from': obj_name,
                            'to': 'Account',
                            'type': 'LOOKUP_TO',
                            'context': f'{obj_name}.{field_name} field'
                        })
                    elif field_name == 'ContactId':
                        relationships.append({
                            'from': obj_name,
                            'to': 'Contact', 
                            'type': 'LOOKUP_TO',
                            'context': f'{obj_name}.{field_name} field'
                        })
        
        logger.info(f"   ✅ Found {len(relationships)} cross-object relationships")
        return relationships
    
    def save_enhanced_metadata(self, output_dir: str = "converted_metadata"):
        """Save all discovered metadata to JSON files"""
        logger.info(f"💾 Saving enhanced metadata to {output_dir}")
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Parse additional objects
        contact_data = self.parse_contact_object()
        opportunity_data = self.parse_opportunity_object()
        
        all_objects = []
        if contact_data:
            all_objects.append(contact_data)
        if opportunity_data:
            all_objects.append(opportunity_data)
        
        # Save individual object files
        for obj_data in all_objects:
            obj_name = obj_data['name']
            obj_file = output_path / f"{obj_name}.json"
            
            with open(obj_file, 'w') as f:
                json.dump(obj_data, f, indent=2)
            
            logger.info(f"   ✅ Saved {obj_name}.json")
        
        # Analyze and save relationships
        cross_relationships = self.analyze_cross_object_relationships(all_objects)
        
        # Load existing relationships
        existing_rels_file = output_path / "relationships.json"
        existing_relationships = []
        
        if existing_rels_file.exists():
            with open(existing_rels_file, 'r') as f:
                data = json.load(f)
                # Handle both list and dict formats
                if isinstance(data, list):
                    existing_relationships = data
                else:
                    existing_relationships = data.get('relationships', [])
        
        # Combine relationships
        all_relationships = existing_relationships + cross_relationships
        
        # Save enhanced relationships
        enhanced_rels = {
            'metadata': {
                'total_relationships': len(all_relationships),
                'cross_object_relationships': len(cross_relationships),
                'objects_analyzed': [obj['name'] for obj in all_objects]
            },
            'relationships': all_relationships
        }
        
        enhanced_rels_file = output_path / "enhanced_relationships.json"
        with open(enhanced_rels_file, 'w') as f:
            json.dump(enhanced_rels, f, indent=2)
        
        logger.info(f"   ✅ Saved enhanced_relationships.json with {len(all_relationships)} total relationships")
        
        return enhanced_rels

def main():
    """Main function to parse enhanced metadata"""
    logger.info("🚀 Enhanced Salesforce Metadata Parser")
    logger.info("=" * 50)
    
    parser = EnhancedMetadataParser()
    
    # Parse package.xml
    components = parser.parse_package_xml()
    
    # Discover additional metadata
    discovered = parser.discover_additional_metadata()
    
    # Save enhanced metadata
    enhanced_data = parser.save_enhanced_metadata()
    
    # Summary
    logger.info("\n📊 ENHANCED METADATA SUMMARY")
    logger.info("=" * 40)
    logger.info(f"Package Components:")
    for metadata_type, members in components.items():
        logger.info(f"   {metadata_type}: {len(members)} items")
    
    logger.info(f"\nDiscovered Files:")
    for category, items in discovered.items():
        if items:
            logger.info(f"   {category}: {len(items)} items")
    
    logger.info(f"\nEnhanced Relationships: {enhanced_data['metadata']['total_relationships']}")
    logger.info(f"Cross-Object Relationships: {enhanced_data['metadata']['cross_object_relationships']}")
    
    logger.info("\n✅ Enhanced metadata parsing complete!")
    logger.info("🚀 Next: Run enhanced_neo4j_loader.py to load into Neo4j")

if __name__ == "__main__":
    main()
