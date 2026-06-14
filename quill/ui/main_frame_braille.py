"""Braille Mode Phase 1 commands (#234 / BR-011).

A mixin on :class:`~quill.ui.main_frame.MainFrame` holding the Braille menu
command handlers: status announcements, page navigation, and page-break tools.
Kept in its own module so the handlers (and their command registrations) do not
grow ``main_frame.py`` past its GATE-11 budget.

All handlers degrade gracefully when the active document is not a braille file
(``_active_brf_resolver`` returns None) or when there is no editor, so they are
safe to invoke from the command palette at any time.
"""

from __future__ import annotations


class BrailleCommandsMixin:
    """Phase 1 Braille command handlers (status, navigation, page tools)."""

    # The mixin relies on attributes/methods provided by MainFrame and its
    # other mixins: _active_brf_resolver, editor, settings, _announce,
    # _set_status, _move_point, _record_location_before_jump, _location_ring,
    # _show_modal_dialog, _show_message_box, _wx, _refresh_statusbar.

    def _build_braille_menu(self) -> object:
        """Build the top-level Braille menu (Status / Navigation / Page Tools)."""
        wx = self._wx
        self._id_braille_read_status = wx.NewIdRef()
        self._id_braille_read_detailed = wx.NewIdRef()
        self._id_braille_line_cell = wx.NewIdRef()
        self._id_braille_page = wx.NewIdRef()
        self._id_braille_print_page = wx.NewIdRef()
        self._id_braille_progress = wx.NewIdRef()
        self._id_braille_go_to_page = wx.NewIdRef()
        self._id_braille_next_page = wx.NewIdRef()
        self._id_braille_prev_page = wx.NewIdRef()
        self._id_braille_insert_break = wx.NewIdRef()
        self._id_braille_remove_break = wx.NewIdRef()
        self._id_braille_normalize = wx.NewIdRef()
        self._id_braille_recalc = wx.NewIdRef()

        menu = wx.Menu()
        status = wx.Menu()
        status.Append(
            self._id_braille_read_status,
            self._menu_label("Read &Status", "braille.read_status"),
        )
        status.Append(
            self._id_braille_read_detailed,
            self._menu_label("Read &Detailed Status", "braille.read_detailed_status"),
        )
        status.Append(
            self._id_braille_line_cell,
            self._menu_label("Read Current &Line and Cell", "braille.read_line_and_cell"),
        )
        status.Append(
            self._id_braille_page,
            self._menu_label("Read Current &Braille Page", "braille.read_braille_page"),
        )
        status.Append(
            self._id_braille_print_page,
            self._menu_label("Read Current &Print Page", "braille.read_print_page"),
        )
        status.Append(
            self._id_braille_progress,
            self._menu_label("Read Pro&gress Summary", "braille.read_progress_summary"),
        )
        menu.AppendSubMenu(status, "&Status")

        navigation = wx.Menu()
        navigation.Append(
            self._id_braille_go_to_page,
            self._menu_label("&Go to Braille Page...", "braille.go_to_page"),
        )
        navigation.Append(
            self._id_braille_next_page,
            self._menu_label("&Next Braille Page", "braille.next_page"),
        )
        navigation.Append(
            self._id_braille_prev_page,
            self._menu_label("&Previous Braille Page", "braille.previous_page"),
        )
        menu.AppendSubMenu(navigation, "&Navigation")

        page_tools = wx.Menu()
        page_tools.Append(
            self._id_braille_insert_break,
            self._menu_label("&Insert Braille Page Break", "braille.insert_page_break"),
        )
        page_tools.Append(
            self._id_braille_remove_break,
            self._menu_label("&Remove Braille Page Break", "braille.remove_page_break"),
        )
        page_tools.Append(
            self._id_braille_normalize,
            self._menu_label("Normalize &Line Endings", "braille.normalize_line_endings"),
        )
        page_tools.Append(
            self._id_braille_recalc,
            self._menu_label("Recalculate Page &Map", "braille.recalculate_page_map"),
        )
        menu.AppendSubMenu(page_tools, "&Page Tools")

        # Phase 5 (BR-022): the Translation submenu only appears when the
        # optional braille pack is installed (and not in safe mode), so users
        # never see disabled translation items.
        translation_items = self._braille_translation_items()
        if translation_items:
            translation = wx.Menu()
            self._id_braille_tr_g1 = wx.NewIdRef()
            self._id_braille_tr_g2 = wx.NewIdRef()
            self._id_braille_tr_sel = wx.NewIdRef()
            self._id_braille_back = wx.NewIdRef()
            translation.Append(
                self._id_braille_tr_g1,
                self._menu_label("Translate to UEB Grade &1", "braille.translate_ueb_g1"),
            )
            translation.Append(
                self._id_braille_tr_g2,
                self._menu_label("Translate to UEB Grade &2", "braille.translate_ueb_g2"),
            )
            translation.Append(
                self._id_braille_tr_sel,
                self._menu_label("Translate &Selection to UEB", "braille.translate_selection"),
            )
            translation.Append(
                self._id_braille_back,
                self._menu_label("&Back-Translate UEB (draft)", "braille.back_translate"),
            )
            menu.AppendSubMenu(translation, "&Translation")

        # Always offer the installer so a user without the pack can get it.
        self._id_braille_install = wx.NewIdRef()
        menu.Append(
            self._id_braille_install,
            self._menu_label("&Install Braille Pack...", "braille.install_pack"),
        )
        return menu

    def _braille_translation_items(self) -> list[tuple[str, str]]:
        """Return ``(label, command_id)`` for the Translation submenu, or [].

        Empty when the optional braille pack is not installed or QUILL is in
        safe mode, so the submenu is hidden rather than shown disabled.
        """
        from quill.core.braille_pack import is_braille_pack_installed

        if getattr(self, "_safe_mode", False) or not is_braille_pack_installed():
            return []
        return [
            ("Translate to UEB Grade 1", "braille.translate_ueb_g1"),
            ("Translate to UEB Grade 2", "braille.translate_ueb_g2"),
            ("Translate Selection to UEB", "braille.translate_selection"),
            ("Back-Translate UEB (draft)", "braille.back_translate"),
        ]

    def _bind_braille_menu(self) -> None:
        """Bind every Braille menu item to its handler.

        Bindings are written one id at a time (rather than a loop) so the menu
        contract test can statically match each ``id=self._id_*`` to a Bind.
        """
        wx = self._wx
        self.frame.Bind(
            wx.EVT_MENU, lambda _e: self.read_braille_status(), id=self._id_braille_read_status
        )
        self.frame.Bind(
            wx.EVT_MENU,
            lambda _e: self.read_detailed_braille_status(),
            id=self._id_braille_read_detailed,
        )
        self.frame.Bind(
            wx.EVT_MENU, lambda _e: self.read_current_line_and_cell(), id=self._id_braille_line_cell
        )
        self.frame.Bind(
            wx.EVT_MENU, lambda _e: self.read_current_braille_page(), id=self._id_braille_page
        )
        self.frame.Bind(
            wx.EVT_MENU, lambda _e: self.read_current_print_page(), id=self._id_braille_print_page
        )
        self.frame.Bind(
            wx.EVT_MENU, lambda _e: self.read_progress_summary(), id=self._id_braille_progress
        )
        self.frame.Bind(
            wx.EVT_MENU, lambda _e: self.go_to_braille_page(), id=self._id_braille_go_to_page
        )
        self.frame.Bind(
            wx.EVT_MENU, lambda _e: self.next_braille_page(), id=self._id_braille_next_page
        )
        self.frame.Bind(
            wx.EVT_MENU, lambda _e: self.previous_braille_page(), id=self._id_braille_prev_page
        )
        self.frame.Bind(
            wx.EVT_MENU,
            lambda _e: self.insert_braille_page_break(),
            id=self._id_braille_insert_break,
        )
        self.frame.Bind(
            wx.EVT_MENU,
            lambda _e: self.remove_braille_page_break(),
            id=self._id_braille_remove_break,
        )
        self.frame.Bind(
            wx.EVT_MENU,
            lambda _e: self.normalize_braille_line_endings(),
            id=self._id_braille_normalize,
        )
        self.frame.Bind(
            wx.EVT_MENU, lambda _e: self.recalculate_braille_page_map(), id=self._id_braille_recalc
        )
        self.frame.Bind(
            wx.EVT_MENU, lambda _e: self.install_braille_pack_command(), id=self._id_braille_install
        )
        if self._braille_translation_items():
            self.frame.Bind(
                wx.EVT_MENU, lambda _e: self.translate_to_ueb_g1(), id=self._id_braille_tr_g1
            )
            self.frame.Bind(
                wx.EVT_MENU, lambda _e: self.translate_to_ueb_g2(), id=self._id_braille_tr_g2
            )
            self.frame.Bind(
                wx.EVT_MENU,
                lambda _e: self.translate_selection_to_ueb(),
                id=self._id_braille_tr_sel,
            )
            self.frame.Bind(
                wx.EVT_MENU, lambda _e: self.back_translate_ueb(), id=self._id_braille_back
            )

    def _register_braille_commands(self) -> None:
        """Register every Phase 1 braille command with the command registry."""
        commands: list[tuple[str, str, object]] = [
            ("braille.read_status", "Read Braille Status", self.read_braille_status),
            (
                "braille.read_detailed_status",
                "Read Detailed Braille Status",
                self.read_detailed_braille_status,
            ),
            (
                "braille.read_line_and_cell",
                "Read Current Line and Cell",
                self.read_current_line_and_cell,
            ),
            (
                "braille.read_braille_page",
                "Read Current Braille Page",
                self.read_current_braille_page,
            ),
            ("braille.read_print_page", "Read Current Print Page", self.read_current_print_page),
            ("braille.read_progress_summary", "Read Progress Summary", self.read_progress_summary),
            ("braille.go_to_page", "Go to Braille Page...", self.go_to_braille_page),
            ("braille.next_page", "Next Braille Page", self.next_braille_page),
            ("braille.previous_page", "Previous Braille Page", self.previous_braille_page),
            (
                "braille.insert_page_break",
                "Insert Braille Page Break",
                self.insert_braille_page_break,
            ),
            (
                "braille.remove_page_break",
                "Remove Braille Page Break",
                self.remove_braille_page_break,
            ),
            (
                "braille.normalize_line_endings",
                "Normalize Line Endings",
                self.normalize_braille_line_endings,
            ),
            (
                "braille.recalculate_page_map",
                "Recalculate Page Map",
                self.recalculate_braille_page_map,
            ),
            ("braille.save_as_clean", "Save As Clean BRF", self.save_as_clean_brf),
            # Phase 5 (BR-022) translation commands + the optional pack installer.
            (
                "braille.translate_ueb_g1",
                "Translate to UEB Grade 1",
                self.translate_to_ueb_g1,
            ),
            (
                "braille.translate_ueb_g2",
                "Translate to UEB Grade 2",
                self.translate_to_ueb_g2,
            ),
            (
                "braille.translate_selection",
                "Translate Selection to UEB",
                self.translate_selection_to_ueb,
            ),
            ("braille.back_translate", "Back-Translate UEB", self.back_translate_ueb),
            ("braille.install_pack", "Install Braille Pack...", self.install_braille_pack_command),
        ]
        for command_id, label, handler in commands:
            self.commands.register(command_id, label, handler, self._binding_for(command_id))

    # ------------------------------------------------------------------
    # Resolution helper
    # ------------------------------------------------------------------

    def _braille_position(self) -> object | None:
        """Return ``(resolver, BraillePosition)`` for the caret, or None."""
        resolver = self._active_brf_resolver()
        editor = getattr(self, "editor", None)
        if resolver is None or editor is None:
            return None
        try:
            offset = editor.GetCurrentPos()
        except Exception:  # noqa: BLE001
            return None
        try:
            return resolver, resolver.resolve(offset)
        except (ValueError, TypeError, IndexError):
            return None

    def _announce_not_braille(self) -> None:
        self._set_status("Not a braille document")
        self._announce("This is not a braille document.")

    def _say(self, message: str) -> None:
        self._announce(message)
        self._set_status(message)

    # ------------------------------------------------------------------
    # Status commands
    # ------------------------------------------------------------------

    def read_braille_status(self) -> None:
        resolved = self._braille_position()
        if resolved is None:
            self._announce_not_braille()
            return
        _resolver, position = resolved
        from quill.core.braille_status import PrintPageInfo, spoken_status

        self._say(spoken_status(position, position.page_count, PrintPageInfo(), self.settings))

    def read_detailed_braille_status(self) -> None:
        resolved = self._braille_position()
        if resolved is None:
            self._announce_not_braille()
            return
        _resolver, position = resolved
        from quill.core.braille_status import (
            ConfidenceLevel,
            PrintPageInfo,
            ProofingStatus,
            detailed_status,
        )

        self._say(
            detailed_status(
                position,
                position.page_count,
                PrintPageInfo(),
                None,
                None,
                ProofingStatus(),
                ConfidenceLevel(),
                self.settings,
            )
        )

    def read_current_line_and_cell(self) -> None:
        resolved = self._braille_position()
        if resolved is None:
            self._announce_not_braille()
            return
        _resolver, p = resolved
        self._say(f"Line {p.line} of {p.line_count_in_page}. Cell {p.cell} of {p.cell_width}.")

    def read_current_braille_page(self) -> None:
        resolved = self._braille_position()
        if resolved is None:
            self._announce_not_braille()
            return
        _resolver, p = resolved
        self._say(f"Braille page {p.page} of {p.page_count}.")

    def read_current_print_page(self) -> None:
        resolved = self._braille_position()
        if resolved is None:
            self._announce_not_braille()
            return
        # Print-page detection lands in Phase 2 (BR-013); report unknown.
        self._say("Print page unknown.")

    def read_progress_summary(self) -> None:
        resolved = self._braille_position()
        if resolved is None:
            self._announce_not_braille()
            return
        _resolver, p = resolved
        percent = round((p.page / p.page_count) * 100) if p.page_count else 0
        self._say(
            f"Braille page {p.page} of {p.page_count}, {percent} percent through the document."
        )

    # ------------------------------------------------------------------
    # Navigation commands
    # ------------------------------------------------------------------

    def go_to_braille_page(self) -> None:
        wx = self._wx
        resolver = self._active_brf_resolver()
        editor = getattr(self, "editor", None)
        if resolver is None or editor is None:
            self._announce_not_braille()
            return
        page_count = resolver.page_map.page_count
        with wx.TextEntryDialog(
            self.frame,
            f"Enter a braille page number (1-{page_count}):",
            "Go to Braille Page",
            value="1",
        ) as dialog:
            if self._show_modal_dialog(dialog, "Go to Braille Page") != wx.ID_OK:
                return
            raw_value = dialog.GetValue().strip()
        try:
            page_number = int(raw_value)
        except ValueError:
            self._show_message_box(
                "Page number must be a number.",
                "Go to Braille Page",
                wx.ICON_ERROR | wx.OK,
            )
            return
        offset = resolver.go_to_page(page_number)
        self._record_location_before_jump()
        self._move_point(offset)
        editor.SetFocus()
        self._location_ring.record(offset)
        clamped = resolver.resolve(offset)
        self._say(f"Braille page {clamped.page} of {clamped.page_count}.")

    def next_braille_page(self) -> None:
        self._step_braille_page(forward=True)

    def previous_braille_page(self) -> None:
        self._step_braille_page(forward=False)

    def _step_braille_page(self, *, forward: bool) -> None:
        resolver = self._active_brf_resolver()
        editor = getattr(self, "editor", None)
        if resolver is None or editor is None:
            self._announce_not_braille()
            return
        try:
            offset = editor.GetCurrentPos()
        except Exception:  # noqa: BLE001
            return
        target = (
            resolver.next_page_offset(offset) if forward else resolver.previous_page_offset(offset)
        )
        if target == offset:
            self._say("No next braille page." if forward else "No previous braille page.")
            return
        self._record_location_before_jump()
        self._move_point(target)
        editor.SetFocus()
        self._location_ring.record(target)
        position = resolver.resolve(target)
        self._say(f"Braille page {position.page} of {position.page_count}.")

    # ------------------------------------------------------------------
    # Page-tool commands
    # ------------------------------------------------------------------

    def insert_braille_page_break(self) -> None:
        editor = getattr(self, "editor", None)
        if editor is None:
            return
        editor.WriteText("\f")
        self._say("Braille page break inserted.")

    def remove_braille_page_break(self) -> None:
        editor = getattr(self, "editor", None)
        if editor is None:
            return
        try:
            text = editor.GetValue()
            pos = editor.GetCurrentPos()
        except Exception:  # noqa: BLE001
            return
        target: int | None = None
        if pos < len(text) and text[pos] == "\f":
            target = pos
        elif pos > 0 and text[pos - 1] == "\f":
            target = pos - 1
        if target is None:
            self._say("No braille page break at the cursor.")
            return
        editor.SetSelection(target, target + 1)
        editor.ReplaceSelection("")
        self._say("Braille page break removed.")

    def normalize_braille_line_endings(self) -> None:
        # Phase 1 stub: the menu item exists so wiring stays stable; the
        # implementation lands in a later phase.
        self._say("Normalize line endings is not available yet.")

    def recalculate_braille_page_map(self) -> None:
        # Drop the cached resolver so the next status refresh rebuilds the map.
        self._brf_resolver_cache = None
        self._refresh_statusbar()
        self._say("Braille page map recalculated.")

    def save_as_clean_brf(self) -> None:
        # Phase 1 stub registered to keep menu wiring stable (#235 / BR-012).
        self._say("Save as clean BRF is not available yet.")

    # ------------------------------------------------------------------
    # Translation commands (#245 / BR-022) -- route through the worker
    # ------------------------------------------------------------------

    def translate_to_ueb_g1(self) -> None:
        editor = getattr(self, "editor", None)
        if editor is None:
            return
        self._translate_and_open(
            source=editor.GetValue(),
            table="en-ueb-g1",
            label=lambda result: (
                f"Translated to UEB G1. {self._brf_page_count(result)} braille pages."
            ),
        )

    def translate_to_ueb_g2(self) -> None:
        editor = getattr(self, "editor", None)
        if editor is None:
            return
        self._translate_and_open(
            source=editor.GetValue(),
            table="en-ueb-g2",
            label=lambda result: (
                f"Translated to UEB G2. {self._brf_page_count(result)} braille pages."
            ),
        )

    def translate_selection_to_ueb(self) -> None:
        editor = getattr(self, "editor", None)
        if editor is None:
            return
        getter = getattr(editor, "GetStringSelection", None)
        selection = getter() if callable(getter) else ""
        self._translate_and_open(
            source=selection,
            table="en-ueb-g2",
            label=lambda result: (
                f"Translated selection to UEB G2. {self._brf_page_count(result)} braille pages."
            ),
        )

    def back_translate_ueb(self) -> None:
        editor = getattr(self, "editor", None)
        if editor is None:
            return
        self._translate_and_open(
            source=editor.GetValue(),
            table="en-ueb-g2",
            draft=True,
            label=lambda result: (
                f"Back-translation draft. {len(result.split())} words. Review against the BRF."
            ),
        )

    def install_braille_pack_command(self) -> None:
        from quill.core.braille_pack import install_braille_pack

        install_braille_pack(self._set_status)
        self._say("Download the QUILL Braille Pack from the documentation (Phase 5, optional).")

    def _translate_and_open(
        self,
        *,
        source: str,
        table: str,
        label,
        draft: bool = False,
    ) -> None:
        from quill.core import braille_worker_client as worker

        if not source.strip():
            self._say("Nothing to translate.")
            return
        try:
            result = (
                worker.back_translate(source, table=table)
                if draft
                else worker.forward_translate(source, table=table)
            )
        except worker.WorkerError as exc:
            self._say(f"Translation failed: {exc}")
            return
        if not result:
            self._say("Translation failed: the worker returned an empty result.")
            return
        from quill.core.document import Document

        self._create_document_tab(Document(text=result), select=True)
        self._say(label(result))

    def _brf_page_count(self, text: str) -> int:
        from quill.core.brf_document import BRFDocument
        from quill.core.brf_page_map import build_page_map

        return build_page_map(BRFDocument.from_text_and_suffix(text, "brf")).page_count
