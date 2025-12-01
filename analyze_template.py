#!/usr/bin/env python3

def analyze_django_template(file_path):
    """Analyze Django template for unmatched if/endif pairs"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if_stack = []
    issues = []
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Check for if statements
        if '{% if ' in line:
            if_stack.append((line_num, line))
        
        # Check for endif statements
        elif '{% endif %}' in line:
            if if_stack:
                if_stack.pop()
            else:
                issues.append(f"Line {line_num}: Unmatched endif - {line}")
        
        # Check for endblock (should not appear inside if blocks)
        elif '{% endblock %}' in line:
            if if_stack:
                print(f"ERROR: Line {line_num}: endblock found but {len(if_stack)} if statement(s) still open:")
                for if_line_num, if_line in if_stack:
                    print(f"  Line {if_line_num}: {if_line}")
                return False
    
    # Check for unmatched if statements
    if if_stack:
        print(f"ERROR: {len(if_stack)} unmatched if statement(s):")
        for if_line_num, if_line in if_stack:
            print(f"  Line {if_line_num}: {if_line}")
        return False
    
    if issues:
        print("Issues found:")
        for issue in issues:
            print(f"  {issue}")
        return False
    
    print("All if/endif pairs are properly matched!")
    return True

if __name__ == "__main__":
    analyze_django_template("templates/services/profile_new.html")