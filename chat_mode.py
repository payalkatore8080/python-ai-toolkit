
import json
from datetime import datetime
from pathlib import Path

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

# Store history in the same folder as this Python file
HISTORY_FILE = Path(__file__).parent / "chat_history.json"

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:3b"


def save_chat(conversation_history):
    """Save the conversation to a JSON file."""

    if not conversation_history:
        console.print("[yellow]No conversation to save.[/yellow]")
        return

    saved_chats = []

    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                saved_chats = json.load(file)

            if not isinstance(saved_chats, list):
                saved_chats = []

        except (json.JSONDecodeError, OSError):
            saved_chats = []

    chat_record = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "messages": conversation_history
    }

    saved_chats.append(chat_record)

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(
            saved_chats,
            file,
            indent=4,
            ensure_ascii=False
        )

    console.print("[bold green]Chat history saved successfully![/bold green]")


def chat_mode():

    conversation_history = []

    console.print(
        Panel(
            "[bold cyan]Welcome to AI Chat Mode![/bold cyan]\n"
            "Ask me anything.\n"
            "Type 'exit' to end the conversation.",
            title="Python AI Toolkit",
            border_style="cyan"
        )
    )

    while True:

        user_message = Prompt.ask("[bold green]You[/bold green]")

        if user_message.strip().lower() == "exit":

            try:
                save_chat(conversation_history)

            except (OSError, TypeError, ValueError) as error:
                console.print(f"[red]Save error: {error}[/red]")

            console.print("[yellow]Chat ended. Goodbye![/yellow]")
            break

        conversation_history.append({
            "role": "user",
            "content": user_message
        })

        try:
            with console.status("[cyan]AI is thinking...[/cyan]"):

                response = httpx.post(
                    OLLAMA_URL,
                    json={
                        "model": MODEL,
                        "messages": conversation_history,
                        "stream": False
                    },
                    timeout=120.0
                )

                response.raise_for_status()

                answer = response.json()["message"]["content"]

            conversation_history.append({
                "role": "assistant",
                "content": answer
            })

            console.print(
                Panel(
                    answer,
                    title="AI Assistant",
                    border_style="green"
                )
            )

        except httpx.HTTPError as error:
            console.print(f"[red]Connection error: {error}[/red]")


if __name__ == "__main__":
    chat_mode()
