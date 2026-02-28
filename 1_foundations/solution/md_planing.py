"""
md_planing.py — Agentic task loop with markdown plan tracking and rich CLI output.

The agent receives a complex task, writes a structured TODO plan to plan.md,
and updates that file as it works through each step.  Progress is streamed to
the terminal via the `rich` library.

Usage:
    uv run md_planing.py
"""

# Force UTF-8 output on Windows so rich can render emoji without codec errors.
import io
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# %%
import json
import os
import textwrap

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.rule import Rule
from rich.text import Text
from rich import box

from ai_tools.tools import LLMQuery
from ai_tools.utils import handle_tool_call

# ---------------------------------------------------------------------------
# Rich console (single shared instance)
# ---------------------------------------------------------------------------
# force_terminal=True prevents rich from falling back to the legacy Windows
# renderer (which uses the old WriteConsoleW API and chokes on emoji).
console = Console(force_terminal=True, highlight=False)

PLAN_FILE = os.path.join(os.path.dirname(__file__), "plan.md")

# ---------------------------------------------------------------------------
# Markdown file helpers (tools exposed to the LLM)
# ---------------------------------------------------------------------------


def write_plan(content: str) -> str:
    """Write the full markdown plan to disk, overwriting any previous version."""
    with open(PLAN_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    console.print(Rule("[bold cyan]📝 Plan written to plan.md[/bold cyan]"))
    console.print(Markdown(content))
    return "Plan written successfully."


def read_plan() -> str:
    """Read and return the current markdown plan from disk."""
    if not os.path.exists(PLAN_FILE):
        return "(plan.md does not exist yet)"
    with open(PLAN_FILE, "r", encoding="utf-8") as f:
        return f.read()


def update_plan(content: str) -> str:
    """Overwrite plan.md with an updated version of the markdown plan."""
    with open(PLAN_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    console.print(Rule("[bold yellow]🔄 Plan updated[/bold yellow]"))
    console.print(Markdown(content))
    return "Plan updated successfully."


def task_complete(summary: str) -> str:
    """
    Signal that the task is fully done.

    Call this as the very last tool when ALL checklist items are complete.
    Pass a short summary of what was accomplished.
    """
    console.print(
        Panel(
            Text(summary, justify="left"),
            title="[bold green]✅ Task Complete[/bold green]",
            border_style="green",
            box=box.DOUBLE_EDGE,
        )
    )
    return f"TASK_COMPLETE: {summary}"


# ---------------------------------------------------------------------------
# Tool schemas (OpenAI function-calling format)
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "write_plan",
            "description": (
                "Write the initial markdown task plan to plan.md. "
                "The plan MUST be a markdown TODO list with checkboxes (- [ ] item). "
                "Call this FIRST before doing anything else."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Full markdown content of the plan (with checkbox items).",
                    }
                },
                "required": ["content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_plan",
            "description": "Read the current plan.md to check which items remain open.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_plan",
            "description": (
                "Update plan.md by rewriting it with completed items checked off "
                "(- [x] item) and any new sub-tasks added. "
                "Call this after finishing each step."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The full updated markdown content.",
                    }
                },
                "required": ["content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "task_complete",
            "description": (
                "Signal that ALL checklist items are done and the task is finished. "
                "Call this exactly once as the final action."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "A brief human-readable summary of what was accomplished.",
                    }
                },
                "required": ["summary"],
            },
        },
    },
]

FUNCTIONS = [write_plan, read_plan, update_plan, task_complete]

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = textwrap.dedent("""
    You are an expert planning assistant that solves complex tasks by following
    a strict, tool-driven workflow:

    1. **write_plan** — ALWAYS start by calling `write_plan` with a markdown
       checklist of every step needed to complete the task.
       Example plan format:
       ```
       # Task: <short title>

       ## Steps
       - [ ] Step 1: ...
       - [ ] Step 2: ...
       - [ ] Step 3: ...
       ```

    2. Work through steps one by one. For each step:
       a. Think through what needs to be done.
       b. Do the work (reason, calculate, research, produce output, etc.).
       c. Call `update_plan` to mark the step complete (- [x]) and add any
          sub-tasks you discovered along the way.

    3. When EVERY item is checked off, call `task_complete` with a short
       summary of the results.

    Rules:
    - Always use tools — never just reply with text alone.
    - Never skip `write_plan` at the start.
    - Be thorough but concise.
    - After completing a step, always call `update_plan` before moving on.
""").strip()

# ---------------------------------------------------------------------------
# Agentic loop
# ---------------------------------------------------------------------------


def run_agent(task: str, max_iterations: int = 30) -> None:
    """
    Run the planning agent on *task*.

    The agent will:
      1. Receive the task.
      2. Write a markdown plan.
      3. Work through the plan step by step, updating plan.md after each step.
      4. Call task_complete when done.

    Args:
        task: The complex task description to solve.
        max_iterations: Safety cap on tool-call rounds.
    """
    console.print(
        Panel(
            Text(task, justify="left"),
            title="[bold magenta]🤖 Agentic Loop — Task[/bold magenta]",
            border_style="magenta",
            box=box.ROUNDED,
        )
    )

    llm = LLMQuery(
        system_prompt=SYSTEM_PROMPT,
        tools=TOOLS,
        functions=FUNCTIONS,
        tool_choice="auto",
    )

    # Initial query — hand the task to the agent
    console.print(Rule("[dim]Iteration 0 — initial query[/dim]"))
    response = llm.query(task)

    iteration = 0
    done = False

    while llm.tool_calls and iteration < max_iterations and not done:
        iteration += 1
        console.print(Rule(f"[dim]Iteration {iteration}[/dim]"))

        # --- Execute requested tool calls ---
        tool_responses = handle_tool_call(llm.tool_calls, functions=FUNCTIONS)

        # Pretty-print each tool invocation
        for tr in tool_responses:
            name = tr["name"]
            args = tr["arguments"]
            output = tr["output"]

            # Truncate large outputs for the status display
            output_preview = str(output)
            if len(output_preview) > 200:
                output_preview = output_preview[:200] + "…"

            args_str = json.dumps(args, ensure_ascii=False, indent=2)
            if len(args_str) > 300:
                args_str = args_str[:300] + "…"

            console.print(
                Panel(
                    f"[bold]Args:[/bold]\n{args_str}\n\n"
                    f"[bold]Result:[/bold] {output_preview}",
                    title=f"[cyan]🛠  {name}[/cyan]",
                    border_style="cyan",
                    box=box.SIMPLE_HEAVY,
                )
            )

            # Detect task completion signal
            if isinstance(output, str) and output.startswith("TASK_COMPLETE:"):
                done = True

        # Feed tool results back and let the agent continue
        llm.append_tool_result(tool_responses)

        if done:
            break

        response = llm.query(tools=TOOLS)

        # Print any text the agent emitted alongside the tool calls
        if response:
            console.print(
                Panel(
                    Markdown(response),
                    title="[bold green]💬 Agent[/bold green]",
                    border_style="green",
                    box=box.SIMPLE,
                )
            )

    if iteration >= max_iterations:
        console.print(
            Panel(
                "[yellow]Maximum iterations reached — stopping agent loop.[/yellow]",
                border_style="yellow",
            )
        )

    console.print(Rule("[bold]Loop finished[/bold]"))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    TASK = """
A train leaves Boston at 2:00 pm traveling 60 mph.
Another train leaves New York at 3:00 pm traveling 80 mph toward Boston.
When do they meet?
"""

    run_agent(TASK)

# %%
