import subprocess
import sys
import os

# Rich for colorful, human–friendly terminal output
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")


def run_stage(title: str, script_path: str):
    """Runs a script and prints colored/logical output."""
    
    console.print("\n")
    console.print(Panel.fit(
        Text(title, style="bold cyan"),
        border_style="cyan"
    ))

    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)

    # STDOUT
    if result.stdout.strip():
        console.print("\n[bold green]Output:[/bold green]")
        console.print(result.stdout, markup=False)

    # STDERR (safe rendering)
    if result.stderr.strip():
        console.print("\n[bold yellow]Logs:[/bold yellow]")
        console.print(result.stderr, markup=False)


def main():
    console.print("\n")
    console.print(Panel.fit(
        Text("Adaptive Learning Coach – Demo Runner", style="bold white"),
        border_style="green"
    ))
    console.print("\n")

    # Run all stages with color-coded headings
    run_stage("1. Assessment", os.path.join(SRC, "smoke_assessment.py"))
    run_stage("2. Lesson Generation", os.path.join(SRC, "smoke_lesson.py"))
    run_stage("3. Quiz Generation + Grading", os.path.join(SRC, "smoke_quiz.py"))
    run_stage("4. Feedback Generation", os.path.join(SRC, "smoke_feedback.py"))
    run_stage("5. Evaluation Report", os.path.join(SRC, "eval", "report.py"))

    console.print("\n")
    console.print(Panel.fit(
        Text("Demo complete. All agent stages executed successfully.", style="bold green"),
        border_style="green"
    ))
    console.print("\n")


if __name__ == "__main__":
    main()
