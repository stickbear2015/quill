from __future__ import annotations

from quill.ui.main_frame import MainFrame


class _Frame:
    pass


class _Wx:
    def __init__(self, single_choice: str = "", texts: list[str] | None = None) -> None:
        self._single_choice = single_choice
        self._texts = list(texts) if texts is not None else []
        self.single_choice_calls: list[tuple[str, ...]] = []
        self.text_calls: list[str] = []

    def GetSingleChoice(self, message, caption, choices, parent=None):  # noqa: N802
        self.single_choice_calls.append((message, caption))
        return self._single_choice

    def GetTextFromUser(self, message, caption, parent=None):  # noqa: N802
        self.text_calls.append(message)
        if self._texts:
            return self._texts.pop(0)
        return ""


def _build_frame(wx: _Wx) -> MainFrame:
    frame = MainFrame.__new__(MainFrame)
    frame.frame = _Frame()
    frame._wx = wx
    frame._status: list[str] = []
    frame._set_status = lambda message: frame._status.append(message)
    return frame


def test_prompt_heading_style_levels_all_runs_without_nameerror() -> None:
    # Regression for BUG-2: these prompts previously called bare wx.* and
    # raised NameError because wx is only stored as self._wx.
    wx = _Wx(single_choice="All heading levels")
    frame = _build_frame(wx)

    result = frame._prompt_heading_style_levels("markdown")

    assert result == set(range(1, 7))
    assert wx.single_choice_calls  # the choice dialog was reached, no NameError


def test_prompt_heading_style_runs_without_nameerror() -> None:
    wx = _Wx(single_choice="Keep existing", texts=["Arial", ""])
    frame = _build_frame(wx)

    style = frame._prompt_heading_style()

    assert style is not None
    assert style.font_family == "Arial"
    # Font family, size, and alignment prompts all executed.
    assert len(wx.text_calls) == 2
    assert wx.single_choice_calls
