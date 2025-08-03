from llama_cpp import Llama
import re
import sys
import os

# Add src directory to path if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from embeddings import EmbeddingSystem


class RAGSystem:
    def __init__(self, model_path="models/"):
        """Initialize RAG system with GGUF Mistral model and embedding system."""
        self.embedding_system = EmbeddingSystem()
        self.model_path = model_path
        self.model = None

    def load_mistral_model(self, model_file="mistral-7b-instruct-v0.1.Q4_K_M.gguf"):
        """Load Mistral GGUF model for text generation."""
        model_filepath = os.path.join(self.model_path, model_file)

        if not os.path.exists(model_filepath):
            raise FileNotFoundError(f"Model file not found: {model_filepath}")

        print(f"Loading Mistral GGUF model from {model_filepath}...")

        self.model = Llama(
            model_path=model_filepath,
            n_ctx=4096,  # Context window
            n_threads=8,  # Number of CPU threads
            n_gpu_layers=0,  # Use CPU only (set to -1 for GPU)
            verbose=False
        )

        print("Mistral GGUF model loaded successfully!")

    def initialize_system(self, data_path="data/employees.json"):
        """Initialize the complete RAG system."""
        # Load employee data and generate embeddings
        self.embedding_system.load_employee_data(data_path)
        self.embedding_system.generate_embeddings()
        print("Employee embeddings generated!")

    def extract_query_requirements(self, query):
        """Extract requirements from natural language query."""
        requirements = {
            'skills': [],
            'min_experience': 0,
            'project_type': None,
            'availability_required': True
        }

        # Extract experience requirements
        exp_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(?:with\s*)?(\d+)\+?\s*years?',
            r'experienced?\s*(?:with\s*)?(\d+)\+?\s*years?'
        ]

        for pattern in exp_patterns:
            match = re.search(pattern, query.lower())
            if match:
                requirements['min_experience'] = int(match.group(1))
                break

        # Extract skills/technologies
        tech_keywords = [
            'python', 'java', 'javascript', 'react', 'vue', 'angular', 'node.js',
            'aws', 'docker', 'kubernetes', 'tensorflow', 'pytorch', 'ml', 'ai',
            'machine learning', 'deep learning', 'nlp', 'computer vision',
            'flutter', 'react native', 'mobile', 'ios', 'android',
            'sql', 'postgresql', 'mongodb', 'redis', 'microservices',
            'devops', 'ci/cd', 'terraform', 'go', 'rust', 'c++', 'c#'
        ]

        query_lower = query.lower()
        for tech in tech_keywords:
            if tech in query_lower:
                requirements['skills'].append(tech)

        # Extract project types
        if any(word in query_lower for word in ['healthcare', 'medical', 'health']):
            requirements['project_type'] = 'healthcare'
        elif any(word in query_lower for word in ['mobile', 'app', 'ios', 'android']):
            requirements['project_type'] = 'mobile'
        elif any(word in query_lower for word in ['web', 'website', 'frontend']):
            requirements['project_type'] = 'web'

        return requirements

    def retrieve_relevant_employees(self, query, top_k=5):
        """Retrieve relevant employees using semantic search."""
        # Get semantic search results
        candidates = self.embedding_system.search_employees(query, top_k=10)

        # Extract query requirements
        requirements = self.extract_query_requirements(query)

        # Apply filters
        if requirements['availability_required']:
            candidates = self.embedding_system.filter_by_availability(candidates)

        if requirements['min_experience'] > 0:
            candidates = self.embedding_system.filter_by_experience(
                candidates, min_years=requirements['min_experience']
            )

        if requirements['skills']:
            candidates = self.embedding_system.filter_by_skills(
                candidates, requirements['skills']
            )

        return candidates[:top_k]

    def create_prompt(self, query, relevant_employees):
        """Create prompt for Mistral to generate response."""
        if not relevant_employees:
            return f"""[INST] You are an HR assistant. A user asked: "{query}"

Unfortunately, no employees match these criteria. Please provide a helpful response explaining that no matches were found and suggest alternative approaches.

Respond in a professional, helpful tone. [/INST]"""

        employees_context = ""
        for i, emp in enumerate(relevant_employees, 1):
            skills_text = ", ".join(emp['skills'])
            projects_text = ", ".join(emp['projects'])

            employees_context += f"""
{i}. **{emp['name']}** ({emp['role']})
   - Experience: {emp['experience_years']} years
   - Skills: {skills_text}
   - Key Projects: {projects_text}
   - Availability: {emp['availability']}
   - Department: {emp['department']}
"""

        prompt = f"""[INST] You are an intelligent HR assistant helping to find the right employees for projects. 

User Query: "{query}"

Based on the query, here are the most relevant employees:
{employees_context}

Please provide a natural, conversational response that:
1. Acknowledges the user's request
2. Presents the best candidates with specific reasons why they're good fits
3. Highlights relevant experience and skills
4. Mentions availability status
5. Offers to provide more details if needed

Keep the response professional but friendly, and focus on the most relevant matches first. [/INST]"""

        return prompt

    def generate_response(self, prompt, max_tokens=512):
        """Generate response using Mistral GGUF model."""
        if self.model is None:
            raise ValueError("Mistral model not loaded. Call load_mistral_model() first.")

        response = self.model(
            prompt,
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.9,
            stop=["[/INST]", "</s>"],
            echo=False
        )

        return response['choices'][0]['text'].strip()

    def process_query(self, query):
        """Complete RAG pipeline: Retrieve, Augment, Generate."""
        try:
            # Step 1: Retrieve relevant employees
            relevant_employees = self.retrieve_relevant_employees(query)

            # Step 2: Augment - create context-rich prompt
            prompt = self.create_prompt(query, relevant_employees)

            # Step 3: Generate natural language response
            if self.model is not None:
                response = self.generate_response(prompt)
            else:
                # Fallback to template response if model not loaded
                if relevant_employees:
                    response = f"Found {len(relevant_employees)} relevant employees for your query. Here are the top matches:\n\n"
                    for emp in relevant_employees:
                        response += f"• {emp['name']} - {emp['role']} with {emp['experience_years']} years experience\n"
                else:
                    response = "No employees found matching your criteria. Please try a different query."

            return {
                "response": response,
                "relevant_employees": relevant_employees,
                "query": query
            }

        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error processing your query: {str(e)}",
                "relevant_employees": [],
                "query": query
            }