#!/usr/bin/env python3
"""
Salesforce Metadata Chatbot - No Neo4j Required!
Uses pre-computed relationships from JSON + Vector DB for semantic search
"""

import json
import os
from typing import List, Dict, Any
from dataclasses import dataclass
import chromadb
from sentence_transformers import SentenceTransformer

@dataclass
class MetadataReference:
    source: str
    target: str
    relationship_type: str
    context: str = ""
    metadata: Dict[str, Any] = None

class SalesforceMetadataChatbot:
    def __init__(self, relationships_file: str = "converted_metadata/relationships.json"):
        """Initialize chatbot with pre-computed relationships"""
        
        # Load relationships from JSON (no Neo4j needed!)
        self.relationships = self.load_relationships(relationships_file)
        
        # Setup vector database for semantic search
        self.setup_vector_db()
        
        # Load sentence transformer for embeddings
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        print("🤖 Salesforce Metadata Chatbot initialized!")
        print(f"📊 Loaded {len(self.relationships)} relationships")
    
    def load_relationships(self, file_path: str) -> List[Dict]:
        """Load pre-computed relationships from JSON"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data.get('relationships', [])
        except FileNotFoundError:
            print(f"❌ Relationships file not found: {file_path}")
            return []
    
    def setup_vector_db(self):
        """Setup ChromaDB for semantic search"""
        self.chroma_client = chromadb.Client()
        
        # Create collection for metadata descriptions
        try:
            self.collection = self.chroma_client.get_collection("salesforce_metadata")
        except:
            self.collection = self.chroma_client.create_collection("salesforce_metadata")
            self.populate_vector_db()
    
    def populate_vector_db(self):
        """Populate vector DB with relationship descriptions"""
        documents = []
        metadatas = []
        ids = []
        
        for i, rel in enumerate(self.relationships):
            # Create natural language description
            description = self.create_relationship_description(rel)
            documents.append(description)
            metadatas.append(rel)
            ids.append(f"rel_{i}")
        
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"✅ Added {len(documents)} relationship descriptions to vector DB")
    
    def create_relationship_description(self, relationship: Dict) -> str:
        """Convert relationship to natural language"""
        source = relationship.get('from', '')
        target = relationship.get('to', '')
        rel_type = relationship.get('type', '')
        
        # Create human-readable descriptions
        descriptions = {
            'HAS_FIELD': f"{source} object has field {target}",
            'DISPLAYS_FIELD': f"{source} layout displays field {target}",
            'REFERENCES': f"{source} class references {target}",
            'USES_OBJECT': f"{source} class uses {target} object",
            'HAS_LAYOUT': f"{source} object has layout {target}",
            'HAS_TRIGGER': f"{source} object has trigger {target}",
            'DEPENDS_ON': f"{source} depends on {target}",
            'CALLS_METHOD': f"{source} calls method in {target}"
        }
        
        return descriptions.get(rel_type, f"{source} {rel_type.lower().replace('_', ' ')} {target}")
    
    def find_references(self, entity_name: str) -> List[MetadataReference]:
        """Find all references to a specific entity (field, object, class, etc.)"""
        references = []
        
        for rel in self.relationships:
            # Check if entity is referenced as target
            if rel.get('to', '').lower() == entity_name.lower():
                references.append(MetadataReference(
                    source=rel.get('from', ''),
                    target=rel.get('to', ''),
                    relationship_type=rel.get('type', ''),
                    context=rel.get('context', ''),
                    metadata=rel
                ))
            
            # Check if entity is the source
            elif rel.get('from', '').lower() == entity_name.lower():
                references.append(MetadataReference(
                    source=rel.get('from', ''),
                    target=rel.get('to', ''),
                    relationship_type=rel.get('type', ''),
                    context=rel.get('context', ''),
                    metadata=rel
                ))
        
        return references
    
    def semantic_search(self, query: str, n_results: int = 10) -> List[Dict]:
        """Perform semantic search on relationships"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        return results['metadatas'][0] if results['metadatas'] else []
    
    def answer_question(self, question: str) -> str:
        """Main chatbot function - answer user questions"""
        question_lower = question.lower()
        
        # Pattern matching for common questions
        if "where" in question_lower and "reference" in question_lower:
            return self.handle_reference_question(question)
        
        elif "what uses" in question_lower or "what depends" in question_lower:
            return self.handle_dependency_question(question)
        
        elif "show me" in question_lower or "list" in question_lower:
            return self.handle_list_question(question)
        
        else:
            # Fallback to semantic search
            return self.handle_semantic_question(question)
    
    def handle_reference_question(self, question: str) -> str:
        """Handle 'Where are references for X?' type questions"""
        
        # Extract entity name (simple approach - can be improved with NLP)
        words = question.split()
        entity_candidates = []
        
        # Look for capitalized words or words after "for"
        for i, word in enumerate(words):
            if word.lower() == "for" and i + 1 < len(words):
                entity_candidates.append(words[i + 1].strip('?.,'))
            elif word[0].isupper() and len(word) > 2:
                entity_candidates.append(word.strip('?.,'))
        
        if not entity_candidates:
            return "❓ I couldn't identify which entity you're asking about. Please specify the field, object, or class name."
        
        entity = entity_candidates[0]
        references = self.find_references(entity)
        
        if not references:
            return f"❌ No references found for '{entity}'. It might not exist or have no relationships."
        
        # Format response
        response = f"🎯 **References for {entity}:**\n\n"
        
        # Group by relationship type
        by_type = {}
        for ref in references:
            rel_type = ref.relationship_type
            if rel_type not in by_type:
                by_type[rel_type] = []
            by_type[rel_type].append(ref)
        
        # Format each group
        type_icons = {
            'HAS_FIELD': '📋',
            'DISPLAYS_FIELD': '📱',
            'REFERENCES': '💻',
            'USES_OBJECT': '🔗',
            'HAS_LAYOUT': '📄',
            'HAS_TRIGGER': '⚡',
            'DEPENDS_ON': '🔄',
            'CALLS_METHOD': '📞'
        }
        
        for rel_type, refs in by_type.items():
            icon = type_icons.get(rel_type, '🔸')
            response += f"{icon} **{rel_type.replace('_', ' ').title()}:**\n"
            
            for ref in refs:
                if ref.target.lower() == entity.lower():
                    response += f"   • {ref.source} → {ref.target}\n"
                else:
                    response += f"   • {ref.source} → {ref.target}\n"
            response += "\n"
        
        response += f"📊 **Total References:** {len(references)}"
        return response
    
    def handle_dependency_question(self, question: str) -> str:
        """Handle dependency-related questions"""
        # Use semantic search for complex dependency questions
        results = self.semantic_search(question, n_results=5)
        
        if not results:
            return "❓ I couldn't find any dependency information for your question."
        
        response = "🔗 **Dependency Information:**\n\n"
        for result in results:
            source = result.get('from', '')
            target = result.get('to', '')
            rel_type = result.get('type', '')
            response += f"• {source} --{rel_type}--> {target}\n"
        
        return response
    
    def handle_list_question(self, question: str) -> str:
        """Handle list/show questions"""
        results = self.semantic_search(question, n_results=10)
        
        response = "📋 **Here's what I found:**\n\n"
        for result in results:
            description = self.create_relationship_description(result)
            response += f"• {description}\n"
        
        return response
    
    def handle_semantic_question(self, question: str) -> str:
        """Handle general questions using semantic search"""
        results = self.semantic_search(question, n_results=5)
        
        if not results:
            return "❓ I couldn't find relevant information for your question. Try asking about specific fields, objects, or classes."
        
        response = "🔍 **Based on your question, here's what I found:**\n\n"
        for result in results:
            description = self.create_relationship_description(result)
            response += f"• {description}\n"
        
        return response
    
    def get_statistics(self) -> Dict[str, int]:
        """Get chatbot statistics"""
        stats = {}
        for rel in self.relationships:
            rel_type = rel.get('type', 'UNKNOWN')
            stats[rel_type] = stats.get(rel_type, 0) + 1
        
        return stats

def main():
    """Demo the chatbot"""
    print("🚀 Starting Salesforce Metadata Chatbot (No Neo4j Required!)")
    
    # Initialize chatbot
    chatbot = SalesforceMetadataChatbot()
    
    # Show statistics
    stats = chatbot.get_statistics()
    print(f"\n📊 Relationship Statistics:")
    for rel_type, count in sorted(stats.items()):
        print(f"   {rel_type}: {count}")
    
    # Demo questions
    demo_questions = [
        "Where are the references for Industry?",
        "What uses the Account object?",
        "Show me all field relationships",
        "What depends on AccountHandler?"
    ]
    
    print(f"\n🎯 Demo Questions:")
    for question in demo_questions:
        print(f"\n❓ **Question:** {question}")
        answer = chatbot.answer_question(question)
        print(f"🤖 **Answer:**\n{answer}")
        print("-" * 60)

if __name__ == "__main__":
    main()
