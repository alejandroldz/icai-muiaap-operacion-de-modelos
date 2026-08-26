from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]


class AssetTestCase(unittest.TestCase):
    def test_valid_and_invalid_contract_samples_are_json(self) -> None:
        samples = MODULE_ROOT / "examples" / "pump-maintenance-api" / "samples"
        valid = json.loads((samples / "prediction-valid.json").read_text("utf-8"))
        invalid = json.loads((samples / "prediction-invalid.json").read_text("utf-8"))

        self.assertIsInstance(valid["measurements"]["vibration_mm_s"], float)
        self.assertIsInstance(invalid["measurements"]["vibration_mm_s"], str)

    def test_postman_collection_covers_health_success_and_422(self) -> None:
        postman = MODULE_ROOT / "examples" / "postman"
        collection = json.loads(
            (postman / "pump-maintenance-s7.postman_collection.json").read_text("utf-8")
        )
        environment = json.loads(
            (postman / "local-s7.postman_environment.json").read_text("utf-8")
        )

        names = {item["name"] for item in collection["item"]}
        self.assertEqual(
            names,
            {"Health", "Prediction - valid (200)", "Prediction - invalid (422)"},
        )
        values = {item["key"]: item["value"] for item in environment["values"]}
        self.assertEqual(values["base_url"], "http://127.0.0.1:8000")

    def test_module_contains_both_classes_and_separated_solution(self) -> None:
        required = [
            MODULE_ROOT / "README.md",
            MODULE_ROOT / "guides" / "class-1-practices.md",
            MODULE_ROOT / "guides" / "class-2-workshop.md",
            MODULE_ROOT / "sessions" / "01-http-rest-json" / "README.md",
            MODULE_ROOT / "sessions" / "02-wine-http-gateway" / "README.md",
            MODULE_ROOT
            / "exercises"
            / "01-http-json-microexercises"
            / "problem"
            / "README.md",
            MODULE_ROOT
            / "exercises"
            / "01-http-json-microexercises"
            / "solution"
            / "README.md",
            MODULE_ROOT
            / "exercises"
            / "02-api-client-lab"
            / "problem"
            / "starter"
            / "client.py",
            MODULE_ROOT / "solutions" / "02-api-client-lab" / "README.md",
            MODULE_ROOT / "exercises" / "03-wine-http-gateway" / "README.md",
            MODULE_ROOT
            / "exercises"
            / "03-wine-http-gateway"
            / "problem"
            / "starter"
            / "README.md",
            MODULE_ROOT / "solutions" / "03-wine-http-gateway" / "README.md",
            MODULE_ROOT / "examples" / "wine-quality-api" / "README.md",
            MODULE_ROOT / "examples" / "curl" / "README.md",
            MODULE_ROOT / "examples" / "postman" / "README.md",
            MODULE_ROOT / "examples" / "transcripts" / "fallback-session.txt",
        ]
        missing = [
            str(path.relative_to(MODULE_ROOT))
            for path in required
            if not path.is_file()
        ]
        self.assertEqual(missing, [])

    def test_teacher_guide_covers_timing_statuses_and_fallback(self) -> None:
        guide = (MODULE_ROOT / "guides" / "class-1-practices.md").read_text("utf-8")

        for expected in (
            "120 minutos",
            "90 minutos",
            "30 minutos",
            "200",
            "201",
            "204",
            "400",
            "401",
            "403",
            "404",
            "409",
            "422",
            "429",
            "500",
            "503",
            "Postman",
            "fallback",
            "S8",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, guide)

    def test_python_requirement_is_312(self) -> None:
        pyproject = (MODULE_ROOT / "pyproject.toml").read_text("utf-8")
        self.assertIn('requires-python = ">=3.12"', pyproject)

    def test_root_setup_is_unlocked_and_includes_test_and_style_tools(self) -> None:
        pyproject = (MODULE_ROOT / "pyproject.toml").read_text("utf-8")
        module_readme = (MODULE_ROOT / "README.md").read_text("utf-8")
        week_readme = (MODULE_ROOT.parents[1] / "README.md").read_text("utf-8")
        guide = (MODULE_ROOT / "guides" / "class-1-practices.md").read_text("utf-8")
        combined = module_readme + guide

        self.assertIn("Python 3.12", combined)
        self.assertIn("uv sync\nuv run pytest -q", module_readme)
        for readme in (week_readme, module_readme):
            normalized = " ".join(readme.split())
            self.assertIn("puede crear un `uv.lock` local no versionado", normalized)
            self.assertIn("starter", readme)
            self.assertIn("solución", readme.lower())
        self.assertIn("uv sync --locked --extra app", module_readme)
        self.assertIn("uv run python examples/pump-maintenance-api/server.py", combined)
        self.assertIn("uv run python examples/python-client/client.py", combined)
        self.assertIn("uv run pytest -q", module_readme)
        self.assertIn("uv run ruff check .", module_readme)
        self.assertIn("uv run ruff format --check .", module_readme)
        self.assertIn("[dependency-groups]", pyproject)
        self.assertIn('"pytest>=8.0,<9.0"', pyproject)
        self.assertIn('"ruff>=0.8,<1.0"', pyproject)
        self.assertIn("[tool.pytest.ini_options]", pyproject)
        self.assertIn('testpaths = ["tests"]', pyproject)
        self.assertIn(
            'description = "Prácticas de HTTP, REST y cliente Wine Quality"',
            pyproject,
        )
        self.assertTrue(
            (
                MODULE_ROOT
                / "exercises"
                / "03-wine-http-gateway"
                / "problem"
                / "starter"
                / "uv.lock"
            ).is_file()
        )
        self.assertTrue(
            (MODULE_ROOT / "solutions" / "03-wine-http-gateway" / "uv.lock").is_file()
        )

    def test_navigation_separates_class_one_class_two_and_week_eight(self) -> None:
        module_readme = (MODULE_ROOT / "README.md").read_text("utf-8")
        lab = (
            MODULE_ROOT / "exercises" / "02-api-client-lab" / "problem" / "README.md"
        ).read_text("utf-8")
        guide = (MODULE_ROOT / "guides" / "class-1-practices.md").read_text("utf-8")
        session_one = (
            MODULE_ROOT / "sessions" / "01-http-rest-json" / "README.md"
        ).read_text("utf-8")

        for expected in (
            "Clase 1",
            "Clase 2",
            "03-wine-http-gateway",
            "FastAPI",
            "S8",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, module_readme)

        combined = module_readme + lab + guide + session_one
        self.assertNotIn("se diseñará aparte", combined.lower())
        self.assertIn("03-wine-http-gateway", lab)
        self.assertIn("class-2-workshop.md", guide)
        self.assertIn("02-wine-http-gateway", session_one)

    def test_class_two_guide_has_exact_timing_and_teacher_support(self) -> None:
        guide = (MODULE_ROOT / "guides" / "class-2-workshop.md").read_text("utf-8")

        for timing in (
            "0–10",
            "10–25",
            "25–45",
            "45–62",
            "62–82",
            "82–100",
            "100–112",
            "112–120",
        ):
            with self.subTest(timing=timing):
                self.assertIn(timing, guide)
        for section in (
            "Preparación",
            "Pistas graduadas",
            "Evidencias",
            "Debrief",
        ):
            with self.subTest(section=section):
                self.assertIn(section, guide)

    def test_remote_request_id_is_diagnostic_and_not_the_controller_id(self) -> None:
        guide = (MODULE_ROOT / "guides" / "class-2-workshop.md").read_text("utf-8")
        solution = (
            MODULE_ROOT / "solutions" / "03-wine-http-gateway" / "README.md"
        ).read_text("utf-8")
        combined = guide + solution

        self.assertIn("last_request_id", combined)
        self.assertIn("identificador local", combined)
        self.assertIn("diagnóstico", combined)
        self.assertNotIn("controlador pueda correlacionar", combined)
        self.assertNotIn("correlacionar la pantalla con la respuesta HTTP", combined)

    def test_starter_readme_explains_red_green_workflow_and_two_terminals(
        self,
    ) -> None:
        readme = (
            MODULE_ROOT
            / "exercises"
            / "03-wine-http-gateway"
            / "problem"
            / "starter"
            / "README.md"
        ).read_text("utf-8")

        for expected in (
            "Terminal 1",
            "Terminal 2",
            "17 green / 17 red",
            "uv sync",
            "uv run pytest -q",
            "uv run ruff check .",
            "uv run ruff format --check .",
            "uv run python examples/wine-quality-api/server.py",
            "MODEL_API_URL=http://127.0.0.1:8000 uv run streamlit run app.py",
            '$env:MODEL_API_URL = "http://127.0.0.1:8000"',
            "tests/test_http_gateway.py",
            "tests/test_app_gateway_selection.py",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, readme)

    def test_solution_readme_is_a_complete_teacher_replication_guide(self) -> None:
        readme = (
            MODULE_ROOT / "solutions" / "03-wine-http-gateway" / "README.md"
        ).read_text("utf-8")

        for expected in (
            "uv sync --locked --extra app",
            "uv run pytest -q",
            "uv run ruff check .",
            "uv run ruff format --check .",
            "GET /health",
            "prediction-valid.json",
            "prediction-invalid.json",
            "--mode unavailable",
            "--port 8765",
            "DemoGateway",
            "HttpInferenceGateway",
            "MODEL_API_URL=http://127.0.0.1:8000",
            '$env:MODEL_API_URL = "http://127.0.0.1:8000"',
            "Checklist visual",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, readme)

    def test_wine_api_readme_documents_the_observable_contract(self) -> None:
        readme = (
            MODULE_ROOT / "examples" / "wine-quality-api" / "README.md"
        ).read_text("utf-8")

        for expected in (
            "caja negra",
            "GET /health",
            "POST /v1/predictions",
            "request_id",
            "X-Request-Id",
            "200",
            "400",
            "404",
            "413",
            "422",
            "503",
            "fixed_acidity",
            "volatile_acidity",
            "citric_acid",
            "residual_sugar",
            "chlorides",
            "free_sulfur_dioxide",
            "total_sulfur_dioxide",
            "density",
            "ph",
            "sulphates",
            "alcohol",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, readme)

    def test_microexercises_are_guided_and_use_only_essential_statuses(self) -> None:
        root = MODULE_ROOT / "exercises" / "01-http-json-microexercises"
        problem = (root / "problem" / "README.md").read_text("utf-8")
        solution = (root / "solution" / "README.md").read_text("utf-8")

        def markdown_section(document: str, number: int) -> str:
            match = re.search(
                rf"^## {number}\.[^\n]*(?:\n|$)(.*?)(?=^## {number + 1}\.|\Z)",
                document,
                re.MULTILINE | re.DOTALL,
            )
            if match is None:
                self.fail(f"Missing Markdown section ## {number}.")
            return match.group(1)

        for expected in (
            "\u00bfSale del proceso Python?",
            "\u00bfUsa HTTP?",
            "\u00bfLa ruta nombra una acci\u00f3n o un recurso?",
            "[M\u00c9TODO] /v1/[RECURSO]",
            "[M\u00c9TODO] /v1/[RECURSO]/[ID]",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, problem)

        expected_statuses = {"200", "400", "422", "503"}
        for document_name, document in (("problem", problem), ("solution", solution)):
            with self.subTest(document=document_name):
                status_section = markdown_section(document, 4)
                status_codes = set(re.findall(r"(?<!\w)\d{3}(?!\w)", status_section))
                self.assertEqual(status_codes, expected_statuses)

        solution_design = markdown_section(solution, 5)
        self.assertRegex(
            solution_design,
            r"(?m)^\s*POST\s+/v1/predictions\s*$",
        )
        self.assertRegex(
            solution_design,
            r"(?m)^\s*GET\s+/v1/predictions/pred-42\s*$",
        )


if __name__ == "__main__":
    unittest.main()
