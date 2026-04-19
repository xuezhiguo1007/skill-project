from __future__ import annotations

import argparse
import json

from skill_project.services.skill_service import (
    SCENARIOS,
    list_skills,
    run_scenario,
    run_scenario_with_prompt,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate DeepAgents skill routing with local skills."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-skills", help="List configured local skills.")

    run_parser = subparsers.add_parser("run", help="Run a verification scenario.")
    run_parser.add_argument(
        "--scenario",
        choices=sorted(SCENARIOS),
        required=True,
        help="Which validation scenario to run.",
    )
    run_parser.add_argument(
        "--model",
        default="gpt-4.1-mini",
        help="Override the configured OpenAI model name.",
    )
    run_parser.add_argument(
        "--prompt",
        help="Override the built-in scenario prompt.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.command == "list-skills":
        print(json.dumps(list_skills(), ensure_ascii=False, indent=2))
        return

    if args.command == "run":
        if args.prompt:
            result = run_scenario_with_prompt(
                scenario=args.scenario,
                prompt=args.prompt,
                model_name=args.model,
            )
        else:
            result = run_scenario(
                scenario=args.scenario,
                model_name=args.model,
            )
        print(f"# {result['title']}\n")
        print("## Prompt\n")
        print(result["prompt"])
        print("\n## Response\n")
        print(result["response"])
        return

    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
