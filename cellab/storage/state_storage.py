"""
cellab/storage/state_storage.py
--------------------------------
Gestionarea istoricului simulării în memorie și serializarea/recuperarea
experimentelor din fișiere JSON pe disc.

Conform cerințelor Livrabilului 2:
  - store_intermediate=True  → se păstrează toate generațiile 0..N în `history`
  - store_intermediate=False → se păstrează doar generația 0 (initial_snapshot)
                               și ultima generație calculată (latest_snapshot)
"""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING

from cellab.core.id_generator import IDGenerator
from cellab.core.models import AutomatonDefinition, CellType, ExperimentParams
from cellab.world.grid import GridState


class StateStorage:
    """
    Gestionează istoricul generațiilor unui experiment de automat celular.

    Attributes
    ----------
    store_intermediate : bool
        Dacă True, toate generațiile sunt păstrate în `history`.
        Dacă False, se păstrează doar prima și ultima generație.
    history : list[GridState]
        Lista generațiilor înregistrate (goală dacă store_intermediate=False).
    initial_snapshot : GridState | None
        Prima stare înregistrată (generația 0).
    latest_snapshot : GridState | None
        Ultima stare înregistrată (mereu actualizată).
    """

    def __init__(self, store_intermediate: bool = True) -> None:
        self.store_intermediate: bool = store_intermediate
        self.history: list[GridState] = []
        self.initial_snapshot: GridState | None = None
        self.latest_snapshot: GridState | None = None

    # ------------------------------------------------------------------
    # Înregistrare stare
    # ------------------------------------------------------------------

    def record_state(self, state: GridState) -> None:
        """
        Înregistrează o stare de generație nouă.

        - Salvează prima stare în `initial_snapshot`.
        - Actualizează mereu `latest_snapshot`.
        - Adaugă la `self.history` doar dacă `store_intermediate` este True.

        Parameters
        ----------
        state : GridState
            Starea de înregistrat.
        """
        if self.initial_snapshot is None:
            self.initial_snapshot = state

        self.latest_snapshot = state

        if self.store_intermediate:
            self.history.append(state)

    # Alias utilizat de SimulationEngine (compatibilitate cu codul existent)
    def add_state(self, state: GridState) -> None:
        """Alias pentru record_state() — compatibilitate cu SimulationEngine."""
        self.record_state(state)

    # ------------------------------------------------------------------
    # Interogare stări
    # ------------------------------------------------------------------

    def get_state_at_generation(self, gen_idx: int) -> GridState | None:
        """
        Returnează starea de la generația `gen_idx`.

        Funcționează corect indiferent dacă `store_intermediate` este True sau False:
        - Dacă historia e goală (store_intermediate=False), returnează
          `initial_snapshot` (gen 0) sau `latest_snapshot` (ultima gen)
          când indicii corespund.
        - Altfel, caută liniar în `history` după `generation_index`.

        Parameters
        ----------
        gen_idx : int
            Indexul generației căutate (0-based).

        Returns
        -------
        GridState | None
            Starea găsită sau None dacă nu există.
        """
        if self.store_intermediate:
            for s in self.history:
                if s.generation_index == gen_idx:
                    return s
            return None

        # store_intermediate=False — verificăm snapshot-urile
        if self.initial_snapshot is not None and self.initial_snapshot.generation_index == gen_idx:
            return self.initial_snapshot
        if self.latest_snapshot is not None and self.latest_snapshot.generation_index == gen_idx:
            return self.latest_snapshot
        return None

    def get_all_states(self) -> list[GridState]:
        """
        Returnează lista tuturor stărilor disponibile.

        - store_intermediate=True  → returnează `history` (toate generațiile).
        - store_intermediate=False → returnează [initial_snapshot, latest_snapshot]
          (fără duplicate dacă există o singură generație).

        Returns
        -------
        list[GridState]
            Lista stărilor disponibile.
        """
        if self.store_intermediate:
            return list(self.history)

        # store_intermediate=False
        result: list[GridState] = []
        if self.initial_snapshot is not None:
            result.append(self.initial_snapshot)
        if (
            self.latest_snapshot is not None
            and self.latest_snapshot is not self.initial_snapshot
        ):
            result.append(self.latest_snapshot)
        return result

    # ------------------------------------------------------------------
    # Serializare JSON
    # ------------------------------------------------------------------

    def save_experiment_to_file(
        self,
        filepath: str,
        definition: AutomatonDefinition,
        params: ExperimentParams,
    ) -> None:
        """
        Salvează experimentul complet (definiție, parametri, stări) într-un fișier JSON.

        Parameters
        ----------
        filepath : str
            Calea fișierului de destinație (directoarele părinți vor fi create automat).
        definition : AutomatonDefinition
            Definiția automatului celular.
        params : ExperimentParams
            Parametrii experimentului.
        """
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

        states_data = [_grid_state_to_dict(s) for s in self.get_all_states()]

        payload = {
            "definition": _automaton_definition_to_dict(definition),
            "params": _experiment_params_to_dict(params),
            "store_intermediate": self.store_intermediate,
            "states": states_data,
        }

        with open(filepath, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------
    # Deserializare JSON
    # ------------------------------------------------------------------

    @staticmethod
    def load_experiment_from_file(
        filepath: str,
    ) -> tuple[AutomatonDefinition, ExperimentParams, "StateStorage"]:
        """
        Citește un fișier JSON și reconstruiește obiectele
        ``AutomatonDefinition``, ``ExperimentParams`` și ``StateStorage``.

        Contoarele IDGenerator sunt actualizate cu `sync_counter` pentru a
        evita coliziunile de ID-uri după restaurare.

        Parameters
        ----------
        filepath : str
            Calea fișierului JSON de citit.

        Returns
        -------
        tuple[AutomatonDefinition, ExperimentParams, StateStorage]
            Trioul de obiecte reconstruite.
        """
        with open(filepath, "r", encoding="utf-8") as fh:
            payload = json.load(fh)

        definition = _automaton_definition_from_dict(payload["definition"])
        params = _experiment_params_from_dict(payload["params"])
        store_intermediate: bool = payload.get("store_intermediate", True)

        storage = StateStorage(store_intermediate=store_intermediate)
        for state_dict in payload["states"]:
            gs = _grid_state_from_dict(state_dict)
            # Înregistrăm direct în history / snapshots, fără filtrare
            if storage.initial_snapshot is None:
                storage.initial_snapshot = gs
            storage.latest_snapshot = gs
            if store_intermediate:
                storage.history.append(gs)

        # Sincronizăm contoarele IDGenerator pentru toate categoriile
        IDGenerator.sync_counter(IDGenerator.CAT_AUTOMATON, definition.automaton_id)
        IDGenerator.sync_counter(IDGenerator.CAT_EXPERIMENT, params.experiment_id)
        for gs in storage.get_all_states():
            IDGenerator.sync_counter(IDGenerator.CAT_GRID_STATE, gs.state_id)

        return definition, params, storage

    # ------------------------------------------------------------------
    # Repr util
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        n = len(self.history) if self.store_intermediate else len(self.get_all_states())
        return (
            f"StateStorage(store_intermediate={self.store_intermediate}, "
            f"states_stored={n})"
        )


# ==========================================================================
# Funcții helper private — serializare / deserializare
# ==========================================================================


def _cell_type_to_dict(ct: CellType) -> dict:
    return {
        "state_id": ct.state_id,
        "name": ct.name,
        "symbol": ct.symbol,
        "color_hex": ct.color_hex,
    }


def _automaton_definition_to_dict(defn: AutomatonDefinition) -> dict:
    return {
        "automaton_id": defn.automaton_id,
        "name": defn.name,
        "dimension": defn.dimension,
        "neighborhood_type": defn.neighborhood_type,
        "cell_types": [_cell_type_to_dict(ct) for ct in defn.cell_types],
    }


def _experiment_params_to_dict(params: ExperimentParams) -> dict:
    return {
        "experiment_id": params.experiment_id,
        "automaton_name": params.automaton_name,
        "width": params.width,
        "height": params.height,
        "num_generations": params.num_generations,
        "store_intermediate": params.store_intermediate,
        "boundary_type": params.boundary_type,
        "init_mode": params.init_mode,
        "random_seed": params.random_seed,
    }


def _grid_state_to_dict(gs: GridState) -> dict:
    return {
        "state_id": gs.state_id,
        "generation_index": gs.generation_index,
        "width": gs.width,
        "height": gs.height,
        "boundary_type": gs.boundary_type,
        "default_border_state": gs.default_border_state,
        "cells": gs.cells,
    }


def _automaton_definition_from_dict(d: dict) -> AutomatonDefinition:
    defn = AutomatonDefinition(
        name=d["name"],
        dimension=d["dimension"],
        neighborhood_type=d["neighborhood_type"],
        automaton_id=d["automaton_id"],
    )
    for ct_dict in d["cell_types"]:
        ct = CellType(
            state_id=ct_dict["state_id"],
            name=ct_dict["name"],
            symbol=ct_dict["symbol"],
            color_hex=ct_dict.get("color_hex", "#FFFFFF"),
        )
        defn.cell_types.append(ct)
    return defn


def _experiment_params_from_dict(d: dict) -> ExperimentParams:
    return ExperimentParams(
        automaton_name=d["automaton_name"],
        width=d["width"],
        height=d["height"],
        num_generations=d["num_generations"],
        store_intermediate=d.get("store_intermediate", True),
        boundary_type=d.get("boundary_type", "FIXED"),
        init_mode=d.get("init_mode", "CUSTOM"),
        random_seed=d.get("random_seed", 42),
        experiment_id=d["experiment_id"],
    )


def _grid_state_from_dict(d: dict) -> GridState:
    gs = GridState(
        width=d["width"],
        height=d["height"],
        generation_index=d["generation_index"],
        boundary_type=d.get("boundary_type", "FIXED"),
        default_border_state=d.get("default_border_state", 0),
        state_id=d["state_id"],
    )
    # Suprascrierea celulelor cu datele din JSON (deep copy)
    gs.cells = [list(row) for row in d["cells"]]
    return gs
