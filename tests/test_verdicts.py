"""Verdikte und die Einordnung der Rasterinstanzen an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier.

Die Analysen und Zeilen werden von Hand gebaut, nicht aus Seeds gerechnet."""

import pytest

import lpb_algorithm as A
import lpb_evaluation as ev
from lpb_scenario import Instance


def _analyse(ausgang, ffd, l1, l2, lp, opt):
    inst = Instance((10, 20), 100)
    return ev.Analysis(inst, ((0,), (1,)), ffd, l1, l2, {"wert": lp, "muster": [], "preise": []}, A.lp_aufgerundet(lp), opt, ausgang, ev.Settings())


# --- verdict_ausgang ------------------------------------------------------------------------------------------------------------------------


def test_ausgang_l1():
    kind, text = ev.verdict_ausgang(_analyse("l1", 7, 7, 7, 7.0, 7))
    assert kind == "success" and "FFD braucht **7** Container" in text and "Volumenschranke L1 ist 7" in text and "**bewiesen optimal**" in text and "7.0000, aufgerundet 7" in text


def test_ausgang_l2():
    kind, text = ev.verdict_ausgang(_analyse("l2", 11, 9, 11, 11.0, 11))
    assert kind == "success" and "L1 sagt nur 9, aber L2 ist 11" in text and "11.0000, aufgerundet 11, das bestätigt es" in text


def test_ausgang_lp_beweist_nennt_l1_l2_lp_und_optimum():
    kind, text = ev.verdict_ausgang(_analyse("lp_beweist", 6, 5, 5, 5.142857, 6))
    assert kind == "success"
    assert "**6** Container" in text and "L1 (5) und L2 (5)" in text and "5.1429, aufgerundet 6" in text and "durch den LP-Wert **bewiesen optimal** (Optimum 6)" in text


def test_ausgang_lp_scharf_ist_eine_warnung_mit_der_differenz():
    kind, text = ev.verdict_ausgang(_analyse("lp_scharf", 6, 5, 5, 5.0, 5))
    assert kind == "warning" and "**6** Container" in text and "5.0000, aufgerundet 5" in text and "Optimum ist **5**" in text and "1 Container zu viel" in text
    assert "L1 (5) und L2 (5) auch" in text


def test_ausgang_lp_scharf_wenn_l2_unter_dem_optimum_liegt():
    kind, text = ev.verdict_ausgang(_analyse("lp_scharf", 7, 4, 4, 5.0, 5))
    assert "2 Container zu viel" in text and "L1 (4) und L2 (4) nicht" in text


def test_ausgang_lp_schwach_ist_eine_warnung():
    kind, text = ev.verdict_ausgang(_analyse("lp_schwach", 7, 5, 5, 5.0, 6))
    assert kind == "warning" and "Optimum ist aber **6**" in text and "5.0000, aufgerundet 5" in text and "zu schwach" in text


def test_ausgang_offen():
    kind, text = ev.verdict_ausgang(_analyse("offen", 9, 7, 7, 7.5, None))
    assert kind == "info" and "7.5000, aufgerundet 8" in text and "nicht berechnet" in text


# --- instanz_code (Einordnung der Rasterinstanzen), mit Stub-Funktionen für LP und Packbarkeit ---------------------------------------------------


def _code(sizes, cap, lp, packbar=None):
    return ev.instanz_code(Instance(tuple(sizes), cap), lambda inst: lp, packbar or (lambda inst, m: None))


def test_code_l1_braucht_keinen_lp_und_hat_keine_flags():
    def verboten(inst):
        raise AssertionError("der LP darf bei FFD = L1 nicht gerechnet werden")

    assert ev.instanz_code(Instance((5, 5, 4, 3, 3), 10), verboten, lambda i, m: None) == ("1", False, False)


def test_code_l2():
    assert _code((6, 6, 6, 2), 10, 3.0) == ("2", False, False)            # FFD 3 = L2 > L1 = 2
    assert _code((6, 6, 6, 2), 10, 2.0) == ("2", False, True)             # LP-Stub 2,0: aufgerundet 2 liegt unter L2 = 3, Flag „unter“
    assert _code((6, 6, 6, 2), 10, 2.5) == ("2", False, False)            # 2,5 wird auf 3 aufgerundet: gleich L2


def test_code_p_und_ueber_flag():
    assert _code((4, 4, 4, 4, 3), 10, 2.5) == ("P", True, False)          # FFD 3, L2 = 2, aufgerundeter LP 3 über L2 und gleich FFD


def test_code_t_v_u_je_nach_packbarkeit():
    inst = (4, 4, 3, 3, 3, 3)                                               # FFD 3, L1 = L2 = 2
    assert _code(inst, 10, 2.0, lambda i, m: True) == ("T", False, False)
    assert _code(inst, 10, 2.0, lambda i, m: False) == ("V", False, False)
    assert _code(inst, 10, 2.0, lambda i, m: None) == ("U", False, False)


def test_code_packbar_wird_mit_ffd_minus_eins_gefragt():
    gefragt = []

    def packbar(inst, m):
        gefragt.append(m)
        return True

    _code((4, 4, 3, 3, 3, 3), 10, 2.0, packbar)
    assert gefragt == [2]


def test_code_x_wenn_lp_mehr_als_eins_unter_ffd():
    assert _code((4, 4, 3, 3, 3, 3), 10, 1.0) == ("X", False, True)       # aufgerundet 1 < FFD - 1 = 2, und unter L2 = 2


def test_code_wirft_wenn_der_lp_ueber_ffd_liegt():
    with pytest.raises(ValueError):
        _code((4, 4, 3, 3, 3, 3), 10, 3.5)


# --- verdict_raster -----------------------------------------------------------------------------------------------------------------------------


def _zeile(**k):
    z = {"name": "große Teile (20 bis 80 %)", "n": 20, "instanzen": 100, "l1": 24, "l2": 63, "lp_beweist": 9, "lp_scharf": 0, "offen_unentschieden": 0, "rundung_verletzt": 0,
         "lp_weit_unter": 0, "ueber_l2": 9, "unter_l2": 0, "zeitlimit": 10.0}
    z.update(k)
    return z


def test_raster_basis_ist_info_und_nennt_alle_pflichtzahlen():
    kind, text = ev.verdict_raster(_zeile())
    assert kind == "info"
    assert "»große Teile (20 bis 80 %)« mit n = 20" in text and "L1 bei 24 von 100 Instanzen" in text and "L2 zusätzlich bei 63 und der LP-Wert noch bei 9" in text
    assert "liegt in 9 Instanzen über L2 und in 0 darunter" in text
    for wort in ("gleich dem Optimum", "nicht entschieden", "über dem aufgerundeten", "mehr als einen Container"):
        assert wort not in text


def test_raster_scharf_ist_info_unentschieden_ist_warnung():
    kind, text = ev.verdict_raster(_zeile(lp_scharf=3))
    assert kind == "info" and "In 3 Instanzen ist der aufgerundete LP-Wert gleich dem Optimum, FFD braucht dort einen Container mehr." in text
    kind, text = ev.verdict_raster(_zeile(offen_unentschieden=2))
    assert kind == "warning" and "In 2 Instanzen liegt der aufgerundete LP-Wert einen Container unter FFD und das Optimum ist nicht entschieden (ILP nach 10 s abgebrochen)." in text


def test_raster_rundung_verletzt_und_lp_weit_unter_sind_warnungen():
    kind, text = ev.verdict_raster(_zeile(rundung_verletzt=1))
    assert kind == "warning" and "In 1 Instanzen liegt das Optimum über dem aufgerundeten LP-Wert." in text
    kind, text = ev.verdict_raster(_zeile(lp_weit_unter=4, unter_l2=2))
    assert kind == "warning" and "In 4 Instanzen liegt der aufgerundete LP-Wert mehr als einen Container unter FFD." in text and "und in 2 darunter" in text


# --- Suche -----------------------------------------------------------------------------------------------------------------------------------


def test_suche_ohne_gegenbeispiel_ist_info_mit_literaturhinweis():
    zeilen = [{"n": 8, "instanzen": 1500, "gleich": 1500, "verletzt": 0}, {"n": 11, "instanzen": 600, "gleich": 600, "verletzt": 0}]
    kind, text = ev.verdict_suche(zeilen)
    assert kind == "info" and "In 2100 zufälligen Instanzen mit 8 bis 11 Paketen" in text and "in 2100 gleich dem aufgerundeten LP-Wert und in 0 größer" in text and "keines gefunden" in text


def test_suche_mit_gegenbeispiel_ist_warnung():
    zeilen = [{"n": 9, "instanzen": 100, "gleich": 98, "verletzt": 2}]
    kind, text = ev.verdict_suche(zeilen)
    assert kind == "warning" and "in 98 gleich" in text and "in 2 größer" in text and "unter dem Optimum" in text


def test_suche_zeile_zaehlt_jede_luecke_ueber_null_als_verletzt():
    daten = {"suche": {"9": {"instanzen": 10, "luecken": {"0": 7, "1": 2, "2": 1}}}}
    assert ev.suche_zeile(9, daten) == {"n": 9, "instanzen": 10, "gleich": 7, "verletzt": 3}
    assert ev.suche_zeile(9, {"suche": {"9": {"instanzen": 5, "luecken": {"0": 5}}}}) == {"n": 9, "instanzen": 5, "gleich": 5, "verletzt": 0}
