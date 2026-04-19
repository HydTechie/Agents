PROMPT = """
Extract flows strictly from the text.

Allowed flows:
Search, View, Create, Edit, Copy, Delete, Restore

Do NOT infer anything not present.

Return a single JSON array. Each element must be an object with:
- "name": string (flow title)
- "steps": array of { "action": string, "condition": string or omit if none }

Example shape (structure only):
[{"name": "Example", "steps": [{"action": "Open screen"}, {"action": "Save", "condition": "valid"}]}]

Output only valid JSON — no markdown fences, no commentary before or after.
"""
