import re

def check_variable_naming_quality(code):
    """Checks if variable names follow snake_case and are meaningful."""
    snake_case_pattern = re.compile(r'^[a-z]+(_[a-z0-9]+)*$')
    bad_variable_names = []
    lines = code.split("\n")
    for line in lines:
        match = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_])\s=', line)
        for var in match:
            if len(var) < 2 or not snake_case_pattern.match(var):
                bad_variable_names.append(var)
    return {"bad_variables": bad_variable_names, "score": max(0, 10 - len(bad_variable_names))}

def check_comment_density(code):
    """Calculates the ratio of comments to total lines."""
    lines = code.split("\n")
    comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
    ratio = comment_lines / len(lines) if lines else 0
    score = min(10, round(ratio * 20))
    return {"comment_ratio": ratio, "score": score}

def check_indentation_consistency(code):
    """Detects inconsistent indentation (mix of tabs/spaces)."""
    lines = code.split("\n")
    uses_tabs = any("\t" in line for line in lines)
    uses_spaces = any("    " in line for line in lines)
    if uses_tabs and uses_spaces:
        return {"consistent": False, "score": 3}
    return {"consistent": True, "score": 10}

def check_code_length(code):
    """Evaluates code length based on number of lines."""
    lines = len(code.split("\n"))
    score = max(0, 10 - (lines // 20))
    return {"lines": lines, "score": score}

def calculate_readability_score(code):
    """Aggregates readability metrics into a final score."""
    var_quality = check_variable_naming_quality(code)
    comment_density = check_comment_density(code)
    indentation_consistency = check_indentation_consistency(code)
    code_length = check_code_length(code)

    total_score = (var_quality["score"] + comment_density["score"] +
                   indentation_consistency["score"] + code_length["score"]) / 4

    return {
        "total_score": round(total_score, 2),
        "variable_naming": var_quality,
        "comment_density": comment_density,
        "indentation_consistency": indentation_consistency,
        "code_length": code_length
    } 