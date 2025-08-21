# 🔍 Neo4j Query & Traversal Guide for Salesforce Metadata

## 🎯 **COMPREHENSIVE QUERY COLLECTION**

### **🏗️ BASIC EXPLORATION QUERIES**

#### **1. Database Overview**
```cypher
// Count all nodes by type
MATCH (n) 
RETURN labels(n) as NodeType, count(n) as Count
ORDER BY Count DESC
```

#### **2. Relationship Overview**
```cypher
// Count all relationships by type
MATCH ()-[r]->()
RETURN type(r) as RelationshipType, count(r) as Count
ORDER BY Count DESC
```

#### **3. Database Schema**
```cypher
// View database schema
CALL db.schema.visualization()
```

### **📊 OBJECT & FIELD ANALYSIS**

#### **4. Account Object Deep Dive**
```cypher
// Complete Account object ecosystem
MATCH (o:CustomObject {name: 'Account'})-[r]-(connected)
RETURN o, r, connected
LIMIT 50
```

#### **5. Field Usage Patterns**
```cypher
// Which fields are used most across components
MATCH (f:CustomField)<-[r]-(component)
RETURN f.name as FieldName, 
       f.object as ObjectName,
       type(r) as UsageType,
       labels(component) as ComponentType,
       count(*) as UsageCount
ORDER BY UsageCount DESC
```

#### **6. Layout Field Analysis**
```cypher
// Fields displayed on each layout
MATCH (l:Layout)-[:DISPLAYS_FIELD]->(f:CustomField)
RETURN l.name as Layout, 
       collect(f.name) as Fields,
       count(f) as FieldCount
ORDER BY FieldCount DESC
```

### **🏗️ CLASS & CODE ANALYSIS**

#### **7. Class Dependency Chain**
```cypher
// Find class dependency chains
MATCH path = (c:ApexClass)-[:DEPENDS_ON_CLASS*1..3]->(dep:ApexClass)
RETURN path
LIMIT 10
```

#### **8. Method Call Analysis**
```cypher
// Classes and their method calls
MATCH (c:ApexClass)-[r:CALLS_METHOD]->(target)
RETURN c.name as Class,
       r.details as MethodCall,
       target.name as TargetClass
```

#### **9. Object Usage by Classes**
```cypher
// Which objects are used by which classes
MATCH (c:ApexClass)-[r:USES_OBJECT]->(o:CustomObject)
RETURN c.name as Class,
       o.name as Object,
       r.details as Usage
```

### **⚡ TRIGGER & AUTOMATION ANALYSIS**

#### **10. Trigger Flow Visualization**
```cypher
// Complete trigger execution flow
MATCH (o:CustomObject)-[:HAS_TRIGGER]->(t:ApexTrigger)-[:DELEGATES_TO_HANDLER]->(h:ApexClass)
RETURN o.name as Object,
       t.name as Trigger,
       t.trigger_events as Events,
       h.name as Handler
```

#### **11. Automation Components**
```cypher
// All automation components for an object
MATCH (o:CustomObject {name: 'Account'})-[r]-(automation)
WHERE type(r) IN ['HAS_TRIGGER', 'HAS_WORKFLOW']
RETURN o.name as Object,
       type(r) as AutomationType,
       automation.name as Component
```

### **🎨 UI & LAYOUT ANALYSIS**

#### **12. Layout Complexity Comparison**
```cypher
// Compare layout complexity
MATCH (l:Layout)-[:DISPLAYS_FIELD]->(f:CustomField)
WITH l, count(f) as fieldCount
MATCH (l)-[:SHOWS_RELATED_LIST]->(rl)
WITH l, fieldCount, count(rl) as relatedListCount
RETURN l.name as Layout,
       fieldCount as Fields,
       relatedListCount as RelatedLists,
       (fieldCount + relatedListCount) as TotalComplexity
ORDER BY TotalComplexity DESC
```

#### **13. Field Display Patterns**
```cypher
// Fields that appear on multiple layouts
MATCH (f:CustomField)<-[:DISPLAYS_FIELD]-(l:Layout)
WITH f, collect(l.name) as layouts, count(l) as layoutCount
WHERE layoutCount > 1
RETURN f.name as Field,
       f.object as Object,
       layouts as AppearsOnLayouts,
       layoutCount as LayoutCount
ORDER BY layoutCount DESC
```

### **🔗 RELATIONSHIP TRAVERSAL QUERIES**

#### **14. Impact Analysis - What Depends on a Component**
```cypher
// Find everything that depends on AccountHandler
MATCH (component)-[r]->(target:ApexClass {name: 'AccountHandler'})
RETURN component.name as DependentComponent,
       labels(component) as ComponentType,
       type(r) as RelationshipType,
       r.details as Details
```

#### **15. Dependency Analysis - What a Component Depends On**
```cypher
// Find everything AccountHandler depends on
MATCH (source:ApexClass {name: 'AccountHandler'})-[r]->(dependency)
RETURN dependency.name as Dependency,
       labels(dependency) as DependencyType,
       type(r) as RelationshipType,
       r.details as Details
```

#### **16. Multi-Hop Relationships**
```cypher
// Find indirect relationships (2-3 hops)
MATCH path = (start:ApexClass {name: 'AccountTrigger'})-[*2..3]-(end)
WHERE start <> end
RETURN path
LIMIT 10
```

### **📈 ADVANCED ANALYTICS**

#### **17. Component Connectivity Score**
```cypher
// Most connected components
MATCH (n)
OPTIONAL MATCH (n)-[r1]->()
OPTIONAL MATCH ()-[r2]->(n)
WITH n, count(r1) as outgoing, count(r2) as incoming
RETURN labels(n) as NodeType,
       n.name as Component,
       outgoing as OutgoingConnections,
       incoming as IncomingConnections,
       (outgoing + incoming) as TotalConnections
ORDER BY TotalConnections DESC
LIMIT 20
```

#### **18. Orphaned Components**
```cypher
// Find components with no relationships
MATCH (n)
WHERE NOT (n)-[]-()
RETURN labels(n) as NodeType, n.name as Component
```

#### **19. Critical Path Analysis**
```cypher
// Find components that are in many relationship paths
MATCH path = (start)-[*2..4]-(end)
WITH nodes(path) as pathNodes
UNWIND pathNodes as node
WITH node, count(*) as pathCount
WHERE pathCount > 5
RETURN labels(node) as NodeType,
       node.name as Component,
       pathCount as PathsThrough
ORDER BY pathCount DESC
```

### **🔍 SPECIFIC USE CASE QUERIES**

#### **20. Field Security Analysis**
```cypher
// Fields that are accessed by code but not displayed on layouts
MATCH (f:CustomField)
OPTIONAL MATCH (f)<-[:DISPLAYS_FIELD]-(l:Layout)
OPTIONAL MATCH (f)<-[:ACCESSES_FIELD]-(c:ApexClass)
WITH f, count(l) as layoutUsage, count(c) as codeUsage
WHERE codeUsage > 0 AND layoutUsage = 0
RETURN f.object as Object,
       f.name as Field,
       codeUsage as UsedInCode,
       layoutUsage as DisplayedOnLayouts
```

#### **21. Integration Points**
```cypher
// Find external integration points
MATCH (c:ApexClass)-[r]-(external)
WHERE type(r) IN ['CALLS_WEBSERVICE', 'USES_EMAIL_TEMPLATE', 'USES_STATIC_RESOURCE']
RETURN c.name as Class,
       type(r) as IntegrationType,
       external.name as ExternalResource
```

#### **22. Data Flow Analysis**
```cypher
// Trace data flow from trigger to final processing
MATCH path = (o:CustomObject)-[:HAS_TRIGGER]->(t:ApexTrigger)-[:DELEGATES_TO_HANDLER]->(h:ApexClass)-[:USES_OBJECT]->(target:CustomObject)
RETURN o.name as SourceObject,
       t.name as Trigger,
       h.name as Handler,
       target.name as TargetObject
```

### **🎯 PERFORMANCE & OPTIMIZATION QUERIES**

#### **23. Query Performance Analysis**
```cypher
// Use EXPLAIN to analyze query performance
EXPLAIN MATCH (c:ApexClass)-[:DEPENDS_ON_CLASS*1..2]->(dep)
RETURN c.name, collect(dep.name)
```

#### **24. Index Usage**
```cypher
// Show available indexes
SHOW INDEXES
```

#### **25. Database Statistics**
```cypher
// Get database statistics
CALL db.stats.retrieve('GRAPH COUNTS')
```

## 🚀 **TRAVERSAL PATTERNS**

### **Pattern 1: Breadth-First Search**
```cypher
// Explore all components within 2 hops of AccountHandler
MATCH (start:ApexClass {name: 'AccountHandler'})
CALL apoc.path.expand(start, null, null, 1, 2) YIELD path
RETURN path
```

### **Pattern 2: Depth-First Search**
```cypher
// Deep dependency chain exploration
MATCH path = (start:ApexClass {name: 'AccountHandler'})-[*1..5]->(end)
RETURN path
ORDER BY length(path) DESC
LIMIT 5
```

### **Pattern 3: Shortest Path**
```cypher
// Find shortest path between two components
MATCH (start:ApexClass {name: 'AccountTrigger'}),
      (end:CustomObject {name: 'Account'})
MATCH path = shortestPath((start)-[*]-(end))
RETURN path
```

## 📊 **VISUALIZATION TIPS**

### **For Neo4j Browser:**
1. **Limit Results**: Always use `LIMIT` for large datasets
2. **Color Coding**: Different node types get different colors
3. **Expand Nodes**: Click nodes to see more relationships
4. **Save Queries**: Use favorites for common queries

### **For Custom Visualization:**
```cypher
// Export data for external visualization
MATCH (n)-[r]->(m)
RETURN n.name as source, 
       type(r) as relationship, 
       m.name as target,
       labels(n) as sourceType,
       labels(m) as targetType
```

## 🎯 **NEXT STEPS**

1. **Start with Basic Queries**: Begin with overview queries
2. **Explore Your Data**: Use the Account ecosystem query
3. **Analyze Dependencies**: Focus on class and trigger relationships
4. **Build Custom Queries**: Modify examples for your specific needs
5. **Create Dashboards**: Use results to build monitoring dashboards

Your Salesforce metadata graph is now ready for comprehensive exploration! 🎉
