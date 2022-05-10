#!/usr/bin/env python3
import ast
import re

import astunparse
import codemod

TRUE_FALSE_NONE = {"True", "False", "None"}

COMMENT_REGEX = re.compile(r"(\s*).*\)(\s*\#.*)")


class Malformed(Exception):
    def __init__(self, message="Malformed", *, node):
        super().__init__(f"{message}: {node}: {astunparse.unparse(node)}")


def parse_args(node):
    args = []
    kwarg_list = []

    for arg in node.args:
        args.append(astunparse.unparse(arg).replace("\n", ""))
    for kwarg in node.keywords:
        kwarg_list.append(astunparse.unparse(kwarg).replace("\n", ""))

    return args, kwarg_list


def parse_args_and_msg(node, required_args_count, *, raise_if_malformed=True):
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

    if raise_if_malformed and len(args) != required_args_count:
        raise Malformed(node=node)

    return args, kwarg_list, f", {msg}" if msg else ""


def _handle_equal_or_unequal(node, *, is_op, cmp_op):
    args, kwarg_list, msg_with_comma = parse_args_and_msg(node, 2, raise_if_malformed=False)

    if len(args) != 2 or len(kwarg_list) > 0:
        raise Malformed(f"Potentially malformed", node=node)

    if args[0] in TRUE_FALSE_NONE:
        return f"assert {args[1]} {is_op} {args[0]}{msg_with_comma}"
    if args[1] in TRUE_FALSE_NONE:
        return f"assert {args[0]} {is_op} {args[1]}{msg_with_comma}"

    return f"assert {args[0]} {cmp_op} {args[1]}{msg_with_comma}"


def _handle_prefix_or_suffix(node, *, prefix="", suffix=""):
    args, _, msg_with_comma = parse_args_and_msg(node, 1)
    return f"assert {prefix}{args[0]}{suffix}{msg_with_comma}"


def _handle_generic_binary(node, *, op):
    args, _, msg_with_comma = parse_args_and_msg(node, 2)
    return f"assert {args[0]} {op} {args[1]}{msg_with_comma}"


def _handle_generic_call(node, *, func):
    args, _, msg_with_comma = parse_args_and_msg(node, 2)
    return f"assert {func}({args[0]}, {args[1]}){msg_with_comma}"


def _handle_almost_equal(node, *, op):
    args, _, msg_with_comma = parse_args_and_msg(node, 2)
    return f"assert round({args[0]} - {args[1]}, 7) {op} 0{msg_with_comma}"


def handle_equal(node):
    return _handle_equal_or_unequal(node, is_op="is", cmp_op="==")


def handle_not_equal(node):
    return _handle_equal_or_unequal(node, is_op="is not", cmp_op="!=")


def handle_contains(node):
    args, kwarg_list, msg_with_comma = parse_args_and_msg(node, 2)
    if not kwarg_list:
        if len(args) <= 2:
            return f"assert {args[1]} in {args[0]}{msg_with_comma}"
    kwarg = kwarg_list[0].split("=")
    return f'assert {args[1]} in {args[0]} and {args[0]}["{kwarg[0]}"] == {kwarg[1]}{msg_with_comma}'


def handle_true(node):
    return _handle_prefix_or_suffix(node, prefix="")


def handle_false(node):
    return _handle_prefix_or_suffix(node, prefix="not ")


def handle_in(node):
    return _handle_generic_binary(node, op="in")


def handle_not_in(node):
    return _handle_generic_binary(node, op="not in")


def handle_is(node):
    return _handle_generic_binary(node, op="is")


def handle_is_not(node):
    return _handle_generic_binary(node, op="is not")


def handle_is_none(node):
    return _handle_prefix_or_suffix(node, suffix=" is None")


def handle_is_not_none(node):
    return _handle_prefix_or_suffix(node, suffix=" is not None")


def handle_is_instance(node):
    return _handle_generic_call(node, func="isinstance")


def handle_not_is_instance(node):
    return _handle_generic_call(node, func="not isinstance")


def handle_less(node):
    return _handle_generic_binary(node, op="<")


def handle_less_equal(node):
    return _handle_generic_binary(node, op="<=")


def handle_greater(node):
    return _handle_generic_binary(node, op=">")


def handle_greater_equal(node):
    return _handle_generic_binary(node, op=">=")


def handle_almost_equal(node):
    return _handle_almost_equal(node, op=">=")


def handle_not_almost_equal(node):
    return _handle_almost_equal(node, op="!=")


def handle_raises(node, **kwargs):
    if kwargs.get("withitem"):
        return handle_with_raises(node, **kwargs)
    args, _ = parse_args(node)
    if len(args) > 2:
        raise Malformed(node=node)
    if len(args) == 2:
        return f"pytest.raises({args[0]}, {args[1]})"


def handle_with_raises(node, **kwargs):
    args, _ = parse_args(node)
    optional_vars = kwargs.get('optional_vars', None)
    if len(args) > 1:
        raise Malformed(node=node)

    if optional_vars:
        return f"with pytest.raises({args[0]}) as {optional_vars.id}:"
    return f"with pytest.raises({args[0]}):"


assert_mapping = {
    "assertEqual": handle_equal,
    "assertEquals": handle_equal,
    "assertNotEqual": handle_not_equal,
    "assertNotEquals": handle_not_equal,
    "assert_": handle_true,
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

    try:
        if isinstance(node, ast.With):
            return f(node_call, withitem=True, optional_vars=node.items[0].optional_vars)
        return f(node_call)
    except Malformed as e:
        print(str(e))
        return None


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
                codemod.Patch(0, end_line_number=0, new_lines="import pytest\n")
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
    import sys
    if sys.version_info < (3, 8):
        raise RuntimeError("This script requires Python version >=3.8")

    try:
        path = sys.argv[1]
    except IndexError:
        path = "."

    codemod.Query(
        assert_patches, path_filter=is_py, root_directory=path
    ).run_interactive()
    print(
        "\nHINT: Consider running a formatter to correctly format your new assertions!"
    )


if __name__ == "__main__":
    main()
