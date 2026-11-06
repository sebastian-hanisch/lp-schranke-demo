"""Jede Zahl der README und der App-Texte, nachgerechnet (DEMO-PLAYBOOK §4 und §11a).

* Das vorberechnete Raster (lpb_precomputed.json): die Aufteilung L1 / L2 / offen aller neun Zellen frisch (schnell, ohne LP), die vollständigen Codes der Zellen mit 12 Paketen
  (LP mit allen Mustern, Teilmengen-DP), bei 20 und 30 Paketen eine Stichprobe offener Instanzen (Spaltenerzeugung, ganzzahliges Programm für „LP trifft das Optimum“).
* Die Befunde der README werden aus denselben Auswertungsfunktionen wie in der App berechnet, über das GANZE Raster gezählt und als Text in der README gesucht.
* Der Text des Expanders „Annahmen, Grenzen und bekannte Probleme“ steht wörtlich in der README.
Dezimalzahlen stehen in der README mit Komma, in der App mit Punkt."""

import itertools
from pathlib import Path

import pytest

import lpb_algorithm as A
import lpb_constants as C
import lpb_evaluation as ev
from lpb_scenario import raster_instanz

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
ZELLEN = list(itertools.product(range(len(C.VERTEILUNGEN)), range(len(C.MESS_N))))
NAME = {0: "mittel", 1: "groß", 2: "breit"}


def codes(d, ni):
    return ev.vorberechnet()["zellen"][ev.zelle_schluessel(d, ni)]["codes"]


def test_raster_hat_alle_zellen_und_die_parameter():
    daten = ev.vorberechnet()
    assert daten["instanzen"] == C.INSTANZEN == 100 and daten["cap"] == C.MESS_CAP == 1000 and daten["ilp_zeitlimit"] == C.ILP_ZEITLIMIT == 60.0
    assert set(daten["zellen"]) == {ev.zelle_schluessel(d, ni) for d, ni in ZELLEN} and len(ZELLEN) == 9
    assert all(len(z["codes"]) == 100 and set(z["codes"]) <= set(C.AUSGANG_CODES) for z in daten["zellen"].values())
    assert set(daten["suche"]) == {str(n) for n in C.SUCHE_N}


@pytest.mark.parametrize("d,ni", ZELLEN)
def test_aufteilung_l1_l2_offen_stimmt_mit_frischer_rechnung(d, ni):
    z = ev.zaehlen(codes(d, ni))
    frisch = ev.aufteilung_frisch(d, ni)
    offen = z["lp_beweist"] + z["lp_scharf"] + z["offen_unentschieden"] + z["rundung_verletzt"] + z["lp_weit_unter"]
    assert (z["l1"], z["l2"], offen) == (frisch["l1"], frisch["l2"], frisch["offen"])


@pytest.mark.parametrize("d", range(3))
def test_codes_der_zellen_mit_12_paketen_stimmen_mit_lp_und_dp_ueberein(d):
    ni = C.MESS_N.index(12)
    erwartet, ueber, unter = [], 0, 0
    for j in range(C.INSTANZEN):
        code, o, u = ev.instanz_code(raster_instanz(d, ni, j), lambda inst: A.lp_loesen(inst.sizes, inst.cap)["wert"],
                                     lambda inst, m: A.optimum(inst.sizes, inst.cap) <= m)
        erwartet.append(code)
        ueber += o
        unter += u
    assert "".join(erwartet) == codes(d, ni)
    z = ev.vorberechnet()["zellen"][ev.zelle_schluessel(d, ni)]
    assert (z["lp_ueber_l2"], z["lp_unter_l2"]) == (ueber, unter)


@pytest.mark.parametrize("d,ni", [(d, ni) for d, ni in ZELLEN if C.MESS_N[ni] > 12])
def test_stichprobe_der_zellen_mit_20_und_30_paketen_stimmt_mit_der_spaltenerzeugung_ueberein(d, ni):
    from dev.cg import lp_wert_cg

    offene = [j for j, c in enumerate(codes(d, ni)) if c in "PTU"][:2]
    assert offene, "keine offene Instanz in der Zelle"
    for j in offene:
        gespeichert = codes(d, ni)[j]
        stub = {"T": True, "U": None}.get(gespeichert, True)             # die gespeicherte Antwort der Packbarkeit (V gibt es nicht)
        code, _, _ = ev.instanz_code(raster_instanz(d, ni, j), lambda inst: lp_wert_cg(list(inst.sizes), inst.cap), lambda inst, m: stub)
        assert code == gespeichert, (d, ni, j)


@pytest.mark.parametrize("d", range(3))
def test_stichprobe_lp_trifft_das_optimum_stimmt_mit_dem_ganzzahligen_programm_ueberein(d):
    """Je eine Instanz mit Code T bei 20 Paketen: eine Packung mit FFD - 1 Containern existiert wirklich (ganzzahliges Programm)."""
    from dev.ilp import ilp_machbar

    ni = C.MESS_N.index(20)
    ts = [j for j, c in enumerate(codes(d, ni)) if c == "T"][:1]
    for j in ts:
        inst = raster_instanz(d, ni, j)
        f = len(A.ffd(inst.sizes, inst.cap))
        assert ilp_machbar(inst.sizes, f - 1, inst.cap, 180.0) is True, (d, j)


# --- Befunde der README --------------------------------------------------------------------------------------------------------------------


def alle():
    return {(d, ni): ev.zeile(d, ni) for d, ni in ZELLEN}


def test_readme_tabelle_gibt_jede_zelle_wieder():
    for (d, ni), z in alle().items():
        zeile = (f"| {NAME[d]} | {z['n']} | {z['l1']} | {z['l2']} | {z['lp_beweist']} | {z['lp_scharf']} | {z['offen_unentschieden']} | {z['rundung_verletzt']} | {z['lp_weit_unter']} |")
        assert zeile in README, zeile
        assert sum(z[k] for k in ("l1", "l2", "lp_beweist", "lp_scharf", "offen_unentschieden", "rundung_verletzt", "lp_weit_unter")) == z["instanzen"] == 100


def test_gesamtzahlen_der_900_instanzen():
    z = alle().values()
    s = {k: sum(x[k] for x in z) for k in ("l1", "l2", "lp_beweist", "lp_scharf", "offen_unentschieden", "rundung_verletzt", "lp_weit_unter", "ueber_l2", "unter_l2")}
    offen = s["lp_beweist"] + s["lp_scharf"] + s["offen_unentschieden"] + s["rundung_verletzt"] + s["lp_weit_unter"]
    assert (s["l1"], s["l2"], offen) == (431, 340, 129) and sum(x["instanzen"] for x in z) == 900
    assert "sind 431 durch L1 bewiesen, 340 erst durch L2; **129 bleiben offen**" in README
    assert (s["lp_beweist"], s["lp_scharf"], s["offen_unentschieden"]) == (66, 55, 8) and s["lp_beweist"] + s["lp_scharf"] + s["offen_unentschieden"] == 129
    assert "beweist der aufgerundete LP-Wert bei 66 die Optimalität von FFD**" in README and "Bei **55** ist der aufgerundete LP-Wert gleich dem Optimum" in README and "**8** sind nicht entschieden" in README
    assert s["rundung_verletzt"] == 0 and s["lp_weit_unter"] == 0 and "**Die Rundung ist in keiner Instanz verletzt** (0 von 129)" in README
    assert s["unter_l2"] == 0 and s["ueber_l2"] == 66 == s["lp_beweist"] and "unter L2 und in 66 darüber" in README and "**0 von 900**" in README


def test_die_acht_nicht_entschiedenen_liegen_bei_n_30_mittel_und_breit():
    u = {k: z["offen_unentschieden"] for k, z in alle().items() if z["offen_unentschieden"]}
    assert u == {(0, 2): 7, (2, 2): 1} and "(7 bei mittleren Teilen mit n = 30, 1 bei breiten Teilen mit n = 30)" in README


def test_mittlere_teile_l2_beweist_nie_mehr_als_l1_und_lp_in_10_von_300():
    z = [ev.zeile(0, ni) for ni in range(3)]
    assert sum(x["l2"] for x in z) == 0 and sum(x["lp_beweist"] for x in z) == 10 and sum(x["instanzen"] for x in z) == 300
    assert "L2 beweist in 0 von 300 Instanzen mehr als L1, der LP-Wert in 10 von 300 zusätzlich" in README


def test_jede_lp_bewiesene_instanz_liegt_ueber_l2_und_jede_unentschiedene_hat_lp_gleich_ffd_minus_eins():
    """In den Zellen mit 12 Paketen nachgerechnet (voll): erst durch LP bewiesen heißt aufgerundeter LP-Wert über L2 und gleich FFD."""
    ni = C.MESS_N.index(12)
    for d in range(3):
        for j, c in enumerate(codes(d, ni)):
            if c != "P":
                continue
            inst = raster_instanz(d, ni, j)
            z = A.lp_aufgerundet(A.lp_loesen(inst.sizes, inst.cap)["wert"])
            assert z == len(A.ffd(inst.sizes, inst.cap)) and z > A.l2(inst.sizes, inst.cap)


# --- Suche ----------------------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("n", [8, 9])
def test_suche_stimmt_mit_frischer_rechnung(n):
    assert ev.suche_zelle(n) == ev.vorberechnet()["suche"][str(n)]


def test_suche_zaehlungen_und_readme():
    zeilen = [ev.suche_zeile(n) for n in C.SUCHE_N]
    assert [(z["instanzen"], z["gleich"], z["verletzt"]) for z in zeilen] == [(1500, 1500, 0), (1500, 1500, 0), (1500, 1500, 0), (600, 600, 0)]
    for z in zeilen:
        assert f"| {z['n']} | {z['instanzen']} | {z['gleich']} | {z['verletzt']} |" in README
    assert sum(z["instanzen"] for z in zeilen) == 5100 == sum(C.SUCHE_INSTANZEN.values()) and "In **0 von 5100** zufälligen Instanzen" in README


# --- Beispiele und Texte --------------------------------------------------------------------------------------------------------------------


def test_readme_beispieltabelle_und_handrechnung():
    namen = {"l2": "erst durch L2 bewiesen", "lp_beweist": "erst durch LP bewiesen", "lp_scharf": "LP trifft das Optimum, FFD verliert"}
    for i in range(4):
        a = ev.analyse(ev.Settings(i))
        zeile = f"| {C.BEISPIEL_NAMEN[i]} | {sum(a.inst.sizes)} | {a.ffd} | {a.schranke_l1} | {a.schranke_l2} | {str(round(a.lp['wert'], 4)).replace('.', ',')} | {a.lp_zahl} | {a.opt} | {namen[a.ausgang]} |"
        assert zeile in README, zeile
    assert "LP = 1 + 1,5 = **2,5**, aufgerundet 3" in README and "ist der LP-Wert 36/7 ≈ 5,1429" in README


def test_annahmen_text_der_app_steht_woertlich_in_der_readme():
    assert C.ASSUMPTIONS_MARKDOWN in README


def test_zahlen_im_annahmen_text_sind_die_der_konstanten():
    t = C.ASSUMPTIONS_MARKDOWN
    assert f"bis {C.OPT_LIMIT} Pakete" in t and f"{C.INSTANZEN} Instanzen" in t and f"{sum(C.SUCHE_INSTANZEN.values())} zufällige Instanzen" in t and "60 Sekunden Zeitlimit" in t
