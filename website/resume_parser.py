import re

def parse_resume_text(text):
    """
    Parse raw resume text and extract structured data.
    Returns a dictionary matching the required JSON format.
    """
    
    lines = text.strip().split('\n')
    resume = {
        "name": "",
        "title": "",
        "email": "",
        "phone": "",
        "portfolio_link": "",
        "linkedin_link": "",
        "github_link": "",
        "additional_link": "",
        "summary": "",
        "education": [],
        "experience": [],
        "projects": [],
        "skills": [],
        "tools": [],
        "certifications": []
    }
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        resume["email"] = emails[0]
    
    # Extract phone (Indian format primarily)
    phone_pattern = r'(\+91[\s-]?)?[6-9]\d{9}|\d{10}'
    phones = re.findall(phone_pattern, text)
    if phones:
        resume["phone"] = ''.join(phones[0]) if isinstance(phones[0], tuple) else phones[0]
        resume["phone"] = re.sub(r'[^\d]', '', resume["phone"])[-10:]  # Keep last 10 digits
    
    # Extract LinkedIn
    linkedin_pattern = r'(https?://)?([a-z]{2,3}\.)?linkedin\.com/\S+'
    linkedin = re.search(linkedin_pattern, text, re.IGNORECASE)
    if linkedin:
        resume["linkedin_link"] = linkedin.group(0).split()[0]
    
    # Extract GitHub
    github_pattern = r'(https?://)?github\.com/\S+'
    github = re.search(github_pattern, text, re.IGNORECASE)
    if github:
        resume["github_link"] = github.group(0).split()[0]
    
    # Extract portfolio/website
    portfolio_pattern = r'(https?://)?[\w\-]+\.(dev|com|io|in|me|tech)/?\S*'
    portfolios = re.findall(portfolio_pattern, text, re.IGNORECASE)
    for port in portfolios:
        url = port[0] + port[1] if isinstance(port, tuple) else port
        if 'linkedin' not in url.lower() and 'github' not in url.lower():
            resume["portfolio_link"] = url
            break
    
    # Extract name (first non-empty line, usually)
    for line in lines[:5]:  # Check first 5 lines
        line = line.strip()
        if line and len(line.split()) <= 5 and not re.search(r'[@\d]', line):
            resume["name"] = line
            break
    
    # Parse sections
    current_section = None
    section_content = []
    
    section_keywords = {
        'summary': ['summary', 'about', 'profile', 'objective'],
        'education': ['education', 'academic', 'qualification'],
        'experience': ['experience', 'work', 'employment', 'internship'],
        'projects': ['projects', 'portfolio'],
        'skills': ['skills', 'technical skills', 'expertise'],
        'tools': ['tools', 'technologies'],
        'certifications': ['certifications', 'certificates', 'courses']
    }
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if line is a section header
        line_lower = line.lower()
        is_header = False
        
        for section, keywords in section_keywords.items():
            if any(keyword in line_lower for keyword in keywords):
                # Save previous section
                if current_section and section_content:
                    _process_section(resume, current_section, section_content)
                
                current_section = section
                section_content = []
                is_header = True
                break
        
        if not is_header and current_section:
            section_content.append(line)
    
    # Process last section
    if current_section and section_content:
        _process_section(resume, current_section, section_content)
    
    # Fallback: if name not found, use first line
    if not resume["name"] and lines:
        resume["name"] = lines[0].strip()
    
    # Ensure at least one entry in required arrays
    if not resume["education"]:
        resume["education"].append({
            "degree": "Please fill in your degree",
            "institution": "Please fill in your institution",
            "batch": "2020 - 2024"
        })
    
    if not resume["experience"]:
        resume["experience"].append({
            "company": "Please fill in your experience",
            "description": "Please describe your role and achievements"
        })
    
    if not resume["projects"]:
        resume["projects"].append({
            "title": "Please fill in your project",
            "bullets": ["Please add project details"]
        })
    
    if not resume["certifications"]:
        resume["certifications"].append({
            "name": "Please fill in certification",
            "description": "Please add description"
        })
    
    if not resume["skills"]:
        resume["skills"].append("Please add your skills")
    
    if not resume["tools"]:
        resume["tools"].append("Please add your tools")
    
    return resume

def _process_section(resume, section, content):
    """Process content for a specific section"""
    
    if section == 'summary':
        resume["summary"] = ' '.join(content).strip()
    
    elif section == 'education':
        # Group lines into education entries (simple heuristic)
        for i in range(0, len(content), 3):
            degree = content[i] if i < len(content) else ""
            institution = content[i+1] if i+1 < len(content) else ""
            batch = content[i+2] if i+2 < len(content) else ""
            
            if degree:
                resume["education"].append({
                    "degree": degree,
                    "institution": institution,
                    "batch": batch
                })
    
    elif section == 'experience':
        # Each experience is company line + description lines
        current_exp = None
        for line in content:
            # If line looks like a company/role (contains - or @ or has capital letters)
            if '-' in line or '@' in line or re.search(r'[A-Z][a-z]+ [A-Z]', line):
                if current_exp:
                    resume["experience"].append(current_exp)
                current_exp = {
                    "company": line,
                    "description": ""
                }
            elif current_exp:
                current_exp["description"] += " " + line
        
        if current_exp:
            resume["experience"].append(current_exp)
    
    elif section == 'projects':
        # Each project is title + bullet points
        current_project = None
        for line in content:
            # If line doesn't start with bullet, it's likely a title
            if not line.startswith(('•', '-', '*', '→')):
                if current_project:
                    resume["projects"].append(current_project)
                current_project = {
                    "title": line,
                    "bullets": []
                }
            elif current_project:
                # Remove bullet character
                bullet = re.sub(r'^[•\-\*→]\s*', '', line)
                current_project["bullets"].append(bullet)
        
        if current_project:
            resume["projects"].append(current_project)
    
    elif section == 'skills':
        # Each line is a skill entry
        resume["skills"] = [line for line in content if line]
    
    elif section == 'tools':
        # Each line or comma-separated values
        for line in content:
            if ',' in line:
                resume["tools"].extend([t.strip() for t in line.split(',')])
            else:
                resume["tools"].append(line)
    
    elif section == 'certifications':
        # Pairs of lines: name + description
        for i in range(0, len(content), 2):
            name = content[i] if i < len(content) else ""
            desc = content[i+1] if i+1 < len(content) else ""
            
            if name:
                resume["certifications"].append({
                    "name": name,
                    "description": desc
                })
