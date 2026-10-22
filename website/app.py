from flask import Flask, render_template_string, request, jsonify, send_file
import json
import subprocess
import os
from datetime import datetime
from resume_parser import parse_resume_text
from database import init_database, save_resume, get_resume_stats

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ARCHIVE_FOLDER = 'archive'  # Store all generated PDFs here
CPP_ENGINE_PATH = os.path.join('..', 'engine', 'resume_engine.exe')  # Change to 'resume_engine' for Linux/Mac

# Create necessary folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(ARCHIVE_FOLDER, exist_ok=True)

# Initialize database
init_database()

# HTML Template (embedded in Python file)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ATS Resume Builder</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            color: #1a1a1a;
            line-height: 1.6;
            padding: 20px;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: #ffffff;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }

        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            border-bottom: 2px solid #e0e0e0;
        }

        .tab-btn {
            padding: 12px 30px;
            border: none;
            background: transparent;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            color: #666;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }

        .tab-btn:hover {
            color: #1a1a1a;
        }

        .tab-btn.active {
            color: #1a1a1a;
            border-bottom-color: #1a1a1a;
        }

        .tab-content {
            display: block;
        }

        header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid #1a1a1a;
        }

        h1 {
            font-size: 2.5em;
            color: #1a1a1a;
            margin-bottom: 10px;
        }

        .tagline {
            font-size: 1.1em;
            color: #666;
        }

        .section {
            margin-bottom: 30px;
        }

        .section h2 {
            font-size: 1.3em;
            color: #1a1a1a;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 1px solid #e0e0e0;
        }

        .form-group {
            margin-bottom: 15px;
        }

        label {
            display: block;
            margin-bottom: 5px;
            color: #333;
            font-weight: 500;
        }

        .required {
            color: #666;
            font-size: 0.9em;
        }

        input[type="text"],
        input[type="email"],
        input[type="tel"],
        input[type="url"],
        textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            background: #fafafa;
            transition: all 0.3s;
        }

        input:focus,
        textarea:focus {
            outline: none;
            border-color: #1a1a1a;
            background: #fff;
        }

        textarea {
            resize: vertical;
            min-height: 80px;
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }

        .dynamic-item {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 10px;
            border-left: 3px solid #1a1a1a;
        }

        button {
            padding: 12px 25px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
        }

        .btn-add {
            background: #1a1a1a;
            color: #fff;
            margin-top: 10px;
        }

        .btn-add:hover {
            background: #333;
        }

        .btn-remove {
            background: #666;
            color: #fff;
            margin-top: 10px;
            font-size: 12px;
            padding: 8px 15px;
        }

        .btn-remove:hover {
            background: #888;
        }

        .btn-submit {
            background: #1a1a1a;
            color: #fff;
            padding: 15px 40px;
            font-size: 16px;
            display: block;
            margin: 30px auto 0;
        }

        .btn-submit:hover {
            background: #333;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }

        .loading {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }

        .loading-content {
            text-align: center;
            color: #fff;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #1a1a1a;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .success {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            justify-content: center;
            align-items: center;
            z-index: 1001;
        }

        .success-box {
            background: #fff;
            padding: 40px;
            border-radius: 8px;
            text-align: center;
            max-width: 400px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }

        .success-box-large {
            background: #fff;
            padding: 30px;
            border-radius: 8px;
            text-align: center;
            max-width: 900px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }

        .pdf-preview {
            border: 2px solid #e0e0e0;
            border-radius: 4px;
            background: #f9f9f9;
            margin: 20px 0;
        }

        .pdf-preview embed {
            border-radius: 4px;
        }

        .success-box h2 {
            color: #1a1a1a;
            margin-bottom: 20px;
        }

        .btn-download {
            background: #1a1a1a;
            color: #fff;
            padding: 12px 30px;
            text-decoration: none;
            display: inline-block;
            margin: 10px 5px;
            border-radius: 4px;
        }

        .btn-download:hover {
            background: #333;
        }

        small {
            display: block;
            color: #888;
            font-size: 0.85em;
            margin-top: 5px;
        }

        @media (max-width: 768px) {
            .container {
                padding: 20px;
            }

            .form-row {
                grid-template-columns: 1fr;
            }

            h1 {
                font-size: 1.8em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>ATS Resume Builder</h1>
            <p class="tagline">Build your professional, ATS-friendly resume</p>
        </header>

        <!-- Tab Navigation -->
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('form')">Form Input</button>
            <button class="tab-btn" onclick="switchTab('smart')">Smart Paste</button>
            <button class="tab-btn" onclick="switchTab('json')">JSON Paste</button>
        </div>

        <!-- Smart Paste Tab -->
        <div id="smartTab" class="tab-content" style="display: none;">
            <div class="section">
                <h2>🪄 Smart Paste - Just Copy & Paste Your Resume!</h2>
                <p style="color: #666; margin-bottom: 15px;">
                    Copy your entire resume from anywhere (Word, PDF, website) and paste it here. 
                    Our parser will automatically extract your information!
                </p>
                <p style="color: #888; font-size: 0.9em; margin-bottom: 15px;">
                    💡 Tip: Works best with clearly labeled sections like "Education", "Experience", "Skills", etc.
                </p>
                <textarea id="smartInput" rows="20" style="font-family: inherit; font-size: 13px;" placeholder="Paste your complete resume here...

Example:
John Doe
john@example.com | 9876543210
https://linkedin.com/in/johndoe | https://github.com/johndoe

SUMMARY
Software developer with 3 years experience...

EDUCATION
B.Tech Computer Science
ABC University
2019 - 2023

EXPERIENCE
Software Developer - XYZ Tech
Developed web applications using React...

PROJECTS
E-commerce Website
- Built using MERN stack
- Integrated payment gateway

SKILLS
JavaScript, Python, React, Node.js

TOOLS
Git, Docker, VS Code

CERTIFICATIONS
AWS Certified Developer
Training in cloud development"></textarea>
                <button type="button" class="btn-submit" onclick="parseSmartInput()">🪄 Parse & Generate Resume</button>
                <p style="color: #888; font-size: 0.85em; margin-top: 10px; text-align: center;">
                    After parsing, you can review and edit the extracted data before generating
                </p>
            </div>
        </div>

        <!-- JSON Input Tab -->
        <div id="jsonTab" class="tab-content" style="display: none;">
            <div class="section">
                <h2>Paste Your Resume JSON</h2>
                <p style="color: #666; margin-bottom: 15px;">
                    Paste your complete resume data in JSON format below. 
                    <a href="#" onclick="showSampleJSON(); return false;" style="color: #1a1a1a; text-decoration: underline;">View sample format</a>
                </p>
                <textarea id="jsonInput" rows="20" style="font-family: 'Courier New', monospace; font-size: 12px;" placeholder='{\n  "name": "Your Name",\n  "email": "your.email@example.com",\n  ...\n}'></textarea>
                <button type="button" class="btn-submit" onclick="generateFromJSON()">Generate Resume from JSON</button>
            </div>
        </div>

        <!-- Form Input Tab -->
        <form id="resumeForm" class="tab-content">
            <!-- Personal Information -->
            <div class="section">
                <h2>Personal Information</h2>
                
                <div class="form-group">
                    <label>Full Name <span class="required">*</span></label>
                    <input type="text" id="name" required>
                </div>

                <div class="form-group">
                    <label>Professional Title (Optional)</label>
                    <input type="text" id="title">
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label>Email <span class="required">*</span></label>
                        <input type="email" id="email" required>
                    </div>

                    <div class="form-group">
                        <label>Phone <span class="required">*</span></label>
                        <input type="tel" id="phone" required>
                    </div>
                </div>
            </div>

            <!-- Links -->
            <div class="section">
                <h2>Links (Optional)</h2>
                
                <div class="form-row">
                    <div class="form-group">
                        <label>Portfolio</label>
                        <input type="url" id="portfolio_link">
                    </div>

                    <div class="form-group">
                        <label>LinkedIn</label>
                        <input type="url" id="linkedin_link">
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label>GitHub</label>
                        <input type="url" id="github_link">
                    </div>

                    <div class="form-group">
                        <label>Additional Link</label>
                        <input type="url" id="additional_link">
                    </div>
                </div>
            </div>

            <!-- Summary -->
            <div class="section">
                <h2>Professional Summary <span class="required">*</span></h2>
                <div class="form-group">
                    <textarea id="summary" rows="4" required></textarea>
                    <small>Brief professional summary highlighting your key skills</small>
                </div>
            </div>

            <!-- Education -->
            <div class="section">
                <h2>Education <span class="required">*</span></h2>
                <div id="educationContainer">
                    <div class="dynamic-item education-item">
                        <div class="form-group">
                            <label>Degree</label>
                            <input type="text" class="education-degree" required>
                        </div>
                        <div class="form-group">
                            <label>Institution</label>
                            <input type="text" class="education-institution" required>
                        </div>
                        <div class="form-group">
                            <label>Batch</label>
                            <input type="text" class="education-batch" required>
                        </div>
                    </div>
                </div>
                <button type="button" class="btn-add" onclick="addEducation()">+ Add Education</button>
            </div>

            <!-- Experience -->
            <div class="section">
                <h2>Experience <span class="required">*</span></h2>
                <div id="experienceContainer">
                    <div class="dynamic-item experience-item">
                        <div class="form-group">
                            <label>Company / Role</label>
                            <input type="text" class="experience-company" required>
                        </div>
                        <div class="form-group">
                            <label>Description</label>
                            <textarea class="experience-description" rows="3" required></textarea>
                        </div>
                    </div>
                </div>
                <button type="button" class="btn-add" onclick="addExperience()">+ Add Experience</button>
            </div>

            <!-- Projects -->
            <div class="section">
                <h2>Projects <span class="required">*</span></h2>
                <div id="projectsContainer">
                    <div class="dynamic-item project-item">
                        <div class="form-group">
                            <label>Project Title</label>
                            <input type="text" class="project-title" required>
                        </div>
                        <div class="form-group">
                            <label>Bullet Points (one per line)</label>
                            <textarea class="project-bullets" rows="4" required></textarea>
                            <small>Each line becomes a bullet point</small>
                        </div>
                        <button type="button" class="btn-remove" onclick="removeProject(this)">Remove</button>
                    </div>
                </div>
                <button type="button" class="btn-add" onclick="addProject()">+ Add Project</button>
            </div>

            <!-- Skills -->
            <div class="section">
                <h2>Skills <span class="required">*</span></h2>
                <div class="form-group">
                    <textarea id="skills" rows="4" required></textarea>
                    <small>One skill per line</small>
                </div>
            </div>

            <!-- Tools -->
            <div class="section">
                <h2>Tools <span class="required">*</span></h2>
                <div class="form-group">
                    <textarea id="tools" rows="4" required></textarea>
                    <small>One tool per line</small>
                </div>
            </div>

            <!-- Certifications -->
            <div class="section">
                <h2>Certifications <span class="required">*</span></h2>
                <div id="certificationsContainer">
                    <div class="dynamic-item certification-item">
                        <div class="form-group">
                            <label>Certification Name</label>
                            <input type="text" class="certification-name" required>
                        </div>
                        <div class="form-group">
                            <label>Description</label>
                            <textarea class="certification-description" rows="2" required></textarea>
                        </div>
                        <button type="button" class="btn-remove" onclick="removeCertification(this)">Remove</button>
                    </div>
                </div>
                <button type="button" class="btn-add" onclick="addCertification()">+ Add Certification</button>
            </div>

            <button type="submit" class="btn-submit">Generate Resume</button>
        </form>
    </div>

    <!-- Loading Overlay -->
    <div class="loading" id="loading">
        <div class="loading-content">
            <div class="spinner"></div>
            <p>Generating your resume...</p>
        </div>
    </div>

    <!-- Success Modal with Preview -->
    <div class="success" id="success">
        <div class="success-box-large">
            <h2>✓ Resume Generated!</h2>
            <p style="margin-bottom: 20px;">Preview your resume below</p>
            
            <!-- PDF Preview -->
            <div class="pdf-preview">
                <embed id="pdfPreview" type="application/pdf" width="100%" height="600px">
            </div>
            
            <div style="margin-top: 20px;">
                <a href="#" id="downloadLink" class="btn-download">⬇ Download Resume</a>
                <button onclick="closeSuccess()" class="btn-download" style="background: #666;">✕ Close</button>
            </div>
        </div>
    </div>

    <script>
        // Tab switching
        function switchTab(tab) {
            const formTab = document.getElementById('resumeForm');
            const jsonTab = document.getElementById('jsonTab');
            const smartTab = document.getElementById('smartTab');
            const tabs = document.querySelectorAll('.tab-btn');

            tabs.forEach(t => t.classList.remove('active'));

            formTab.style.display = 'none';
            jsonTab.style.display = 'none';
            smartTab.style.display = 'none';

            if (tab === 'form') {
                formTab.style.display = 'block';
                tabs[0].classList.add('active');
            } else if (tab === 'smart') {
                smartTab.style.display = 'block';
                tabs[1].classList.add('active');
            } else {
                jsonTab.style.display = 'block';
                tabs[2].classList.add('active');
            }
        }

        // Parse smart input
        async function parseSmartInput() {
            const text = document.getElementById('smartInput').value.trim();
            
            if (!text) {
                alert('Please paste your resume text');
                return;
            }

            document.getElementById('loading').style.display = 'flex';

            try {
                // Send to backend for parsing
                const response = await fetch('/parse-text', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: text})
                });

                const result = await response.json();

                if (result.success) {
                    // Show parsed JSON in JSON tab for review
                    document.getElementById('jsonInput').value = JSON.stringify(result.data, null, 2);
                    document.getElementById('loading').style.display = 'none';
                    
                    // Ask user if they want to review or generate directly
                    if (confirm('Resume parsed successfully! Click OK to review/edit, or Cancel to generate immediately.')) {
                        switchTab('json');
                    } else {
                        // Generate directly
                        generateFromJSON();
                    }
                } else {
                    document.getElementById('loading').style.display = 'none';
                    alert('Error parsing resume: ' + result.error);
                }
            } catch (error) {
                document.getElementById('loading').style.display = 'none';
                alert('Error: ' + error.message);
            }
        }

        // Show sample JSON
        function showSampleJSON() {
            const sample = {
                "name": "John Doe",
                "title": "Software Developer",
                "email": "john.doe@example.com",
                "phone": "9876543210",
                "portfolio_link": "",
                "linkedin_link": "https://linkedin.com/in/johndoe",
                "github_link": "https://github.com/johndoe",
                "additional_link": "",
                "summary": "Software developer with 2 years of experience in web development...",
                "education": [
                    {
                        "degree": "B.Tech Computer Science",
                        "institution": "XYZ College",
                        "batch": "2019 - 2023"
                    }
                ],
                "experience": [
                    {
                        "company": "Software Developer - ABC Tech",
                        "description": "Developed web applications using React and Node.js..."
                    }
                ],
                "projects": [
                    {
                        "title": "E-commerce Website",
                        "bullets": [
                            "Built using MERN stack",
                            "Implemented payment gateway",
                            "Deployed on AWS"
                        ]
                    }
                ],
                "skills": [
                    "languages: JavaScript, Python",
                    "frameworks: React, Django"
                ],
                "tools": [
                    "Git",
                    "VS Code",
                    "Docker"
                ],
                "certifications": [
                    {
                        "name": "AWS Certified Developer",
                        "description": "Certified in AWS development practices"
                    }
                ]
            };
            document.getElementById('jsonInput').value = JSON.stringify(sample, null, 2);
        }

        // Generate from JSON
        async function generateFromJSON() {
            const jsonText = document.getElementById('jsonInput').value.trim();
            
            if (!jsonText) {
                alert('Please paste your JSON data');
                return;
            }

            try {
                const resumeData = JSON.parse(jsonText);
                document.getElementById('loading').style.display = 'flex';

                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(resumeData)
                });

                const result = await response.json();
                document.getElementById('loading').style.display = 'none';

                if (result.success) {
                    document.getElementById('downloadLink').href = '/download/' + result.filename;
                    document.getElementById('success').style.display = 'flex';
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                document.getElementById('loading').style.display = 'none';
                alert('Invalid JSON format or generation error: ' + error.message);
            }
        }

        // Dynamic form functions
        function addEducation() {
            const container = document.getElementById('educationContainer');
            const div = document.createElement('div');
            div.className = 'dynamic-item education-item';
            div.innerHTML = `
                <div class="form-group">
                    <label>Degree</label>
                    <input type="text" class="education-degree" required>
                </div>
                <div class="form-group">
                    <label>Institution</label>
                    <input type="text" class="education-institution" required>
                </div>
                <div class="form-group">
                    <label>Batch</label>
                    <input type="text" class="education-batch" required>
                </div>
                <button type="button" class="btn-remove" onclick="this.parentElement.remove()">Remove</button>
            `;
            container.appendChild(div);
        }

        function addExperience() {
            const container = document.getElementById('experienceContainer');
            const div = document.createElement('div');
            div.className = 'dynamic-item experience-item';
            div.innerHTML = `
                <div class="form-group">
                    <label>Company / Role</label>
                    <input type="text" class="experience-company" required>
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <textarea class="experience-description" rows="3" required></textarea>
                </div>
                <button type="button" class="btn-remove" onclick="this.parentElement.remove()">Remove</button>
            `;
            container.appendChild(div);
        }

        function addProject() {
            const container = document.getElementById('projectsContainer');
            const div = document.createElement('div');
            div.className = 'dynamic-item project-item';
            div.innerHTML = `
                <div class="form-group">
                    <label>Project Title</label>
                    <input type="text" class="project-title" required>
                </div>
                <div class="form-group">
                    <label>Bullet Points (one per line)</label>
                    <textarea class="project-bullets" rows="4" required></textarea>
                    <small>Each line becomes a bullet point</small>
                </div>
                <button type="button" class="btn-remove" onclick="removeProject(this)">Remove</button>
            `;
            container.appendChild(div);
        }

        function removeProject(btn) {
            if (document.querySelectorAll('.project-item').length > 1) {
                btn.parentElement.remove();
            } else {
                alert('You must have at least one project');
            }
        }

        function addCertification() {
            const container = document.getElementById('certificationsContainer');
            const div = document.createElement('div');
            div.className = 'dynamic-item certification-item';
            div.innerHTML = `
                <div class="form-group">
                    <label>Certification Name</label>
                    <input type="text" class="certification-name" required>
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <textarea class="certification-description" rows="2" required></textarea>
                </div>
                <button type="button" class="btn-remove" onclick="removeCertification(this)">Remove</button>
            `;
            container.appendChild(div);
        }

        function removeCertification(btn) {
            if (document.querySelectorAll('.certification-item').length > 1) {
                btn.parentElement.remove();
            } else {
                alert('You must have at least one certification');
            }
        }

        // Collect form data
        function collectFormData() {
            const data = {
                name: document.getElementById('name').value.trim(),
                title: document.getElementById('title').value.trim(),
                email: document.getElementById('email').value.trim(),
                phone: document.getElementById('phone').value.trim(),
                portfolio_link: document.getElementById('portfolio_link').value.trim(),
                linkedin_link: document.getElementById('linkedin_link').value.trim(),
                github_link: document.getElementById('github_link').value.trim(),
                additional_link: document.getElementById('additional_link').value.trim(),
                summary: document.getElementById('summary').value.trim(),
                skills: document.getElementById('skills').value.trim().split('\\n').filter(s => s.trim()),
                tools: document.getElementById('tools').value.trim().split('\\n').filter(t => t.trim()),
                education: [],
                experience: [],
                projects: [],
                certifications: []
            };

            document.querySelectorAll('.education-item').forEach(item => {
                data.education.push({
                    degree: item.querySelector('.education-degree').value.trim(),
                    institution: item.querySelector('.education-institution').value.trim(),
                    batch: item.querySelector('.education-batch').value.trim()
                });
            });

            document.querySelectorAll('.experience-item').forEach(item => {
                data.experience.push({
                    company: item.querySelector('.experience-company').value.trim(),
                    description: item.querySelector('.experience-description').value.trim()
                });
            });

            document.querySelectorAll('.project-item').forEach(item => {
                const bullets = item.querySelector('.project-bullets').value.trim()
                    .split('\\n').filter(b => b.trim());
                data.projects.push({
                    title: item.querySelector('.project-title').value.trim(),
                    bullets: bullets
                });
            });

            document.querySelectorAll('.certification-item').forEach(item => {
                data.certifications.push({
                    name: item.querySelector('.certification-name').value.trim(),
                    description: item.querySelector('.certification-description').value.trim()
                });
            });

            return data;
        }

        // Form submission
        document.getElementById('resumeForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = collectFormData();
            document.getElementById('loading').style.display = 'flex';

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(formData)
                });

                const result = await response.json();
                document.getElementById('loading').style.display = 'none';

                if (result.success) {
                    document.getElementById('downloadLink').href = '/download/' + result.filename;
                    document.getElementById('success').style.display = 'flex';
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                document.getElementById('loading').style.display = 'none';
                alert('Failed to generate resume: ' + error.message);
            }
        });

        function closeSuccess() {
            document.getElementById('success').style.display = 'none';
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/parse-text', methods=['POST'])
def parse_text():
    """Parse raw resume text into structured JSON"""
    try:
        text = request.json.get('text', '')
        if not text:
            return jsonify({'success': False, 'error': 'No text provided'}), 400
        
        # Parse the text
        resume_data = parse_resume_text(text)
        
        return jsonify({
            'success': True,
            'data': resume_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate_resume():
    try:
        resume_data = request.json
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_filename = f'resume_{timestamp}.json'
        pdf_filename = f'resume_{timestamp}.pdf'
        
        json_path = os.path.join(UPLOAD_FOLDER, json_filename)
        pdf_path = os.path.join(OUTPUT_FOLDER, pdf_filename)
        archive_path = os.path.join(ARCHIVE_FOLDER, pdf_filename)
        
        # Save JSON file
        with open(json_path, 'w') as f:
            json.dump(resume_data, f, indent=2)
        
        # Call C++ engine
        result = subprocess.run(
            [CPP_ENGINE_PATH, json_path, pdf_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return jsonify({
                'success': False,
                'error': f'Engine error: {result.stderr}'
            }), 500
        
        if not os.path.exists(pdf_path):
            return jsonify({
                'success': False,
                'error': 'PDF was not generated'
            }), 500
        
        # Copy PDF to archive for data collection
        import shutil
        shutil.copy2(pdf_path, archive_path)
        
        # Save to database
        user_ip = request.remote_addr
        resume_id = save_resume(resume_data, json_path, archive_path, user_ip)
        
        return jsonify({
            'success': True,
            'filename': pdf_filename,
            'resume_id': resume_id
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(file_path, as_attachment=True, download_name=f'ATS_Resume_{filename}')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/preview/<filename>')
def preview_file(filename):
    """Preview PDF in browser"""
    try:
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        return send_file(file_path, mimetype='application/pdf')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/stats')
def admin_stats():
    """Admin page to view statistics"""
    stats = get_resume_stats()
    
    html = f'''
    <html>
    <head>
        <title>Resume Builder - Admin Stats</title>
        <style>
            body {{
                font-family: 'Segoe UI', sans-serif;
                background: #f5f5f5;
                padding: 40px;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #1a1a1a;
                margin-bottom: 30px;
            }}
            .stat-box {{
                background: #f9f9f9;
                padding: 20px;
                border-radius: 4px;
                margin-bottom: 20px;
                border-left: 4px solid #1a1a1a;
            }}
            .stat-label {{
                color: #666;
                font-size: 0.9em;
                margin-bottom: 5px;
            }}
            .stat-value {{
                font-size: 2em;
                font-weight: bold;
                color: #1a1a1a;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #e0e0e0;
            }}
            th {{
                background: #1a1a1a;
                color: white;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Resume Builder Statistics</h1>
            
            <div class="stat-box">
                <div class="stat-label">Total Resumes Generated</div>
                <div class="stat-value">{stats['total_resumes']}</div>
            </div>
            
            <div class="stat-box">
                <div class="stat-label">Unique Users</div>
                <div class="stat-value">{stats['unique_users']}</div>
            </div>
            
            <h2>📅 Daily Activity (Last 7 Days)</h2>
            <table>
                <tr>
                    <th>Date</th>
                    <th>Resumes Generated</th>
                </tr>
                {''.join([f'<tr><td>{day[0]}</td><td>{day[1]}</td></tr>' for day in stats['daily_stats']])}
            </table>
            
            <p style="margin-top: 30px; color: #666;">
                📁 PDFs stored in: <code>archive/</code><br>
                💾 Database: <code>resumes.db</code>
            </p>
        </div>
    </body>
    </html>
    '''
    
    return html

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
