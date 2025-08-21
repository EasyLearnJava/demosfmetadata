"""
Step 1 – Convert Salesforce CustomObject metadata (XML) to
JSON files suitable for loading into Neo4j.

- Walks through <metadata_root>/objects/**/<ObjectName>.object-meta.xml
- Converts XML → Python dict
- Extracts Object nodes + Field nodes + relationships
- Saves two JSON files: nodes.json and relationships.json
"""

import xmltodict
import json
from pathlib import Path

# Change this to the root of your metadata folder (e.g. 'force-app/main/default')
METADATA_ROOT = Path("force-app/main/default")

nodes = []
relationships = []

def load_xml_dict(path):
    with open(path, "r", encoding="utf-8") as f:
        return xmltodict.parse(f.read())

def handle_custom_object(xml_dict):
    obj_meta = xml_dict["CustomObject"]
    obj_name = obj_meta["fullName"]
    # Add Object node
    nodes.append({
        "label": "Object",
        "name": obj_name,
        "properties": {
            "label": obj_meta.get("label"),
            "pluralLabel": obj_meta.get("pluralLabel")
        }
    })
    # Handle fields
    fields = obj_meta.get("fields", [])
    # xmltodict returns a dict for a single element and a list when there are multiples
    if isinstance(fields, dict):
        fields = [fields]
    for f in fields:
        field_name = f["fullName"]
        # Add field node
        nodes.append({
            "label": "Field",
            "name": field_name,
            "properties": {
                "type": f.get("type"),
                "label": f.get("label")
            }
        })
        # Add relationship
        relationships.append({
            "fromLabel": "Object",
            "fromName": obj_name,
            "toLabel":   "Field",
            "toName":    field_name,
            "type":      "HAS_FIELD"
        })

def walk_objects():
    objects_dir = METADATA_ROOT / "objects"
    for folder in objects_dir.iterdir():
        xml_path = folder / f"{folder.name}.object-meta.xml"
        if xml_path.exists():
            xml_dict = load_xml_dict(xml_path)
            handle_custom_object(xml_dict)

if __name__ == "__main__":
    walk_objects()

    # Save outputs
    with open("nodes.json", "w", encoding="utf-8") as f_nodes:
        json.dump(nodes, f_nodes, indent=2)

    with open("relationships.json", "w", encoding="utf-8") as f_rels:
        json.dump(relationships, f_rels, indent=2)

    print("✅ Conversion complete.  nodes.json and relationships.json created.")
