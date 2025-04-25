import os
import re
from groq import Groq

class SQLTranslator:
    def __init__(self):
        self.table_schema = {
            "users": ["id", "name"],
            # Add other tables and their columns here as you create them
        }
        
        # Initialize Groq client
        self.groq_client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
        )
        
    def translate(self, natural_language_query):
        """Convert natural language query to SQL using Groq LLM"""
        try:
            # Create a prompt with context about the database schema
            schema_context = self._get_schema_context()
            
            if not schema_context:
                return "Error: No schema information available. Please ensure you have selected a database and it contains tables."
            
            prompt = f"""
You are a helpful and secure SQL assistant. Your task is to convert natural language into safe and correct MySQL queries that follow standard CRUD patterns.

DATABASE SCHEMA:
{schema_context}

RULES:
- Generate only ONE SQL query - no extra text, comments, or explanations
- Do NOT generate DROP, TRUNCATE, or ALTER statements
- Do NOT generate DELETE or UPDATE queries without a WHERE clause
- Do NOT use * in SELECT statements; select specific columns
- LIMIT large result sets (default to LIMIT 100 if not specified)
- Ensure the query is syntactically correct for MySQL
- Use the exact table and column names as shown in the schema

USER REQUEST: {natural_language_query}

SQL QUERY:
"""
            
            # Get response from Groq
            if not os.environ.get("GROQ_API_KEY"):
                return "Error: GROQ_API_KEY environment variable is not set. Please set it in your .env file."
                
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.1,  # Low temperature for more deterministic output
                max_tokens=200,   # Limit response length
            )
            
            sql_query = chat_completion.choices[0].message.content.strip()
            
            # Validate the SQL query for safety
            if self._is_unsafe_query(sql_query):
                return "Error: Generated query contains unsafe operations. Please rephrase your request."
            
            return sql_query
            
        except Exception as e:
            return f"Error: Failed to generate SQL query: {str(e)}"
    
    def _get_schema_context(self):
        """Generate a string representation of the database schema"""
        if not self.table_schema:
            return ""
            
        schema_str = "Current Database Schema:\n\n"
        for table, columns in self.table_schema.items():
            schema_str += f"Table: `{table}`\n"
            schema_str += "Columns:\n"
            for column in columns:
                schema_str += f"  - {column}\n"
            schema_str += "\n"
        
        return schema_str
    
    def _is_unsafe_query(self, query):
        """Check if the query contains unsafe operations"""
        query = query.strip().upper()
        
        # Check for unsafe operations
        unsafe_operations = ["DROP", "TRUNCATE", "ALTER"]
        for op in unsafe_operations:
            if op in query:
                return True
        
        # Check for UPDATE or DELETE without WHERE
        if query.startswith("UPDATE") and "WHERE" not in query:
            return True
        
        if query.startswith("DELETE") and "WHERE" not in query:
            return True
        
        return False
    
    def update_schema(self, table_name, columns):
        """Update the table schema with new tables or columns"""
        self.table_schema[table_name] = columns
        
    def get_table_schema(self):
        """Return the current table schema"""
        return self.table_schema 