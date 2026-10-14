"""Lambda Calculus 解譯器 —— 命令列介面 (CLI)

用法範例：
    python main.py examples/factorial.lam        # 計算內附的階乘範例
    python main.py examples/fibonacci.lam        # 計算內附的費氏數列範例
    python main.py -e "(\\x. x) y"               # 直接計算一行運算式
    python main.py examples/factorial.lam -q     # 只顯示最後結果

選項：
    -e, --expr EXPR   直接給定運算式（不讀檔案）
    --max-steps N     最多歸約步數（預設 100000，防止不停機）
    -q, --quiet       只顯示結果，不顯示每一步的計算過程
    --redex           每一步額外標示所歸約的 redex
"""

import argparse
import os
import sys

from lambda_engine import (
    DEFAULT_MAX_STEPS,
    evaluate,
    evaluate_program,
    parse,
    to_str,
)

# 讓 Windows 主控台也能正確顯示中文
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 專案資料夾，用來找內建範例
HERE = os.path.dirname(os.path.abspath(__file__))
EXAMPLES = os.path.join(HERE, "examples")


def print_trace(title, trace, show_redex=False, quiet=False):
    """印出單一運算式的計算過程與結果。"""
    print("=" * 70)
    print(f"目標：{title}")
    print("=" * 70)

    steps = trace["steps"]
    if not quiet:
        print(f"計算過程（Normal order，共 {trace['count']} 步）：")
        for i, term in enumerate(steps):
            if show_redex and i > 0:
                print(f"{i:>6}: {term}")
                print(f"        ↳ redex: {trace['redexes'][i - 1]}")
            else:
                print(f"{i:>6}: {term}")
        print("-" * 70)

    if trace["truncated"]:
        print(f"（已達 --max-steps={len(steps) - 1} 上限，尚未化成 normal form）")

    print(f"結果：{to_str(trace['result'])}")
    print(f"β-歸約步數：{trace['count']}")
    print()


def run_file(path, show_redex=False, quiet=False, max_steps=DEFAULT_MAX_STEPS):
    with open(path, "r", encoding="utf-8") as handle:
        text = handle.read()
    print(f"# 檔案：{path}\n")
    traces = evaluate_program(text, max_steps=max_steps)
    if not traces:
        print("（檔案中沒有可計算的運算式）")
        return
    for trace in traces:
        title = trace["source"]
        print_trace(title, trace, show_redex=show_redex, quiet=quiet)


def run_expr(source, show_redex=False, quiet=False, max_steps=DEFAULT_MAX_STEPS):
    trace = evaluate(parse(source), defs=None, max_steps=max_steps)
    print_trace(source, trace, show_redex=show_redex, quiet=quiet)


def run_bundled_examples(show_redex=False, quiet=False, max_steps=DEFAULT_MAX_STEPS):
    """跑內附的兩個範例檔。"""
    paths = [
        os.path.join(EXAMPLES, name)
        for name in ("factorial.lam", "fibonacci.lam")
    ]
    for path in paths:
        if os.path.exists(path):
            run_file(path, show_redex=show_redex, quiet=quiet, max_steps=max_steps)


def print_usage_hint():
    print(__doc__)
    print("內附範例：")
    for name in ("factorial.lam", "fibonacci.lam"):
        if os.path.exists(os.path.join(EXAMPLES, name)):
            print(f"    python main.py examples/{name}")
    print("\n提示：Church 數的完整歸約步數很多（fact 3 約 646 步），")
    print("      可加 -q 只看結果，或把輸出重導到檔案：")
    print("      python main.py examples/factorial.lam > out.txt")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Lambda Calculus 解譯器（Normal order，顯示完整計算過程）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("file", nargs="?", help="要計算的 .lam 檔")
    parser.add_argument("-e", "--expr", help="直接給定運算式字串")
    parser.add_argument(
        "--max-steps",
        type=int,
        default=DEFAULT_MAX_STEPS,
        help=f"最多歸約步數（預設 {DEFAULT_MAX_STEPS}）",
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="只顯示結果")
    parser.add_argument(
        "--redex", action="store_true", help="每一步額外標示所歸約的 redex"
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    try:
        if args.expr is not None:
            run_expr(args.expr, args.redex, args.quiet, args.max_steps)
        elif args.file:
            run_file(args.file, args.redex, args.quiet, args.max_steps)
        else:
            print_usage_hint()
    except SyntaxError as exc:
        print(f"語法錯誤：{exc}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"找不到檔案：{args.file}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
