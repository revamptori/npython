"""Command line interface for ``npy``, the npython tool.

``npy run file.py [args...]`` executes *file.py* with npython.
``npy install|uninstall|list|pip`` manage Python packages through npython's own
pip, so libraries install into npython's site-packages and work natively.
Any other invocation falls back to a regular Python interpreter: only
``npy run`` is npython, everything else is Python.
"""

from __future__ import annotations

import os
import shutil
import sys
from typing import Optional, Sequence

from . import __version__

NPYTHON_NOT_FOUND = 2

# Subcommands that are executed with the npython interpreter itself.
_NPYTHON_COMMANDS = frozenset({"run", "install", "uninstall", "list", "pip", "shell"})


def _norm(path: str) -> str:
    return os.path.normpath(path)


def find_npython() -> Optional[str]:
    """Return the path of the npython interpreter, or None if not found."""
    override = os.environ.get("NPY_PYTHON")
    if override:
        return override

    # cli.py lives in <prefix>/lib/pythonX.Y/npy/ (installed) or
    # <repo>/Lib/npy/ (source tree).  The npython binary is either at the
    # repository root (source tree) or in <prefix>/bin (installed).
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        _norm(os.path.join(here, "..", "..", "python")),
        _norm(os.path.join(here, "..", "..", "bin", "python3.16")),
        _norm(os.path.join(here, "..", "..", "bin", "python3")),
        _norm(os.path.join(here, "..", "..", "bin", "python")),
    ]
    for candidate in candidates:
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


def find_python() -> str:
    """Return a regular Python interpreter (used for the non-``run`` fallback)."""
    return shutil.which("python3") or shutil.which("python") or "python3"


def _exec_or_die(binary: str, argv: list) -> None:
    try:
        os.execv(binary, argv)
    except OSError as exc:
        print(f"npy: failed to execute {binary}: {exc}", file=sys.stderr)
        sys.exit(127)


def _npython_not_found() -> int:
    print(
        "npy: the npython interpreter was not found. "
        "Build npython first (./configure && make python) or set NPY_PYTHON.",
        file=sys.stderr,
    )
    return NPYTHON_NOT_FOUND


def argv_for(command: str, args: Sequence[str], npython: Optional[str]) -> list:
    """Build the argument vector to execute for *command*.

    Used by :func:`main` and by tests (no interpreter is executed).
    """
    if command == "run":
        if not args:
            raise ValueError("'run' requires a file argument")
        # sys.argv[0] of the executed program is the script being run.
        return [npython, args[0]] + list(args[1:])
    if command == "shell":
        return [npython]
    if command == "pip":
        return [npython, "-m", "pip"] + list(args)
    if command == "install":
        return [npython, "-m", "pip", "install"] + list(args)
    if command == "uninstall":
        # Non-interactive by default.
        return [npython, "-m", "pip", "uninstall", "-y"] + list(args)
    if command == "list":
        return [npython, "-m", "pip", "list"] + list(args)
    # Anything else: regular Python ("otherwise it's python").
    return [find_python(), command] + list(args)


def main(argv: Optional[Sequence[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    if "--version" in argv or "-V" in argv:
        print(f"npy {__version__} (npython)")
        return 0

    if not argv:
        # No subcommand: behave like regular Python (interactive REPL).
        _exec_or_die(find_python(), [find_python()])
        return 0  # unreachable

    command, args = argv[0], argv[1:]
    npython = find_npython()

    if command == "run":
        if not args:
            print("npy: 'run' requires a file argument", file=sys.stderr)
            return 2
        if npython is None:
            return _npython_not_found()

    if command in _NPYTHON_COMMANDS and npython is None:
        return _npython_not_found()

    exec_argv = argv_for(command, args, npython)
    _exec_or_die(exec_argv[0], exec_argv)
    return 0  # unreachable
