# 🔧 Manual Neo4j Setup Guide

## 🎯 **CURRENT STATUS**
✅ **Virtual Environment**: Ready with all dependencies  
✅ **Java**: Installed (Java 24)  
✅ **Docker**: Installed but not running  
✅ **Metadata**: Converted to JSON (199 relationships)  

## 🚀 **OPTION 1: Neo4j Desktop (Recommended)**

### **Step 1: Download Neo4j Desktop**
1. Go to: https://neo4j.com/download/
2. Click "Download Neo4j Desktop"
3. Fill out the form (use any email)
4. Download and install Neo4j Desktop

### **Step 2: Create Database**
1. Open Neo4j Desktop
2. Click "New" → "Create Project"
3. Name: "Salesforce Metadata"
4. Click "Add" → "Local DBMS"
5. Name: "SF-Metadata"
6. Password: `salesforce123` (remember this!)
7. Version: 5.x (latest)
8. Click "Create"

### **Step 3: Start Database**
1. Click the "Start" button on your database
2. Wait for status to show "Active"
3. Click "Open" to access Neo4j Browser

### **Step 4: Update Connection Settings**
Edit `neo4j_loader.py` line 348:
```python
NEO4J_PASSWORD = "salesforce123"  # Your database password
```

### **Step 5: Load Data**
```bash
# Activate virtual environment
sf_metadata_env\Scripts\activate

# Load metadata
python neo4j_loader.py
```

## 🐳 **OPTION 2: Docker (If Docker Desktop is Running)**

### **Step 1: Start Docker Desktop**
1. Open Docker Desktop application
2. Wait for it to show "Engine running"
3. Green whale icon in system tray

### **Step 2: Run Docker Setup**
```bash
python docker_neo4j_setup.py
```

This will:
- Start Neo4j container
- Set password to `salesforce123`
- Configure data volumes
- Update loader settings

## 🌐 **OPTION 3: Manual Download & Install**

### **Step 1: Download Neo4j Community**
1. Go to: https://neo4j.com/deployment-center/
2. Select "Community Server"
3. Download Windows ZIP file
4. Extract to your project folder

### **Step 2: Configure Neo4j**
1. Navigate to `neo4j/conf/`
2. Edit `neo4j.conf`:
```properties
# Uncomment and set initial password
dbms.security.auth_enabled=true
dbms.default_database=neo4j

# Memory settings for metadata
server.memory.heap.initial_size=1G
server.memory.heap.max_size=2G
server.memory.pagecache.size=1G
```

### **Step 3: Start Neo4j**
```bash
cd neo4j\bin
neo4j.bat console
```

### **Step 4: Set Password**
1. Open: http://localhost:7474
2. Login: neo4j/neo4j
3. Set new password: `salesforce123`

## 🔍 **VERIFICATION STEPS**

### **Test Connection**
```bash
# Activate environment
sf_metadata_env\Scripts\activate

# Test Neo4j connection
python -c "
from neo4j import GraphDatabase
try:
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'salesforce123'))
    with driver.session() as session:
        result = session.run('RETURN 1 as test')
        print('✅ Neo4j connection successful!')
    driver.close()
except Exception as e:
    print(f'❌ Connection failed: {e}')
"
```

### **Load Metadata**
```bash
python neo4j_loader.py
```

**Expected Output:**
```
✅ Database cleared successfully
✅ Constraints and indexes created
✅ CustomObject nodes loaded successfully
✅ Layout nodes loaded successfully  
✅ ApexClass nodes loaded successfully
✅ ApexTrigger nodes loaded successfully
✅ Workflow nodes loaded successfully
✅ Relationships loaded successfully

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

## 🎯 **QUICK START QUERIES**

Once data is loaded, try these queries in Neo4j Browser:

### **1. Overview of All Data**
```cypher
MATCH (n) 
RETURN labels(n) as NodeType, count(n) as Count
ORDER BY Count DESC
```

### **2. Account Object Ecosystem**
```cypher
MATCH (o:CustomObject {name: 'Account'})-[r]-(connected)
RETURN o, r, connected
LIMIT 25
```

### **3. Class Dependencies**
```cypher
MATCH (c:ApexClass)-[:DEPENDS_ON_CLASS]->(dep:ApexClass)
RETURN c.name as Class, dep.name as DependsOn
```

### **4. Trigger Flow**
```cypher
MATCH (o:CustomObject)-[:HAS_TRIGGER]->(t:ApexTrigger)-[:DELEGATES_TO_HANDLER]->(h:ApexClass)
RETURN o.name as Object, t.name as Trigger, h.name as Handler
```

### **5. Field Usage Analysis**
```cypher
MATCH (f:CustomField)<-[r]-(component)
WHERE f.object = 'Account'
RETURN f.name as Field, type(r) as UsedBy, labels(component) as ComponentType, count(*) as Usage
ORDER BY Usage DESC
```

## 🔧 **TROUBLESHOOTING**

### **Common Issues:**

1. **"Connection refused"**
   - Check if Neo4j is running
   - Verify port 7687 is not blocked
   - Try: http://localhost:7474

2. **"Authentication failed"**
   - Check password in `neo4j_loader.py`
   - Reset password in Neo4j Browser

3. **"Java not found"**
   - Java is already installed ✅
   - If issues, restart command prompt

4. **"Memory errors"**
   - Increase heap size in neo4j.conf
   - Close other applications

### **Get Help:**
- Neo4j Browser: http://localhost:7474
- Check logs in Neo4j installation folder
- Docker logs: `docker logs sf-metadata-neo4j`

## 🎉 **SUCCESS INDICATORS**

You'll know everything is working when:
1. ✅ Neo4j Browser loads at http://localhost:7474
2. ✅ You can login with your credentials
3. ✅ `python neo4j_loader.py` completes successfully
4. ✅ Queries return your Salesforce metadata
5. ✅ You see 199 relationships in the graph

**Your Salesforce metadata graph database will be ready for exploration!** 🚀
