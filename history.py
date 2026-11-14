
import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

console = Console()

HISTORY_FILE = Path(__file__).parent / "chat_history.json"


def view_chat_history():

    if not HISTORY_FILE.exists():
        console.print("[yellow]No chat history found.[/yellow]")
        return

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            saved_chats = json.load(file)

    except (json.JSONDecodeError, OSError) as error:
        console.print(f"[red]Could not read history: {error}[/red]")
        return

    if not saved_chats:
        console.print("[yellow]Your chat history is empty.[/yellow]")
        return

    console.print(
        Panel(
            "[bold cyan]Your Previous Conversations[/bold cyan]",
            border_style="cyan"
        )
    )

    for index, chat in enumerate(saved_chats, start=1):

        console.print(
            f"\n[bold yellow]Conversation {index}[/bold yellow]"
        )
        console.print(f"[dim]Date: {chat.get('date', 'Unknown')}[/dim]")

        for message in chat.get("messages", []):

            role = message.get("role", "unknown")
            content = message.get("content", "")

            if role == "user":
                console.print(f"[bold green]You:[/bold green] {content}")

            elif role == "assistant":
                console.print(
                    f"[bold cyan]AI Assistant:[/bold cyan] {content}"
                )

        console.print("-" * 60)


if __name__ == "__main__":
    view_chat_history()
