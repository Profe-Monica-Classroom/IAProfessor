import os
from collections import Counter
from typing import TypedDict
from urllib.parse import quote

import requests
from pydantic import TypeAdapter, ValidationError

from models.recharge import (
    CustomerStatusResponse,
    RechargeRecord,
    RechargeRequest,
)
from models.failure_report import (
    FailureReport,
    FailureReportListResponse,
    FailureReportRequest,
)

AMOUNTS = (50, 100, 200, 500)


class DashboardData(TypedDict):
    recharges: list[RechargeRecord]
    total_recharges: int
    gross_revenue: float
    five_g_recharges: int
    revenue_by_amount: dict[int, float]
    recharges_by_location: dict[str, int]


class DashboardAPIError(Exception):
    """Raised when the dashboard cannot obtain valid data from the API."""


def _api_base_url() -> str:
    return os.getenv("RECHARGE_API_URL", "http://127.0.0.1:8000").rstrip("/")


def load_dashboard_data(api_key: str) -> DashboardData:
    try:
        response = requests.get(
            f"{_api_base_url()}/api/v1/recharges/stats",
            headers={"X-API-Key": api_key},
            timeout=5,
        )
        response.raise_for_status()
        payload = response.json()
        recharges = TypeAdapter(list[RechargeRecord]).validate_python(
            payload["recharges"]
        )
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response else None
        if status_code == 401:
            message = (
                "La API rechazó la API Key. Ingresa en el panel lateral "
                "la misma clave configurada al iniciar la API."
            )
        elif status_code == 503:
            message = (
                "La API no tiene configurada RECHARGE_API_KEY. "
                "Reiníciala después de configurarla."
            )
        else:
            message = (
                "No se pudieron cargar las recargas "
                f"(código HTTP {status_code})."
            )
        raise DashboardAPIError(message) from exc
    except (
        requests.RequestException,
        ValueError,
        KeyError,
        TypeError,
        ValidationError,
    ) as exc:
        raise DashboardAPIError(
            "No se pudieron cargar los datos del servicio de recargas."
        ) from exc

    revenue_by_amount: dict[int, float] = {amount: 0.0 for amount in AMOUNTS}
    location_counts: Counter[str] = Counter()
    for recharge in recharges:
        amount = int(recharge.amount)
        revenue_by_amount[amount] += recharge.amount
        location_counts[recharge.location] += 1

    return {
        "recharges": recharges,
        "total_recharges": len(recharges),
        "gross_revenue": sum(recharge.amount for recharge in recharges),
        "five_g_recharges": sum(
            recharge.network_type == "5G" for recharge in recharges
        ),
        "revenue_by_amount": revenue_by_amount,
        "recharges_by_location": dict(
            sorted(location_counts.items(), key=lambda item: item[0].casefold())
        ),
    }


def submit_recharge(recharge: RechargeRequest, api_key: str) -> RechargeRecord:
    try:
        response = requests.post(
            f"{_api_base_url()}/api/v1/recharges/apply",
            json=recharge.model_dump(mode="json"),
            headers={"X-API-Key": api_key},
            timeout=5,
        )
    except requests.RequestException as exc:
        raise DashboardAPIError(
            "No se pudo conectar con el servicio para procesar la recarga."
        ) from exc

    if response.status_code == 400:
        message = "Los datos de la recarga no son válidos."
    elif response.status_code == 401:
        message = "La API Key no es válida."
    elif response.status_code == 409:
        message = "Este identificador ya fue procesado; no se aplicó otra recarga."
    elif response.status_code == 503:
        message = "El servicio no tiene configurada la autenticación transaccional."
    elif response.status_code != 201:
        message = (
            "No se pudo procesar la recarga "
            f"(código HTTP {response.status_code})."
        )
    else:
        try:
            return TypeAdapter(RechargeRecord).validate_python(response.json())
        except (
            requests.RequestException,
            ValueError,
            TypeError,
            ValidationError,
        ) as exc:
            raise DashboardAPIError(
                "El servicio devolvió una respuesta de recarga inválida."
            ) from exc

    raise DashboardAPIError(message)


def fetch_customer_status(msisdn: str, api_key: str) -> CustomerStatusResponse:
    encoded_msisdn = quote(msisdn, safe="")
    try:
        response = requests.get(
            f"{_api_base_url()}/api/v1/recharges/customer/status/{encoded_msisdn}",
            headers={"X-API-Key": api_key},
            timeout=5,
        )
    except requests.RequestException as exc:
        raise DashboardAPIError(
            "No se pudo conectar con el servicio para consultar el estado de red."
        ) from exc

    if response.status_code == 404:
        message = "No se encontraron recargas para ese número."
    elif response.status_code == 401:
        message = "La API Key no es válida."
    elif response.status_code == 503:
        message = "El servicio no tiene configurada la autenticación transaccional."
    elif response.status_code != 200:
        message = (
            "No se pudo consultar el estado de red "
            f"(código HTTP {response.status_code})."
        )
    else:
        try:
            return TypeAdapter(CustomerStatusResponse).validate_python(
                response.json()
            )
        except (
            requests.RequestException,
            ValueError,
            TypeError,
            ValidationError,
        ) as exc:
            raise DashboardAPIError(
                "El servicio devolvió un estado de red inválido."
            ) from exc

    raise DashboardAPIError(message)


def submit_failure_report(
    report: FailureReportRequest, api_key: str
) -> FailureReport:
    try:
        response = requests.post(
            f"{_api_base_url()}/api/v1/reports/internet-failures",
            json=report.model_dump(mode="json"),
            headers={"X-API-Key": api_key},
            timeout=5,
        )
    except requests.RequestException as exc:
        raise DashboardAPIError(
            "No se pudo conectar con el servicio para registrar el reporte."
        ) from exc

    if response.status_code == 400:
        message = "Revisa los datos del reporte e inténtalo de nuevo."
    elif response.status_code == 401:
        message = "La API Key no es válida."
    elif response.status_code == 503:
        message = "El servicio no tiene configurada la autenticación transaccional."
    elif response.status_code != 201:
        message = (
            "No se pudo registrar el reporte "
            f"(código HTTP {response.status_code})."
        )
    else:
        try:
            return TypeAdapter(FailureReport).validate_python(response.json())
        except (
            requests.RequestException,
            ValueError,
            TypeError,
            ValidationError,
        ) as exc:
            raise DashboardAPIError(
                "El servicio devolvió un reporte inválido."
            ) from exc

    raise DashboardAPIError(message)


def load_recent_failure_reports(api_key: str) -> list[FailureReport]:
    try:
        response = requests.get(
            f"{_api_base_url()}/api/v1/reports/internet-failures",
            headers={"X-API-Key": api_key},
            timeout=5,
        )
    except requests.RequestException as exc:
        raise DashboardAPIError(
            "No se pudieron cargar los reportes de fallas."
        ) from exc

    if response.status_code == 401:
        raise DashboardAPIError("La API Key no es válida.")
    if response.status_code == 503:
        raise DashboardAPIError(
            "El servicio no tiene configurada la autenticación transaccional."
        )
    if response.status_code != 200:
        raise DashboardAPIError(
            "No se pudieron cargar los reportes "
            f"(código HTTP {response.status_code})."
        )

    try:
        payload = response.json()
        return TypeAdapter(FailureReportListResponse).validate_python(
            payload
        ).reports
    except (
        requests.RequestException,
        ValueError,
        TypeError,
        ValidationError,
    ) as exc:
        raise DashboardAPIError(
            "El servicio devolvió una lista de reportes inválida."
        ) from exc
