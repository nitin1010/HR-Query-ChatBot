from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.rag_system import RAGSystem
from src.data_loader import DataLoader

app = FastAPI(
    title="HR Resource Query Chatbot API",
    description="AI-powered HR assistant for finding employees based on natural language queries",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
rag_system = None
data_loader = DataLoader()


class ChatQuery(BaseModel):
    query: str
    top_k: Optional[int] = 5


class ChatResponse(BaseModel):
    response: str
    relevant_employees: List[Dict[str, Any]]
    query: str


class EmployeeSearchQuery(BaseModel):
    skills: Optional[List[str]] = None
    min_experience: Optional[int] = None
    max_experience: Optional[int] = None
    department: Optional[str] = None
    availability: Optional[str] = None
    project_keyword: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize RAG system on startup."""
    global rag_system
    try:
        print("Initializing HR Chatbot...")
        rag_system = RAGSystem()

        # Load employee data and embeddings
        rag_system.initialize_system()

        # Try to load Mistral model (this might take time)
        try:
            rag_system.load_mistral_model()
            print("RAG system fully initialized with Mistral!")
        except Exception as e:
            print(f"Warning: Could not load Mistral model: {e}")
            print("The system will work with embeddings only.")

    except Exception as e:
        print(f"Error during startup: {e}")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "HR Resource Query Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat - Post natural language queries",
            "search": "/employees/search - Search employees with filters",
            "employees": "/employees - Get all employees",
            "stats": "/employees/stats - Get dataset statistics"
        }
    }


@app.post("/chat", response_model=ChatResponse)
async def chat_query(query: ChatQuery):
    """Process natural language HR queries using RAG system."""
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")

    try:
        result = rag_system.process_query(query.query)
        return ChatResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.get("/employees/search")
async def search_employees(
        skills: Optional[str] = None,
        min_experience: Optional[int] = None,
        max_experience: Optional[int] = None,
        department: Optional[str] = None,
        availability: Optional[str] = None,
        project_keyword: Optional[str] = None
):
    """Search employees with specific filters."""
    try:
        employees = data_loader.get_all_employees()

        # Apply filters
        if skills:
            skill_list = [s.strip() for s in skills.split(',')]
            filtered_employees = []
            for emp in employees:
                emp_skills_lower = [skill.lower() for skill in emp.get('skills', [])]
                if any(skill.lower() in emp_skills_lower for skill in skill_list):
                    filtered_employees.append(emp)
            employees = filtered_employees

        if min_experience is not None:
            employees = [emp for emp in employees if emp.get('experience_years', 0) >= min_experience]

        if max_experience is not None:
            employees = [emp for emp in employees if emp.get('experience_years', 0) <= max_experience]

        if department:
            employees = [emp for emp in employees if emp.get('department', '').lower() == department.lower()]

        if availability:
            employees = [emp for emp in employees if emp.get('availability', '').lower() == availability.lower()]

        if project_keyword:
            filtered_employees = []
            for emp in employees:
                projects = emp.get('projects', [])
                if any(project_keyword.lower() in project.lower() for project in projects):
                    filtered_employees.append(emp)
            employees = filtered_employees

        return {"employees": employees, "count": len(employees)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching employees: {str(e)}")


@app.get("/employees")
async def get_all_employees():
    """Get all employees."""
    try:
        employees = data_loader.get_all_employees()
        return {"employees": employees, "count": len(employees)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching employees: {str(e)}")


@app.get("/employees/{employee_id}")
async def get_employee(employee_id: int):
    """Get specific employee by ID."""
    try:
        employee = data_loader.get_employee_by_id(employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        return employee
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching employee: {str(e)}")


@app.get("/employees/stats")
async def get_employee_stats():
    """Get statistics about the employee dataset."""
    try:
        stats = data_loader.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating statistics: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "rag_system_loaded": rag_system is not None,
        "model_loaded": rag_system.model is not None if rag_system else False
    }