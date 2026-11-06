"""Kern an den Mini-Instanzen von Hand (Rechnung in tests/conftest.py) und an den Beispielen der App."""

import math

import pytest

import lpb_algorithm as A
import lpb_constants as C
import lpb_evaluation as ev
from lpb_scenario import beispiel


def _gueltig(sizes, cap, lp, tol=1e-7):
    """Die angezeigte LP-Lösung ist gültig: jedes Muster passt, jede Paketgröße ist mindestens so oft überdeckt, wie sie vorkommt, die Gewichte summieren sich zum LP-Wert."""
    assert abs(sum(w for _, w in lp["muster"]) - lp["wert"]) < tol
    for groesse in set(sizes):
        ueberdeckt = sum(w * m.count(groesse) for m, w in lp["muster"])
        assert ueberdeckt >= sizes.count(groesse) - tol, groesse
    assert all(sum(m) <= cap and w > 0 for m, w in lp["muster"])


@pytest.mark.parametrize("fixture,lp,ausgang", [("mini_lp", 2.5, "lp_beweist"), ("mini_scharf", 2.0, "lp_scharf"), ("mini_l1", 2.0, "l1"), ("mini_l2", 3.0, "l2")])
def test_mini_instanzen_von_hand(request, fixture, lp, ausgang):
    inst = request.getfixturevalue(fixture)
    l = A.lp_loesen(inst.sizes, inst.cap)
    assert l["wert"] == pytest.approx(lp, abs=1e-9)
    f = len(A.ffd(inst.sizes, inst.cap))
    opt = A.optimum(inst.sizes, inst.cap)
    assert A.ausgang(f, A.l1(inst.sizes, inst.cap), A.l2(inst.sizes, inst.cap), A.lp_aufgerundet(l["wert"]), opt) == ausgang
    _gueltig(inst.sizes, inst.cap, l)


def test_mini_lp_muster_von_hand(mini_lp):
    """Zusammengefasst nach den Größen ist die Lösung eindeutig: {4, 4} mit Gewicht 1,5 und {4, 3} mit Gewicht 1."""
    l = A.lp_loesen(mini_lp.sizes, mini_lp.cap)
    assert [(m, pytest.approx(w)) for m, w in l["muster"]] == [((4, 4), pytest.approx(1.5)), ((4, 3), pytest.approx(1.0))]
    assert A.ffd(mini_lp.sizes, 10) == [[0, 1], [2, 3], [4]] and A.l1(mini_lp.sizes, 10) == A.l2(mini_lp.sizes, 10) == 2 and A.optimum(mini_lp.sizes, 10) == 3


def test_mini_scharf_ffd_von_hand(mini_scharf):
    assert A.ffd(mini_scharf.sizes, 10) == [[0, 1], [2, 3, 4], [5]] and A.optimum(mini_scharf.sizes, 10) == 2


# --- die Beispiele der App (Stück 2 und dieser Reihe) ---------------------------------------------------------------------------------------


@pytest.mark.parametrize("index,summe,ffd,l1,l2,lp,opt,aus", [
    (0, 19, 3, 2, 2, 2.5, 3, "lp_beweist"),
    (1, 834, 11, 9, 11, 11.0, 11, "l2"),
    (2, 498, 6, 5, 5, 36 / 7, 6, "lp_beweist"),
    (3, 496, 6, 5, 5, 5.0, 5, "lp_scharf"),
])
def test_beispiele(index, summe, ffd, l1, l2, lp, opt, aus):
    inst = beispiel(index)
    assert sum(inst.sizes) == summe
    a = ev.analyse(ev.Settings(index))
    assert (a.ffd, a.schranke_l1, a.schranke_l2, a.opt, a.ausgang) == (ffd, l1, l2, opt, aus)
    assert a.lp["wert"] == pytest.approx(lp, abs=1e-9) and a.lp_zahl == math.ceil(lp - 1e-6)
    _gueltig(inst.sizes, inst.cap, a.lp)


def test_beispiel_3_lp_ist_sechsunddreissig_siebtel_und_beweist_ffd_wo_l1_und_l2_es_nicht_konnten():
    a = ev.analyse(ev.Settings(2))
    assert abs(a.lp["wert"] - 36 / 7) < 1e-9 and a.schranke_l2 == 5 < a.lp_zahl == a.ffd == a.opt == 6


def test_aufrunden_mit_toleranz():
    assert A.lp_aufgerundet(5.0) == 5 and A.lp_aufgerundet(5.0000000001) == 5 and A.lp_aufgerundet(4.9999999999) == 5
    assert A.lp_aufgerundet(5.000002) == 6 and A.lp_aufgerundet(2.5) == 3 and A.lp_aufgerundet(0.0) == 0


def test_ausgang_ordnung_der_zweige():
    assert A.ausgang(5, 5, 5, 5, 5) == "l1"             # FFD = L1 = L2 = LP: zuerst L1
    assert A.ausgang(5, 4, 5, 5, 5) == "l2"
    assert A.ausgang(6, 5, 5, 6, 6) == "lp_beweist"
    assert A.ausgang(6, 5, 5, 5, 5) == "lp_scharf"
    assert A.ausgang(7, 5, 5, 5, 6) == "lp_schwach"     # Optimum über dem aufgerundeten LP-Wert, FFD darüber
    assert A.ausgang(6, 5, 5, 5, None) == "offen"
    assert A.ausgang(5, 5, 6, 5, None) == "l1"          # bewiesen, obwohl das Optimum unbekannt ist
