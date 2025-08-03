from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class Employee(BaseModel):
    id: int
    name: str
    skills: List[str]
    experience_years: int = Field(ge=0, description="Years of experience")
    projects: List[str]
    availability: str = Field(description="available or busy")
    department: str
    role: str
    similarity_score: Optional[float] = Field(None, description="Similarity score from search")

class ChatQuery(BaseModel):
    query: str = Field(description="Natural language query about employee search")
    top_k: Optional[int] = Field(default=5, ge=1, le=20, description="Number of top results to return")

class ChatResponse(BaseModel):
    response: str = Field(description="Natural language response from the AI")
    relevant_employees: List[Dict[str, Any]] = Field(description="List of relevant employees found")
    query: str = Field(description="Original query")

class EmployeeSearchQuery(BaseModel):
    skills: Optional[List[str]] = Field(None, description="Required skills")
    min_experience: Optional[int] = Field(None, ge=0, description="Minimum years of experience")
    max_experience: Optional[int] = Field(None, ge=0, description="Maximum years of experience")
    department: Optional[str] = Field(None, description="Department name")
    availability: Optional[str] = Field(None, description="available or busy")
    project_keyword: Optional[str] = Field(None, description="Keyword to search in projects")

class EmployeeSearchResponse(BaseModel):
    employees: List[Employee]
    count: int = Field(description="Number of employees found")

class HealthCheck(BaseModel):
    status: str
    rag_system_loaded: bool
    model_loaded: bool

class Statistics(BaseModel):
    total_employees: int
    available_employees: int
    busy_employees: int
    average_experience: float
    departments: Dict[str, int]
    top_skills: Dict[str, int]