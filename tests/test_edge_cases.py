"""Randfälle: leere Eingabe, ein Paket, ungültige Eingaben, Instanzen mit Gleichständen, Aufzählung aller Muster, feste Seeds (auch dieselben wie in Stück 2)."""

import pytest

import lpb_algorithm as A
import lpb_constants as C
from lpb_scenario import Instance, live_instanz, raster_instanz, raster_seed, suche_instanz, zufallsinstanz


def test_leere_eingabe():
    assert A.ffd((), 10) == [] and A.l1((), 10) == 0 and A.l2((), 10) == 0 and A.optimum((), 10) == 0
    assert A.lp_loesen((), 10) == {"wert": 0.0, "muster": [], "preise": []}


def test_ein_paket_und_paket_gleich_kapazitaet():
    l = A.lp_loesen((7,), 10)
    assert l["wert"] == pytest.approx(1.0) and l["muster"] == [((7,), pytest.approx(1.0))]
    assert A.ffd((10, 10), 10) == [[0], [1]] and A.lp_loesen((10, 10), 10)["wert"] == pytest.approx(2.0)


def test_gleiche_groessen_werden_zusammengefasst():
    l = A.lp_loesen((5, 5, 5, 5), 10)
    assert l["wert"] == pytest.approx(2.0) and l["muster"] == [((5, 5), pytest.approx(2.0))]


def test_mehr_exemplare_als_vorhanden_gibt_es_nicht():
    """Eine einzige 4 darf nicht mehrfach in einem Muster stehen: (35, 23, 30, 4, 43) mit Kapazität 47 hat LP 4 (die vier großen Pakete passen nie zu zweit), nicht 3,5."""
    assert A.lp_loesen((35, 23, 30, 4, 43), 47)["wert"] == pytest.approx(4.0, abs=1e-9)


def test_aufzaehlung_aller_muster_ist_beschraenkt():
    assert len(A.alle_muster((1,) * 3, 3)) == 7                     # alle nichtleeren Teilmengen von 3 Paketen
    with pytest.raises(ValueError):
        A.alle_muster((1,) * 15, 100)


def test_ungueltige_eingaben_werfen():
    with pytest.raises(ValueError):
        A.ffd((11,), 10)
    with pytest.raises(ValueError):
        A.ffd((0,), 10)
    with pytest.raises(ValueError):
        Instance((3, 4), 0)
    with pytest.raises(ValueError):
        Instance((3, 12), 10)
    with pytest.raises(ValueError):
        Instance((3.5,), 10)


def test_zufallsinstanzen_sind_fest_und_liegen_im_bereich():
    a = zufallsinstanz(0.2, 0.8, 30, raster_seed(1, 2, 3), 1000)
    assert a == zufallsinstanz(0.2, 0.8, 30, raster_seed(1, 2, 3), 1000) and a.n == 30 and all(200 <= s <= 800 for s in a.sizes)
    assert zufallsinstanz(0.2, 0.8, 30, raster_seed(1, 2, 4), 1000) != a
    assert live_instanz(2, 12, 5).cap == 100 and min(live_instanz(2, 12, 5).sizes) >= 1


def test_rasterinstanzen_sind_dieselben_wie_in_stueck_2():
    """Seeds und Größen sind an drei Instanzen von schranken-beweis-demo (Stück 2) festgehalten: gleicher Seed, gleicher Generator, gleiche Pakete."""
    assert raster_seed(0, 0, 0) == 1_001_000 and raster_seed(2, 2, 5) == 3_003_005 and raster_seed(1, 1, 17) == 2_002_017
    assert raster_instanz(0, 0, 0).sizes[:8] == (466, 284, 381, 429, 124, 141, 343, 307)
    assert raster_instanz(2, 2, 5).sizes[:8] == (557, 813, 417, 43, 215, 36, 497, 37)
    assert raster_instanz(1, 1, 17).sizes[:8] == (534, 518, 737, 401, 347, 475, 210, 433)
    assert raster_instanz(1, 1, 17).cap == C.MESS_CAP and raster_instanz(1, 1, 17).n == 20


def test_raster_seeds_sind_je_zelle_und_instanz_verschieden():
    seeds = {raster_seed(d, n, j) for d in range(3) for n in range(3) for j in range(C.INSTANZEN)}
    assert len(seeds) == 3 * 3 * C.INSTANZEN


def test_suchinstanzen_sind_fest_und_im_bereich():
    s = suche_instanz(9, 4)
    assert s == suche_instanz(9, 4) and len(s) == 9 and all(C.SUCHE_MIN <= x <= C.SUCHE_MAX for x in s) and s != suche_instanz(9, 5) and s != suche_instanz(10, 4)[:9]
