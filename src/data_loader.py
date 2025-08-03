import json
import os
from typing import List, Dict, Any


class DataLoader:
    def __init__(self, data_path: str = "data/employees.json"):
        self.data_path = data_path
        self.employees = []

    def load_employees(self) -> List[Dict[str, Any]]:
        """Load employee data from JSON file."""
        try:
            if not os.path.exists(self.data_path):
                raise FileNotFoundError(f"Employee data file not found: {self.data_path}")

            with open(self.data_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.employees = data.get('employees', [])

            print(f"Loaded {len(self.employees)} employees from {self.data_path}")
            return self.employees

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {self.data_path}: {str(e)}")
        except Exception as e:
            raise Exception(f"Error loading employee data: {str(e)}")

    def get_all_employees(self) -> List[Dict[str, Any]]:
        """Get all employees."""
        if not self.employees:
            self.load_employees()
        return self.employees

    def get_employee_by_id(self, employee_id: int) -> Dict[str, Any]:
        """Get employee by ID."""
        if not self.employees:
            self.load_employees()

        for employee in self.employees:
            if employee.get('id') == employee_id:
                return employee
        return None

    def get_employees_by_skill(self, skill: str) -> List[Dict[str, Any]]:
        """Get employees who have a specific skill."""
        if not self.employees:
            self.load_employees()

        skill_lower = skill.lower()
        matching_employees = []

        for employee in self.employees:
            employee_skills = [s.lower() for s in employee.get('skills', [])]
            if skill_lower in employee_skills:
                matching_employees.append(employee)

        return matching_employees

    def get_employees_by_experience(self, min_years: int, max_years: int = None) -> List[Dict[str, Any]]:
        """Get employees by experience range."""
        if not self.employees:
            self.load_employees()

        matching_employees = []
        for employee in self.employees:
            exp_years = employee.get('experience_years', 0)
            if exp_years >= min_years:
                if max_years is None or exp_years <= max_years:
                    matching_employees.append(employee)

        return matching_employees

    def get_available_employees(self) -> List[Dict[str, Any]]:
        """Get only available employees."""
        if not self.employees:
            self.load_employees()

        return [emp for emp in self.employees if emp.get('availability') == 'available']

    def get_employees_by_department(self, department: str) -> List[Dict[str, Any]]:
        """Get employees by department."""
        if not self.employees:
            self.load_employees()

        department_lower = department.lower()
        return [emp for emp in self.employees
                if emp.get('department', '').lower() == department_lower]

    def search_employees_by_project(self, project_keyword: str) -> List[Dict[str, Any]]:
        """Search employees who worked on projects containing keyword."""
        if not self.employees:
            self.load_employees()

        keyword_lower = project_keyword.lower()
        matching_employees = []

        for employee in self.employees:
            projects = employee.get('projects', [])
            for project in projects:
                if keyword_lower in project.lower():
                    matching_employees.append(employee)
                    break  # Don't add same employee multiple times

        return matching_employees

    def get_statistics(self) -> Dict[str, Any]:
        """Get basic statistics about the employee dataset."""
        if not self.employees:
            self.load_employees()

        total_employees = len(self.employees)
        available_count = len(self.get_available_employees())

        # Calculate average experience
        total_exp = sum(emp.get('experience_years', 0) for emp in self.employees)
        avg_experience = total_exp / total_employees if total_employees > 0 else 0

        # Get department distribution
        departments = {}
        for emp in self.employees:
            dept = emp.get('department', 'Unknown')
            departments[dept] = departments.get(dept, 0) + 1

        # Get skill frequency
        skills = {}
        for emp in self.employees:
            for skill in emp.get('skills', []):
                skills[skill] = skills.get(skill, 0) + 1

        return {
            'total_employees': total_employees,
            'available_employees': available_count,
            'busy_employees': total_employees - available_count,
            'average_experience': round(avg_experience, 1),
            'departments': departments,
            'top_skills': dict(sorted(skills.items(), key=lambda x: x[1], reverse=True)[:10])
        }