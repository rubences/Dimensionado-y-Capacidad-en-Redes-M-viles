from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


W_CHIPS = 3.84e6
ETA_TARGET = 0.70
I_FACTOR = 0.65

SERVICES = {
    "Voz AMR 12.2 kb/s": 12.2e3,
    "Datos  32 kb/s": 32e3,
    "Datos  64 kb/s": 64e3,
}

SPEEDS_KMH = [3, 15, 50]
ACTIVITY_FACTORS = np.arange(0.40, 0.75, 0.05)

EBN0_REF_DB = {
    "Voz AMR 12.2 kb/s": 5.0,
    "Datos  32 kb/s": 4.0,
    "Datos  64 kb/s": 3.5,
}

DELTA_FF_DB = {3: 0.0, 15: 1.5, 50: 3.5}

PC_SCENARIOS_DB = {
    "PC eficaz (3 km/h, Δff=0 dB)": 0.0,
    "PC ligero (15 km/h, Δff=+1.5 dB)": 1.5,
    "PC degradado (50 km/h, Δff=+3.5 dB)": 3.5,
}


@dataclass(frozen=True)
class Conclusion:
    title: str
    detail: str


def processing_gain(rb: float) -> float:
    return W_CHIPS / rb


def ebn0_linear(service_name: str, speed_kmh: float) -> float:
    eb_n0_db = EBN0_REF_DB[service_name] + np.interp(speed_kmh, [3, 15, 50], [0.0, 1.5, 3.5])
    return 10 ** (eb_n0_db / 10)


def uplink_load(
    users: float,
    rb: float,
    activity: float,
    ebn0_lin: float,
    W: float = W_CHIPS,
    i: float = I_FACTOR,
) -> float:
    x = ebn0_lin * rb / W
    return users * (1 + i) * (activity * x) / (1 + x)


def nmax(
    rb: float,
    activity: float,
    ebn0_lin: float,
    eta_tgt: float = ETA_TARGET,
    W: float = W_CHIPS,
    i: float = I_FACTOR,
) -> float:
    x = ebn0_lin * rb / W
    return (eta_tgt / (1 + i)) * (1 + x) / (activity * x)


def delta_load(rb: float, activity: float, ebn0_lin: float, W: float = W_CHIPS, i: float = I_FACTOR) -> float:
    x = ebn0_lin * rb / W
    return (1 + i) * (activity * x) / (1 + x)


def build_speed_table(activity: float = 0.50) -> pd.DataFrame:
    records = []
    for service_name, rb in SERVICES.items():
        row = {"Servicio": service_name}
        for speed in SPEEDS_KMH:
            row[f"{speed} km/h"] = int(nmax(rb, activity, ebn0_linear(service_name, speed)))
        records.append(row)
    return pd.DataFrame(records).set_index("Servicio")


def build_activity_table(speed: int = 3) -> pd.DataFrame:
    records = []
    for service_name, rb in SERVICES.items():
        row = {"Servicio": service_name}
        for activity in ACTIVITY_FACTORS:
            row[f"v={activity:.2f}"] = int(nmax(rb, activity, ebn0_linear(service_name, speed)))
        records.append(row)
    return pd.DataFrame(records).set_index("Servicio")


def build_summary_table() -> pd.DataFrame:
    rows = []
    for service_name, rb in SERVICES.items():
        for speed in SPEEDS_KMH:
            for activity in [0.40, 0.50, 0.70]:
                rows.append(
                    {
                        "Servicio": service_name,
                        "Vel. [km/h]": speed,
                        "Act. v": activity,
                        "Gp [dB]": round(10 * np.log10(processing_gain(rb)), 1),
                        "Eb/N0 [dB]": round(EBN0_REF_DB[service_name] + DELTA_FF_DB[speed], 1),
                        "Nmax": int(nmax(rb, activity, ebn0_linear(service_name, speed))),
                    }
                )
    return pd.DataFrame(rows)


def build_pc_comparison(activity: float = 0.50) -> pd.DataFrame:
    rows = []
    for scenario_name, delta in PC_SCENARIOS_DB.items():
        row = {"Escenario PC": scenario_name}
        for service_name, rb in SERVICES.items():
            ebn0_lin = 10 ** ((EBN0_REF_DB[service_name] + delta) / 10)
            row[service_name] = int(nmax(rb, activity, ebn0_lin))
        rows.append(row)
    return pd.DataFrame(rows).set_index("Escenario PC")


def build_speed_curves() -> dict[str, list[dict[str, object]]]:
    speed_range = np.array([1, 3, 5, 10, 15, 20, 30, 50, 70, 100])
    curves: dict[str, list[dict[str, object]]] = {}
    for service_name, rb in SERVICES.items():
        traces = []
        for activity, style in [(0.40, "--"), (0.50, "-"), (0.70, ":")]:
            values = [round(nmax(rb, activity, ebn0_linear(service_name, speed)), 2) for speed in speed_range]
            traces.append(
                {
                    "label": f"v={activity:.2f}",
                    "linestyle": style,
                    "x": speed_range.tolist(),
                    "y": values,
                }
            )
        curves[service_name] = traces
    return curves


def build_activity_curves() -> dict[str, list[dict[str, object]]]:
    activity_range = np.round(np.linspace(0.30, 0.90, 100), 3)
    curves: dict[str, list[dict[str, object]]] = {}
    for service_name, rb in SERVICES.items():
        traces = []
        for speed, style in [(3, "-"), (15, "--"), (50, ":")]:
            values = [round(nmax(rb, activity, ebn0_linear(service_name, speed)), 2) for activity in activity_range]
            traces.append(
                {
                    "label": f"{speed} km/h",
                    "linestyle": style,
                    "x": activity_range.tolist(),
                    "y": values,
                }
            )
        curves[service_name] = traces
    return curves


def admission_control_simulation(arrivals: list[dict[str, object]], eta_tgt: float = ETA_TARGET) -> tuple[pd.DataFrame, float]:
    current_load = 0.0
    results = []
    for index, request in enumerate(arrivals, start=1):
        service_name = str(request["service"])
        speed = int(request["speed_kmh"])
        activity = float(request["activity"])
        dl = delta_load(SERVICES[service_name], activity, ebn0_linear(service_name, speed))
        admitted = current_load + dl <= eta_tgt
        if admitted:
            current_load += dl
        results.append(
            {
                "t": index,
                "Servicio": service_name,
                "v. km/h": speed,
                "Actividad": round(activity, 2),
                "Δη": round(dl, 4),
                "η acum.": round(current_load, 4),
                "Admitida": "Si" if admitted else "No",
            }
        )
    return pd.DataFrame(results), current_load


def build_admission_example(seed: int = 42, arrivals_count: int = 30) -> tuple[pd.DataFrame, float]:
    rng = np.random.default_rng(seed)
    service_names = list(SERVICES.keys())
    arrivals = [
        {
            "service": rng.choice(service_names, p=[0.4, 0.4, 0.2]),
            "speed_kmh": int(rng.choice(SPEEDS_KMH, p=[0.5, 0.35, 0.15])),
            "activity": float(np.round(rng.uniform(0.40, 0.70), 2)),
        }
        for _ in range(arrivals_count)
    ]
    return admission_control_simulation(arrivals)


def build_dashboard_payload() -> dict[str, object]:
    speed_table = build_speed_table()
    activity_table = build_activity_table()
    summary_table = build_summary_table()
    pc_table = build_pc_comparison()
    admission_table, final_load = build_admission_example()

    key_points = [
        Conclusion(
            title="La movilidad reduce la capacidad uplink",
            detail="A igualdad de servicio y actividad, el Nmax cae al aumentar la velocidad porque crece el Eb/N0 requerido y empeora el seguimiento del control de potencia.",
        ),
        Conclusion(
            title="Los servicios de 64 kb/s penalizan mucho más la célula",
            detail="La menor ganancia de procesado hace que unas pocas sesiones intensivas consuman una parte desproporcionada del presupuesto de interferencia.",
        ),
        Conclusion(
            title="La admisión por carga es más útil que contar usuarios",
            detail="La decisión operativa correcta es limitar nuevas sesiones intensivas cuando la carga estimada supera 0.70 y bloquearlas de forma estricta por encima de 0.72.",
        ),
    ]

    return {
        "cards": {
            "eta_target": ETA_TARGET,
            "intercell_factor": I_FACTOR,
            "w_mchips": round(W_CHIPS / 1e6, 2),
            "max_voice_3_kmh": int(nmax(SERVICES["Voz AMR 12.2 kb/s"], 0.50, ebn0_linear("Voz AMR 12.2 kb/s", 3))),
            "max_data64_3_kmh": int(nmax(SERVICES["Datos  64 kb/s"], 0.50, ebn0_linear("Datos  64 kb/s", 3))),
            "max_data64_50_kmh": int(nmax(SERVICES["Datos  64 kb/s"], 0.50, ebn0_linear("Datos  64 kb/s", 50))),
            "admission_final_load": round(final_load, 4),
        },
        "tables": {
            "speed": speed_table.reset_index().to_dict(orient="records"),
            "activity": activity_table.reset_index().to_dict(orient="records"),
            "summary": summary_table.to_dict(orient="records"),
            "pc": pc_table.reset_index().to_dict(orient="records"),
            "admission": admission_table.to_dict(orient="records"),
        },
        "charts": {
            "speed_curves": build_speed_curves(),
            "activity_curves": build_activity_curves(),
            "admission_load": {
                "x": admission_table["t"].tolist(),
                "y": admission_table["η acum."].tolist(),
                "threshold": ETA_TARGET,
            },
            "pc_bars": {
                "labels": list(SERVICES.keys()),
                "series": [
                    {
                        "label": scenario_name,
                        "values": [int(pc_table.loc[scenario_name, service_name]) for service_name in SERVICES.keys()],
                    }
                    for scenario_name in pc_table.index
                ],
            },
        },
        "conclusions": [point.__dict__ for point in key_points],
    }