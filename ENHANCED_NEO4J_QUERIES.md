# 🚀 Enhanced Neo4j Queries for Salesforce Metadata

*Powerful queries to explore your comprehensive Account, Contact, and Opportunity metadata*

---

## 🎯 **GETTING STARTED**

**Open Neo4j Browser**: http://localhost:7474  
**Login**: neo4j / salesforce123

---

## 🏢 **1. OBJECT ECOSYSTEM QUERIES**

### **Complete Salesforce Ecosystem**
```cypher
MATCH (o:CustomObject)
RETURN o.name as Object, 
       [(o)-[:HAS_FIELD]->(f) | f.name] as Fields,
       [(o)-[:HAS_LISTVIEW]->(lv) | lv.name] as ListViews
ORDER BY o.name
```

### **Cross-Object Relationships**
```cypher
MATCH (a:CustomObject)-[r:BELONGS_TO|RELATES_TO]->(b:CustomObject)
RETURN a.name as FromObject, 
       type(r) as Relationship, 
       b.name as ToObject,
       r.context as Context
```

### **Visual Object Network**
```cypher
MATCH (o:CustomObject)-[r]-(connected:CustomObject)
RETURN o, r, connected
```

---

## 📝 **2. FIELD ANALYSIS QUERIES**

### **All Fields Across All Objects**
```cypher
MATCH (o:CustomObject)-[:HAS_FIELD]->(f:CustomField)
RETURN o.name as Object, 
       f.name as Field, 
       f.type as Type,
       f.label as Label,
       f.required as Required
ORDER BY o.name, f.name
```

### **Field Types Distribution**
```cypher
MATCH (f:CustomField)
RETURN f.type as FieldType, count(f) as Count
ORDER BY Count DESC
```

### **Required Fields Analysis**
```cypher
MATCH (o:CustomObject)-[:HAS_FIELD]->(f:CustomField)
WHERE f.required = true
RETURN o.name as Object, 
       collect(f.name) as RequiredFields,
       count(f) as RequiredFieldCount
ORDER BY RequiredFieldCount DESC
```

### **Lookup Fields (Cross-Object References)**
```cypher
MATCH (o:CustomObject)-[:HAS_FIELD]->(f:CustomField)
WHERE f.name ENDS WITH 'Id' AND f.name <> 'Id'
RETURN o.name as Object, 
       f.name as LookupField,
       f.type as Type
ORDER BY o.name
```

---

## 📊 **3. CONTACT OBJECT DEEP DIVE**

### **Contact Object Complete Profile**
```cypher
MATCH (c:CustomObject {name: 'Contact'})
OPTIONAL MATCH (c)-[:HAS_FIELD]->(f:CustomField)
OPTIONAL MATCH (c)-[:HAS_LISTVIEW]->(lv:ListView)
OPTIONAL MATCH (c)-[r]->(related:CustomObject)
RETURN c.name as Object,
       count(DISTINCT f) as FieldCount,
       count(DISTINCT lv) as ListViewCount,
       collect(DISTINCT related.name) as RelatedObjects,
       collect(DISTINCT type(r)) as RelationshipTypes
```

### **Contact Fields by Type**
```cypher
MATCH (c:CustomObject {name: 'Contact'})-[:HAS_FIELD]->(f:CustomField)
RETURN f.type as FieldType, 
       collect(f.name) as Fields,
       count(f) as Count
ORDER BY Count DESC
```

### **Contact List Views**
```cypher
MATCH (c:CustomObject {name: 'Contact'})-[:HAS_LISTVIEW]->(lv:ListView)
RETURN lv.name as ListView, 
       lv.label as Label
ORDER BY lv.name
```

---

## 💰 **4. OPPORTUNITY OBJECT DEEP DIVE**

### **Opportunity Object Complete Profile**
```cypher
MATCH (o:CustomObject {name: 'Opportunity'})
OPTIONAL MATCH (o)-[:HAS_FIELD]->(f:CustomField)
OPTIONAL MATCH (o)-[:HAS_LISTVIEW]->(lv:ListView)
OPTIONAL MATCH (o)-[:HAS_WEBLINK]->(wl:WebLink)
OPTIONAL MATCH (o)-[r]->(related:CustomObject)
RETURN o.name as Object,
       count(DISTINCT f) as FieldCount,
       count(DISTINCT lv) as ListViewCount,
       count(DISTINCT wl) as WebLinkCount,
       collect(DISTINCT related.name) as RelatedObjects
```

### **Opportunity Sales Process Fields**
```cypher
MATCH (o:CustomObject {name: 'Opportunity'})-[:HAS_FIELD]->(f:CustomField)
WHERE f.name IN ['StageName', 'Amount', 'CloseDate', 'Probability', 'Type']
RETURN f.name as Field, 
       f.type as Type,
       f.label as Label
ORDER BY f.name
```

### **Opportunity List Views (Sales Pipeline)**
```cypher
MATCH (o:CustomObject {name: 'Opportunity'})-[:HAS_LISTVIEW]->(lv:ListView)
RETURN lv.name as ListView,
       lv.label as Label
ORDER BY lv.name
```

---

## 🔗 **5. RELATIONSHIP ANALYSIS QUERIES**

### **Most Connected Objects**
```cypher
MATCH (o:CustomObject)
RETURN o.name as Object,
       [(o)-[:HAS_FIELD]->(f) | f.name] as Fields,
       size([(o)-[:HAS_FIELD]->(f) | f]) as FieldCount,
       size([(o)-[:HAS_LISTVIEW]->(lv) | lv]) as ListViewCount,
       size([(o)-[:HAS_WEBLINK]->(wl) | wl]) as WebLinkCount
ORDER BY FieldCount DESC
```

### **Cross-Object Dependencies**
```cypher
MATCH path = (a:CustomObject)-[:BELONGS_TO|RELATES_TO*1..2]->(b:CustomObject)
RETURN [node in nodes(path) | node.name] as DependencyChain,
       length(path) as ChainLength
ORDER BY ChainLength DESC
```

### **Field Usage Across Layouts**
```cypher
MATCH (l:Layout)-[:DISPLAYS_FIELD]->(f:CustomField)<-[:HAS_FIELD]-(o:CustomObject)
RETURN f.name as Field,
       o.name as Object,
       count(l) as LayoutCount,
       collect(l.name) as Layouts
ORDER BY LayoutCount DESC, f.name
```

---

## 💻 **6. APEX CODE INTEGRATION QUERIES**

### **Apex Classes and Their Object Dependencies**
```cypher
MATCH (c:ApexClass)-[r]->(o:CustomObject)
RETURN c.name as ApexClass,
       type(r) as RelationshipType,
       o.name as Object,
       r.context as Context
ORDER BY c.name
```

### **Complete Account Ecosystem (All Connected Components)**
```cypher
MATCH (account:CustomObject {name: 'Account'})
OPTIONAL MATCH (account)-[r1]-(connected1)
OPTIONAL MATCH (connected1)-[r2]-(connected2)
WHERE connected2 <> account
RETURN account, r1, connected1, r2, connected2
LIMIT 50
```

---

## 📈 **7. IMPACT ANALYSIS QUERIES**

### **What Would Break If We Change Account Object?**
```cypher
MATCH (account:CustomObject {name: 'Account'})
MATCH (account)<-[r]-(dependent)
RETURN labels(dependent)[0] as DependentType,
       dependent.name as DependentName,
       type(r) as RelationshipType,
       r.context as Context
ORDER BY DependentType, DependentName
```

### **Field Impact Analysis (Example: AccountId)**
```cypher
MATCH (f:CustomField)
WHERE f.name CONTAINS 'Account'
MATCH (f)<-[:HAS_FIELD]-(o:CustomObject)
OPTIONAL MATCH (f)<-[:DISPLAYS_FIELD]-(l:Layout)
RETURN f.name as Field,
       o.name as Object,
       collect(DISTINCT l.name) as DisplayedInLayouts,
       count(DISTINCT l) as LayoutCount
ORDER BY LayoutCount DESC
```

---

## 🎯 **8. BUSINESS PROCESS QUERIES**

### **Lead-to-Cash Process Objects**
```cypher
MATCH path = (contact:CustomObject {name: 'Contact'})-[:BELONGS_TO]->(account:CustomObject {name: 'Account'})<-[:BELONGS_TO]-(opp:CustomObject {name: 'Opportunity'})
RETURN contact.name as Contact,
       account.name as Account,
       opp.name as Opportunity,
       "Lead-to-Cash Process" as BusinessProcess
```

### **Customer 360 View (All Related Objects)**
```cypher
MATCH (account:CustomObject {name: 'Account'})
MATCH (contact:CustomObject {name: 'Contact'})-[:BELONGS_TO]->(account)
MATCH (opp:CustomObject {name: 'Opportunity'})-[:BELONGS_TO]->(account)
RETURN account, contact, opp
```

---

## 📊 **9. METADATA STATISTICS QUERIES**

### **Complete Database Statistics**
```cypher
MATCH (n)
RETURN labels(n)[0] as NodeType, 
       count(n) as Count
ORDER BY Count DESC
```

### **Relationship Statistics**
```cypher
MATCH ()-[r]->()
RETURN type(r) as RelationshipType, 
       count(r) as Count
ORDER BY Count DESC
```

### **Object Complexity Score**
```cypher
MATCH (o:CustomObject)
RETURN o.name as Object,
       size([(o)-[:HAS_FIELD]->(f) | f]) as Fields,
       size([(o)-[:HAS_LISTVIEW]->(lv) | lv]) as ListViews,
       size([(o)-[:HAS_WEBLINK]->(wl) | wl]) as WebLinks,
       (size([(o)-[:HAS_FIELD]->(f) | f]) + 
        size([(o)-[:HAS_LISTVIEW]->(lv) | lv]) + 
        size([(o)-[:HAS_WEBLINK]->(wl) | wl])) as ComplexityScore
ORDER BY ComplexityScore DESC
```

---

## 🎉 **10. VISUAL EXPLORATION QUERIES**

### **Complete Metadata Graph (Limited)**
```cypher
MATCH (n)-[r]-(m)
RETURN n, r, m
LIMIT 100
```

### **Object-Centric View (Choose Your Object)**
```cypher
// Replace 'Account' with 'Contact' or 'Opportunity' to explore different objects
MATCH (center:CustomObject {name: 'Account'})-[r]-(connected)
RETURN center, r, connected
LIMIT 50
```

### **Field Relationship Network**
```cypher
MATCH (o:CustomObject)-[:HAS_FIELD]->(f:CustomField)
MATCH (l:Layout)-[:DISPLAYS_FIELD]->(f)
RETURN o, f, l
LIMIT 30
```

---

## 🚀 **GETTING STARTED TIPS**

1. **Start Simple**: Begin with the Object Ecosystem queries
2. **Use LIMIT**: Add `LIMIT 25` to large queries to avoid overwhelming results
3. **Visual Mode**: Click the graph view icon in Neo4j Browser for visual exploration
4. **Export Results**: Use the download button to export query results as CSV
5. **Save Favorites**: Bookmark your most useful queries in Neo4j Browser

## 🎯 **YOUR ENHANCED METADATA IS READY FOR EXPLORATION!**

**You now have a comprehensive graph database with 3 objects, 94 fields, and 236 relationships ready for analysis!** 🎉
