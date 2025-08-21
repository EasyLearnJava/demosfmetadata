#!/usr/bin/env python3
"""
Comprehensive Salesforce Metadata Parser
Parse all metadata including individual field files for Contact and Opportunity
"""

import xml.etree.ElementTree as ET
import os
import json
from pathlib import Path
from typing import Dict, List, Set
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveMetadataParser:
    def __init__(self, metadata_dir: str = "."):
        self.metadata_dir = Path(metadata_dir)
        self.objects_data = {}
        self.relationships = []
        
    def parse_object_with_fields(self, object_name: str) -> Dict:
        """Parse an object and all its individual field files"""
        logger.info(f"📋 Parsing {object_name} object with individual fields...")
        
        object_dir = self.metadata_dir / "force-app" / "main" / "default" / "objects" / object_name
        
        if not object_dir.exists():
            logger.warning(f"❌ {object_name} directory not found")
            return {}
        
        object_data = {
            'name': object_name,
            'type': 'CustomObject',
            'fields': [],
            'listViews': [],
            'webLinks': []
        }
        
        # Parse individual field files
        fields_dir = object_dir / "fields"
        if fields_dir.exists():
            for field_file in fields_dir.glob("*.field-meta.xml"):
                field_data = self.parse_field_file(field_file)
                if field_data:
                    object_data['fields'].append(field_data)
        
        # Parse list views
        listviews_dir = object_dir / "listViews"
        if listviews_dir.exists():
            for listview_file in listviews_dir.glob("*.listView-meta.xml"):
                listview_data = self.parse_listview_file(listview_file)
                if listview_data:
                    object_data['listViews'].append(listview_data)
        
        # Parse web links
        weblinks_dir = object_dir / "webLinks"
        if weblinks_dir.exists():
            for weblink_file in weblinks_dir.glob("*.webLink-meta.xml"):
                weblink_data = self.parse_weblink_file(weblink_file)
                if weblink_data:
                    object_data['webLinks'].append(weblink_data)
        
        logger.info(f"   ✅ {object_name}: {len(object_data['fields'])} fields, {len(object_data['listViews'])} list views, {len(object_data['webLinks'])} web links")
        return object_data
    
    def parse_field_file(self, field_file: Path) -> Dict:
        """Parse individual field file"""
        try:
            tree = ET.parse(field_file)
            root = tree.getroot()
            
            # Extract field name from filename
            field_name = field_file.stem.replace('.field-meta', '')
            
            field_data = {
                'name': field_name,
                'type': 'Unknown',
                'label': field_name
            }
            
            # Parse field properties
            for child in root:
                tag_name = child.tag.replace('{http://soap.sforce.com/2006/04/metadata}', '')
                
                if tag_name == 'type':
                    field_data['type'] = child.text
                elif tag_name == 'label':
                    field_data['label'] = child.text
                elif tag_name == 'description':
                    field_data['description'] = child.text
                elif tag_name == 'required':
                    field_data['required'] = child.text == 'true'
                elif tag_name == 'unique':
                    field_data['unique'] = child.text == 'true'
                elif tag_name == 'length':
                    field_data['length'] = child.text
                elif tag_name == 'precision':
                    field_data['precision'] = child.text
                elif tag_name == 'scale':
                    field_data['scale'] = child.text
                elif tag_name == 'referenceTo':
                    field_data['referenceTo'] = child.text
                elif tag_name == 'relationshipName':
                    field_data['relationshipName'] = child.text
            
            return field_data
            
        except Exception as e:
            logger.warning(f"⚠️ Error parsing field file {field_file}: {e}")
            return {}
    
    def parse_listview_file(self, listview_file: Path) -> Dict:
        """Parse individual list view file"""
        try:
            tree = ET.parse(listview_file)
            root = tree.getroot()
            
            listview_name = listview_file.stem.replace('.listView-meta', '')
            
            listview_data = {
                'name': listview_name,
                'type': 'ListView'
            }
            
            # Parse list view properties
            for child in root:
                tag_name = child.tag.replace('{http://soap.sforce.com/2006/04/metadata}', '')
                
                if tag_name == 'label':
                    listview_data['label'] = child.text
                elif tag_name == 'filterScope':
                    listview_data['filterScope'] = child.text
                elif tag_name == 'columns':
                    if 'columns' not in listview_data:
                        listview_data['columns'] = []
                    listview_data['columns'].append(child.text)
            
            return listview_data
            
        except Exception as e:
            logger.warning(f"⚠️ Error parsing listview file {listview_file}: {e}")
            return {}
    
    def parse_weblink_file(self, weblink_file: Path) -> Dict:
        """Parse individual web link file"""
        try:
            tree = ET.parse(weblink_file)
            root = tree.getroot()
            
            weblink_name = weblink_file.stem.replace('.webLink-meta', '')
            
            weblink_data = {
                'name': weblink_name,
                'type': 'WebLink'
            }
            
            # Parse web link properties
            for child in root:
                tag_name = child.tag.replace('{http://soap.sforce.com/2006/04/metadata}', '')
                
                if tag_name == 'displayType':
                    weblink_data['displayType'] = child.text
                elif tag_name == 'url':
                    weblink_data['url'] = child.text
                elif tag_name == 'linkType':
                    weblink_data['linkType'] = child.text
            
            return weblink_data
            
        except Exception as e:
            logger.warning(f"⚠️ Error parsing weblink file {weblink_file}: {e}")
            return {}
    
    def analyze_comprehensive_relationships(self) -> List[Dict]:
        """Analyze comprehensive relationships including field-level relationships"""
        logger.info("🔗 Analyzing comprehensive relationships...")
        
        relationships = []
        
        # Standard Salesforce object relationships
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
        
        # Analyze field-level relationships
        for obj_name, obj_data in self.objects_data.items():
            # Object to field relationships
            for field in obj_data.get('fields', []):
                field_name = field.get('name', '')
                
                relationships.append({
                    'from': obj_name,
                    'to': field_name,
                    'type': 'HAS_FIELD',
                    'context': f'{obj_name} object has field {field_name}'
                })
                
                # Lookup/Reference relationships
                reference_to = field.get('referenceTo')
                if reference_to:
                    relationships.append({
                        'from': obj_name,
                        'to': reference_to,
                        'type': 'REFERENCES',
                        'context': f'{obj_name}.{field_name} references {reference_to}'
                    })
                
                # Special field relationships
                if field_name.endswith('Id') and field_name != 'Id':
                    target_object = field_name.replace('Id', '')
                    if target_object in ['Account', 'Contact', 'Opportunity']:
                        relationships.append({
                            'from': obj_name,
                            'to': target_object,
                            'type': 'LOOKUP_TO',
                            'context': f'{obj_name}.{field_name} lookup to {target_object}'
                        })
            
            # Object to list view relationships
            for listview in obj_data.get('listViews', []):
                listview_name = listview.get('name', '')
                
                relationships.append({
                    'from': obj_name,
                    'to': listview_name,
                    'type': 'HAS_LISTVIEW',
                    'context': f'{obj_name} object has list view {listview_name}'
                })
            
            # Object to web link relationships
            for weblink in obj_data.get('webLinks', []):
                weblink_name = weblink.get('name', '')
                
                relationships.append({
                    'from': obj_name,
                    'to': weblink_name,
                    'type': 'HAS_WEBLINK',
                    'context': f'{obj_name} object has web link {weblink_name}'
                })
        
        logger.info(f"   ✅ Found {len(relationships)} comprehensive relationships")
        return relationships
    
    def save_comprehensive_metadata(self, output_dir: str = "converted_metadata"):
        """Save comprehensive metadata to JSON files"""
        logger.info(f"💾 Saving comprehensive metadata to {output_dir}")
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Parse Contact and Opportunity with all their fields
        contact_data = self.parse_object_with_fields('Contact')
        opportunity_data = self.parse_object_with_fields('Opportunity')
        
        # Store in objects_data for relationship analysis
        if contact_data:
            self.objects_data['Contact'] = contact_data
        if opportunity_data:
            self.objects_data['Opportunity'] = opportunity_data
        
        # Save individual object files
        for obj_name, obj_data in self.objects_data.items():
            obj_file = output_path / f"{obj_name}_comprehensive.json"
            
            with open(obj_file, 'w') as f:
                json.dump(obj_data, f, indent=2)
            
            logger.info(f"   ✅ Saved {obj_name}_comprehensive.json")
        
        # Analyze and save comprehensive relationships
        comprehensive_relationships = self.analyze_comprehensive_relationships()
        
        # Load existing relationships
        existing_rels_file = output_path / "relationships.json"
        existing_relationships = []
        
        if existing_rels_file.exists():
            with open(existing_rels_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    existing_relationships = data
                else:
                    existing_relationships = data.get('relationships', [])
        
        # Combine relationships
        all_relationships = existing_relationships + comprehensive_relationships
        
        # Save comprehensive relationships
        comprehensive_rels = {
            'metadata': {
                'total_relationships': len(all_relationships),
                'comprehensive_relationships': len(comprehensive_relationships),
                'objects_analyzed': list(self.objects_data.keys()),
                'contact_fields': len(contact_data.get('fields', [])) if contact_data else 0,
                'opportunity_fields': len(opportunity_data.get('fields', [])) if opportunity_data else 0
            },
            'relationships': all_relationships
        }
        
        comprehensive_rels_file = output_path / "comprehensive_relationships.json"
        with open(comprehensive_rels_file, 'w') as f:
            json.dump(comprehensive_rels, f, indent=2)
        
        logger.info(f"   ✅ Saved comprehensive_relationships.json with {len(all_relationships)} total relationships")
        
        return comprehensive_rels

def main():
    """Main function to parse comprehensive metadata"""
    logger.info("🚀 Comprehensive Salesforce Metadata Parser")
    logger.info("=" * 60)
    
    parser = ComprehensiveMetadataParser()
    
    # Save comprehensive metadata
    comprehensive_data = parser.save_comprehensive_metadata()
    
    # Summary
    logger.info("\n📊 COMPREHENSIVE METADATA SUMMARY")
    logger.info("=" * 50)
    
    metadata = comprehensive_data['metadata']
    logger.info(f"Objects Analyzed: {metadata['objects_analyzed']}")
    logger.info(f"Contact Fields: {metadata['contact_fields']}")
    logger.info(f"Opportunity Fields: {metadata['opportunity_fields']}")
    logger.info(f"Total Relationships: {metadata['total_relationships']}")
    logger.info(f"New Comprehensive Relationships: {metadata['comprehensive_relationships']}")
    
    logger.info("\n✅ Comprehensive metadata parsing complete!")
    logger.info("🚀 Next: Run enhanced_neo4j_loader.py to load into Neo4j")

if __name__ == "__main__":
    main()
