# Salesforce Metadata to Neo4j Converter

This project converts Salesforce XML metadata files to JSON format and loads them into a Neo4j graph database for analysis and visualization.

## 🎯 Project Overview

The solution consists of two main components:
1. **Metadata Converter** (`metadata_converter.py`) - Converts XML metadata to JSON
2. **Neo4j Loader** (`neo4j_loader.py`) - Loads JSON data into Neo4j graph database

## 📊 Conversion Results

✅ **Successfully Converted:**
- **1 CustomObject** (Account) with 38 fields
- **4 Layouts** (Marketing, Sales, Support, Standard)
- **5 Apex Classes** (AccountCallOutService, AccountCallOutServiceHelper, AccountEmailHelper, AccountHandler, AccountHandlerTest)
- **1 Apex Trigger** (AccountTrigger)
- **1 Workflow** (Account workflow)
- **54 Relationships** between all components

## 📁 Generated Files

The conversion created the following files in the `converted_metadata/` directory:

```
converted_metadata/
├── objects.json              # CustomObject metadata
├── layouts.json              # Layout metadata  
├── classes.json              # Apex Class metadata and source code
├── triggers.json             # Apex Trigger metadata and source code
├── workflows.json            # Workflow metadata
├── relationships.json        # All relationships between components
├── complete_metadata.json    # Combined metadata file
└── conversion_stats.json     # Conversion statistics
```

## 🔗 Relationship Types

The converter identifies and creates the following relationships:

- `CustomObject` -[:HAS_FIELD]-> `CustomField`
- `CustomObject` -[:HAS_LISTVIEW]-> `ListView`
- `CustomObject` -[:HAS_WEBLINK]-> `WebLink`
- `CustomObject` -[:HAS_LAYOUT]-> `Layout`
- `CustomObject` -[:HAS_TRIGGER]-> `ApexTrigger`
- `CustomObject` -[:HAS_WORKFLOW]-> `Workflow`
- `ApexClass` -[:DEPENDS_ON]-> `CustomObject` (extracted from source code)

## 🚀 Getting Started

### Prerequisites

1. **Python 3.7+** installed
2. **Neo4j Database** (optional, for graph loading)

### Step 1: Run the Metadata Converter

```bash
# The converter has already been run successfully
python metadata_converter.py
```

### Step 2: Install Neo4j (Optional)

If you want to load data into Neo4j:

```bash
# Download and install Neo4j Desktop or Community Edition
# https://neo4j.com/download/

# Or use Docker:
docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
```

### Step 3: Load Data into Neo4j

```bash
# Install Neo4j Python driver
pip install neo4j

# Update connection details in neo4j_loader.py, then run:
python neo4j_loader.py
```

## 📈 Data Analysis Examples

### JSON Analysis

You can analyze the converted JSON data directly:

```python
import json

# Load objects data
with open('converted_metadata/objects.json', 'r') as f:
    objects = json.load(f)

# Analyze Account object
account = objects[0]
print(f"Account has {len(account['fields'])} fields")
print(f"Field names: {[f['name'] for f in account['fields']]}")

# Load relationships
with open('converted_metadata/relationships.json', 'r') as f:
    relationships = json.load(f)

# Count relationship types
from collections import Counter
rel_types = Counter(r['type'] for r in relationships)
print("Relationship distribution:", rel_types)
```

### Neo4j Cypher Queries

Once loaded into Neo4j, you can run these queries:

```cypher
-- View all objects and their fields
MATCH (o:CustomObject)-[:HAS_FIELD]->(f:CustomField) 
RETURN o.name, collect(f.name) as fields

-- Find classes that depend on objects
MATCH (c:ApexClass)-[:DEPENDS_ON]->(o:CustomObject) 
RETURN c.name, o.name

-- View object relationships
MATCH (o:CustomObject)-[r]->(n) 
RETURN o.name, type(r), labels(n), n.name

-- Find triggers and their objects
MATCH (o:CustomObject)-[:HAS_TRIGGER]->(t:ApexTrigger) 
RETURN o.name, t.name

-- Analyze field distribution
MATCH (o:CustomObject)-[:HAS_FIELD]->(f:CustomField) 
RETURN o.name, count(f) as field_count 
ORDER BY field_count DESC
```

## 🔧 Customization

### Adding New Metadata Types

To convert additional metadata types, modify `metadata_converter.py`:

1. Add processing method (e.g., `process_custom_tabs()`)
2. Add to `convert_all_metadata()` method
3. Update relationship creation logic

### Modifying Relationships

Edit the relationship creation logic in each processing method to capture different relationship types.

### Neo4j Schema Customization

Modify `neo4j_loader.py` to:
- Add new node labels
- Create additional properties
- Implement custom relationship types

## 📊 Current Metadata Structure

### CustomObject (Account)
- **Properties**: name, enableFeeds, enableHistory, sharingModel
- **Connected to**: 38 CustomFields, 5 ListViews, 1 WebLink

### CustomFields
- **Count**: 38 fields including standard and custom fields
- **Examples**: Name, AccountNumber, Industry, Active__c, SLA__c

### Apex Classes
- **Count**: 5 classes with full source code
- **Dependencies**: Automatically extracted from source code
- **Examples**: AccountHandler, AccountCallOutService

### Layouts
- **Count**: 4 different layouts for Account object
- **Types**: Marketing, Sales, Support, Standard layouts

## 🎯 Next Steps

1. **Explore the Data**: Review the generated JSON files
2. **Set up Neo4j**: Install and configure Neo4j database
3. **Load into Neo4j**: Run the loader script to create the graph
4. **Analyze Relationships**: Use Cypher queries to explore metadata relationships
5. **Extend Coverage**: Add more metadata types as needed
6. **Build Visualizations**: Create dashboards using Neo4j Browser or custom tools

## 🔍 Key Insights from Conversion

- **Account Object Complexity**: 38 fields showing rich data model
- **Code Dependencies**: Classes show dependencies on custom objects
- **Layout Variations**: Multiple layouts for different user personas
- **Trigger Integration**: AccountTrigger connects to AccountHandler class
- **Workflow Automation**: Account workflow for business process automation

## 🛠️ Troubleshooting

### Common Issues

1. **XML Parsing Errors**: Check for malformed XML files
2. **Neo4j Connection**: Verify database is running and credentials are correct
3. **Missing Files**: Ensure all metadata files are present in force-app directory

### Error Handling

The converter includes comprehensive error handling and logging. Check `conversion_stats.json` for any errors encountered during conversion.

## 📝 Technical Notes

- **XML Namespace Handling**: Automatically removes Salesforce namespaces
- **Source Code Analysis**: Uses regex patterns to extract dependencies
- **Relationship Inference**: Creates logical relationships based on metadata structure
- **JSON Structure**: Optimized for Neo4j loading with proper node/relationship separation
