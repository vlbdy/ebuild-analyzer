def dump_ast(node, source, indent=0):
    text = source[node.start_byte:node.end_byte].decode("utf-8")

    print(
        " " * indent +
        f"[{node.type}] "
        f"'{text[:40].replace(chr(10), ' ')}'"
    )

    for child in node.children:
        dump_ast(child, source, indent + 4)
