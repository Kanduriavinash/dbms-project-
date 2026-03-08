# check_templates.py
import sys
import os
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError

# adjust if your templates folder is named differently
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

if not os.path.isdir(TEMPLATES_DIR):
    print("Templates folder not found at:", TEMPLATES_DIR)
    sys.exit(1)

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)

errors = 0
for root, _, files in os.walk(TEMPLATES_DIR):
    for f in files:
        if not f.endswith((".html", ".j2")):
            continue
        rel_dir = os.path.relpath(root, TEMPLATES_DIR)
        tpl_path = os.path.join(rel_dir, f) if rel_dir != "." else f
        try:
            # load/parse template (compiles AST) — will raise TemplateSyntaxError if invalid
            env.get_template(tpl_path)
        except TemplateSyntaxError as e:
            errors += 1
            print("SyntaxError in template:", tpl_path)
            print("  message:", e.message)
            print("  lineno:", e.lineno)
            print("  source snippet:")
            try:
                with open(os.path.join(root, f), "r", encoding="utf-8") as fh:
                    lines = fh.readlines()
                    start = max(0, e.lineno - 4)
                    end = min(len(lines), e.lineno + 2)
                    for i in range(start, end):
                        # show line numbers
                        prefix = ">>" if (i+1)==e.lineno else "  "
                        print(f"{prefix} {i+1:4d}: {lines[i].rstrip()}")
            except Exception:
                pass
            print("-" * 60)

if errors == 0:
    print("No template syntax errors found.")
else:
    print(f"Found {errors} template syntax error(s).")
    sys.exit(2)
