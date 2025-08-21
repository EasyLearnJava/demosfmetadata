#!/usr/bin/env python3
"""
Salesforce Metadata to JSON Converter for Neo4j
Converts Salesforce XML metadata files to JSON format suitable for Neo4j graph database loading.
"""

import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional
import re
from datetime import datetime

class SalesforceMetadataConverter:
    def __init__(self, source_dir: str = "force-app/main/default", output_dir: str = "converted_metadata"):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.metadata_types = {}
        self.relationships = []
        self.conversion_stats = {
            'objects_processed': 0,
            'fields_processed': 0,
            'layouts_processed': 0,
            'classes_processed': 0,
            'triggers_processed': 0,
            'workflows_processed': 0,
            'errors': []
        }
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
    def remove_namespace(self, tag: str) -> str:
        """Remove XML namespace from tag names"""
        return tag.split('}')[-1] if '}' in tag else tag
    
    def xml_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """Convert XML element to dictionary recursively"""
        result = {}
        
        # Handle element text
        if element.text and element.text.strip():
            if len(element) == 0:  # Leaf node
                return element.text.strip()
            else:
                result['_text'] = element.text.strip()
        
        # Handle attributes
        if element.attrib:
            result['_attributes'] = element.attrib
            
        # Handle child elements
        children = {}
        for child in element:
            child_tag = self.remove_namespace(child.tag)
            child_value = self.xml_to_dict(child)
            
            if child_tag in children:
                # Convert to list if multiple elements with same tag
                if not isinstance(children[child_tag], list):
                    children[child_tag] = [children[child_tag]]
                children[child_tag].append(child_value)
            else:
                children[child_tag] = child_value
                
        result.update(children)
        return result if result else None
    
    def process_custom_object(self, object_path: Path) -> Dict[str, Any]:
        """Process CustomObject metadata"""
        object_name = object_path.name
        object_data = {
            'id': f"object_{object_name}",
            'type': 'CustomObject',
            'name': object_name,
            'metadata': {},
            'fields': [],
            'listViews': [],
            'webLinks': []
        }
        
        # Process main object file
        object_file = object_path / f"{object_name}.object-meta.xml"
        if object_file.exists():
            try:
                tree = ET.parse(object_file)
                root = tree.getroot()
                object_data['metadata'] = self.xml_to_dict(root)
                self.conversion_stats['objects_processed'] += 1
            except Exception as e:
                self.conversion_stats['errors'].append(f"Error processing {object_file}: {str(e)}")
        
        # Process fields
        fields_dir = object_path / "fields"
        if fields_dir.exists():
            for field_file in fields_dir.glob("*.field-meta.xml"):
                field_data = self.process_field(field_file, object_name)
                if field_data:
                    object_data['fields'].append(field_data)
                    # Create relationship
                    self.relationships.append({
                        'from': object_data['id'],
                        'to': field_data['id'],
                        'type': 'HAS_FIELD'
                    })
        
        # Process list views
        listviews_dir = object_path / "listViews"
        if listviews_dir.exists():
            for listview_file in listviews_dir.glob("*.listView-meta.xml"):
                listview_data = self.process_listview(listview_file, object_name)
                if listview_data:
                    object_data['listViews'].append(listview_data)
                    # Create relationship
                    self.relationships.append({
                        'from': object_data['id'],
                        'to': listview_data['id'],
                        'type': 'HAS_LISTVIEW'
                    })
        
        # Process web links
        weblinks_dir = object_path / "webLinks"
        if weblinks_dir.exists():
            for weblink_file in weblinks_dir.glob("*.webLink-meta.xml"):
                weblink_data = self.process_weblink(weblink_file, object_name)
                if weblink_data:
                    object_data['webLinks'].append(weblink_data)
                    # Create relationship
                    self.relationships.append({
                        'from': object_data['id'],
                        'to': weblink_data['id'],
                        'type': 'HAS_WEBLINK'
                    })
        
        return object_data
    
    def process_field(self, field_file: Path, object_name: str) -> Optional[Dict[str, Any]]:
        """Process CustomField metadata"""
        try:
            tree = ET.parse(field_file)
            root = tree.getroot()
            field_name = field_file.stem.replace('.field-meta', '')
            
            field_data = {
                'id': f"field_{object_name}_{field_name}",
                'type': 'CustomField',
                'name': field_name,
                'object': object_name,
                'metadata': self.xml_to_dict(root)
            }
            
            self.conversion_stats['fields_processed'] += 1
            return field_data
            
        except Exception as e:
            self.conversion_stats['errors'].append(f"Error processing field {field_file}: {str(e)}")
            return None
    
    def process_listview(self, listview_file: Path, object_name: str) -> Optional[Dict[str, Any]]:
        """Process ListView metadata"""
        try:
            tree = ET.parse(listview_file)
            root = tree.getroot()
            listview_name = listview_file.stem.replace('.listView-meta', '')
            
            return {
                'id': f"listview_{object_name}_{listview_name}",
                'type': 'ListView',
                'name': listview_name,
                'object': object_name,
                'metadata': self.xml_to_dict(root)
            }
            
        except Exception as e:
            self.conversion_stats['errors'].append(f"Error processing listview {listview_file}: {str(e)}")
            return None
    
    def process_weblink(self, weblink_file: Path, object_name: str) -> Optional[Dict[str, Any]]:
        """Process WebLink metadata"""
        try:
            tree = ET.parse(weblink_file)
            root = tree.getroot()
            weblink_name = weblink_file.stem.replace('.webLink-meta', '')
            
            return {
                'id': f"weblink_{object_name}_{weblink_name}",
                'type': 'WebLink',
                'name': weblink_name,
                'object': object_name,
                'metadata': self.xml_to_dict(root)
            }
            
        except Exception as e:
            self.conversion_stats['errors'].append(f"Error processing weblink {weblink_file}: {str(e)}")
            return None
    
    def process_layout(self, layout_file: Path) -> Optional[Dict[str, Any]]:
        """Process Layout metadata with comprehensive field and section analysis"""
        try:
            tree = ET.parse(layout_file)
            root = tree.getroot()
            layout_name = layout_file.stem.replace('.layout-meta', '')

            # Extract object name from layout name (e.g., "Account-Account Layout" -> "Account")
            object_name = layout_name.split('-')[0]

            layout_data = {
                'id': f"layout_{layout_name.replace(' ', '_').replace('(', '').replace(')', '').replace('%28', '').replace('%29', '')}",
                'type': 'Layout',
                'name': layout_name,
                'object': object_name,
                'metadata': self.xml_to_dict(root),
                'fields_on_layout': [],
                'sections': [],
                'related_lists': []
            }

            # Extract fields from layout
            fields_on_layout = self._extract_layout_fields(root)
            layout_data['fields_on_layout'] = fields_on_layout

            # Extract sections
            sections = self._extract_layout_sections(root)
            layout_data['sections'] = sections

            # Extract related lists
            related_lists = self._extract_related_lists(root)
            layout_data['related_lists'] = related_lists

            # Create comprehensive relationships
            self._create_layout_relationships(layout_data['id'], object_name, fields_on_layout, related_lists)

            self.conversion_stats['layouts_processed'] += 1
            return layout_data

        except Exception as e:
            self.conversion_stats['errors'].append(f"Error processing layout {layout_file}: {str(e)}")
            return None

    def process_apex_class(self, class_file: Path) -> Optional[Dict[str, Any]]:
        """Process Apex Class metadata and source code with comprehensive relationship extraction"""
        try:
            class_name = class_file.stem
            class_data = {
                'id': f"class_{class_name}",
                'type': 'ApexClass',
                'name': class_name,
                'source_code': '',
                'metadata': {},
                'comprehensive_dependencies': {}
            }

            # Read source code
            if class_file.exists():
                with open(class_file, 'r', encoding='utf-8') as f:
                    class_data['source_code'] = f.read()

            # Read metadata
            meta_file = class_file.with_suffix('.cls-meta.xml')
            if meta_file.exists():
                tree = ET.parse(meta_file)
                root = tree.getroot()
                class_data['metadata'] = self.xml_to_dict(root)

            # Extract comprehensive dependencies
            dependencies = self.extract_comprehensive_dependencies(
                class_data['source_code'], class_name, 'ApexClass'
            )
            class_data['comprehensive_dependencies'] = dependencies

            # Create detailed relationships
            self._create_class_relationships(class_data['id'], dependencies)

            self.conversion_stats['classes_processed'] += 1
            return class_data

        except Exception as e:
            self.conversion_stats['errors'].append(f"Error processing class {class_file}: {str(e)}")
            return None

    def process_trigger(self, trigger_file: Path) -> Optional[Dict[str, Any]]:
        """Process Apex Trigger metadata and source code with comprehensive analysis"""
        try:
            trigger_name = trigger_file.stem
            trigger_data = {
                'id': f"trigger_{trigger_name}",
                'type': 'ApexTrigger',
                'name': trigger_name,
                'source_code': '',
                'metadata': {},
                'trigger_events': [],
                'comprehensive_dependencies': {}
            }

            # Read source code
            if trigger_file.exists():
                with open(trigger_file, 'r', encoding='utf-8') as f:
                    trigger_data['source_code'] = f.read()

            # Read metadata
            meta_file = trigger_file.with_suffix('.trigger-meta.xml')
            if meta_file.exists():
                tree = ET.parse(meta_file)
                root = tree.getroot()
                trigger_data['metadata'] = self.xml_to_dict(root)

            # Extract trigger details
            trigger_object = self.extract_trigger_object(trigger_data['source_code'])
            trigger_events = self.extract_trigger_events(trigger_data['source_code'])

            if trigger_object:
                trigger_data['object'] = trigger_object
                trigger_data['trigger_events'] = trigger_events

                # Create comprehensive relationships
                self.relationships.append({
                    'from': f"object_{trigger_object}",
                    'to': trigger_data['id'],
                    'type': 'HAS_TRIGGER',
                    'details': f"Trigger events: {', '.join(trigger_events)}"
                })

            # Extract comprehensive dependencies
            dependencies = self.extract_comprehensive_dependencies(
                trigger_data['source_code'], trigger_name, 'ApexTrigger'
            )
            trigger_data['comprehensive_dependencies'] = dependencies

            # Create detailed relationships for trigger
            self._create_trigger_relationships(trigger_data['id'], dependencies, trigger_object)

            self.conversion_stats['triggers_processed'] += 1
            return trigger_data

        except Exception as e:
            self.conversion_stats['errors'].append(f"Error processing trigger {trigger_file}: {str(e)}")
            return None

    def process_workflow(self, workflow_file: Path) -> Optional[Dict[str, Any]]:
        """Process Workflow metadata"""
        try:
            tree = ET.parse(workflow_file)
            root = tree.getroot()
            workflow_name = workflow_file.stem.replace('.workflow-meta', '')

            workflow_data = {
                'id': f"workflow_{workflow_name}",
                'type': 'Workflow',
                'name': workflow_name,
                'object': workflow_name,  # Workflow files are named after the object
                'metadata': self.xml_to_dict(root)
            }

            # Create relationship to object
            self.relationships.append({
                'from': f"object_{workflow_name}",
                'to': workflow_data['id'],
                'type': 'HAS_WORKFLOW'
            })

            self.conversion_stats['workflows_processed'] += 1
            return workflow_data

        except Exception as e:
            self.conversion_stats['errors'].append(f"Error processing workflow {workflow_file}: {str(e)}")
            return None

    def extract_comprehensive_dependencies(self, source_code: str, component_name: str, component_type: str) -> Dict[str, List[str]]:
        """Extract ALL possible dependencies and relationships from source code"""
        dependencies = {
            'objects': [],
            'classes': [],
            'fields': [],
            'methods': [],
            'custom_settings': [],
            'web_services': [],
            'email_templates': [],
            'custom_labels': [],
            'static_resources': [],
            'triggers': [],
            'workflows': []
        }

        # 1. SOQL/SOSL Queries - Extract objects and fields
        soql_patterns = [
            r'\[SELECT\s+(.*?)\s+FROM\s+([A-Z][a-zA-Z0-9_]*(?:__c)?)\b',
            r'Database\.query\s*\(\s*[\'"]SELECT\s+(.*?)\s+FROM\s+([A-Z][a-zA-Z0-9_]*(?:__c)?)\b',
            r'Database\.getQueryLocator\s*\(\s*[\'"]SELECT\s+(.*?)\s+FROM\s+([A-Z][a-zA-Z0-9_]*(?:__c)?)\b',
            r'\bFROM\s+([A-Z][a-zA-Z0-9_]*(?:__c)?)\b'
        ]

        for pattern in soql_patterns:
            matches = re.findall(pattern, source_code, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if isinstance(match, tuple) and len(match) == 2:
                    fields_str, object_name = match
                    dependencies['objects'].append(object_name)
                    # Extract individual fields from SELECT clause
                    field_matches = re.findall(r'\b([A-Z][a-zA-Z0-9_]*(?:__c)?)\b', fields_str)
                    dependencies['fields'].extend([f"{object_name}.{field}" for field in field_matches])
                elif isinstance(match, str):
                    dependencies['objects'].append(match)

        # 2. DML Operations and Object References
        dml_patterns = [
            r'\b(?:insert|update|delete|upsert)\s+([A-Z][a-zA-Z0-9_]*(?:__c)?)\b',
            r'\bnew\s+([A-Z][a-zA-Z0-9_]*(?:__c)?)\s*\(',
            r'List<([A-Z][a-zA-Z0-9_]*(?:__c)?)>',
            r'Map<[^,]+,\s*([A-Z][a-zA-Z0-9_]*(?:__c)?)>',
            r'Set<([A-Z][a-zA-Z0-9_]*(?:__c)?)>',
            r'Schema\.([A-Z][a-zA-Z0-9_]*(?:__c)?)',
            r'Schema\.getGlobalDescribe\(\)\.get\([\'"]([A-Z][a-zA-Z0-9_]*(?:__c)?)[\'"]'
        ]

        for pattern in dml_patterns:
            matches = re.findall(pattern, source_code, re.IGNORECASE)
            dependencies['objects'].extend(matches)

        # 3. Field References
        field_patterns = [
            r'\.([A-Z][a-zA-Z0-9_]*(?:__c)?)(?:\s*=|\s*!=|\s*>|\s*<)',  # Field assignments/comparisons
            r'\.get\([\'"]([A-Z][a-zA-Z0-9_]*(?:__c)?)[\'"]',  # Dynamic field access
            r'\.put\([\'"]([A-Z][a-zA-Z0-9_]*(?:__c)?)[\'"]',  # Dynamic field setting
        ]

        for pattern in field_patterns:
            matches = re.findall(pattern, source_code)
            dependencies['fields'].extend(matches)

        # 4. Class Dependencies and Method Calls
        class_patterns = [
            r'\b([A-Z][a-zA-Z0-9_]+)\.([a-zA-Z][a-zA-Z0-9_]*)\s*\(',  # Static method calls
            r'\bnew\s+([A-Z][a-zA-Z0-9_]+)\s*\(',  # Class instantiation
            r'extends\s+([A-Z][a-zA-Z0-9_]+)\b',  # Inheritance
            r'implements\s+([A-Z][a-zA-Z0-9_]+)\b',  # Interface implementation
            r'@([A-Z][a-zA-Z0-9_]+)',  # Annotations
            r'catch\s*\(\s*([A-Z][a-zA-Z0-9_]+Exception)',  # Exception handling
        ]

        system_classes = {'System', 'Database', 'String', 'Integer', 'Boolean', 'Decimal', 'Date', 'DateTime',
                         'Time', 'Messaging', 'Http', 'HttpRequest', 'HttpResponse', 'JSON', 'Math', 'Test',
                         'Schema', 'UserInfo', 'Limits', 'ApexPages', 'PageReference', 'Blob', 'Crypto',
                         'Pattern', 'Matcher', 'Exception', 'DmlException', 'QueryException'}

        for pattern in class_patterns:
            matches = re.findall(pattern, source_code)
            for match in matches:
                if isinstance(match, tuple):
                    class_name, method_name = match
                    if class_name not in system_classes:
                        dependencies['classes'].append(class_name)
                        dependencies['methods'].append(f"{class_name}.{method_name}")
                else:
                    if match not in system_classes:
                        dependencies['classes'].append(match)

        # 5. Custom Settings and Custom Metadata
        custom_settings_patterns = [
            r'([A-Z][a-zA-Z0-9_]*__c)\.getInstance\(\)',
            r'([A-Z][a-zA-Z0-9_]*__c)\.getValues\(\)',
            r'([A-Z][a-zA-Z0-9_]*__c)\.getAll\(\)',
            r'([A-Z][a-zA-Z0-9_]*__mdt)\b'  # Custom metadata types
        ]

        for pattern in custom_settings_patterns:
            matches = re.findall(pattern, source_code)
            dependencies['custom_settings'].extend(matches)

        # 6. Web Service and HTTP Callouts
        webservice_patterns = [
            r'\.setEndpoint\s*\(\s*[\'"]([^\'"]+)[\'"]',
            r'@RestResource\s*\(\s*urlMapping\s*=\s*[\'"]([^\'"]+)[\'"]',
            r'@HttpGet|@HttpPost|@HttpPut|@HttpDelete|@HttpPatch',
            r'Webservice\s+static',
            r'Http\s+\w+\s*=\s*new\s+Http\(\)',
        ]

        for pattern in webservice_patterns:
            matches = re.findall(pattern, source_code)
            dependencies['web_services'].extend(matches)

        # 7. Email Templates and Messaging
        email_patterns = [
            r'\.setTemplateId\s*\(\s*[\'"]([^\'"]+)[\'"]',
            r'EmailTemplate\s+\w+',
            r'Messaging\.SingleEmailMessage',
            r'Messaging\.MassEmailMessage',
            r'Messaging\.sendEmail'
        ]

        for pattern in email_patterns:
            matches = re.findall(pattern, source_code)
            dependencies['email_templates'].extend(matches)

        # 8. Custom Labels
        label_patterns = [
            r'Label\.([A-Z][a-zA-Z0-9_]*)',
            r'\$Label\.([A-Z][a-zA-Z0-9_]*)'
        ]

        for pattern in label_patterns:
            matches = re.findall(pattern, source_code)
            dependencies['custom_labels'].extend(matches)

        # 9. Static Resources
        static_resource_patterns = [
            r'\$Resource\.([A-Z][a-zA-Z0-9_]*)',
            r'StaticResource\.([A-Z][a-zA-Z0-9_]*)'
        ]

        for pattern in static_resource_patterns:
            matches = re.findall(pattern, source_code)
            dependencies['static_resources'].extend(matches)

        # Remove duplicates and clean up
        for key in dependencies:
            dependencies[key] = list(set([dep for dep in dependencies[key] if dep and len(dep) > 1]))

        return dependencies

    def _create_class_relationships(self, class_id: str, dependencies: Dict[str, List[str]]) -> None:
        """Create comprehensive relationships for Apex classes"""

        # Object dependencies
        for obj in dependencies['objects']:
            self.relationships.append({
                'from': class_id,
                'to': f"object_{obj}",
                'type': 'USES_OBJECT',
                'details': 'References object in SOQL/DML operations'
            })

        # Class dependencies
        for cls in dependencies['classes']:
            self.relationships.append({
                'from': class_id,
                'to': f"class_{cls}",
                'type': 'DEPENDS_ON_CLASS',
                'details': 'Calls methods or instantiates class'
            })

        # Field dependencies
        for field in dependencies['fields']:
            if '.' in field:
                obj_name, field_name = field.split('.', 1)
                self.relationships.append({
                    'from': class_id,
                    'to': f"field_{obj_name}_{field_name}",
                    'type': 'ACCESSES_FIELD',
                    'details': f'Accesses field {field_name} on {obj_name}'
                })

        # Method call relationships
        for method in dependencies['methods']:
            if '.' in method:
                cls_name, method_name = method.split('.', 1)
                self.relationships.append({
                    'from': class_id,
                    'to': f"class_{cls_name}",
                    'type': 'CALLS_METHOD',
                    'details': f'Calls method {method_name}'
                })

        # Custom settings dependencies
        for setting in dependencies['custom_settings']:
            self.relationships.append({
                'from': class_id,
                'to': f"object_{setting}",
                'type': 'USES_CUSTOM_SETTING',
                'details': 'Accesses custom setting or metadata'
            })

        # Web service relationships
        for service in dependencies['web_services']:
            if service.startswith('http'):
                self.relationships.append({
                    'from': class_id,
                    'to': f"webservice_{service.replace('/', '_').replace(':', '_')}",
                    'type': 'CALLS_WEBSERVICE',
                    'details': f'Makes HTTP callout to {service}'
                })

        # Email template relationships
        for template in dependencies['email_templates']:
            self.relationships.append({
                'from': class_id,
                'to': f"emailtemplate_{template}",
                'type': 'USES_EMAIL_TEMPLATE',
                'details': 'Uses email template for messaging'
            })

        # Custom label relationships
        for label in dependencies['custom_labels']:
            self.relationships.append({
                'from': class_id,
                'to': f"customlabel_{label}",
                'type': 'USES_CUSTOM_LABEL',
                'details': 'References custom label'
            })

        # Static resource relationships
        for resource in dependencies['static_resources']:
            self.relationships.append({
                'from': class_id,
                'to': f"staticresource_{resource}",
                'type': 'USES_STATIC_RESOURCE',
                'details': 'References static resource'
            })

    def _create_trigger_relationships(self, trigger_id: str, dependencies: Dict[str, List[str]], trigger_object: str) -> None:
        """Create comprehensive relationships for Apex triggers"""

        # Handler class relationships (common pattern)
        for cls in dependencies['classes']:
            if 'Handler' in cls or 'Helper' in cls:
                self.relationships.append({
                    'from': trigger_id,
                    'to': f"class_{cls}",
                    'type': 'DELEGATES_TO_HANDLER',
                    'details': f'Trigger delegates business logic to handler class'
                })
            else:
                self.relationships.append({
                    'from': trigger_id,
                    'to': f"class_{cls}",
                    'type': 'CALLS_CLASS',
                    'details': 'Trigger calls methods in this class'
                })

        # Object relationships (beyond the primary trigger object)
        for obj in dependencies['objects']:
            if obj != trigger_object:  # Don't duplicate the main trigger relationship
                self.relationships.append({
                    'from': trigger_id,
                    'to': f"object_{obj}",
                    'type': 'AFFECTS_OBJECT',
                    'details': f'Trigger performs operations on {obj}'
                })

        # Field access relationships
        for field in dependencies['fields']:
            if '.' in field:
                obj_name, field_name = field.split('.', 1)
                self.relationships.append({
                    'from': trigger_id,
                    'to': f"field_{obj_name}_{field_name}",
                    'type': 'MODIFIES_FIELD',
                    'details': f'Trigger modifies or reads field {field_name}'
                })

    def extract_trigger_object(self, source_code: str) -> Optional[str]:
        """Extract the object name from trigger definition"""
        pattern = r'trigger\s+\w+\s+on\s+(\w+)\s*\('
        match = re.search(pattern, source_code, re.IGNORECASE)
        return match.group(1) if match else None

    def extract_trigger_events(self, source_code: str) -> List[str]:
        """Extract trigger events (before insert, after update, etc.)"""
        pattern = r'trigger\s+\w+\s+on\s+\w+\s*\(\s*([^)]+)\s*\)'
        match = re.search(pattern, source_code, re.IGNORECASE)
        if match:
            events_str = match.group(1)
            # Split by comma and clean up
            events = [event.strip() for event in events_str.split(',')]
            return events
        return []

    def _extract_layout_fields(self, layout_root: ET.Element) -> List[str]:
        """Extract all fields referenced in a layout"""
        fields = []

        # Look for layoutItems that contain field references
        for item in layout_root.iter():
            tag_name = self.remove_namespace(item.tag)
            if tag_name == 'field' and item.text:
                fields.append(item.text.strip())

        return list(set(fields))

    def _extract_layout_sections(self, layout_root: ET.Element) -> List[Dict[str, Any]]:
        """Extract layout sections and their properties"""
        sections = []

        for section in layout_root.iter():
            tag_name = self.remove_namespace(section.tag)
            if tag_name == 'layoutSection':
                section_data = {
                    'label': '',
                    'columns': 1,
                    'fields': []
                }

                for child in section:
                    child_tag = self.remove_namespace(child.tag)
                    if child_tag == 'label' and child.text:
                        section_data['label'] = child.text.strip()
                    elif child_tag == 'layoutColumns':
                        for field_item in child.iter():
                            field_tag = self.remove_namespace(field_item.tag)
                            if field_tag == 'field' and field_item.text:
                                section_data['fields'].append(field_item.text.strip())

                if section_data['label'] or section_data['fields']:
                    sections.append(section_data)

        return sections

    def _extract_related_lists(self, layout_root: ET.Element) -> List[Dict[str, Any]]:
        """Extract related lists from layout"""
        related_lists = []

        for related_list in layout_root.iter():
            tag_name = self.remove_namespace(related_list.tag)
            if tag_name == 'relatedList':
                list_data = {
                    'object': '',
                    'fields': [],
                    'label': ''
                }

                for child in related_list:
                    child_tag = self.remove_namespace(child.tag)
                    if child_tag == 'relatedList' and child.text:
                        list_data['object'] = child.text.strip()
                    elif child_tag == 'fields':
                        for field in child.iter():
                            if field.text:
                                list_data['fields'].append(field.text.strip())

                if list_data['object']:
                    related_lists.append(list_data)

        return related_lists

    def _create_layout_relationships(self, layout_id: str, object_name: str, fields: List[str], related_lists: List[Dict[str, Any]]) -> None:
        """Create comprehensive relationships for layouts"""

        # Layout to object relationship
        self.relationships.append({
            'from': f"object_{object_name}",
            'to': layout_id,
            'type': 'HAS_LAYOUT',
            'details': f'Layout displays {len(fields)} fields'
        })

        # Layout to field relationships
        for field in fields:
            self.relationships.append({
                'from': layout_id,
                'to': f"field_{object_name}_{field}",
                'type': 'DISPLAYS_FIELD',
                'details': f'Field {field} is displayed on layout'
            })

        # Related list relationships
        for related_list in related_lists:
            if related_list['object']:
                self.relationships.append({
                    'from': layout_id,
                    'to': f"object_{related_list['object']}",
                    'type': 'SHOWS_RELATED_LIST',
                    'details': f'Layout shows related {related_list["object"]} records'
                })

                # Related list field relationships
                for field in related_list['fields']:
                    self.relationships.append({
                        'from': layout_id,
                        'to': f"field_{related_list['object']}_{field}",
                        'type': 'DISPLAYS_RELATED_FIELD',
                        'details': f'Related list displays field {field}'
                    })

    def convert_all_metadata(self) -> Dict[str, Any]:
        """Convert all metadata to JSON format"""
        print("Starting Salesforce metadata conversion...")

        all_metadata = {
            'objects': [],
            'layouts': [],
            'classes': [],
            'triggers': [],
            'workflows': [],
            'relationships': [],
            'conversion_info': {
                'timestamp': datetime.now().isoformat(),
                'source_directory': str(self.source_dir),
                'output_directory': str(self.output_dir)
            }
        }

        # Process Custom Objects
        objects_dir = self.source_dir / "objects"
        if objects_dir.exists():
            print(f"Processing objects from {objects_dir}")
            for object_dir in objects_dir.iterdir():
                if object_dir.is_dir():
                    print(f"  Processing object: {object_dir.name}")
                    object_data = self.process_custom_object(object_dir)
                    if object_data:
                        all_metadata['objects'].append(object_data)

        # Process Layouts
        layouts_dir = self.source_dir / "layouts"
        if layouts_dir.exists():
            print(f"Processing layouts from {layouts_dir}")
            for layout_file in layouts_dir.glob("*.layout-meta.xml"):
                print(f"  Processing layout: {layout_file.name}")
                layout_data = self.process_layout(layout_file)
                if layout_data:
                    all_metadata['layouts'].append(layout_data)

        # Process Apex Classes
        classes_dir = self.source_dir / "classes"
        if classes_dir.exists():
            print(f"Processing classes from {classes_dir}")
            for class_file in classes_dir.glob("*.cls"):
                print(f"  Processing class: {class_file.name}")
                class_data = self.process_apex_class(class_file)
                if class_data:
                    all_metadata['classes'].append(class_data)

        # Process Triggers
        triggers_dir = self.source_dir / "triggers"
        if triggers_dir.exists():
            print(f"Processing triggers from {triggers_dir}")
            for trigger_file in triggers_dir.glob("*.trigger"):
                print(f"  Processing trigger: {trigger_file.name}")
                trigger_data = self.process_trigger(trigger_file)
                if trigger_data:
                    all_metadata['triggers'].append(trigger_data)

        # Process Workflows
        workflows_dir = self.source_dir / "workflows"
        if workflows_dir.exists():
            print(f"Processing workflows from {workflows_dir}")
            for workflow_file in workflows_dir.glob("*.workflow-meta.xml"):
                print(f"  Processing workflow: {workflow_file.name}")
                workflow_data = self.process_workflow(workflow_file)
                if workflow_data:
                    all_metadata['workflows'].append(workflow_data)

        # Add relationships
        all_metadata['relationships'] = self.relationships

        return all_metadata

    def save_json_files(self, metadata: Dict[str, Any]) -> None:
        """Save converted metadata to separate JSON files"""
        print(f"\nSaving JSON files to {self.output_dir}")

        # Save individual metadata types
        for metadata_type in ['objects', 'layouts', 'classes', 'triggers', 'workflows']:
            if metadata[metadata_type]:
                output_file = self.output_dir / f"{metadata_type}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata[metadata_type], f, indent=2, ensure_ascii=False)
                print(f"  Saved {len(metadata[metadata_type])} {metadata_type} to {output_file}")

        # Save relationships
        if metadata['relationships']:
            relationships_file = self.output_dir / "relationships.json"
            with open(relationships_file, 'w', encoding='utf-8') as f:
                json.dump(metadata['relationships'], f, indent=2, ensure_ascii=False)
            print(f"  Saved {len(metadata['relationships'])} relationships to {relationships_file}")

        # Save complete metadata
        complete_file = self.output_dir / "complete_metadata.json"
        with open(complete_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print(f"  Saved complete metadata to {complete_file}")

        # Save conversion statistics
        stats_file = self.output_dir / "conversion_stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.conversion_stats, f, indent=2, ensure_ascii=False)
        print(f"  Saved conversion statistics to {stats_file}")

    def print_summary(self) -> None:
        """Print conversion summary"""
        print("\n" + "="*60)
        print("CONVERSION SUMMARY")
        print("="*60)
        print(f"Objects processed: {self.conversion_stats['objects_processed']}")
        print(f"Fields processed: {self.conversion_stats['fields_processed']}")
        print(f"Layouts processed: {self.conversion_stats['layouts_processed']}")
        print(f"Classes processed: {self.conversion_stats['classes_processed']}")
        print(f"Triggers processed: {self.conversion_stats['triggers_processed']}")
        print(f"Workflows processed: {self.conversion_stats['workflows_processed']}")
        print(f"Relationships created: {len(self.relationships)}")

        if self.conversion_stats['errors']:
            print(f"\nErrors encountered: {len(self.conversion_stats['errors'])}")
            for error in self.conversion_stats['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(self.conversion_stats['errors']) > 5:
                print(f"  ... and {len(self.conversion_stats['errors']) - 5} more errors")
        else:
            print("\nNo errors encountered!")

        print("="*60)


def main():
    """Main execution function"""
    print("Salesforce Metadata to JSON Converter for Neo4j")
    print("=" * 50)

    # Initialize converter
    converter = SalesforceMetadataConverter()

    # Check if source directory exists
    if not converter.source_dir.exists():
        print(f"Error: Source directory {converter.source_dir} does not exist!")
        return

    try:
        # Convert all metadata
        metadata = converter.convert_all_metadata()

        # Save JSON files
        converter.save_json_files(metadata)

        # Print summary
        converter.print_summary()

        print(f"\nConversion completed successfully!")
        print(f"Output files saved to: {converter.output_dir}")
        print("\nNext steps:")
        print("1. Review the generated JSON files")
        print("2. Check conversion_stats.json for any errors")
        print("3. Use the JSON files to load data into Neo4j")
        print("4. The relationships.json file contains all the graph relationships")

    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
