"""Kennzahlen, Verdikt-Logik und die vorberechneten Experimente (Raster aus Stück 2 mit LP, Suche nach Gegenbeispielen; lpb_precomputed.json)."""

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import lpb_algorithm as A
import lpb_constants as C
from lpb_scenario import Instance, beispiel, live_instanz, raster_instanz

PRECOMPUTED = Path(__file__).resolve().parent / "lpb_precomputed.json"


@dataclass(frozen=True)
class Settings:
    beispiel: int = 0
    verteilung: int = 0
    n: int = C.DEFAULT_N
    seed: int = C.DEFAULT_SEED


@dataclass(frozen=True)
class Analysis:
    inst: Instance
    bins: tuple           # FFD-Packung
    ffd: int
    schranke_l1: int
    schranke_l2: int
    lp: dict              # LP-Lösung (lpb_algorithm.lp_loesen): wert, muster, preise
    lp_zahl: int          # aufgerundeter LP-Wert
    opt: object           # exaktes Optimum (int) oder None
    ausgang: str
    settings: Settings


def instanz(s: Settings) -> Instance:
    return live_instanz(s.verteilung, s.n, s.seed) if s.beispiel == C.ZUFALL else beispiel(s.beispiel)


def analyse(s: Settings) -> Analysis:
    inst = instanz(s)
    bins = A.ffd(inst.sizes, inst.cap)
    assert A.container_pruefen(inst.sizes, bins, inst.cap)
    s1, s2 = A.l1(inst.sizes, inst.cap), A.l2(inst.sizes, inst.cap)
    lp = A.lp_loesen(inst.sizes, inst.cap)
    zahl = A.lp_aufgerundet(lp["wert"])
    opt = A.optimum(inst.sizes, inst.cap, C.OPT_LIMIT)
    return Analysis(inst, tuple(tuple(b) for b in bins), len(bins), s1, s2, lp, zahl, opt, A.ausgang(len(bins), s1, s2, zahl, opt), s)


# ------------------------------------------------------------------------------------------------------------------------------------------
# Verdikte (reine Funktionen: (Art, Text))


def verdict_ausgang(a: Analysis) -> tuple[str, str]:
    """Kernfrage: Wer beweist hier, dass FFD optimal ist, oder woran liegt es, dass es nicht bewiesen ist?"""
    f, s1, s2, lp, z, opt = a.ffd, a.schranke_l1, a.schranke_l2, a.lp["wert"], a.lp_zahl, a.opt
    werte = f"der LP-Wert ist {lp:.4f}, aufgerundet {z}"
    if a.ausgang == "l1":
        return "success", f"FFD braucht **{f}** Container, und die Volumenschranke L1 ist {s1}: FFD ist **bewiesen optimal**; {werte}."
    if a.ausgang == "l2":
        return "success", (f"FFD braucht **{f}** Container. L1 sagt nur {s1}, aber L2 ist {s2}: FFD ist **bewiesen optimal**; {werte}, das bestätigt es.")
    if a.ausgang == "lp_beweist":
        return "success", (f"FFD braucht **{f}** Container. Die Schranken L1 ({s1}) und L2 ({s2}) können das nicht beweisen, aber {werte}: "
                           f"FFD ist durch den LP-Wert **bewiesen optimal** (Optimum {opt}).")
    if a.ausgang == "lp_scharf":
        return "warning", (f"FFD braucht **{f}** Container; {werte}, und das Optimum ist **{opt}**: FFD braucht {f - opt} Container zu viel. "
                           f"Die LP-Schranke trifft das Optimum, L1 ({s1}) und L2 ({s2}) {'auch' if s2 == opt else 'nicht'}.")
    if a.ausgang == "lp_schwach":
        return "warning", (f"FFD braucht **{f}** Container; {werte}, das Optimum ist aber **{opt}**: Die Rundung des LP-Wertes liegt unter dem Optimum, die LP-Schranke ist hier zu schwach.")
    return "info", f"FFD braucht **{f}** Container; {werte}. Das Optimum ist bei dieser Paketzahl nicht berechnet."


# ------------------------------------------------------------------------------------------------------------------------------------------
# Raster (dieselben Instanzen wie Stück 2)


def instanz_code(inst: Instance, lp_wert, packbar):
    """Ausgangscode einer Rasterinstanz (Codes siehe lpb_constants): `lp_wert(inst)` liefert den LP-Wert, `packbar(inst, m)` die Antwort auf „gibt es eine Packung mit höchstens m
    Containern?“ (True, False oder None bei Zeitlimit). Gibt (Code, LP über L2, LP unter L2) zurück; der aufgerundete LP-Wert darf nie über FFD liegen."""
    f = len(A.ffd(inst.sizes, inst.cap))
    s1, s2 = A.l1(inst.sizes, inst.cap), A.l2(inst.sizes, inst.cap)
    if f == s1:
        # Der LP-Wert ist mindestens Summe/Kapazität, aufgerundet also mindestens L1 = FFD, und höchstens FFD: gleich FFD = L1 = L2. Ein LP ist nicht nötig.
        return "1", False, False
    z = A.lp_aufgerundet(lp_wert(inst))
    if z > f:
        raise ValueError("aufgerundeter LP-Wert über FFD: Fehler im LP oder in FFD")
    ueber, unter = z > s2, z < s2
    if f == s2:
        return "2", ueber, unter
    if z == f:
        return "P", ueber, unter
    if z == f - 1:
        r = packbar(inst, f - 1)
        return ("T" if r is True else "V" if r is False else "U"), ueber, unter
    return "X", ueber, unter


def zelle_schluessel(verteilung: int, n_index: int) -> str:
    return f"{C.VERTEILUNGEN[verteilung][0]}|{C.MESS_N[n_index]}"


@lru_cache(maxsize=1)
def vorberechnet() -> dict:
    return json.loads(PRECOMPUTED.read_text(encoding="utf-8"))


def zaehlen(codes: str) -> dict:
    return {name: codes.count(code) for code, name in C.AUSGANG_CODES.items()}


def zeile(verteilung: int, n_index: int, daten: dict | None = None) -> dict:
    daten = daten or vorberechnet()
    z = daten["zellen"][zelle_schluessel(verteilung, n_index)]
    return {"name": C.VERTEILUNGEN[verteilung][1], "n": C.MESS_N[n_index], "instanzen": len(z["codes"]), **zaehlen(z["codes"]),
            "ueber_l2": z["lp_ueber_l2"], "unter_l2": z["lp_unter_l2"], "zeitlimit": daten["ilp_zeitlimit"]}


def aufteilung_frisch(verteilung: int, n_index: int, instanzen: int = C.INSTANZEN) -> dict:
    """Zählt ohne LP, wie viele Instanzen einer Zelle FFD gleich L1, gleich L2 (über L1) oder darüber haben (schnell und exakt; Gegenprobe zur Datei)."""
    out = {"l1": 0, "l2": 0, "offen": 0}
    for j in range(instanzen):
        inst = raster_instanz(verteilung, n_index, j)
        f = len(A.ffd(inst.sizes, inst.cap))
        s1, s2 = A.l1(inst.sizes, inst.cap), A.l2(inst.sizes, inst.cap)
        out["l1" if f == s1 else "l2" if f == s2 else "offen"] += 1
    return out


def verdict_raster(z: dict) -> tuple[str, str]:
    """Verdikt zur gewählten Zelle: wer FFD beweist und was beim LP-Wert offen bleibt (reine Funktion, Zählungen aus `zeile`)."""
    text = (f"Für »{z['name']}« mit n = {z['n']} Paketen beweist die Volumenschranke L1 bei {z['l1']} von {z['instanzen']} Instanzen, dass FFD optimal ist, "
            f"L2 zusätzlich bei {z['l2']} und der LP-Wert noch bei {z['lp_beweist']}.")
    if z["lp_scharf"]:
        text += f" In {z['lp_scharf']} Instanzen ist der aufgerundete LP-Wert gleich dem Optimum, FFD braucht dort einen Container mehr."
    if z["offen_unentschieden"]:
        text += f" In {z['offen_unentschieden']} Instanzen liegt der aufgerundete LP-Wert einen Container unter FFD und das Optimum ist nicht entschieden (ILP nach {z['zeitlimit']:.0f} s abgebrochen)."
    if z["rundung_verletzt"]:
        text += f" In {z['rundung_verletzt']} Instanzen liegt das Optimum über dem aufgerundeten LP-Wert."
    if z["lp_weit_unter"]:
        text += f" In {z['lp_weit_unter']} Instanzen liegt der aufgerundete LP-Wert mehr als einen Container unter FFD."
    text += f" Der aufgerundete LP-Wert liegt in {z['ueber_l2']} Instanzen über L2 und in {z['unter_l2']} darunter."
    schwach = z["offen_unentschieden"] + z["rundung_verletzt"] + z["lp_weit_unter"]
    return ("warning" if schwach else "info"), text


# ------------------------------------------------------------------------------------------------------------------------------------------
# Suche nach Gegenbeispielen zur Rundung


def suche_zelle(n: int, instanzen: int | None = None) -> dict:
    """Rechnet eine Größe der Suche frisch: Verteilung von (Optimum minus aufgerundeter LP-Wert) über `instanzen` feste Zufallsinstanzen (Teilmengen-DP, LP mit allen Mustern)."""
    from lpb_scenario import suche_instanz

    luecken: dict[int, int] = {}
    anzahl = C.SUCHE_INSTANZEN[n] if instanzen is None else instanzen
    for j in range(anzahl):
        sizes = suche_instanz(n, j)
        opt = A.optimum(sizes, C.SUCHE_CAP, C.OPT_LIMIT)
        z = A.lp_aufgerundet(A.lp_loesen(sizes, C.SUCHE_CAP)["wert"])
        luecken[opt - z] = luecken.get(opt - z, 0) + 1
    return {"instanzen": anzahl, "luecken": {str(g): c for g, c in sorted(luecken.items())}}


def suche_zeile(n: int, daten: dict | None = None) -> dict:
    daten = daten or vorberechnet()
    z = daten["suche"][str(n)]
    return {"n": n, "instanzen": z["instanzen"], "gleich": z["luecken"].get("0", 0), "verletzt": sum(c for g, c in z["luecken"].items() if int(g) > 0)}


def verdict_suche(zeilen: list[dict]) -> tuple[str, str]:
    gesamt = sum(z["instanzen"] for z in zeilen)
    gleich = sum(z["gleich"] for z in zeilen)
    verletzt = sum(z["verletzt"] for z in zeilen)
    text = (f"In {gesamt} zufälligen Instanzen mit {min(z['n'] for z in zeilen)} bis {max(z['n'] for z in zeilen)} Paketen ist das Optimum in {gleich} gleich dem aufgerundeten LP-Wert "
            f"und in {verletzt} größer.")
    if verletzt:
        return "warning", text + " Hier liegt die LP-Schranke unter dem Optimum."
    return "info", text + " Gegenbeispiele sind aus der Literatur bekannt; diese Suche hat keines gefunden."
