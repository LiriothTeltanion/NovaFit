"""Small regression tests for the restored NovaFit package."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import novafit
from novafit.database import init_db
from novafit.weather import get_weather


class NovaFitSmokeTests(unittest.TestCase):
    def test_package_imports(self) -> None:
        self.assertEqual(novafit.__version__, "1.0.0")

    def test_database_can_initialize_at_custom_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "smoke.db"
            init_db(database_path)
            self.assertTrue(database_path.exists())

    def test_tls_is_not_disabled_globally(self) -> None:
        self.assertNotEqual(os.environ.get("PYTHONHTTPSVERIFY"), "0")

    @patch("novafit.weather.requests.get")
    def test_weather_request_keeps_certificate_verification(
        self, mocked_get: Mock
    ) -> None:
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "current_weather": {
                "temperature": 28.0,
                "windspeed": 12.0,
                "weathercode": 1,
            },
            "hourly": {"relative_humidity_2m": [35]},
        }
        mocked_get.return_value = response

        result = get_weather("beersheba")

        self.assertEqual(result["status"], "success")
        _, kwargs = mocked_get.call_args
        self.assertNotIn("verify", kwargs)


if __name__ == "__main__":
    unittest.main()
