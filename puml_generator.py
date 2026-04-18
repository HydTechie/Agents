def to_puml(flow):
    lines = ["@startuml", "start"]
    for step in flow["steps"]:
        if step.get("condition"):
            lines.append(f'if ({step["condition"]}) then (Yes)')
        lines.append(f':{step["action"]};')
    lines.append("stop\n@enduml")
    return "\n".join(lines)
