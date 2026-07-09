import asyncio

import pytest

pytest.importorskip("textual")

from textual.widgets import Static, TextArea

from nobots.tui.app import NobotsTUI

AI_SAMPLE = (
    "In today's rapidly evolving landscape, we must delve into the multifaceted "
    "tapestry of innovation. This is a testament to progress. It underscores the "
    "importance of synergy. Furthermore, we leverage seamless solutions — every day "
    "— to foster growth — across teams — and streamline outcomes — at scale — for "
    "all. Moreover, this pivotal moment cannot be overstated. It is important to "
    "note that we embark on a journey. We utilize holistic frameworks. We showcase "
    "meticulous care. We emphasize intricate detail. Nevertheless, the paramount "
    "goal remains. It plays a crucial role. This marks a pivotal moment for us all."
)


def test_typing_ai_text_renders_detection() -> None:
    async def scenario() -> str:
        app = NobotsTUI()
        async with app.run_test() as pilot:
            input_area = app.query_one("#input", TextArea)
            input_area.text = AI_SAMPLE
            input_area.post_message(TextArea.Changed(input_area))
            await pilot.pause()
            output = app.query_one("#output", Static)
            return str(output.render())

    rendered = asyncio.run(scenario())
    assert "AI Tells Found: True" in rendered
    assert "Signals Agree" in rendered
