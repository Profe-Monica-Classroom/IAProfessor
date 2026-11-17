from uuid import uuid4

import plotly.graph_objects as go
import streamlit as st
from pydantic import ValidationError

from controllers.dashboard_controller import (
    DashboardAPIError,
    fetch_customer_status,
    load_recent_failure_reports,
    load_dashboard_data,
    submit_failure_report,
    submit_recharge,
)
from models.failure_report import FailureReportRequest
from models.recharge import CustomerStatusResponse, RechargeRequest

PRIMARY_BLUE = "#0168b3"
LIGHT_BLUE = "#7ec8e3"
TEAL = "#00a6a6"
PALETTE = [PRIMARY_BLUE, LIGHT_BLUE, TEAL, "#64b5f6"]
FAILURE_TYPE_LABELS = {
    "NO_INTERNET": "Sin acceso a Internet",
    "INTERMITTENT": "Conexión intermitente",
    "SLOW": "Navegación lenta",
    "OTHER": "Otro problema",
}


def _format_integer(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def _format_amount(value: float) -> str:
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _mask_msisdn(msisdn: str) -> str:
    return f"{'*' * max(len(msisdn) - 4, 0)}{msisdn[-4:]}"


def _render_recharge_form(api_key: str) -> None:
    if "recharge_transaction_id" not in st.session_state:
        st.session_state["recharge_transaction_id"] = uuid4().hex

    with st.expander("Realizar una recarga", expanded=True):
        with st.form("recharge_form"):
            msisdn = st.text_input(
                "Número de teléfono (MSISDN)",
                placeholder="Ej.: 04141234567",
            )
            first_column, second_column = st.columns(2)
            amount = first_column.selectbox(
                "Monto de recarga",
                options=(50, 100, 200, 500),
            )
            network_type = second_column.selectbox(
                "Tipo de red",
                options=("4G", "5G"),
            )
            location = st.text_input(
                "Zona o ciudad",
                placeholder="Ej.: Caracas",
            )
            st.text_input(
                "ID de transacción",
                value=st.session_state["recharge_transaction_id"],
                disabled=True,
                help="Se genera automáticamente para prevenir transacciones duplicadas.",
            )
            submitted = st.form_submit_button(
                "Aplicar recarga",
                type="primary",
                width="stretch",
            )

        if not submitted:
            return
        if not api_key:
            st.error("Ingresa la API Key transaccional en el panel lateral.")
            return

        try:
            recharge = RechargeRequest(
                msisdn=msisdn,
                amount=amount,
                network_type=network_type,
                location=location,
                transaction_id=st.session_state["recharge_transaction_id"],
            )
            result = submit_recharge(recharge, api_key)
        except DashboardAPIError as exc:
            st.error(str(exc))
            return

        st.session_state["last_recharge_message"] = (
            f"Recarga aplicada correctamente. ID: {result.transaction_id}"
        )
        st.session_state["recharge_transaction_id"] = uuid4().hex
        st.rerun()


def _render_network_status_panel(api_key: str) -> None:
    st.subheader("Consulta de estado de red")
    st.caption(
        "El estado es simulado según la ubicación de la última recarga del MSISDN."
    )
    with st.form("network_status_form"):
        msisdn = st.text_input(
            "MSISDN para consultar",
            placeholder="Ej.: 04141234567",
        )
        submitted = st.form_submit_button(
            "Consultar estado",
            type="primary",
        )

    if submitted:
        st.session_state.pop("network_status_result", None)
        if not api_key:
            st.error("Ingresa la API Key en el panel lateral.")
        elif not msisdn.strip():
            st.error("Ingresa un MSISDN para realizar la consulta.")
        else:
            try:
                result = fetch_customer_status(msisdn.strip(), api_key)
            except DashboardAPIError as exc:
                st.error(str(exc))
            else:
                st.session_state["network_status_result"] = result.model_dump(
                    mode="json"
                )

    status_data = st.session_state.get("network_status_result")
    if not status_data:
        st.info("Consulta un MSISDN para ver el estado de red.")
        return

    result = CustomerStatusResponse.model_validate(status_data)
    network_status = result.network_status
    st.caption(f"MSISDN consultado: {_mask_msisdn(result.msisdn)}")

    if network_status.status == "DEGRADED":
        st.error(f"Red degradada: {network_status.details}")
    else:
        st.success(f"Red operativa: {network_status.details}")

    recharge = result.latest_recharge
    columns = st.columns(3)
    columns[0].metric("Ubicación", recharge.location)
    columns[1].metric("Red de última recarga", recharge.network_type)
    columns[2].metric("Monto de última recarga", _format_amount(recharge.amount))
    st.caption(f"Última recarga registrada: {recharge.timestamp}")


def _render_failure_reports_panel(api_key: str) -> None:
    st.subheader("Reportar falla de acceso a Internet")
    st.caption(
        "Registra el incidente para que el equipo de soporte pueda darle seguimiento."
    )

    success_message = st.session_state.pop("last_failure_report_message", None)
    if success_message:
        st.success(success_message)

    with st.form("failure_report_form"):
        first_column, second_column = st.columns(2)
        msisdn = first_column.text_input(
            "Número de teléfono (MSISDN)",
            placeholder="Ej.: 04141234567",
        )
        location = second_column.text_input(
            "Zona o ciudad",
            placeholder="Ej.: Caracas",
        )
        third_column, fourth_column = st.columns(2)
        network_type = third_column.selectbox(
            "Tipo de red afectada",
            options=("4G", "5G"),
        )
        failure_type = fourth_column.selectbox(
            "Tipo de falla",
            options=tuple(FAILURE_TYPE_LABELS),
            format_func=FAILURE_TYPE_LABELS.get,
        )
        description = st.text_area(
            "Descripción del problema",
            placeholder="Describe cuándo comenzó y qué ocurre al conectarte.",
            max_chars=1200,
        )
        submitted = st.form_submit_button(
            "Enviar reporte",
            type="primary",
            width="stretch",
        )

    if submitted:
        if not api_key:
            st.error("Ingresa la API Key en el panel lateral.")
        else:
            try:
                report_request = FailureReportRequest(
                    msisdn=msisdn,
                    location=location,
                    network_type=network_type,
                    failure_type=failure_type,
                    description=description,
                )
                report = submit_failure_report(report_request, api_key)
            except ValidationError:
                st.error(
                    "Verifica el MSISDN, la ubicación y que la descripción "
                    "tenga al menos 10 caracteres."
                )
            except DashboardAPIError as exc:
                st.error(str(exc))
            else:
                st.session_state["last_failure_report_message"] = (
                    f"Reporte registrado. Folio: {report.report_id}"
                )
                st.rerun()

    if not api_key:
        st.info("Ingresa la API Key para consultar y guardar reportes.")
        return

    try:
        reports = load_recent_failure_reports(api_key)
    except DashboardAPIError as exc:
        st.error(str(exc))
        return

    st.subheader("Reportes recientes")
    if not reports:
        st.info("Todavía no hay reportes de fallas registrados.")
        return

    for report in reports:
        with st.container(border=True):
            st.caption(
                f"Folio {report.report_id} · "
                f"{FAILURE_TYPE_LABELS[report.failure_type]} · "
                f"{'Abierto' if report.status == 'OPEN' else report.status}"
            )
            columns = st.columns(3)
            columns[0].metric("MSISDN", _mask_msisdn(report.msisdn))
            columns[1].metric("Ubicación", report.location)
            columns[2].metric("Red afectada", report.network_type)
            st.text(f"Descripción: {report.description}")
            st.caption(f"Reportado: {report.reported_at}")


def render_dashboard() -> None:
    st.set_page_config(
        page_title="Recargas | Telefónica Prepago",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(
        f"""
        <style>
        .stApp {{ background-color: #ffffff; }}
        [data-testid="stMetric"] {{
            background: #f2f8fc;
            border: 1px solid #d6eaf5;
            border-radius: 12px;
            padding: 18px;
        }}
        [data-testid="stMetricLabel"] p {{ color: {PRIMARY_BLUE}; }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title("Dashboard de Recargas")
    st.caption("Monitoreo operativo y adopción de redes 4G/5G")

    with st.sidebar:
        st.subheader("Acceso transaccional")
        api_key = st.text_input(
            "API Key",
            type="password",
            help="Se mantiene durante esta sesión y no se incluye en los datos de recarga.",
        )

    dashboard_tab, network_tab, reports_tab = st.tabs(
        [
            "Dashboard de recargas",
            "Monitoreo de red",
            "Reportar falla de Internet",
        ]
    )
    with dashboard_tab:
        _render_recharge_dashboard(api_key)
    with network_tab:
        _render_network_status_panel(api_key)
    with reports_tab:
        _render_failure_reports_panel(api_key)


def _render_recharge_dashboard(api_key: str) -> None:
    success_message = st.session_state.pop("last_recharge_message", None)
    if success_message:
        st.success(success_message)

    _render_recharge_form(api_key)

    if not api_key:
        st.info("Ingresa la API Key para cargar los indicadores de recargas.")
        return

    try:
        data = load_dashboard_data(api_key)
    except DashboardAPIError as exc:
        st.error(str(exc))
        st.info("Verifica que la API esté disponible e inténtalo de nuevo.")
        return

    kpi_columns = st.columns(3)
    kpi_columns[0].metric(
        "Volumen operativo total",
        _format_integer(data["total_recharges"]),
    )
    kpi_columns[1].metric(
        "Ingreso bruto",
        _format_amount(data["gross_revenue"]),
    )
    kpi_columns[2].metric(
        "Volumen de adopción 5G",
        _format_integer(data["five_g_recharges"]),
    )

    chart_columns = st.columns(2)
    with chart_columns[0]:
        st.subheader("Distribución de ingresos por monto")
        revenue_figure = go.Figure(
            data=[
                go.Pie(
                    labels=[
                        f"{amount}" for amount in data["revenue_by_amount"]
                    ],
                    values=list(data["revenue_by_amount"].values()),
                    hole=0.48,
                    marker=dict(colors=PALETTE),
                    hovertemplate="Monto %{label}<br>Ingreso %{value}<extra></extra>",
                )
            ]
        )
        revenue_figure.update_layout(
            margin=dict(t=16, b=16, l=12, r=12),
            legend_title_text="Monto",
            paper_bgcolor="white",
            font_color=PRIMARY_BLUE,
        )
        st.plotly_chart(revenue_figure, width="stretch")

    with chart_columns[1]:
        st.subheader("Recargas por zona o ciudad")
        locations = data["recharges_by_location"]
        location_figure = go.Figure(
            data=[
                go.Bar(
                    x=list(locations.keys()),
                    y=list(locations.values()),
                    marker_color=PRIMARY_BLUE,
                    hovertemplate="%{x}<br>Recargas %{y}<extra></extra>",
                )
            ]
        )
        location_figure.update_layout(
            margin=dict(t=16, b=16, l=12, r=12),
            paper_bgcolor="white",
            plot_bgcolor="white",
            font_color=PRIMARY_BLUE,
            xaxis_title=None,
            yaxis_title="Recargas",
        )
        st.plotly_chart(location_figure, width="stretch")

    if not data["recharges"]:
        st.info("Aún no hay recargas registradas.")
