# 🚀 Quick Neo4j Setup (5 Minutes)

## 📥 **STEP 1: Download & Install Neo4j Desktop**

1. **Download**: The browser opened to https://neo4j.com/download/
2. **Fill Form**: Use any email address
3. **Download**: Click "Download Neo4j Desktop"
4. **Install**: Run the installer as administrator
5. **Launch**: Open Neo4j Desktop

## 🗄️ **STEP 2: Create Database**

1. **Create Project**:
   - Click "New" → "Create Project"
   - Name: "Salesforce Metadata"

2. **Add Database**:
   - Click "Add" → "Local DBMS"
   - Name: "SF-Metadata"
   - Password: `salesforce123` (important - remember this!)
   - Version: Select latest (5.x)
   - Click "Create"

3. **Start Database**:
   - Click the "Start" button
   - Wait for status to show "Active" (green)

## 🌐 **STEP 3: Access Neo4j Browser**

1. **Open Browser**: Click "Open" button on your database
2. **Login**:
   - Username: `neo4j`
   - Password: `salesforce123`
3. **Success**: You should see the Neo4j Browser interface

## 📊 **STEP 4: Load Your Salesforce Data**

Open command prompt in your project folder and run:

```bash
# Activate virtual environment
sf_metadata_env\Scripts\activate

# Load your 199 relationships into Neo4j
python neo4j_loader.py
```

**Expected Output:**
```
✅ Database cleared successfully
✅ Constraints and indexes created
✅ CustomObject nodes loaded successfully (1 objects)
✅ Layout nodes loaded successfully (4 layouts)
✅ ApexClass nodes loaded successfully (5 classes)
✅ ApexTrigger nodes loaded successfully (1 triggers)
✅ Workflow nodes loaded successfully (1 workflows)
✅ Relationships loaded successfully (199 relationships)

Database Statistics:
- CustomObject: 1
- CustomField: 38
- Layout: 4
- ApexClass: 5
- ApexTrigger: 1
- Workflow: 1
- ListView: 5
- WebLink: 1
- Relationships: 199
```

## 🔍 **STEP 5: Your First Query**

In Neo4j Browser, run this query to see your Account ecosystem:

```cypher
MATCH (o:CustomObject {name: 'Account'})-[r]-(connected)
RETURN o, r, connected
LIMIT 25
```

## ✅ **SUCCESS INDICATORS**

You'll know it's working when:
1. ✅ Neo4j Desktop shows database as "Active"
2. ✅ Browser opens at http://localhost:7474
3. ✅ Data loader completes successfully
4. ✅ Query shows your Salesforce metadata graph

## 🔧 **If You Have Issues**

Run the troubleshooter again:
```bash
python troubleshoot_neo4j.py
```

## 🎯 **What You'll Get**

Once loaded, you'll have a complete graph database with:
- **Account Object** with all 38 fields
- **5 Apex Classes** with dependencies
- **4 Layouts** with field relationships
- **1 Trigger** with handler connections
- **199 Total Relationships** connecting everything

**Total setup time: ~5 minutes** ⏱️
