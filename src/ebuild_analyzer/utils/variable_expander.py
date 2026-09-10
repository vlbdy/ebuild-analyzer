import re


def expand_variable(contents: bytes, variable_name: str, variable_value: str) -> bytes:
    # Expand variables of the form ${VAR}
    contents = contents.replace(f"${{{variable_name}}}".encode(), variable_value.encode())
    # Expand variables of the form $VAR
    # The regex here prevents the substitution from expanding variables that have $VAR as a substring
    print(variable_name)
    contents = re.sub(
        rb"\$" + re.escape(variable_name.encode()) + rb"(?![A-Za-z0-9_])",
        variable_value.encode(),
        contents
    )
    return contents
