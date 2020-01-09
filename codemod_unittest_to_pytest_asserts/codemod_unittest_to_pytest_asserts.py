#!/usr/bin/env python3
import ast
import re
import sys

import astunparse
import codemod

if sys.version_info[0] != 3 or sys.version_info[1] < 8:
    print("This script requires Python version >3.8")
    sys.exit(1)

COMMENT_REGEX = re.compile(r"(\s*).*\)(\s*\#.*)")


def parse_args(node):
    args = []
    kwarg_list = []

    for arg in node.args:
        args.append(astunparse.unparse(arg).replace("\n", ""))
    for kwarg in node.keywords:
        kwarg_list.append(astunparse.unparse(kwarg).replace("\n", ""))

    return args, kwarg_list


def parse_args_and_msg(node, required_args_count):
    args, kwarg_list = parse_args(node)
    msg = ""

    for i, kwarg in enumerate(kwarg_list):
        key, val = kwarg.split("=")
        if key == "msg":
            msg = val
            kwarg_list.pop(i)
            break

    if len(args) > required_args_count and type(args[required_args_count]) == str:
        msg = args.pop(required_args_count)

    return args, kwarg_list, f", {msg}" if msg else ""


def handle_equal(node):
    args, kwarg_list, msg_with_comma = parse_args_and_msg(node, 2)

    if len(args) != 2 or len(kwarg_list) > 0:
        print(f"Potentially malformed: {node}: {astunparse.unparse(node)}\n")
        return

    if args[0] in ["True", "False", "None"]:
        return f"assert {args[1]} is {args[0]}{msg_with_comma}"
    if args[1] in ["True", "False", "None"]:
        return f"assert {args[0]} is {args[1]}{msg_with_comma}"

    return f"assert {args[0]} == {args[1]}{msg_with_comma}"


def handle_not_equal(node):
    args, kwarg_list, msg_with_comma = parse_args_and_msg(node, 2)

    if len(args) != 2 or len(kwarg_list) > 0:
        print(f"Potentially malformed: {node}: {astunparse.unparse(node)}\n")
        return

    if args[0] in ["True", "False", "None"]:
        return f"assert {args[1]} is not {args[0]}{msg_with_comma}"
    if args[1] in ["True", "False", "None"]:
        return f"assert {args[0]} is not {args[1]}{msg_with_comma}"

    return f"assert {args[0]} != {args[1]}{msg_with_comma}"


def handle_contains(node):
    args, kwarg_list, msg_with_comma = parse_args_and_msg(node, 2)
    if not kwarg_list:
        if len(args) <= 2:
            return f"assert {args[1]} in {args[0]}{msg_with_comma}"
    kwarg = kwarg_list[0].split("=")
    return f'assert {args[1]} in {args[0]} and {args[0]}["{kwarg[0]}"] == {kwarg[1]}{msg_with_comma}'


def handle_true(node):
    args, _, msg_with_comma = parse_args_and_msg(node, 1)
    if len(args) != 1:
        print(f"Malformed: {node}: {astunparse.unparse(node)}\n")
        return
    return f"assert {args[0]}{msg_with_comma}"


def handle_false(node):
    args, _, msg_with_comma = parse_args_and_msg(node, 1)
    if len(args) != 1:
        print(f"Malformed: {node}: {astunparse.unparse(node)}\n")
        return
    return f"assert not {args[0]}{msg_with_comma}"


def handle_in(node):
    args, _, msg_with_comma = parse_args_and_msg(node, 2)
    if len(args) != 2:
        print(f"Malformed: {node}: {astunparse.unparse(node)}\n")
        return
    return f"assert {args[0]} in {args[1]}{msg_with_comma}"


def handle_not_in(node):
    args, _, msg_with_comma = parse_args_and_msg(node, 2)
    if len(args) != 2:
        print(f"Malformed: {node}: {astunparse.unparse(node)}\n")
        return
    return f"assert {args[0]} not in {args[1]}{msg_with_comma}"


def handle_is(node):
    args, _, msg_with_comma = parse_args_and_msg(node, 2)
    if len(args) != 2:
        print(f"Malformed: {node}: {astunparse.unparse(node)}\n")
        return
    return f"assert {args[0]} is {args[1]}{msg_with_comma}"


def handle_is_none(node):
    args, _, msg_with_comma = parse_args_and_msg(node, 1)
    if len(args) != 1:
        print(f"Malformed: {node}: {astunparse.unparse(node)}\n")
        return
    return f"assert {args[0]} is None{msg_with_comma}"


def handle_is_not(node):
    args, _, msg_with_comma = parse_args_and_msg(node, 2)
    if len(args) != 2:
        print(f"Malformed: {node}: {astunparse.unparse(node)}\n")
        return
    return f"assert {args[0]} is not {args[1]}{msg_with_comma}"


def handle_is_not_none(node):
    args, _, msg_with_comma = parse_args_and_msg(node, 1)
    if len(args) != 1:
        print(f"Malformed: {node}: {astunparse.unparse(node)}\n")
        return
    return f"assert {args[0]} is not None{msg_with_comma}"


def handle_is_instance(node):
    args, _, msg_with_comma = parse_args_and_msg(node, 2)
    if len(args) != 2:
        print(f"Malformed: {node}: {astunparse.unparse(node)}\n")
        return
    return f"assert isinstance({args[0]}, {args[1]}){msg_with_comma}"


def handle_not_is_instance(node):
    args, _, msg_with_comma = parse_args_and_msg(node, 2)
    if len(args) != 2:
        print(f"Malformed: {node}: {astunparse.unparse(node)}\n")
        return
    return f"assert not isinstance({args[0]}, {args[1]}){msg_with_comma}"


def handle_less(node):
    args, _, msg_with_comma = parse_args_and_msg(node, 2)
    if len(args) != 2:
        print(f"Malformed: {node}: {astunparse.unparse(node)}\n")
        return
    return f"assert {args[0]} < {args[1]}{msg_with_comma}"


def handle_less_equal(node):
    args, _, msg_with_comma = parse_args_and_msg(node, 2)
    if len(args) != 2:
        print(f"Malformed: {node}: {astunparse.unparse(node)}\n")
        return
    return f"assert {args[0]} <= {args[1]}{msg_with_comma}"


def handle_greater(node):
    args, _, msg_with_comma = parse_args_and_msg(node, 2)
    if len(args) != 2:
        print(f"Malformed: {node}: {astunparse.unparse(node)}\n")
        return
    return f"assert {args[0]} > {args[1]}{msg_with_comma}"


def handle_greater_equal(node):
    args, _, msg_with_comma = parse_args_and_msg(node, 2)
    if len(args) != 2:
        print(f"Malformed: {node}: {astunparse.unparse(node)}\n")
        return
    return f"assert {args[0]} >= {args[1]}{msg_with_comma}"


def handle_almost_equal(node):
    args, _, msg_with_comma = parse_args_and_msg(node, 2)
    if len(args) != 2:
        print(f"Malformed: {node}: {astunparse.unparse(node)}\n")
        return
    return f"assert round({args[0]} - {args[1]}, 7) >= 0{msg_with_comma}"


def handle_not_almost_equal(node):
    args, _, msg_with_comma = parse_args_and_msg(node, 2)
    if len(args) != 2:
        print(f"Malformed: {node}: {astunparse.unparse(node)}\n")
        return
    return f"assert round({args[0]} - {args[1]}, 7) != 0{msg_with_comma}"


def handle_raises(node, **kwargs):
    if kwargs.get("withitem"):
        return handle_with_raises(node)
    args, _ = parse_args(node)
    if len(args) > 2:
        print(f"Malformed: {node}: {astunparse.unparse(node)}\n")
        return
    if len(args) == 2:
        return f"pytest.raises({args[0]}, {args[1]})"


def handle_with_raises(node):
    args, _ = parse_args(node)
    if len(args) > 1:
        print(f"Malformed: {node}: {astunparse.unparse(node)}\n")
        return
    if len(args) == 1:
        return f"with pytest.raises({args[0]}):"


assert_mapping = {
    "assertEqual": handle_equal,
    "assertEquals": handle_equal,
    "assertNotEqual": handle_not_equal,
    "assertNotEquals": handle_not_equal,
    "assertTrue": handle_true,
    "assertFalse": handle_false,
    "assertIn": handle_in,
    "assertNotIn": handle_not_in,
    "assertIs": handle_is,
    "assertIsNot": handle_is_not,
    "assertIsNone": handle_is_none,
    "assertIsNotNone": handle_is_not_none,
    "assertIsInstance": handle_is_instance,
    "assertNotIsInstance": handle_not_is_instance,
    "assertLess": handle_less,
    "assertLessEqual": handle_less_equal,
    "assertGreater": handle_greater,
    "assertGreaterEqual": handle_greater_equal,
    "assertAlmostEqual": handle_almost_equal,
    "assertNotAlmostEqual": handle_not_almost_equal,
    "assertRaises": handle_raises,
}


def convert(node):

    node_call = node_get_call(node)
    f = assert_mapping.get(node_get_func_attr(node_call), None)
    if not f:
        return None

    if isinstance(node, ast.With):
        return f(node_call, withitem=True)
    return f(node_call)


def dfs_walk(node):
    """
    Walk along the nodes of the AST in a DFS fashion returning the pre-order-tree-traversal
    """

    stack = [node]
    for child in ast.iter_child_nodes(node):
        stack.extend(dfs_walk(child))
    return stack


def node_get_func_attr(node):
    if isinstance(node, ast.Call):
        return getattr(node.func, "attr", None)


def node_get_call(node):
    if not (isinstance(node, ast.Expr) or isinstance(node, ast.With)):
        return False

    if isinstance(node, ast.Expr):
        value = getattr(node, "value", None)
        if isinstance(value, ast.Call):
            return value

    if isinstance(node, ast.With):
        value = getattr(
            node.items[0], "context_expr", None
        )  # Naively choosing the first item in the with
        if isinstance(value, ast.Call):
            return value
    return None


def get_col_offset(node):
    return node.col_offset


def get_lineno(node):
    # We generally use `lineno` from the AST node, but special case for `With` expressions
    if isinstance(node, ast.With):
        return node.items[0].context_expr.lineno

    return node.lineno


def get_end_lineno(node):
    # We generally use `end_lineno` directly from the AST node, but special case for `With` expressions
    if isinstance(node, ast.With):
        return node.items[0].context_expr.end_lineno

    return node.end_lineno


def assert_patches(list_of_lines):
    """
    Main method where we get the list of lines from codemod.
    1. Parses it with AST
    2. Traverses the AST in a pre-order-tree traversal
    3. Grab the Call values we are interested in e.g. `assertEqual()`
    4. Try executing `convert` on the Call node or continue
    5. Construct a codemod.Patch for the conversion and replace start->end lines with the conversion
    6. Handle special cases with importing pytest if it used and not imported, and append comment if it exists.
    """

    patches = []
    joined_lines = "".join(list_of_lines)
    ast_parsed = ast.parse(joined_lines)

    pytest_imported = "import pytest" in joined_lines

    line_deviation = 0
    for node in dfs_walk(ast_parsed):
        if not node_get_call(node):
            continue

        converted = convert(node)
        if not converted:
            continue

        assert_line = get_col_offset(node) * " " + converted + "\n"
        start_line = get_lineno(node)
        end_line = get_end_lineno(node)

        patches.append(
            codemod.Patch(
                start_line - line_deviation - 1,
                end_line_number=end_line - line_deviation,
                new_lines=assert_line,
            )
        )

        requires_import = "pytest." in assert_line
        if requires_import and not pytest_imported:
            patches.append(
                codemod.Patch(0, end_line_number=0, new_lines="import pytest\n",)
            )
            line_deviation -= 1
            pytest_imported = True

        comment_line = COMMENT_REGEX.search(
            list_of_lines[min(end_line - 1, len(list_of_lines) - 1)]
        )
        line_deviation += end_line - start_line

        if comment_line:
            comment = comment_line.group(1) + comment_line.group(2).lstrip() + "\n"
            patches.append(
                codemod.Patch(
                    end_line - line_deviation,
                    end_line_number=end_line - line_deviation,
                    new_lines=comment,
                )
            )
            line_deviation -= 1

    return patches


def is_py(filename):
    """
    Filter method using filename's to select what files to evaluate for codemodding
    """

    return filename.split(".")[-1] == "py"


def main():
    codemod.Query(assert_patches, path_filter=is_py).run_interactive()
    print(
        "\nHINT: Consider running a formatter to correctly format your new assertions!"
    )


if __name__ == "__main__":
    main()
