import unittest
from unittest.mock import Mock, patch

import requests

from controllers.dashboard_controller import (
    DashboardAPIError,
    fetch_customer_status,
    load_recent_failure_reports,
    load_dashboard_data,
    submit_failure_report,
    submit_recharge,
)
from models.failure_report import FailureReportRequest
from models.recharge import RechargeRequest


class DashboardControllerTests(unittest.TestCase):
    @patch("controllers.dashboard_controller.requests.get")
    def test_load_dashboard_data_calculates_kpis_and_chart_groups(
        self, get: Mock
    ) -> None:
        response = Mock()
        response.json.return_value = {
            "recharges": [
                {
                    "msisdn": "04141111111",
                    "amount": 100,
                    "network_type": "5G",
                    "location": "Caracas",
                    "transaction_id": "tx-1",
                    "timestamp": "2026-11-16T12:00:00+00:00",
                },
                {
                    "msisdn": "04142222222",
                    "amount": 50,
                    "network_type": "4G",
                    "location": "Mérida",
                    "transaction_id": "tx-2",
                    "timestamp": "2026-11-16T12:01:00+00:00",
                },
                {
                    "msisdn": "04143333333",
                    "amount": 100,
                    "network_type": "4G",
                    "location": "Caracas",
                    "transaction_id": "tx-3",
                    "timestamp": "2026-11-16T12:02:00+00:00",
                },
            ]
        }
        get.return_value = response

        data = load_dashboard_data("test-key")

        get.assert_called_once_with(
            "http://127.0.0.1:8000/api/v1/recharges/stats",
            headers={"X-API-Key": "test-key"},
            timeout=5,
        )
        response.raise_for_status.assert_called_once_with()
        self.assertEqual(data["total_recharges"], 3)
        self.assertEqual(data["gross_revenue"], 250)
        self.assertEqual(data["five_g_recharges"], 1)
        self.assertEqual(data["revenue_by_amount"], {50: 50, 100: 200, 200: 0, 500: 0})
        self.assertEqual(data["recharges_by_location"], {"Caracas": 2, "Mérida": 1})

    @patch("controllers.dashboard_controller.requests.get")
    def test_load_dashboard_data_explains_unauthorized_api_key(
        self, get: Mock
    ) -> None:
        response = Mock()
        response.status_code = 401
        error = requests.HTTPError(response=response)
        failed_response = Mock()
        failed_response.raise_for_status.side_effect = error
        get.return_value = failed_response

        with self.assertRaisesRegex(DashboardAPIError, "API Key"):
            load_dashboard_data("invalid-key")

    @patch("controllers.dashboard_controller.requests.post")
    def test_submit_recharge_posts_payload_and_returns_record(self, post: Mock) -> None:
        response = Mock()
        response.status_code = 201
        response.json.return_value = {
            "msisdn": "04141111111",
            "amount": 100,
            "network_type": "5G",
            "location": "Caracas",
            "transaction_id": "tx-demo",
            "timestamp": "2026-11-16T12:00:00+00:00",
        }
        post.return_value = response
        recharge = RechargeRequest(
            msisdn="04141111111",
            amount=100,
            network_type="5G",
            location="Caracas",
            transaction_id="tx-demo",
        )

        result = submit_recharge(recharge, "test-key")

        self.assertEqual(result.transaction_id, "tx-demo")
        post.assert_called_once_with(
            "http://127.0.0.1:8000/api/v1/recharges/apply",
            json=recharge.model_dump(mode="json"),
            headers={"X-API-Key": "test-key"},
            timeout=5,
        )

    @patch("controllers.dashboard_controller.requests.post")
    def test_submit_recharge_reports_duplicate_transaction(self, post: Mock) -> None:
        response = Mock()
        response.status_code = 409
        post.return_value = response
        recharge = RechargeRequest(
            msisdn="04141111111",
            amount=100,
            network_type="5G",
            location="Caracas",
            transaction_id="tx-demo",
        )

        with self.assertRaisesRegex(DashboardAPIError, "ya fue procesado"):
            submit_recharge(recharge, "test-key")

    @patch("controllers.dashboard_controller.requests.get")
    def test_fetch_customer_status_returns_typed_status(self, get: Mock) -> None:
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "msisdn": "04141111111",
            "latest_recharge": {
                "msisdn": "04141111111",
                "amount": 100,
                "network_type": "5G",
                "location": "Guatire",
                "transaction_id": "tx-demo",
                "timestamp": "2026-11-16T12:00:00+00:00",
            },
            "network_status": {
                "status": "DEGRADED",
                "details": "Falla simulada en estación de recarga.",
            },
        }
        get.return_value = response

        result = fetch_customer_status("04141111111", "test-key")

        self.assertEqual(result.network_status.status, "DEGRADED")
        self.assertEqual(result.latest_recharge.location, "Guatire")
        get.assert_called_once_with(
            "http://127.0.0.1:8000/api/v1/recharges/customer/status/04141111111",
            headers={"X-API-Key": "test-key"},
            timeout=5,
        )

    @patch("controllers.dashboard_controller.requests.get")
    def test_fetch_customer_status_reports_missing_customer(self, get: Mock) -> None:
        response = Mock()
        response.status_code = 404
        get.return_value = response

        with self.assertRaisesRegex(DashboardAPIError, "No se encontraron"):
            fetch_customer_status("04149999999", "test-key")

    @patch("controllers.dashboard_controller.requests.post")
    def test_submit_failure_report_returns_persisted_report(self, post: Mock) -> None:
        response = Mock()
        response.status_code = 201
        response.json.return_value = {
            "report_id": "report-001",
            "msisdn": "04141111111",
            "location": "Caracas",
            "network_type": "4G",
            "failure_type": "NO_INTERNET",
            "description": "No hay acceso a Internet desde esta mañana.",
            "status": "OPEN",
            "reported_at": "2026-11-16T12:00:00+00:00",
        }
        post.return_value = response
        report_request = FailureReportRequest(
            msisdn="04141111111",
            location="Caracas",
            network_type="4G",
            failure_type="NO_INTERNET",
            description="No hay acceso a Internet desde esta mañana.",
        )

        report = submit_failure_report(report_request, "test-key")

        self.assertEqual(report.report_id, "report-001")
        self.assertEqual(report.status, "OPEN")
        post.assert_called_once_with(
            "http://127.0.0.1:8000/api/v1/reports/internet-failures",
            json=report_request.model_dump(mode="json"),
            headers={"X-API-Key": "test-key"},
            timeout=5,
        )

    @patch("controllers.dashboard_controller.requests.get")
    def test_load_recent_failure_reports_validates_response(self, get: Mock) -> None:
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "reports": [
                {
                    "report_id": "report-001",
                    "msisdn": "04141111111",
                    "location": "Caracas",
                    "network_type": "4G",
                    "failure_type": "NO_INTERNET",
                    "description": "No hay acceso a Internet desde esta mañana.",
                    "status": "OPEN",
                    "reported_at": "2026-11-16T12:00:00+00:00",
                }
            ]
        }
        get.return_value = response

        reports = load_recent_failure_reports("test-key")

        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0].report_id, "report-001")
        get.assert_called_once_with(
            "http://127.0.0.1:8000/api/v1/reports/internet-failures",
            headers={"X-API-Key": "test-key"},
            timeout=5,
        )


if __name__ == "__main__":
    unittest.main()
