from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from . import __version__
from .engine import verify
from .evidence import write_receipt
from .policy import PolicyError, load_policy

EXIT = {"VERIFIED": 0, "ACTION_REQUIRED": 1, "INDETERMINATE": 2}

def _inside(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="guardian-pa", description="Publication assurance infrastructure")
    p.add_argument("--version", action="version", version=f"guardian-pa {__version__}")
    sub = p.add_subparsers(dest="command", required=True)
    v = sub.add_parser("verify", help="verify a repository before publication")
    v.add_argument("target", nargs="?", default=".")
    v.add_argument("--policy")
    v.add_argument("--receipt")
    v.add_argument("--json", action="store_true", dest="as_json")
    v.add_argument("--verbose", action="store_true")
    return p

def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command != "verify":
        return 2

    target = Path(args.target).resolve()
    try:
        policy = load_policy(args.policy)
    except PolicyError as exc:
        if args.as_json:
            print(json.dumps({"result": "INDETERMINATE", "error": "POLICY_ERROR"}))
        else:
            print("GUARDIAN\n")
            print("Verification could not complete")
            print("\nRESULT: INDETERMINATE")
            print("Reason: policy error", file=sys.stderr)
        return 2

    if args.receipt:
        receipt_path = Path(args.receipt).resolve()
        if _inside(receipt_path, target):
            print("Receipt output must be outside the target repository.", file=sys.stderr)
            return 2
    else:
        receipt_path = None

    verification = verify(target, policy)
    if receipt_path:
        try:
            write_receipt(verification.receipt, receipt_path)
        except OSError as exc:
            print("Could not write receipt.", file=sys.stderr)
            return 2

    if args.as_json:
        print(json.dumps(verification.receipt, indent=2, sort_keys=True))
    else:
        print("GUARDIAN\n")
        print("Verification complete\n")
        symbols = {"PASS": "✓", "FAIL": "!", "INDETERMINATE": "?"}
        for result in verification.checks:
            print(f"{symbols[result.status]} {result.name.title()}: {result.status}")
            if args.verbose:
                for finding in result.findings:
                    print(f"  - {finding.code}")
        print("\nEvidence: generated")
        if receipt_path:
            print("Receipt: written to requested location")
        print(f"\nRESULT: {verification.result}")

    return EXIT[verification.result]

if __name__ == "__main__":
    raise SystemExit(main())
