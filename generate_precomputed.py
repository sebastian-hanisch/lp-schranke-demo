"""Erzeugt lpb_precomputed.json: das Raster mit LP (dieselben Zellen und Seeds wie Stück 2) und die Suche nach Gegenbeispielen zur Rundung.

    python generate_precomputed.py            # rechnet alles neu (ungefähr 10 bis 20 Minuten: LP per Spaltenerzeugung für alle 900 Rasterinstanzen, ILP für die Fälle „LP = FFD - 1“)
    python generate_precomputed.py --retry-u  # rechnet nur die Instanzen mit Code U (ILP nicht entschieden) mit dem Zeitlimit der Konstanten noch einmal
    python generate_precomputed.py --check    # rechnet das Schnelle nach (Aufteilung L1 / L2 / offen je Zelle ohne LP, die Suche bei 8 Paketen) und vergleicht

Codes je Instanz: 1 FFD = L1, 2 FFD = L2, P aufgerundeter LP-Wert = FFD, T LP = FFD - 1 und Packung mit FFD - 1 Containern vorhanden, U LP = FFD - 1 und ILP nicht entschieden,
V LP = FFD - 1 und keine Packung (Rundung verletzt), X aufgerundeter LP-Wert mehr als 1 unter FFD. Das Optimum bei 12 Paketen kommt aus der Teilmengen-DP, bei 20 und 30 aus
`scipy.optimize.milp` mit Zeitlimit C.ILP_ZEITLIMIT; die Zahl der nicht entschiedenen Instanzen hängt von der Rechenzeit ab, die Datei hält den Stand dieses Laufs fest."""

import json
import sys
import time

import lpb_algorithm as A
import lpb_constants as C
import lpb_evaluation as ev
from dev.cg import lp_wert_cg
from dev.ilp import ilp_machbar


def lp_wert(inst) -> float:
    """LP-Wert: bis 12 Pakete mit allen Mustern (schnell), sonst per Spaltenerzeugung (dev/cg.py); beide rechnen dieselbe Relaxation (Tests vergleichen sie)."""
    if inst.n <= C.OPT_LIMIT:
        return A.lp_loesen(inst.sizes, inst.cap)["wert"]
    return lp_wert_cg(list(inst.sizes), inst.cap)


def packbar(inst, m: int):
    """Gibt es eine Packung mit höchstens m Containern? Bis 12 Pakete per Teilmengen-DP, sonst ganzzahliges Programm mit Zeitlimit (None bei Zeitüberschreitung)."""
    if inst.n <= C.OPT_LIMIT:
        return A.optimum(inst.sizes, inst.cap, C.OPT_LIMIT) <= m
    return ilp_machbar(inst.sizes, m, inst.cap, C.ILP_ZEITLIMIT)


def zelle(verteilung: int, n_index: int) -> dict:
    from lpb_scenario import raster_instanz

    codes, ueber, unter = [], 0, 0
    for j in range(C.INSTANZEN):
        code, o, u = ev.instanz_code(raster_instanz(verteilung, n_index, j), lp_wert, packbar)
        codes.append(code)
        ueber += o
        unter += u
    return {"codes": "".join(codes), "lp_ueber_l2": ueber, "lp_unter_l2": unter}


def erzeugen() -> dict:
    daten = {"instanzen": C.INSTANZEN, "cap": C.MESS_CAP, "ilp_zeitlimit": C.ILP_ZEITLIMIT, "zellen": {}, "suche": {}}
    for d in range(len(C.VERTEILUNGEN)):
        for ni in range(len(C.MESS_N)):
            t = time.perf_counter()
            daten["zellen"][ev.zelle_schluessel(d, ni)] = zelle(d, ni)
            c = daten["zellen"][ev.zelle_schluessel(d, ni)]["codes"]
            print(f"{ev.zelle_schluessel(d, ni)}: {time.perf_counter() - t:.0f} s  P {c.count('P')} T {c.count('T')} U {c.count('U')} V {c.count('V')} X {c.count('X')}", flush=True)
    for n in C.SUCHE_N:
        t = time.perf_counter()
        daten["suche"][str(n)] = ev.suche_zelle(n)
        print(f"Suche n = {n}: {time.perf_counter() - t:.0f} s  {daten['suche'][str(n)]['luecken']}", flush=True)
    return daten


def pruefen() -> int:
    gespeichert = ev.vorberechnet()
    schlecht = 0
    for d in range(len(C.VERTEILUNGEN)):
        for ni in range(len(C.MESS_N)):
            z = ev.zaehlen(gespeichert["zellen"][ev.zelle_schluessel(d, ni)]["codes"])
            frisch = ev.aufteilung_frisch(d, ni)
            offen = sum(z[k] for k in ("lp_beweist", "lp_scharf", "offen_unentschieden", "rundung_verletzt", "lp_weit_unter"))
            if (z["l1"], z["l2"], offen) != (frisch["l1"], frisch["l2"], frisch["offen"]):
                schlecht += 1
                print("ABWEICHUNG Aufteilung", ev.zelle_schluessel(d, ni))
    if ev.suche_zelle(8) != gespeichert["suche"]["8"]:
        schlecht += 1
        print("ABWEICHUNG Suche 8")
    print("gleich" if not schlecht else f"{schlecht} Abweichungen")
    return 1 if schlecht else 0


def nachrechnen_unentschiedene() -> int:
    """Rechnet die Instanzen mit Code U (ILP nicht entschieden) mit dem Zeitlimit C.ILP_ZEITLIMIT noch einmal und schreibt die Datei neu.

    Gedacht für den Fall, dass ein Lauf bei ausgelastetem Rechner mit kürzerem Zeitlimit viele Instanzen offen gelassen hat: Die Codes 1, 2, P, T und V bleiben, nur U wird neu entschieden
    (zu T, V oder wieder U). Das Ergebnis entspricht einem Lauf mit diesem Zeitlimit auf ruhigem Rechner."""
    from lpb_scenario import raster_instanz

    daten = json.loads(ev.PRECOMPUTED.read_text(encoding="utf-8"))
    for d in range(len(C.VERTEILUNGEN)):
        for ni in range(len(C.MESS_N)):
            schluessel = ev.zelle_schluessel(d, ni)
            codes = list(daten["zellen"][schluessel]["codes"])
            for j, c in enumerate(codes):
                if c != "U":
                    continue
                inst = raster_instanz(d, ni, j)
                f = len(A.ffd(inst.sizes, inst.cap))
                t = time.perf_counter()
                r = packbar(inst, f - 1)
                codes[j] = "T" if r is True else "V" if r is False else "U"
                print(f"{schluessel} Instanz {j}: {codes[j]} ({time.perf_counter() - t:.0f} s)", flush=True)
            daten["zellen"][schluessel]["codes"] = "".join(codes)
    daten["ilp_zeitlimit"] = C.ILP_ZEITLIMIT
    ev.PRECOMPUTED.write_text(json.dumps(daten, indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print("geschrieben:", ev.PRECOMPUTED)
    return 0


def main() -> int:
    if "--retry-u" in sys.argv:
        return nachrechnen_unentschiedene()
    if "--check" in sys.argv:
        return pruefen()
    text = json.dumps(erzeugen(), indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    ev.PRECOMPUTED.write_text(text, encoding="utf-8")
    print("geschrieben:", ev.PRECOMPUTED)
    return 0


if __name__ == "__main__":
    sys.exit(main())
