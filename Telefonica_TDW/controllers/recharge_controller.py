import os
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

from controllers.security import require_api_key

from models.recharge import (
    CustomerStatusResponse,
    RechargeListResponse,
    RechargeRecord,
    RechargeRequest,
    create_recharge,
    get_latest_recharge_by_msisdn,
    list_recharges,
)

router = APIRouter()
DEFAULT_SIMULATED_DEGRADED_LOCATIONS = frozenset({"guatire", "valencia"})


@router.post(
    "/apply",
    response_model=RechargeRecord,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def apply_recharge(recharge: RechargeRequest) -> RechargeRecord:
    try:
        return create_recharge(recharge)
    except sqlite3.IntegrityError as exc:
        if "recharges.transaction_id" in str(exc):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The transaction_id has already been processed.",
            ) from exc
        raise


@router.get(
    "/stats",
    response_model=RechargeListResponse,
    dependencies=[Depends(require_api_key)],
)
def get_recharge_stats() -> RechargeListResponse:
    return RechargeListResponse(recharges=list_recharges())


@router.get(
    "/customer/status/{msisdn}",
    response_model=CustomerStatusResponse,
    dependencies=[Depends(require_api_key)],
)
def check_customer_status(msisdn: str) -> CustomerStatusResponse:
    latest_recharge = get_latest_recharge_by_msisdn(msisdn)
    if latest_recharge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No recharge record was found for this MSISDN.",
        )

    configured_locations = os.getenv("SIMULATED_DEGRADED_LOCATIONS")
    if configured_locations is None:
        degraded_locations = DEFAULT_SIMULATED_DEGRADED_LOCATIONS
    else:
        degraded_locations = frozenset(
            location.strip().casefold()
            for location in configured_locations.split(",")
            if location.strip()
        )

    location = latest_recharge.location.strip()
    if location.casefold() in degraded_locations:
        network_status = {
            "status": "DEGRADED",
            "details": (
                f"Falla simulada en la estación de recarga de {location}; "
                f"posible impacto en la red {latest_recharge.network_type}."
            ),
        }
    else:
        network_status = {
            "status": "OPERATIONAL",
            "details": (
                f"Estación de recarga operando con normalidad en {location} "
                f"para la red {latest_recharge.network_type}."
            ),
        }

    return CustomerStatusResponse(
        msisdn=latest_recharge.msisdn,
        latest_recharge=latest_recharge,
        network_status=network_status,
    )
