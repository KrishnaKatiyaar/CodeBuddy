import ast
from readability_analyzer import calculate_readability_score
from hotspot_plotter import profile_code, visualize_hotspots
from redundancy_detector import detect_duplicates_and_redundancy
import re
from ai_analyzer import AICodeAnalyzer

def detect_memory_leaks(code):
    """Detects potential memory leaks in Python code."""
    warnings = []
    lines = code.split('\n')
    
    # Check for unclosed files
    for i, line in enumerate(lines, 1):
        if "open(" in line and "with " not in line:
            warnings.append({
                "line": i,
                "severity": "high",
                "issue": "Unclosed file handle detected",
                "fix": "Use 'with open(...) as f:' instead"
            })
    
    return warnings

class StaticAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.issues = []
        self.defined_vars = set()
        self.used_vars = set()
        self.functions = set()
        self.ai_analyzer = AICodeAnalyzer()
    
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.defined_vars.add(node.id)
            self.issues.append({
                'type': 'variable_definition',
                'line': node.lineno,
                'name': node.id
            })
        elif isinstance(node.ctx, ast.Load):
            self.used_vars.add(node.id)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        self.functions.add(node.name)
        self.generic_visit(node)
    
    def check_unused_variables(self):
        self.issues = [issue for issue in self.issues if issue['type'] != 'unused_variable']
        
        for var in (self.defined_vars - self.used_vars):
            var_def = next((issue for issue in self.issues 
                           if issue['type'] == 'variable_definition' and issue['name'] == var), None)
            self.issues.append({
                'type': 'unused_variable',
                'line': var_def.get('line', 0) if var_def else 0,
                'suggestion': f'Variable "{var}" is defined but never used'
            })
        
        self.issues = [issue for issue in self.issues if issue['type'] != 'variable_definition']

def analyze_code(code):
    """Main analysis function that combines all checks."""
    results = {
        'code_analysis': [],
        'memory_leaks': [],
        'ai_analysis': []
    }
    
    try:
        print("1. Starting analysis...")
        tree = ast.parse(code)
        analyzer = StaticAnalyzer()
        
        print("2. Checking for memory leaks...")
        memory_leaks = detect_memory_leaks(code)
        results['memory_leaks'] = memory_leaks
        
        print("3. Checking for code issues...")
        analyzer.visit(tree)
        analyzer.check_unused_variables()
        results['code_analysis'] = analyzer.issues
        
        print("4. Running AI analysis...")
        ai_results = analyzer.ai_analyzer.analyze(code)
        results['ai_analysis'] = ai_results
        
        print("5. Analysis complete:", results)
        return results
        
    except Exception as e:
        print(f"Analysis failed: {str(e)}")
        return {'error': f'Analysis failed: {str(e)}'} 