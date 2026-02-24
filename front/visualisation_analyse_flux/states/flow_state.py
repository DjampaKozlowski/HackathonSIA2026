import reflex as rx
import pandas as pd
import plotly.graph_objects as go
from typing import TypedDict, Any
import logging


class ReconcilData(TypedDict):
    original_idx: int
    data_id: str
    data_ref: str
    confidence: int
    raison: str
    status: str


class FlowState(rx.State):
    reconcil_data: list[ReconcilData] = []
    selected_row_idx: int = -1
    search_query: str = ""
    sort_column: str = "data_id"
    sort_ascending: bool = True
    dataset_name: str = ""

    @rx.event
    def load_data(self):
        try:
            file_path = "assets/test_var_rapprochement.xlsx"
            self.dataset_name = file_path.split("/")[-1].split(".")[0]
            df = pd.read_excel(file_path, engine="openpyxl")
            data = []
            for i, row in df.iterrows():
                data_id = str(row["data_id"]) if pd.notna(row["data_id"]) else "Inconnu"
                raw_ref = row["data_ref"]
                data_ref = str(raw_ref) if pd.notna(raw_ref) else "À créer"
                raw_conf = row["% de rapprochement "]
                if (
                    pd.isna(raw_conf)
                    or str(raw_conf).strip() == "nouvelle variable créée"
                ):
                    confidence = 0
                    status = "Nouvelle variable"
                else:
                    try:
                        confidence = int(float(raw_conf))
                        status = "Rapproché"
                    except:
                        logging.exception("Unexpected error")
                        confidence = 0
                        status = "Nouvelle variable"
                raw_raison = row["raison du rapprochement"]
                raison = str(raw_raison) if pd.notna(raw_raison) else ""
                data.append(
                    {
                        "original_idx": i,
                        "data_id": data_id,
                        "data_ref": data_ref,
                        "confidence": confidence,
                        "raison": raison,
                        "status": status,
                    }
                )
            self.reconcil_data = data
        except Exception as e:
            logging.exception(f"Error: {e}")

    @rx.var
    def sankey_figure(self) -> go.Figure:
        if not self.reconcil_data:
            return go.Figure()
        unmatched_sources = {
            d["data_id"]
            for d in self.reconcil_data
            if d["status"] == "Nouvelle variable"
        }
        left_labels = list(dict.fromkeys((d["data_id"] for d in self.reconcil_data)))
        right_labels = list(dict.fromkeys((d["data_ref"] for d in self.reconcil_data)))
        all_labels = left_labels + right_labels
        display_labels = []
        for label in all_labels:
            if label in unmatched_sources:
                display_labels.append(f"{label} 🆕")
            else:
                display_labels.append(label)
        label_to_idx = {label: i for i, label in enumerate(all_labels)}
        node_colors = []
        for label in all_labels:
            if label in left_labels:
                if label in unmatched_sources:
                    node_colors.append("#fecaca")
                else:
                    node_colors.append("#dbeafe")
            elif label == "À créer":
                node_colors.append("#fee2e2")
            else:
                node_colors.append("#f0f4f8")
        sources = []
        targets = []
        values = []
        link_colors = []
        link_labels = []
        link_customdata = []
        for d in self.reconcil_data:
            src_idx = label_to_idx[d["data_id"]]
            tgt_idx = label_to_idx[d["data_ref"]]
            sources.append(src_idx)
            targets.append(tgt_idx)
            val = d["confidence"] if d["status"] == "Rapproché" else 50
            values.append(val)
            l_label = (
                f"{d['confidence']}%"
                if d["status"] == "Rapproché"
                else "Nouvelle variable"
            )
            link_labels.append(l_label)
            if d["confidence"] >= 95:
                color = "rgba(34, 197, 94, 0.4)"
            elif d["confidence"] >= 80:
                color = "rgba(245, 158, 11, 0.4)"
            else:
                color = "rgba(239, 68, 68, 0.45)"
            link_colors.append(color)
            raison_text = (
                d["raison"] if d["raison"] != "" else "Nouvelle variable à créer"
            )
            link_customdata.append([self.dataset_name, d["confidence"], raison_text])
        fig = go.Figure(
            data=[
                go.Sankey(
                    node=dict(
                        pad=20,
                        thickness=25,
                        line=dict(color="#e2e8f0", width=1),
                        label=display_labels,
                        color=node_colors,
                    ),
                    link=dict(
                        source=sources,
                        target=targets,
                        value=values,
                        color=link_colors,
                        label=link_labels,
                        customdata=link_customdata,
                        hovertemplate="Source: %{customdata[0]}<br>Confiance: %{customdata[1]}%<br>Raison: %{customdata[2]}<extra></extra>",
                    ),
                )
            ]
        )
        fig.update_layout(
            font=dict(size=12, family="Inter"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=20, b=20),
            height=450,
        )
        return fig
        middle_nodes = ["Rapproché", "Nouvelle variable"]
        right_nodes = list(dict.fromkeys((d["data_ref"] for d in self.reconcil_data)))
        for n in left_nodes:
            nodes.append(n)
            node_colors.append("#dbeafe")
        for n in middle_nodes:
            nodes.append(n)
            if n == "Rapproché":
                node_colors.append("#d1fae5")
            else:
                node_colors.append("#fee2e2")
        for n in right_nodes:
            nodes.append(n)
            node_colors.append("#f0f4f8")
        node_indices = {name: i for i, name in enumerate(nodes)}
        sources = []
        targets = []
        values = []
        link_colors = []
        for d in self.reconcil_data:
            sources.append(node_indices[d["data_id"]])
            targets.append(node_indices[d["status"]])
            val = d["confidence"] if d["status"] == "Rapproché" else 50
            values.append(val)
            if d["confidence"] >= 95:
                color = "rgba(34, 197, 94, 0.4)"
            elif d["confidence"] >= 80:
                color = "rgba(245, 158, 11, 0.4)"
            else:
                color = "rgba(239, 68, 68, 0.3)"
            link_colors.append(color)
            sources.append(node_indices[d["status"]])
            targets.append(node_indices[d["data_ref"]])
            values.append(val)
            link_colors.append(color)
        fig = go.Figure(
            data=[
                go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="#e2e8f0", width=1),
                        label=nodes,
                        color=node_colors,
                    ),
                    link=dict(
                        source=sources, target=targets, value=values, color=link_colors
                    ),
                )
            ]
        )
        fig.update_layout(
            font=dict(size=12, family="Inter"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=20, b=20),
            height=450,
        )
        return fig

    @rx.var
    def selected_row_data(self) -> dict[str, str | int]:
        if self.selected_row_idx >= 0 and self.selected_row_idx < len(
            self.reconcil_data
        ):
            d = self.reconcil_data[self.selected_row_idx]
            return {
                "data_id": d["data_id"],
                "data_ref": d["data_ref"],
                "confidence": d["confidence"],
                "raison": d["raison"],
                "status": d["status"],
            }
        return {}

    @rx.var
    def total_variables(self) -> int:
        return len(self.reconcil_data)

    @rx.var
    def matched_count(self) -> int:
        return len([d for d in self.reconcil_data if d["status"] == "Rapproché"])

    @rx.var
    def new_variables_count(self) -> int:
        return len(
            [d for d in self.reconcil_data if d["status"] == "Nouvelle variable"]
        )

    @rx.var
    def avg_confidence(self) -> float:
        matched = [
            d["confidence"] for d in self.reconcil_data if d["status"] == "Rapproché"
        ]
        if not matched:
            return 0.0
        return sum(matched) / len(matched)

    @rx.var
    def filtered_data(self) -> list[ReconcilData]:
        data: list[ReconcilData] = []
        for d in self.reconcil_data:
            if (
                self.search_query.lower() in d["data_id"].lower()
                or self.search_query.lower() in d["data_ref"].lower()
            ):
                data.append(d)
        reverse = not self.sort_ascending
        return sorted(
            data, key=lambda x: str(x.get(self.sort_column, "")), reverse=reverse
        )

    @rx.event
    def set_search_query(self, query: str):
        self.search_query = query

    @rx.event
    def toggle_sort(self, column: str):
        if self.sort_column == column:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_column = column
            self.sort_ascending = True

    @rx.event
    def select_row(self, idx: int):
        self.selected_row_idx = idx

    @rx.event
    def handle_sankey_click(
        self, points: list[dict[str, str | int | float | bool | list | dict]]
    ):
        if len(points) > 0:
            point = points[0]
            if "label" in point:
                label = point["label"]
                for d in self.reconcil_data:
                    if d["data_id"] == label or d["data_ref"] == label:
                        self.selected_row_idx = d["original_idx"]
                        break