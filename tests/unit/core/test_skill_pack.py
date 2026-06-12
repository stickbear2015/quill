"""Tests for quill.core.skill_pack — .sqp parser, validator, and runner."""

from __future__ import annotations

from pathlib import Path

import pytest

from quill.core.skill_pack import (
    SQP_SCHEMA,
    SkillValidationError,
    StepResult,
    parse_skill,
    run_skill,
    validate_skill,
)

_BUNDLED_DIR = (
    Path(__file__).parent.parent.parent.parent / "quill" / "quillins_bundled" / "ai-writing-skills"
)

_MINIMAL = f"""\
---
schema: {SQP_SCHEMA}
name: Minimal Skill
description: A minimal test skill.
author: Test
version: 1.0.0
---

# Step 1: Do something

Write one sentence about {{selection}}.
"""

_TWO_STEP = f"""\
---
schema: {SQP_SCHEMA}
name: Two Step
description: Two steps with output reference.
author: Test
version: 1.0.0
---

# Step 1: Analyse

List the main topics in: {{selection}}

# Step 2: Summarise

Using these topics: {{step1.output}}

Write a one-paragraph summary.

```output
format: text
label: Summary
accept_into: clipboard
```
"""

_WITH_PARAMS = f"""\
---
schema: {SQP_SCHEMA}
name: Parametrised
description: Skill with parameters.
author: Test
version: 1.0.0
parameters:
  - name: tone
    label: Tone
    type: choice
    choices: [formal, casual]
    default: formal
---

# Step 1: Write

Write a {{parameters.tone}} paragraph about: {{selection}}
"""

_WITH_CONDITION = f"""\
---
schema: {SQP_SCHEMA}
name: Branching
description: Skill with conditional branch.
author: Test
version: 1.0.0
---

# Step 1: Detect

Is the following text a question or a statement?
Answer with one word: "question" or "statement".

```input
{{selection}}
```

```condition
if: "{{step1.output}}" contains "question"
then: step2
else: step3
```

# Step 2: Answer the question

Answer the question: {{selection}}

# Step 3: Elaborate the statement

Expand the following statement into a paragraph: {{selection}}
"""


class TestParsing:
    def test_minimal_skill_parses(self) -> None:
        pack = parse_skill(_MINIMAL)
        assert pack.name == "Minimal Skill"
        assert pack.schema == SQP_SCHEMA
        assert len(pack.steps) == 1
        assert pack.steps[0].index == 1

    def test_two_step_parses(self) -> None:
        pack = parse_skill(_TWO_STEP)
        assert len(pack.steps) == 2
        assert pack.steps[1].output is not None
        assert pack.steps[1].output.accept_into == "clipboard"

    def test_parameter_parses(self) -> None:
        pack = parse_skill(_WITH_PARAMS)
        assert len(pack.parameters) == 1
        p = pack.parameters[0]
        assert p.name == "tone"
        assert p.type == "choice"
        assert "formal" in p.choices
        assert p.default == "formal"

    def test_condition_parses(self) -> None:
        pack = parse_skill(_WITH_CONDITION)
        cond = pack.steps[0].condition
        assert cond is not None
        assert cond.operator == "contains"
        assert cond.value == "question"
        assert cond.then_step == 2
        assert cond.else_step == 3

    def test_input_block_extracted(self) -> None:
        pack = parse_skill(_WITH_CONDITION)
        assert pack.steps[0].input_block == "{selection}"

    def test_bad_schema_raises(self) -> None:
        bad = _MINIMAL.replace(SQP_SCHEMA, "quill.skill/99")
        with pytest.raises(SkillValidationError) as exc_info:
            parse_skill(bad)
        assert any("schema" in e for e in exc_info.value.errors)

    def test_missing_name_raises(self) -> None:
        bad = _MINIMAL.replace("name: Minimal Skill\n", "")
        with pytest.raises(SkillValidationError) as exc_info:
            parse_skill(bad)
        assert any("name" in e for e in exc_info.value.errors)

    def test_no_steps_raises(self) -> None:
        no_steps = f"---\nschema: {SQP_SCHEMA}\nname: No Steps\n---\n\nJust prose, no headings.\n"
        with pytest.raises(SkillValidationError) as exc_info:
            parse_skill(no_steps)
        assert any("step" in e for e in exc_info.value.errors)


class TestValidation:
    def test_valid_skill_has_no_errors(self) -> None:
        pack = parse_skill(_MINIMAL)
        assert validate_skill(pack) == []

    def test_forward_step_reference_is_error(self) -> None:
        forward_ref = f"""\
---
schema: {SQP_SCHEMA}
name: Forward Ref
description: x
author: x
version: 1.0.0
---

# Step 1: Use future output

Here is {{step2.output}} — but step 2 hasn't run yet.

# Step 2: Second step

Do something.
"""
        pack = parse_skill(forward_ref)
        errors = validate_skill(pack)
        assert any("hasn't run yet" in e for e in errors)

    def test_unknown_parameter_reference_is_error(self) -> None:
        bad_param = f"""\
---
schema: {SQP_SCHEMA}
name: Bad Param
description: x
author: x
version: 1.0.0
---

# Step 1: Write

Write in {{parameters.nonexistent}} style about {{selection}}.
"""
        pack = parse_skill(bad_param)
        errors = validate_skill(pack)
        assert any("nonexistent" in e for e in errors)

    def test_condition_out_of_range_step_is_error(self) -> None:
        pack = parse_skill(_WITH_CONDITION)
        errors = validate_skill(pack)
        assert errors == []

    def test_invalid_output_format_is_error(self) -> None:
        bad_output = f"""\
---
schema: {SQP_SCHEMA}
name: Bad Output
description: x
author: x
version: 1.0.0
---

# Step 1: Go

Do something.

```output
format: xml
label: Result
accept_into: none
```
"""
        pack = parse_skill(bad_output)
        errors = validate_skill(pack)
        assert any("format" in e for e in errors)


class TestRunner:
    def _collect_sends(self) -> tuple[list[str], list[str]]:
        sent: list[str] = []
        responses = ["response-1", "response-2", "response-3"]
        idx = [0]

        def send(prompt: str) -> str:
            sent.append(prompt)
            r = responses[idx[0]] if idx[0] < len(responses) else "extra"
            idx[0] += 1
            return r

        return sent, send  # type: ignore[return-value]

    def test_single_step_runs(self) -> None:
        pack = parse_skill(_MINIMAL)
        sent, send = self._collect_sends()
        results = run_skill(
            pack, {"selection": "hello world", "document": "", "title": "", "clipboard": ""}, send
        )
        assert len(results) == 1
        assert results[0].output_text == "response-1"
        assert "hello world" in sent[0]

    def test_two_steps_chain_output(self) -> None:
        pack = parse_skill(_TWO_STEP)
        sent, send = self._collect_sends()
        ctx = {
            "selection": "AI is changing the world",
            "document": "",
            "title": "",
            "clipboard": "",
        }
        results = run_skill(pack, ctx, send)
        assert len(results) == 2
        assert "response-1" in sent[1]

    def test_parameter_interpolation(self) -> None:
        pack = parse_skill(_WITH_PARAMS)
        sent, send = self._collect_sends()
        ctx = {
            "selection": "cats",
            "document": "",
            "title": "",
            "clipboard": "",
            "parameters.tone": "casual",
        }
        run_skill(pack, ctx, send)
        assert "casual" in sent[0]

    def test_step_result_fields(self) -> None:
        pack = parse_skill(_MINIMAL)
        _, send = self._collect_sends()
        results = run_skill(
            pack, {"selection": "x", "document": "", "title": "", "clipboard": ""}, send
        )
        r = results[0]
        assert isinstance(r, StepResult)
        assert r.step_index == 1
        assert r.step_heading == "Step 1: Do something"
        assert r.output_text == "response-1"
        assert not r.skipped

    def test_depth_limit(self) -> None:
        pack = parse_skill(_MINIMAL)
        _, send = self._collect_sends()
        with pytest.raises(RecursionError):
            run_skill(
                pack,
                {"selection": "x", "document": "", "title": "", "clipboard": ""},
                send,
                depth=3,
            )


class TestBundledSkills:
    def test_bundled_skills_directory_exists(self) -> None:
        assert _BUNDLED_DIR.is_dir(), f"Bundled skills dir not found: {_BUNDLED_DIR}"

    def test_all_bundled_sqp_files_parse_cleanly(self) -> None:
        sqp_files = list(_BUNDLED_DIR.glob("*.sqp"))
        assert sqp_files, "No .sqp files found in bundled skills directory"
        for path in sqp_files:
            source = path.read_text(encoding="utf-8")
            try:
                pack = parse_skill(source)
            except SkillValidationError as exc:
                pytest.fail(f"{path.name}: parse errors: {exc.errors}")
            errors = validate_skill(pack)
            assert errors == [], f"{path.name}: validation errors: {errors}"

    def test_bundled_skills_have_required_metadata(self) -> None:
        for path in _BUNDLED_DIR.glob("*.sqp"):
            pack = parse_skill(path.read_text(encoding="utf-8"))
            assert pack.name, f"{path.name}: missing name"
            assert pack.description, f"{path.name}: missing description"
            assert pack.author, f"{path.name}: missing author"
            assert pack.steps, f"{path.name}: has no steps"

    def test_manifest_json_exists_and_is_valid(self) -> None:
        import json

        manifest_path = _BUNDLED_DIR / "manifest.json"
        assert manifest_path.is_file()
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert data.get("id") == "com.quill.bundled.ai-writing-skills"
        assert data.get("schema") == "quill.extension/1"

    def test_bundled_quillin_ships_a_license_file(self) -> None:
        assert (_BUNDLED_DIR / "LICENSE").is_file()
