
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from ai_client import generate_response
from chat_mode import chat_mode
from history import view_chat_history

console = Console()


def main():
    while True:
        console.print(
            Panel(
                "[bold cyan]1.[/] Summarize Text\n"
                "[bold cyan]2.[/] Translate Text\n"
                "[bold cyan]3.[/] Sentiment Analysis\n"
                "[bold cyan]4.[/] Exit\n"
                "[bold cyan]5.[/] Chat Mode\n"
                "[bold cyan]6.[/] View Chat History",
                title="Python AI Toolkit",
                border_style="cyan"
            )
        )

        choice = Prompt.ask("Choose an option")

        if choice == "1":
            text = Prompt.ask("Enter text to summarize")
            prompt = f"Summarize this text clearly:\n{text}"

        elif choice == "2":
            text = Prompt.ask("Enter text to translate")
            language = Prompt.ask("Translate into which language?")
            prompt = f"Translate this text into {language}:\n{text}"

        elif choice == "3":
            text = Prompt.ask("Enter text for sentiment analysis")
            prompt = (
                "Analyze the sentiment as Positive, Negative, or Neutral "
                "and explain briefly:\n" + text
            )

        elif choice == "4":
            console.print("[bold green]Thank you for using Python AI Toolkit![/bold green]")
            break

        elif choice == "5":
            chat_mode()

        elif choice == "6":
            view_chat_history()

        else:
            console.print("[red]Invalid choice. Try again.[/red]")
            continue

        if choice in ("1", "2", "3"):
            try:
                with console.status("[cyan]AI is thinking...[/cyan]"):
                    answer = generate_response(prompt)

                console.print(
                    Panel(answer, title="AI Response", border_style="green")
                )

            except Exception as error:
                console.print(f"[red]Error: {error}[/red]")


if __name__ == "__main__":
    main()
