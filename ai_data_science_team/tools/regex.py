import re
from datetime import datetime


def relocate_imports_inside_function(code_text):
    """
    Relocates all import statements in a given Python function and moves them inside the function definition.

    Parameters
    ----------
    code_text : str
        The Python code as a string.

    Returns
    -------
    str
        The modified Python code with imports relocated inside the function.
    """
    # Match all import statements
    import_pattern = r'^\s*(import\s+[^\n]+|from\s+\S+\s+import\s+[^\n]+)\s*$'
    imports = re.findall(import_pattern, code_text, re.MULTILINE)

    # Remove imports from the top-level code
    code_without_imports = re.sub(import_pattern, '', code_text, flags=re.MULTILINE).strip()

    # Find the function definition and insert the imports inside it
    function_pattern = r'(def\s+\w+\s*\(.*?\):)'
    match = re.search(function_pattern, code_without_imports)

    if match:
        function_start = match.end()
        # Insert the imports right after the function definition
        imports_code = '\n    ' + '\n    '.join(imports)  # Indent imports
        modified_code = (
            code_without_imports[:function_start]
            + imports_code
            + code_without_imports[function_start:]
        )
        return modified_code

    # If no function is found, return the original code
    return code_text

def add_comments_to_top(code_text, agent_name="data_wrangler"):
    """
    Adds AI-generated metadata comments to the top of the Python code.

    Parameters
    ----------
    code_text : str
        The Python code to be commented.
    agent_name : str, optional
        The agent name to include in the comments, by default "data_wrangler".

    Returns
    -------
    str
        The Python code with the added comments at the top.
    """
    # Generate timestamp
    time_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Construct the header comments
    header_comments = [
        "# Disclaimer: This function was generated by AI. Please review before using.",
        f"# Agent Name: {agent_name}",
        f"# Time Created: {time_created}\n",        
        ""
    ]

    # Join the header with newlines, then prepend to the existing code_text
    header_block = "\n".join(header_comments)
    return header_block + code_text

def format_agent_name(agent_name: str) -> str:
    
    formatted_name = agent_name.strip().replace("_", " ").upper()
    
    return f"---{formatted_name}----"

def format_recommended_steps(raw_text: str, heading: str = "# Recommended Steps:") -> str:
    # Split text by newline and strip leading/trailing whitespace
    lines = raw_text.strip().split('\n')
    
    # Remove empty lines from the start
    while lines and not lines[0].strip():
        lines.pop(0)

    seen_heading = False
    new_lines = []

    for line in lines:
        # If this line *is exactly* the heading, check if we've seen it already
        if line.strip() == heading:
            if seen_heading:
                # Skip duplicates
                continue
            else:
                seen_heading = True
        new_lines.append(line)

    # If heading was never seen, prepend it
    if not seen_heading:
        new_lines.insert(0, heading)

    return "\n".join(new_lines)

def get_generic_summary(report_dict: dict, code_lang = "python") -> str:
    """
    Takes a dictionary of unknown structure (e.g., from json.loads(...)) 
    and returns a textual summary. It assumes:
      1) 'report_title' (if present) should be displayed first.
      2) If a key includes 'code' or 'function', 
         the value is treated as a code block.
      3) Otherwise, key-value pairs are displayed as text.

    Parameters
    ----------
    report_dict : dict
        The dictionary holding the agent output or user report.

    Returns
    -------
    str
        A formatted summary string.
    """
    # 1) Grab the report title (or default)
    title = report_dict.get("report_title", "Untitled Report")

    lines = []
    lines.append(f"# {title}")

    # 2) Iterate over all other keys
    for key, value in report_dict.items():
        # Skip the title key, since we already displayed it
        if key == "report_title":
            continue

        # 3) Check if it's code or function
        # (You can tweak this logic if you have different rules)
        key_lower = key.lower()
        if "code" in key_lower or "function" in key_lower:
            # Treat as code
            lines.append(f"\n## {format_agent_name(key).upper()}")
            lines.append(f"```{code_lang}\n" + str(value) + "\n```")
        else:
            # 4) Otherwise, just display the key-value as text
            lines.append(f"\n## {format_agent_name(key).upper()}")
            lines.append(str(value))

    return "\n".join(lines)

