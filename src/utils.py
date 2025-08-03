import os
import json
import re
from typing import List, Dict, Any, Optional


def ensure_directory_exists(directory_path: str):
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def save_json(data: Dict[str, Any], filepath: str):
    """Save data to JSON file."""
    ensure_directory_exists(os.path.dirname(filepath))
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(filepath: str) -> Dict[str, Any]:
    """Load data from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters except common punctuation
    text = re.sub(r'[^\w\s\.,!?-]', '', text)
    return text.strip()


def extract_skills_from_text(text: str) -> List[str]:
    """Extract potential skills/technologies from text."""
    # Common programming languages and technologies
    tech_patterns = [
        r'\bpython\b', r'\bjava\b', r'\bjavascript\b', r'\breact\b', r'\bnode\.js\b',
        r'\baws\b', r'\bdocker\b', r'\bkubernetes\b', r'\btensorflow\b', r'\bpytorch\b',
        r'\bmachine learning\b', r'\bml\b', r'\bai\b', r'\bdeep learning\b',
        r'\bsql\b', r'\bpostgresql\b', r'\bmongodb\b', r'\bredis\b',
        r'\bflutter\b', r'\breact native\b', r'\bmobile\b', r'\bios\b', r'\bandroid\b',
        r'\bdevops\b', r'\bci/cd\b', r'\bterraform\b', r'\bgo\b', r'\brust\b', r'\bc\+\+\b'
    ]

    text_lower = text.lower()
    found_skills = []

    for pattern in tech_patterns:
        if re.search(pattern, text_lower):
            # Extract the actual matched text
            match = re.search(pattern, text_lower)
            if match:
                found_skills.append(match.group().replace('\\b', ''))

    return list(set(found_skills))  # Remove duplicates


def extract_experience_years(text: str) -> Optional[int]:
    """Extract experience years from text."""
    patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'(?:with\s*)?(\d+)\+?\s*years?',
        r'experienced?\s*(?:with\s*)?(\d+)\+?\s*years?'
    ]

    text_lower = text.lower()
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            return int(match.group(1))

    return None


def calculate_similarity_threshold(scores: List[float], percentile: float = 0.7) -> float:
    """Calculate similarity threshold based on score distribution."""
    if not scores:
        return 0.0

    sorted_scores = sorted(scores, reverse=True)
    index = int(len(sorted_scores) * percentile)
    return sorted_scores[min(index, len(sorted_scores) - 1)]


def format_employee_summary(employee: Dict[str, Any]) -> str:
    """Format employee data into a readable summary."""
    name = employee.get('name', 'Unknown')
    role = employee.get('role', 'Unknown Role')
    department = employee.get('department', 'Unknown Department')
    experience = employee.get('experience_years', 0)
    skills = ', '.join(employee.get('skills', [])[:5])  # Show top 5 skills
    availability = employee.get('availability', 'unknown')

    summary = f"{name} - {role} in {department}\n"
    summary += f"Experience: {experience} years\n"
    summary += f"Key Skills: {skills}\n"
    summary += f"Status: {availability.title()}\n"

    return summary


def validate_employee_data(employee: Dict[str, Any]) -> bool:
    """Validate employee data structure."""
    required_fields = ['id', 'name', 'skills', 'experience_years', 'projects', 'availability']

    for field in required_fields:
        if field not in employee:
            return False

    # Validate data types
    if not isinstance(employee['id'], int):
        return False
    if not isinstance(employee['name'], str):
        return False
    if not isinstance(employee['skills'], list):
        return False
    if not isinstance(employee['experience_years'], int) or employee['experience_years'] < 0:
        return False
    if not isinstance(employee['projects'], list):
        return False
    if employee['availability'] not in ['available', 'busy']:
        return False

    return True


def create_search_index(employees: List[Dict[str, Any]]) -> Dict[str, List[int]]:
    """Create a simple search index for faster lookups."""
    index = {}

    for i, employee in enumerate(employees):
        # Index by skills
        for skill in employee.get('skills', []):
            skill_lower = skill.lower()
            if skill_lower not in index:
                index[skill_lower] = []
            index[skill_lower].append(i)

        # Index by department
        dept = employee.get('department', '').lower()
        if dept:
            if dept not in index:
                index[dept] = []
            index[dept].append(i)

        # Index by role
        role = employee.get('role', '').lower()
        if role:
            if role not in index:
                index[role] = []
            index[role].append(i)

    return index


def filter_employees_by_index(employees: List[Dict[str, Any]],
                              search_index: Dict[str, List[int]],
                              keywords: List[str]) -> List[Dict[str, Any]]:
    """Filter employees using search index."""
    if not keywords:
        return employees

    relevant_indices = set()

    for keyword in keywords:
        keyword_lower = keyword.lower()
        if keyword_lower in search_index:
            relevant_indices.update(search_index[keyword_lower])

    return [employees[i] for i in relevant_indices if i < len(employees)]


def log_query(query: str, results_count: int, response_time: float, log_file: str = "logs/queries.log"):
    """Log query for analytics."""
    import datetime

    log_entry = {
        'timestamp': datetime.datetime.now().isoformat(),
        'query': query,
        'results_count': results_count,
        'response_time_ms': round(response_time * 1000, 2)
    }

    ensure_directory_exists(os.path.dirname(log_file))

    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry) + '\n')