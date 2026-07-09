"""Minimal Textual TUI for live AI-tell detection.

Live surface over detect_text + clean_prose. As the user types, scans for
AI writing tells and shows families + summary. Pure UI — core logic lives
in nobots.core.detect and nobots.core.prose.
"""

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Header, Footer, TextArea, Static

from nobots.core.detect import detect_text
from nobots.core.prose import clean_prose


class NobotsTUI(App[None]):
    """TUI for live AI-tell detection."""

    CSS = """
    Screen {
        layout: vertical;
    }

    #input {
        height: 50%;
        border: solid $accent;
    }

    #output {
        height: 50%;
        border: solid $accent;
        overflow: auto;
    }

    TextArea {
        width: 1fr;
        height: 1fr;
    }
    """

    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        """Compose the TUI."""
        yield Header()
        with Vertical():
            yield TextArea(id="input", language="markdown", show_line_numbers=True)
            yield Static("Type here to scan for AI tells...", id="output")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize on mount."""
        self.query_one("#input", TextArea).focus()

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Re-run detection whenever the input text changes."""
        output = self.query_one("#output", Static)
        text = event.text_area.text
        if not text.strip():
            output.update("Type here to scan for AI tells...")
            return

        result = detect_text(clean_prose(text))

        lines = [f"AI Tells Found: {result.tells_found}"]
        lines.append(f"Signals Agree: {result.agree}/{result.quorum}")
        if result.families:
            lines.append("\nDetected Families:")
            for family, (vote, msg) in result.families.items():
                lines.append(f"  • {family} (vote={vote}): {msg}")
        if result.summary:
            lines.append(f"\nSummary: {result.summary}")
        if result.context:
            lines.append("\nMetrics:")
            for key, val in result.context.items():
                if val is not None:
                    val_str = f"{val:.2f}" if isinstance(val, float) else str(val)
                    lines.append(f"  • {key}: {val_str}")

        output.update("\n".join(lines))


def run_tui() -> None:
    """Entry point for the TUI."""
    app = NobotsTUI()
    app.run()


if __name__ == "__main__":
    run_tui()
