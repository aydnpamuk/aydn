import argparse


def compute_roi(revenue: float, cost: float) -> float:
    """Compute Return on Investment (ROI)."""
    if cost == 0:
        return 0.0
    return (revenue - cost) / cost


def main() -> None:
    parser = argparse.ArgumentParser(description="Codex Starter CLI")
    subparsers = parser.add_subparsers(dest="command")

    hello_parser = subparsers.add_parser("hello", help="Print hello")
    hello_parser.add_argument("--name", default="World", help="Name to greet")

    roi_parser = subparsers.add_parser("roi", help="Calculate ROI")
    roi_parser.add_argument("--revenue", type=float, required=True)
    roi_parser.add_argument("--cost", type=float, required=True)

    args = parser.parse_args()

    if args.command == "hello":
        print(f"Hello, {args.name}!")
    elif args.command == "roi":
        roi = compute_roi(args.revenue, args.cost)
        print(f"ROI: {roi:.2%}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
