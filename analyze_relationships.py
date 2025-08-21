#!/usr/bin/env python3
"""
Salesforce Metadata Relationship Analyzer
Analyzes the comprehensive relationships extracted from Salesforce metadata.
"""

import json
from collections import Counter, defaultdict
from pathlib import Path
import pandas as pd

class MetadataRelationshipAnalyzer:
    def __init__(self, metadata_dir: str = "converted_metadata"):
        self.metadata_dir = Path(metadata_dir)
        self.relationships = []
        self.objects = []
        self.classes = []
        self.layouts = []
        self.triggers = []
        
        self.load_data()
    
    def load_data(self):
        """Load all metadata and relationships"""
        # Load relationships
        relationships_file = self.metadata_dir / "relationships.json"
        if relationships_file.exists():
            with open(relationships_file, 'r', encoding='utf-8') as f:
                self.relationships = json.load(f)
        
        # Load other metadata
        for metadata_type in ['objects', 'classes', 'layouts', 'triggers']:
            file_path = self.metadata_dir / f"{metadata_type}.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    setattr(self, metadata_type, json.load(f))
    
    def analyze_relationship_types(self):
        """Analyze distribution of relationship types"""
        print("🔗 RELATIONSHIP TYPE ANALYSIS")
        print("=" * 50)
        
        rel_types = Counter(rel['type'] for rel in self.relationships)
        
        for rel_type, count in rel_types.most_common():
            print(f"{rel_type:25} : {count:3d} relationships")
        
        print(f"\nTotal Relationships: {len(self.relationships)}")
        print(f"Unique Relationship Types: {len(rel_types)}")
        return rel_types
    
    def analyze_component_connectivity(self):
        """Analyze which components are most connected"""
        print("\n📊 COMPONENT CONNECTIVITY ANALYSIS")
        print("=" * 50)
        
        # Count incoming and outgoing relationships
        incoming = Counter()
        outgoing = Counter()
        
        for rel in self.relationships:
            outgoing[rel['from']] += 1
            incoming[rel['to']] += 1
        
        print("\nMost Connected Components (Outgoing):")
        for component, count in outgoing.most_common(10):
            component_type = component.split('_')[0]
            component_name = '_'.join(component.split('_')[1:])
            print(f"  {component_type:12} {component_name:30} → {count:3d} connections")
        
        print("\nMost Referenced Components (Incoming):")
        for component, count in incoming.most_common(10):
            component_type = component.split('_')[0]
            component_name = '_'.join(component.split('_')[1:])
            print(f"  {component_type:12} {component_name:30} ← {count:3d} references")
        
        return incoming, outgoing
    
    def analyze_class_dependencies(self):
        """Analyze Apex class dependencies"""
        print("\n🏗️ CLASS DEPENDENCY ANALYSIS")
        print("=" * 50)
        
        class_deps = defaultdict(list)
        method_calls = defaultdict(list)
        
        for rel in self.relationships:
            if rel['type'] == 'DEPENDS_ON_CLASS':
                from_class = rel['from'].replace('class_', '')
                to_class = rel['to'].replace('class_', '')
                class_deps[from_class].append(to_class)
            elif rel['type'] == 'CALLS_METHOD':
                from_class = rel['from'].replace('class_', '')
                method_info = rel['details'].replace('Calls method ', '')
                method_calls[from_class].append(method_info)
        
        print("Class Dependencies:")
        for class_name, deps in class_deps.items():
            print(f"  {class_name:25} → {', '.join(deps)}")
        
        print("\nMethod Calls:")
        for class_name, methods in method_calls.items():
            print(f"  {class_name:25} → {', '.join(methods)}")
        
        return class_deps, method_calls
    
    def analyze_object_field_usage(self):
        """Analyze how fields are used across components"""
        print("\n📋 FIELD USAGE ANALYSIS")
        print("=" * 50)
        
        field_usage = defaultdict(list)
        
        for rel in self.relationships:
            if 'FIELD' in rel['type'] and 'field_' in rel['to']:
                field_id = rel['to']
                # Extract object and field name
                parts = field_id.replace('field_', '').split('_', 1)
                if len(parts) == 2:
                    object_name, field_name = parts
                    field_usage[f"{object_name}.{field_name}"].append({
                        'component': rel['from'],
                        'relationship': rel['type'],
                        'details': rel.get('details', '')
                    })
        
        print("Field Usage Patterns:")
        for field, usages in field_usage.items():
            print(f"\n  {field}:")
            for usage in usages:
                component_type = usage['component'].split('_')[0]
                component_name = '_'.join(usage['component'].split('_')[1:])
                print(f"    {component_type:10} {component_name:20} ({usage['relationship']})")
        
        return field_usage
    
    def analyze_trigger_patterns(self):
        """Analyze trigger patterns and handler relationships"""
        print("\n⚡ TRIGGER PATTERN ANALYSIS")
        print("=" * 50)
        
        for trigger in self.triggers:
            print(f"\nTrigger: {trigger['name']}")
            print(f"  Object: {trigger.get('object', 'Unknown')}")
            print(f"  Events: {', '.join(trigger.get('trigger_events', []))}")
            
            # Find handler relationships
            trigger_id = trigger['id']
            handlers = []
            for rel in self.relationships:
                if rel['from'] == trigger_id and 'HANDLER' in rel['type']:
                    handler_name = rel['to'].replace('class_', '')
                    handlers.append(handler_name)
            
            if handlers:
                print(f"  Handlers: {', '.join(handlers)}")
            
            # Show dependencies
            deps = trigger.get('comprehensive_dependencies', {})
            if deps.get('classes'):
                print(f"  Class Dependencies: {', '.join(deps['classes'])}")
    
    def analyze_layout_complexity(self):
        """Analyze layout complexity and field display patterns"""
        print("\n🎨 LAYOUT COMPLEXITY ANALYSIS")
        print("=" * 50)
        
        layout_fields = defaultdict(int)
        
        for rel in self.relationships:
            if rel['type'] == 'DISPLAYS_FIELD' and 'layout_' in rel['from']:
                layout_name = rel['from'].replace('layout_', '')
                layout_fields[layout_name] += 1
        
        print("Layout Field Counts:")
        for layout, field_count in sorted(layout_fields.items(), key=lambda x: x[1], reverse=True):
            print(f"  {layout:30} : {field_count:3d} fields")
        
        return layout_fields
    
    def generate_impact_analysis(self, component_id: str):
        """Generate impact analysis for a specific component"""
        print(f"\n🎯 IMPACT ANALYSIS FOR: {component_id}")
        print("=" * 60)
        
        # Find all relationships involving this component
        affected_by = []
        affects = []
        
        for rel in self.relationships:
            if rel['from'] == component_id:
                affects.append({
                    'target': rel['to'],
                    'type': rel['type'],
                    'details': rel.get('details', '')
                })
            elif rel['to'] == component_id:
                affected_by.append({
                    'source': rel['from'],
                    'type': rel['type'],
                    'details': rel.get('details', '')
                })
        
        print(f"Components that depend on {component_id}:")
        for item in affected_by:
            print(f"  {item['source']:30} ({item['type']})")
        
        print(f"\nComponents that {component_id} depends on:")
        for item in affects:
            print(f"  {item['target']:30} ({item['type']})")
        
        print(f"\nTotal Impact: {len(affected_by)} dependent, {len(affects)} dependencies")
        
        return affected_by, affects
    
    def export_to_csv(self):
        """Export relationships to CSV for further analysis"""
        print("\n💾 EXPORTING TO CSV")
        print("=" * 30)
        
        # Convert relationships to DataFrame
        df = pd.DataFrame(self.relationships)
        
        # Export main relationships
        csv_file = self.metadata_dir / "relationships_analysis.csv"
        df.to_csv(csv_file, index=False)
        print(f"Relationships exported to: {csv_file}")
        
        # Create summary statistics
        summary_data = []
        rel_types = Counter(rel['type'] for rel in self.relationships)
        
        for rel_type, count in rel_types.items():
            summary_data.append({
                'relationship_type': rel_type,
                'count': count,
                'percentage': round(count / len(self.relationships) * 100, 2)
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_file = self.metadata_dir / "relationship_summary.csv"
        summary_df.to_csv(summary_file, index=False)
        print(f"Summary statistics exported to: {summary_file}")


def main():
    """Main analysis function"""
    print("🔍 SALESFORCE METADATA RELATIONSHIP ANALYZER")
    print("=" * 60)
    
    analyzer = MetadataRelationshipAnalyzer()
    
    # Run all analyses
    analyzer.analyze_relationship_types()
    analyzer.analyze_component_connectivity()
    analyzer.analyze_class_dependencies()
    analyzer.analyze_object_field_usage()
    analyzer.analyze_trigger_patterns()
    analyzer.analyze_layout_complexity()
    
    # Example impact analysis
    analyzer.generate_impact_analysis("class_AccountHandler")
    
    # Export results
    try:
        analyzer.export_to_csv()
    except ImportError:
        print("\n⚠️  pandas not installed - skipping CSV export")
        print("Install with: pip install pandas")
    
    print("\n✅ Analysis Complete!")
    print("\nNext Steps:")
    print("1. Review the analysis results above")
    print("2. Load data into Neo4j for graph visualization")
    print("3. Use the CSV exports for further analysis")
    print("4. Run impact analysis on specific components")


if __name__ == "__main__":
    main()
