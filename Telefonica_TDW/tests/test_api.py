import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from api import app


class RechargeAPITests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.environment = patch.dict(
            os.environ,
            {
                "DATABASE_PATH": str(
                    Path(self.temporary_directory.name) / "test.db"
                ),
                "RECHARGE_API_KEY": "test-key",
                "SIMULATED_DEGRADED_LOCATIONS": "Guatire,Valencia",
            },
        )
        self.environment.start()
        self.client_context = TestClient(app)
        self.client = self.client_context.__enter__()
        self.headers = {"X-API-Key": "test-key"}
        self.payload = {
            "msisdn": "04141234567",
            "amount": 100,
            "network_type": "4G",
            "location": "Caracas",
            "transaction_id": "tx-001",
        }
        self.failure_report_payload = {
            "msisdn": "04141234567",
            "location": "Caracas",
            "network_type": "4G",
            "failure_type": "NO_INTERNET",
            "description": "No hay acceso a Internet desde esta mañana.",
        }

    def tearDown(self) -> None:
        self.client_context.__exit__(None, None, None)
        self.environment.stop()
        self.temporary_directory.cleanup()

    def test_creates_recharge_and_returns_it_in_stats(self) -> None:
        response = self.client.post(
            "/api/v1/recharges/apply", json=self.payload, headers=self.headers
        )

        self.assertEqual(response.status_code, 201)
        self.assertIn("timestamp", response.json())
        stats = self.client.get(
            "/api/v1/recharges/stats", headers=self.headers
        )
        self.assertEqual(stats.status_code, 200)
        self.assertEqual(len(stats.json()["recharges"]), 1)

    def test_duplicate_transaction_returns_conflict_without_duplicate_row(self) -> None:
        first = self.client.post(
            "/api/v1/recharges/apply", json=self.payload, headers=self.headers
        )
        duplicate = self.client.post(
            "/api/v1/recharges/apply", json=self.payload, headers=self.headers
        )

        self.assertEqual(first.status_code, 201)
        self.assertEqual(duplicate.status_code, 409)
        self.assertEqual(
            duplicate.headers["content-type"], "application/problem+json"
        )
        self.assertEqual(
            len(
                self.client.get(
                    "/api/v1/recharges/stats", headers=self.headers
                ).json()["recharges"]
            ),
            1,
        )

    def test_invalid_amount_and_network_return_bad_request(self) -> None:
        invalid_amount = dict(self.payload, amount=75)
        invalid_network = dict(self.payload, network_type="3G")

        for payload in (invalid_amount, invalid_network):
            with self.subTest(payload=payload):
                response = self.client.post(
                    "/api/v1/recharges/apply", json=payload, headers=self.headers
                )
                self.assertEqual(response.status_code, 400)
                self.assertEqual(
                    response.headers["content-type"], "application/problem+json"
                )

    def test_transaction_requires_configured_api_key(self) -> None:
        response = self.client.post(
            "/api/v1/recharges/apply", json=self.payload
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.headers["content-type"], "application/problem+json"
        )

    def test_recharge_stats_requires_api_key(self) -> None:
        response = self.client.get("/api/v1/recharges/stats")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.headers["content-type"], "application/problem+json"
        )

    def test_missing_api_key_configuration_disables_transaction_endpoint(self) -> None:
        with patch.dict(os.environ, {"RECHARGE_API_KEY": ""}):
            response = self.client.post(
                "/api/v1/recharges/apply", json=self.payload, headers=self.headers
            )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.headers["content-type"], "application/problem+json"
        )

    def test_customer_status_simulates_degraded_location(self) -> None:
        payload = dict(self.payload, location="  gUaTiRe  ")
        created = self.client.post(
            "/api/v1/recharges/apply", json=payload, headers=self.headers
        )
        self.assertEqual(created.status_code, 201)

        response = self.client.get(
            "/api/v1/recharges/customer/status/04141234567",
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 200)
        status_data = response.json()
        self.assertEqual(status_data["latest_recharge"]["location"], "  gUaTiRe  ")
        self.assertEqual(status_data["network_status"]["status"], "DEGRADED")
        self.assertIn("red 4G", status_data["network_status"]["details"])

    def test_customer_status_reports_normal_location(self) -> None:
        self.client.post(
            "/api/v1/recharges/apply", json=self.payload, headers=self.headers
        )

        response = self.client.get(
            "/api/v1/recharges/customer/status/04141234567",
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["network_status"]["status"], "OPERATIONAL"
        )

    def test_customer_status_uses_latest_recharge(self) -> None:
        first = self.client.post(
            "/api/v1/recharges/apply",
            json=self.payload,
            headers=self.headers,
        )
        latest_payload = dict(
            self.payload,
            amount=200,
            location="Valencia",
            transaction_id="tx-002",
        )
        latest = self.client.post(
            "/api/v1/recharges/apply",
            json=latest_payload,
            headers=self.headers,
        )
        self.assertEqual(first.status_code, 201)
        self.assertEqual(latest.status_code, 201)

        response = self.client.get(
            "/api/v1/recharges/customer/status/04141234567",
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 200)
        status_data = response.json()
        self.assertEqual(
            status_data["latest_recharge"]["transaction_id"], "tx-002"
        )
        self.assertEqual(status_data["network_status"]["status"], "DEGRADED")

    def test_customer_status_returns_problem_details_when_not_found(self) -> None:
        response = self.client.get(
            "/api/v1/recharges/customer/status/04149999999",
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.headers["content-type"], "application/problem+json"
        )

    def test_customer_status_requires_api_key(self) -> None:
        response = self.client.get(
            "/api/v1/recharges/customer/status/04141234567"
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.headers["content-type"], "application/problem+json"
        )

    def test_creates_failure_report_and_lists_it(self) -> None:
        created = self.client.post(
            "/api/v1/reports/internet-failures",
            json=self.failure_report_payload,
            headers=self.headers,
        )

        self.assertEqual(created.status_code, 201)
        report = created.json()
        self.assertEqual(report["status"], "OPEN")
        self.assertEqual(report["failure_type"], "NO_INTERNET")
        self.assertTrue(report["report_id"])
        self.assertIn("reported_at", report)

        response = self.client.get(
            "/api/v1/reports/internet-failures",
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["reports"], [report])

    def test_failure_report_validation_errors_return_problem_details(self) -> None:
        invalid_report = dict(self.failure_report_payload, description="Sin señal")

        response = self.client.post(
            "/api/v1/reports/internet-failures",
            json=invalid_report,
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.headers["content-type"], "application/problem+json"
        )

    def test_failure_report_endpoints_require_api_key(self) -> None:
        response = self.client.post(
            "/api/v1/reports/internet-failures",
            json=self.failure_report_payload,
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.headers["content-type"], "application/problem+json"
        )


if __name__ == "__main__":
    unittest.main()
