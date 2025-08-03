from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
import os


class EmbeddingSystem:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        """Initialize the embedding system with sentence transformer model."""
        self.model = SentenceTransformer(model_name)
        self.employee_embeddings = None
        self.employees_data = None

    def load_employee_data(self, data_path="data/employees.json"):
        """Load employee data from JSON file."""
        with open(data_path, 'r') as f:
            data = json.load(f)
        self.employees_data = data['employees']
        return self.employees_data

    def create_employee_text(self, employee):
        """Create searchable text representation of an employee."""
        skills_text = ", ".join(employee['skills'])
        projects_text = ", ".join(employee['projects'])

        text = f"""
        Name: {employee['name']}
        Role: {employee['role']}
        Department: {employee['department']}
        Experience: {employee['experience_years']} years
        Skills: {skills_text}
        Projects: {projects_text}
        Availability: {employee['availability']}
        """
        return text.strip()

    def generate_embeddings(self):
        """Generate embeddings for all employees."""
        if self.employees_data is None:
            raise ValueError("Employee data not loaded. Call load_employee_data() first.")

        employee_texts = [self.create_employee_text(emp) for emp in self.employees_data]
        self.employee_embeddings = self.model.encode(employee_texts)
        return self.employee_embeddings

    def search_employees(self, query, top_k=5):
        """Search for employees based on query using semantic similarity."""
        if self.employee_embeddings is None:
            raise ValueError("Embeddings not generated. Call generate_embeddings() first.")

        # Generate query embedding
        query_embedding = self.model.encode([query])

        # Calculate cosine similarity
        similarities = cosine_similarity(query_embedding, self.employee_embeddings)[0]

        # Get top k employees
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            employee = self.employees_data[idx].copy()
            employee['similarity_score'] = float(similarities[idx])
            results.append(employee)

        return results

    def filter_by_availability(self, employees, available_only=True):
        """Filter employees by availability."""
        if available_only:
            return [emp for emp in employees if emp['availability'] == 'available']
        return employees

    def filter_by_experience(self, employees, min_years=0, max_years=None):
        """Filter employees by experience years."""
        filtered = [emp for emp in employees if emp['experience_years'] >= min_years]
        if max_years:
            filtered = [emp for emp in filtered if emp['experience_years'] <= max_years]
        return filtered

    def filter_by_skills(self, employees, required_skills):
        """Filter employees who have all required skills."""
        if not required_skills:
            return employees

        filtered = []
        for emp in employees:
            emp_skills_lower = [skill.lower() for skill in emp['skills']]
            required_skills_lower = [skill.lower() for skill in required_skills]

            if all(skill in emp_skills_lower for skill in required_skills_lower):
                filtered.append(emp)

        return filtered