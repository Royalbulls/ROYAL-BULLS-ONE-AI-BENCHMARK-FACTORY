import argparse
from pathlib import Path
from .generator import generate_task
from .runner import evaluate_candidate

def main():
    parser = argparse.ArgumentParser(prog="benchmark-factory")
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate", help="Generate a sample coding benchmark task")
    gen.add_argument("--title", default="Add two numbers")
    gen.add_argument("--output", default="data/tasks")
    ev = sub.add_parser("evaluate", help="Evaluate a candidate solution")
    ev.add_argument("--task", required=True)
    ev.add_argument("--candidate", required=True)
    ev.add_argument("--output", default="data/reports")
    args = parser.parse_args()
    if args.command == "generate":
        print(f"Task generated: {generate_task(args.title, Path(args.output))}")
    else:
        report = evaluate_candidate(Path(args.task), Path(args.candidate), Path(args.output))
        print(f"Report: {report}")
        print(report.read_text(encoding="utf-8"))

if __name__ == "__main__":
    main()
