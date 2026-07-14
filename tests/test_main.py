import subprocess
import sys
import textwrap
from unittest.mock import patch
from main import run


class TestRun:
    def test_full_pipeline_executes_commands(self, capsys):
        run([
            "Board:",
            "wR .",
            ". bK",
            "Commands:",
            "print board",
        ])
        assert capsys.readouterr().out == "wR .\n. bK\n"

    def test_unknown_command_line_is_skipped(self, capsys):
        run([
            "Board:",
            "wR",
            "Commands:",
            "dance 1 2",
            "print board",
        ])
        assert capsys.readouterr().out == "wR\n"

    def test_invalid_board_prints_error(self, capsys):
        run([
            "Board:",
            "wR wR",
            "wR",
            "Commands:",
        ])
        out = capsys.readouterr().out
        assert out.startswith("ERROR ")

    def test_click_wait_and_capture_flow_end_to_end(self, capsys):
        run([
            "Board:",
            "wR bK",
            "Commands:",
            "click 0 0",
            "click 100 0",
            "wait 1000",
            "print board",
        ])
        assert capsys.readouterr().out == ". wR\n"


class TestMainSubprocess:
    """main() itself (reading real stdin) is a one-line wrapper around
    run(); it is exercised end-to-end via a real subprocess with piped
    stdin (no monkeypatching), which also implicitly proves run() and
    main() are wired together correctly."""

    def test_main_reads_real_stdin(self):
        # הגדרת משתנה סביבה לזיהוי ריצה בבדיקות
        env = __import__("os").environ.copy()
        env["IS_TESTING"] = "1"
        
        script = textwrap.dedent("""
            import sys
            import os
            from main import main
            main()
        """)
        
        project_dir = __import__("os").path.dirname(__import__("os").path.dirname(__file__))
        env["PYTHONPATH"] = project_dir
        
        result = subprocess.run(
            [sys.executable, "-c", script],
            input="Board:\nwR .\nCommands:\nprint board\n",
            capture_output=True,
            text=True,
            env=env,
            cwd=project_dir,
        )
        
        assert result.returncode == 0, result.stderr
        assert result.stdout == "wR .\n"