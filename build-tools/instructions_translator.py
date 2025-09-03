#!/usr/bin/env python3

import re
import json
import argparse

# ----------------------------
# Parse command-line arguments
# ----------------------------
parser = argparse.ArgumentParser(description="Convert a Markdown instructions file into a JSON rules file.")
parser.add_argument("--input_file", required=True, help="Path to the instructions.md file to read from")
parser.add_argument("--output_file", required=True, help="Path where the generated instructions.json file will be saved")
args = parser.parse_args()

# ----------------------------
# Regex to detect a new rule line like: **RULE-ID**: rule text
# WHY: More permissive ID charset (letters, digits, _, -) and flexible spacing.
# ----------------------------
rule_re = re.compile(r'^\s*\*\*([A-Za-z0-9_-]+)\*\*\s*:\s*(.+)')

rules = []
current_rule = None

def flush_current():
    # WHAT: Push the current rule into the list if present.
    # WHY: Avoids duplicate code when starting a new rule or finishing the file.
    global current_rule
    if current_rule:
        # Normalize spaces in accumulated text
        current_rule["text"] = " ".join(current_rule["text"].split())
        rules.append(current_rule)
        current_rule = None

with open(args.input_file, "r", encoding="utf-8") as f:
    for raw_line in f:
        line = raw_line.rstrip("\n")

        # ----------------------------
        # Skip Markdown headers like "# Title" or "## Section"
        # WHY: We only want rule blocks, not document structure.
        # ----------------------------
        if line.lstrip().startswith("#"):
            continue

        # Detect start of a new rule
        m = rule_re.match(line)
        if m:
            # Finish any existing rule before starting a new one
            flush_current()
            current_rule = {"id": m.group(1), "text": m.group(2).strip()}
            continue

        # Blank line -> just a paragraph separator; don't create stray entries
        if not line.strip():
            continue

        # Any other non-empty line is treated as a continuation ONLY if we’re in a rule
        if current_rule:
            # WHY: Preserve readable spacing while flattening lines.
            current_rule["text"] += " " + line.strip()
        else:
            # Not inside a rule and not a header/new-rule -> ignore
            continue

# End of file: flush any pending rule
flush_current()

with open(args.output_file, "w", encoding="utf-8") as out:
    json.dump(rules, out, indent=2, ensure_ascii=False)
