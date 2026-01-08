import argparse
import sys
from typing import Any, Dict, List, Optional

import service


class CLIError(Exception):
    """Custom exception for CLI-related errors."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="TaskManager CLI - správa úloh",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Přidá novou úlohu")
    add_parser.add_argument("--title", required=True, help="Název úlohy")
    add_parser.add_argument(
        "--description", required=False, default="", help="Popis úlohy"
    )
    add_parser.add_argument(
        "--due",
        required=False,
        help="Termín dokončení ve formátu YYYY-MM-DD nebo ISO 8601",
    )
    add_parser.add_argument(
        "--priority",
        required=False,
        default="medium",
        choices=["low", "medium", "high"],
        help="Priorita úlohy",
    )

    list_parser = subparsers.add_parser("list", help="Vypíše úlohy s filtrem")
    list_parser.add_argument(
        "--status",
        required=False,
        choices=["todo", "in-progress", "done"],
        help="Filtrovat podle stavu",
    )
    list_parser.add_argument(
        "--priority",
        required=False,
        choices=["low", "medium", "high"],
        help="Filtrovat podle priority",
    )
    list_parser.add_argument(
        "--before",
        required=False,
        help="Filtrovat úlohy s termínem před datem (YYYY-MM-DD nebo ISO 8601)",
    )

    update_parser = subparsers.add_parser("update", help="Aktualizuje stav úlohy")
    update_parser.add_argument("--id", required=True, type=int, help="ID úlohy")
    update_parser.add_argument(
        "--status",
        required=True,
        choices=["todo", "in-progress", "done"],
        help="Nový stav úlohy",
    )

    remove_parser = subparsers.add_parser("remove", help="Odstraní úlohu")
    remove_parser.add_argument("--id", required=True, type=int, help="ID úlohy")

    show_parser = subparsers.add_parser("show", help="Zobrazí detail úlohy")
    show_parser.add_argument("--id", required=True, type=int, help="ID úlohy")

    return parser


def format_task(task: Dict[str, Any]) -> str:
    return (
        f"ID: {task.get('id')}\n"
        f"Title: {task.get('title')}\n"
        f"Description: {task.get('description', '')}\n"
        f"Due: {task.get('due') or '-'}\n"
        f"Priority: {task.get('priority')}\n"
        f"Status: {task.get('status')}\n"
    )


def format_task_row(task: Dict[str, Any]) -> str:
    return (
        f"[{task.get('id')}] "
        f"{task.get('title')} | "
        f"status: {task.get('status')} | "
        f"priority: {task.get('priority')} | "
        f"due: {task.get('due') or '-'}"
    )


def handle_add(args: argparse.Namespace) -> int:
    task = service.add_task(
        title=args.title,
        description=args.description,
        due=args.due,
        priority=args.priority,
    )
    print("Úloha vytvořena:")
    print(format_task(task))
    return 0


def handle_list(args: argparse.Namespace) -> int:
    tasks = service.list_tasks(
        status=args.status,
        priority=args.priority,
        before=args.before,
    )
    if not tasks:
        print("Žádné úlohy k zobrazení.")
        return 0

    for task in tasks:
        print(format_task_row(task))
    return 0


def handle_update(args: argparse.Namespace) -> int:
    updated = service.update_status(task_id=args.id, status=args.status)
    print("Úloha aktualizována:")
    print(format_task(updated))
    return 0


def handle_remove(args: argparse.Namespace) -> int:
    service.remove_task(task_id=args.id)
    print(f"Úloha {args.id} odstraněna.")
    return 0


def handle_show(args: argparse.Namespace) -> int:
    task = service.get_task(task_id=args.id)
    print(format_task(task))
    return 0


def dispatch(args: argparse.Namespace) -> int:
    command_map = {
        "add": handle_add,
        "list": handle_list,
        "update": handle_update,
        "remove": handle_remove,
        "show": handle_show,
    }
    handler = command_map.get(args.command)
    if handler is None:
        raise CLIError(f"Neznámý příkaz: {args.command}")
    return handler(args)


def run(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        return dispatch(args)
    except CLIError as cli_err:
        print(f"Chyba: {cli_err}", file=sys.stderr)
        return 1
    except service.ValidationError as val_err:
        print(f"Chyba validace: {val_err}", file=sys.stderr)
        return 2
    except service.NotFoundError as nf_err:
        print(f"Nenalezeno: {nf_err}", file=sys.stderr)
        return 3
    except service.StorageError as st_err:
        print(f"Chyba úložiště: {st_err}", file=sys.stderr)
        return 4
    except Exception as exc:  # pragma: no cover - fallback
        print(f"Neočekávaná chyba: {exc}", file=sys.stderr)
        return 9


if __name__ == "__main__":
    sys.exit(run())
