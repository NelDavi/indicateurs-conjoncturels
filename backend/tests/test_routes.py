import ast
import unittest
from pathlib import Path


class SourceContractTests(unittest.TestCase):
    def setUp(self):
        self.routes_src = Path("backend/app/api/routes.py").read_text(encoding="utf-8")
        self.routes_ast = ast.parse(self.routes_src)

    def test_routes_file_declares_required_paths(self):
        expected_paths = [
            '"/indicators"',
            '"/indicators/{indicator_id}"',
            '"/series"',
            '"/data"',
        ]
        for p in expected_paths:
            self.assertIn(p, self.routes_src)

    def test_indicators_and_series_have_pagination_params(self):
        self.assertIn("limit: int = Query(default=100, ge=1, le=1000)", self.routes_src)
        self.assertIn("offset: int = Query(default=0, ge=0)", self.routes_src)

    def test_get_indicator_has_explicit_404(self):
        self.assertIn("HTTPException(status_code=404", self.routes_src)
        self.assertIn("Indicator not found", self.routes_src)

    def test_schemas_use_pydantic_v2_configdict(self):
        indicator_schema = Path("backend/app/schemas/indicator.py").read_text(encoding="utf-8")
        series_schema = Path("backend/app/schemas/series.py").read_text(encoding="utf-8")
        data_schema = Path("backend/app/schemas/data.py").read_text(encoding="utf-8")

        for src in [indicator_schema, series_schema, data_schema]:
            self.assertIn("ConfigDict", src)
            self.assertIn("model_config = ConfigDict(from_attributes=True)", src)
            self.assertNotIn("class Config:", src)


if __name__ == "__main__":
    unittest.main()
