"""Tests for the `npy` command line tool (Lib/npy/)."""

import os
import subprocess
import sys
import tempfile
import unittest

# Repository root: Lib/test/test_npy.py -> <root>
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NPY = os.path.join(ROOT, "npy")
PYTHON = os.path.join(ROOT, "python")

# Make the in-tree `npy` package importable.
sys.path.insert(0, os.path.join(ROOT, "Lib"))
from npy.cli import argv_for, find_python  # noqa: E402


def run_npy(args, **kwargs):
    return subprocess.run([sys.executable, NPY] + args,
                          capture_output=True, text=True, **kwargs)


class NpyCommandTests(unittest.TestCase):
    """The command vectors built by the CLI (no interpreter executed)."""

    NPYTHON = "/fake/path/to/python"

    def test_run(self):
        self.assertEqual(
            argv_for("run", ["script.py"], self.NPYTHON),
            [self.NPYTHON, "script.py"],
        )
        self.assertEqual(
            argv_for("run", ["script.py", "a", "b=c"], self.NPYTHON),
            [self.NPYTHON, "script.py", "a", "b=c"],
        )

    def test_run_requires_a_file(self):
        with self.assertRaises(ValueError):
            argv_for("run", [], self.NPYTHON)

    def test_shell(self):
        self.assertEqual(argv_for("shell", [], self.NPYTHON), [self.NPYTHON])

    def test_install(self):
        self.assertEqual(
            argv_for("install", ["requests"], self.NPYTHON),
            [self.NPYTHON, "-m", "pip", "install", "requests"],
        )
        self.assertEqual(
            argv_for("install", ["a", "b"], self.NPYTHON),
            [self.NPYTHON, "-m", "pip", "install", "a", "b"],
        )

    def test_uninstall(self):
        self.assertEqual(
            argv_for("uninstall", ["requests"], self.NPYTHON),
            [self.NPYTHON, "-m", "pip", "uninstall", "-y", "requests"],
        )

    def test_list(self):
        self.assertEqual(
            argv_for("list", [], self.NPYTHON),
            [self.NPYTHON, "-m", "pip", "list"],
        )

    def test_pip(self):
        self.assertEqual(
            argv_for("pip", ["install", "requests"], self.NPYTHON),
            [self.NPYTHON, "-m", "pip", "install", "requests"],
        )

    def test_fallback_is_regular_python(self):
        # Without `run`, npy behaves like regular Python.
        argv = argv_for("-c", ["pass"], None)
        self.assertEqual(argv, [find_python(), "-c", "pass"])
        self.assertTrue(os.path.basename(argv[0]) in {"python3", "python"})


class NpyIntegrationTests(unittest.TestCase):

    @unittest.skipIf(not os.path.exists(NPY), "npy script not present")
    def test_version(self):
        proc = run_npy(["--version"])
        self.assertEqual(proc.returncode, 0)
        self.assertIn("npy 1.1 (npython)", proc.stdout)

    @unittest.skipIf(not os.path.exists(PYTHON),
                     "npython interpreter not built")
    def test_run_executes_file_with_npython(self):
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write("print('hello from npython')\n")
            name = f.name
        try:
            proc = run_npy(["run", name])
        finally:
            os.unlink(name)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout, "hello from npython\n")

    @unittest.skipIf(not os.path.exists(PYTHON),
                     "npython interpreter not built")
    def test_run_passes_arguments(self):
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write("import sys; print(sys.argv[1:])\n")
            name = f.name
        try:
            proc = run_npy(["run", name, "a", "b=c"])
        finally:
            os.unlink(name)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout, "['a', 'b=c']\n")

    def test_fallback_is_regular_python_process(self):
        # Without 'run', npy behaves like regular Python.
        proc = run_npy(["-c", "import sys; print(sys.implementation.name)"])
        self.assertEqual(proc.returncode, 0)
        self.assertIn(proc.stdout.strip(), {"cpython", "npython"})


if __name__ == "__main__":
    unittest.main()
