import ast


def remove_useless(tree: ast.AST) -> ast.AST:
    # Implement this optimization here
    return tree


def hoist_invariants(tree: ast.AST) -> ast.AST:
    # Implement this optimization here
    return tree


def optimize(tree: ast.AST) -> ast.AST:
    # Implement this optimization here
    return tree


if __name__ == "__main__":
    import argparse
    from pathlib import Path
    ap = argparse.ArgumentParser()
    ap.add_argument("script", type=Path, help="the script to transform")
    g = ap.add_mutually_exclusive_group(required=False)
    g.add_argument("--dont", action="store_true", help="don't optimize")
    g.add_argument("--hoist", action="store_true", help="hoist invariants")
    g.add_argument("--remove", action="store_true", help="remove useless")
    args = ap.parse_args()

    with open(args.script, "r") as f:
        t = ast.parse(f.read())

    if not args.dont:
        if args.hoist:
            t = hoist_invariants(t)
        elif args.remove:
            t = remove_useless(t)
        else:
            t = optimize(t)

    print(ast.unparse(t))
