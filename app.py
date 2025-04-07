from flask import Flask, render_template, request, jsonify, send_file
from static_analyzer import analyze_code
import os
import logging
import ast
import re
import autopep8  # For Python formatting
import jsbeautifier  # For JavaScript formatting
from yapf.yapflib import yapf_api  # Another Python formatter option

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

def detect_memory_leaks(code):
    """Analyzes Python code and detects potential memory leaks."""
    warnings = []
    lines = code.split('\n')

    # Check for unclosed file handles
    for i, line in enumerate(lines, start=1):
        if "open(" in line and "with " not in line:
            warnings.append({
                "line": i,
                "type": "memory_leak",
                "severity": "high",
                "issue": "Unclosed file handle detected",
                "fix": "Use 'with open(...) as f:' instead",
                "code": line.strip()
            })

    # Detect missing .close() calls
    for match in re.finditer(r"(\w+)\s*=\s*open\([^)]+\)", code):
        var_name = match.group(1)
        line_num = code[:match.start()].count('\n') + 1
        if f"{var_name}.close()" not in code:
            warnings.append({
                "line": line_num,
                "type": "memory_leak",
                "severity": "high",
                "issue": f"Possible memory leak: '{var_name}' opened but never closed",
                "fix": f"Add '{var_name}.close()' after usage or use 'with' statement",
                "code": match.group(0)
            })

    # Check for large objects not cleared
    large_data_patterns = [
        (r"(\w+)\s*=\s*\[.+\]", "list"),
        (r"(\w+)\s*=\s*{.+}", "dict"),
        (r"(\w+)\s*=\s*set\(.+\)", "set")
    ]
    
    for pattern, obj_type in large_data_patterns:
        for match in re.finditer(pattern, code):
            var_name = match.group(1)
            line_num = code[:match.start()].count('\n') + 1
            if f"{var_name}.clear()" not in code and f"del {var_name}" not in code:
                warnings.append({
                    "line": line_num,
                    "type": "memory_leak",
                    "severity": "medium",
                    "issue": f"Large {obj_type} object '{var_name}' may cause memory bloat",
                    "fix": f"Consider using '{var_name}.clear()' or 'del {var_name}' when no longer needed",
                    "code": match.group(0)
                })

    return warnings

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ide')
def ide():
    return render_template('ide.html')

@app.route('/api/health')
def health_check():
    return jsonify({"status": "ok"})

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({'error': 'No code provided'}), 400
        
        print("1. Received code for analysis:", data['code'])
        
        results = analyze_code(data['code'])
        print("2. Got analysis results:", results)
        
        if 'error' in results:
            return jsonify(results), 500
            
        # Ensure all fields exist
        results.setdefault('code_analysis', [])
        results.setdefault('memory_leaks', [])
        results.setdefault('ai_analysis', [])
        
        print("3. Sending response:", results)
        return jsonify(results)
        
    except Exception as e:
        print("Error in analyze route:", str(e))
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/hotspot-plot')
def get_hotspot_plot():
    return send_file('hotspot_plot.png', mimetype='image/png')

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        remember = data.get('remember', False)
        
        # Basic validation
        if not email or not password:
            return jsonify({
                "status": "error",
                "message": "Email and password are required"
            }), 400
            
        # TODO: Add actual authentication logic
        if email and password:  # Replace with real authentication
            return jsonify({
                "status": "success",
                "message": "Login successful",
                "redirect": "/dashboard"  # Add redirect URL
            })
        
        return jsonify({
            "status": "error",
            "message": "Invalid credentials"
        }), 401
            
    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred"
        }), 500

@app.route('/auth/google')
def google_auth():
    # TODO: Implement Google OAuth
    return jsonify({
        "status": "success",
        "message": "Google authentication to be implemented"
    })

@app.route('/auth/github')
def github_auth():
    # TODO: Implement GitHub OAuth
    return jsonify({
        "status": "success",
        "message": "GitHub authentication to be implemented"
    })

@app.route('/api/verify-student', methods=['POST'])
def verify_student():
    try:
        data = request.json
        email = data.get('email')
        
        if not email:
            return jsonify({
                "status": "error",
                "message": "Email is required"
            }), 400
            
        # Validate student email
        student_domains = [
            'edu', 'ac.uk', 'ac.in', 'edu.au', 'edu.cn',
            'ac.jp', 'edu.sg', 'ac.nz', 'edu.hk', 'edu.my'
        ]
        
        is_student = any(email.lower().endswith(domain) for domain in student_domains)
        
        if not is_student:
            return jsonify({
                "status": "error",
                "message": "Please use a valid student email address"
            }), 400
            
        # TODO: Send verification email
        # For now, just return success
        return jsonify({
            "status": "success",
            "message": "Verification email sent",
            "redirect": "/student-signup"
        })
            
    except Exception as e:
        app.logger.error(f"Student verification error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Failed to verify student status"
        }), 500

@app.route('/api/start-trial', methods=['POST'])
def start_trial():
    try:
        # TODO: Implement trial signup logic
        return jsonify({
            "status": "success",
            "message": "Trial started successfully",
            "redirect": "/trial-signup"
        })
    except Exception as e:
        app.logger.error(f"Trial start error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Failed to start trial"
        }), 500

@app.route('/student-signup')
def student_signup():
    return render_template('student-signup.html')

@app.route('/trial-signup')
def trial_signup():
    try:
        return render_template('trial-signup.html')
    except Exception as e:
        app.logger.error(f"Error rendering trial signup page: {str(e)}")
        return "Error loading trial signup page", 500

@app.route('/format', methods=['POST'])
def format_code():
    try:
        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        if not code:
            return jsonify({'error': 'No code provided'}), 400
            
        formatted_code = ''
        
        if language == 'python':
            # Use autopep8 for Python
            formatted_code = autopep8.fix_code(code, options={
                'aggressive': 1,
                'max_line_length': 100
            })
        elif language == 'javascript':
            # Use jsbeautifier for JavaScript
            formatted_code = jsbeautifier.beautify(code, {
                'indent_size': 4,
                'space_in_empty_paren': True
            })
        else:
            # Default to Python formatting
            formatted_code = autopep8.fix_code(code)
            
        return jsonify({
            'formatted': formatted_code,
            'language': language
        })
        
    except Exception as e:
        app.logger.error(f"Format error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    try:
        # Make sure the static and templates folders exist
        for folder in ['static', 'templates']:
            if not os.path.exists(folder):
                os.makedirs(folder)
                
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Failed to start server: {str(e)}")