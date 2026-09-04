import re


def strip_jsonc(text: str) -> str:
    """Quita comentarios // y /* */ respetando strings JSON."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    lines: list[str] = []
    for line in text.splitlines():
        in_string = False
        escape = False
        cut = len(line)
        index = 0
        while index < len(line):
            char = line[index]
            if escape:
                escape = False
            elif in_string and char == "\\":
                escape = True
            elif char == '"':
                in_string = not in_string
            elif (
                not in_string
                and char == "/"
                and index + 1 < len(line)
                and line[index + 1] == "/"
            ):
                cut = index
                break
            index += 1
        lines.append(line[:cut])
    return "\n".join(lines)
