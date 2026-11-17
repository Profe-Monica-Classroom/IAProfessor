import unittest
from pathlib import Path
from unittest.mock import patch

from models.failure_report import FailureReport
from streamlit.testing.v1 import AppTest


class DashboardViewTests(unittest.TestCase):
    def test_failure_report_history_renders_without_dataframe_conversion(self) -> None:
        report = FailureReport(
            report_id="report-test",
            msisdn="04141567890",
            location="Guarenas",
            network_type="4G",
            failure_type="SLOW",
            description="La navegación está lenta desde esta mañana.",
            status="OPEN",
            reported_at="2026-11-16T17:00:00+00:00",
        )
        dashboard_data = {
            "recharges": [],
            "total_recharges": 0,
            "gross_revenue": 0,
            "five_g_recharges": 0,
            "revenue_by_amount": {50: 0, 100: 0, 200: 0, 500: 0},
            "recharges_by_location": {},
        }

        with (
            patch(
                "views.dashboard_view.load_recent_failure_reports",
                return_value=[report],
            ),
            patch(
                "views.dashboard_view.load_dashboard_data",
                return_value=dashboard_data,
            ),
        ):
            app = AppTest.from_file(
                Path(__file__).resolve().parents[1] / "dashboard.py",
                default_timeout=10,
            ).run()
            api_key_widget = next(
                widget for widget in app.text_input if widget.label == "API Key"
            )
            app = api_key_widget.set_value("test-key").run()

        self.assertEqual(len(app.exception), 0)
        self.assertTrue(
            any(
                report.description in item.value
                for item in app.text
            )
        )


if __name__ == "__main__":
    unittest.main()
