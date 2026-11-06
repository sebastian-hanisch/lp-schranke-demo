"""Orakel-Tests (DEMO-PLAYBOOK §12): jede Kernroutine gegen einen anderen Rechenweg, feste Seeds, zusammen unter 10 Sekunden.

  LP-Wert (alle Muster, linprog)  gegen  (a) die Spaltenerzeugung (dev/cg.py, anderes Verfahren: nur erzeugte Muster, Preisproblem per DP), (b) ein Dualzertifikat:
                                         Dualpreise y >= 0, jedes zulässige Muster hat Preis <= 1, die Summe der Preise ist der LP-Wert (damit ist der LP-Wert eine gültige untere
                                         Schranke, ohne dem Löser zu glauben).
  Optimum (Teilmengen-DP)         gegen  Aufzählung aller Zerlegungen (n <= 8) und eine zweite DP über Untermengen (n <= 10).
  FFD                             gegen  eine bewusst naive Zweitumsetzung.   L2 gegen die Rechnung über ALLE ganzzahligen alpha.
  Eigenschaften mit exaktem Optimum: LP >= Summe/C, L2 <= aufgerundeter LP-Wert (Dominanz), aufgerundeter LP-Wert <= OPT <= FFD; der Ausgang stimmt mit einer unabhängigen Einordnung überein.
"""

import itertools
import random

import numpy as np
import pytest

import lpb_algorithm as A


def instanzen(anzahl, n_lo, n_hi, cap_lo=5, cap_hi=40, seed0=0):
    for seed in range(seed0, seed0 + anzahl):
        rng = random.Random(seed)
        cap = rng.randint(cap_lo, cap_hi)
        n = rng.randint(n_lo, n_hi)
        yield cap, [rng.randint(1, cap) for _ in range(n)]


# --- LP-Wert ----------------------------------------------------------------------------------------------------------------------------------


def test_lp_stimmt_mit_der_spaltenerzeugung_ueberein():
    from dev.cg import lp_wert_cg

    # Zwei Instanzen mit Gleichständen der Größen (Muster dürfen nicht mehr Exemplare enthalten, als es gibt) und zwölf Zufallsinstanzen mit bis zu 8 Paketen.
    for cap, sizes in [(47, [35, 23, 30, 4, 43]), (10, [4, 4, 4, 4, 3]), (10, [6, 6, 6, 2])] + list(instanzen(12, 2, 8, cap_lo=10, cap_hi=60, seed0=100)):
        assert A.lp_loesen(sizes, cap)["wert"] == pytest.approx(lp_wert_cg(sizes, cap), abs=1e-7), (cap, sizes)


def test_dualzertifikat_beweist_den_lp_wert_als_untere_schranke():
    for cap, sizes in instanzen(60, 1, 10, cap_lo=10, cap_hi=60, seed0=200):
        l = A.lp_loesen(sizes, cap)
        y = np.array(l["preise"])
        assert (y >= -1e-9).all(), (cap, sizes)
        muster = A.alle_muster(sizes, cap)
        assert (muster @ y <= 1 + 1e-7).all(), (cap, sizes)           # jedes zulässige Muster hat höchstens den Preis 1
        assert y.sum() == pytest.approx(l["wert"], abs=1e-7), (cap, sizes)   # Dualwert gleich Primalwert


def test_alle_muster_sind_zulaessig_und_vollstaendig():
    sizes, cap = (4, 4, 3, 2), 8
    m = A.alle_muster(sizes, cap)
    erwartet = {mask for mask in range(1, 16) if sum(s for i, s in enumerate(sizes) if mask >> i & 1) <= cap}
    gefunden = {sum(int(b) << i for i, b in enumerate(zeile)) for zeile in m}
    assert gefunden == erwartet and len(m) == len(erwartet)


def test_lp_randfaelle():
    assert A.lp_loesen([], 10)["wert"] == 0.0 and A.lp_loesen([], 10)["muster"] == []
    assert A.lp_loesen([10], 10)["wert"] == pytest.approx(1.0)
    assert A.lp_loesen([10, 10, 10], 10)["wert"] == pytest.approx(3.0)
    assert A.lp_loesen([5, 5, 5, 5], 10)["wert"] == pytest.approx(2.0)
    assert A.lp_loesen([1] * 12, 12)["wert"] == pytest.approx(1.0)


# --- Optimum ----------------------------------------------------------------------------------------------------------------------------------


def optimum_aufzaehlung(sizes, cap):
    n = len(sizes)
    if n == 0:
        return 0
    best = n

    def rec(i, loads):
        nonlocal best
        if len(loads) >= best:
            return
        if i == n:
            best = len(loads)
            return
        for b in range(len(loads)):
            if loads[b] + sizes[i] <= cap:
                loads[b] += sizes[i]
                rec(i + 1, loads)
                loads[b] -= sizes[i]
        loads.append(sizes[i])
        rec(i + 1, loads)
        loads.pop()

    rec(0, [])
    return best


def optimum_untermengen(sizes, cap):
    n = len(sizes)
    full = (1 << n) - 1
    summe = [0] * (full + 1)
    for m in range(1, full + 1):
        low = (m & -m).bit_length() - 1
        summe[m] = summe[m & (m - 1)] + sizes[low]
    g = [0] * (full + 1)
    for m in range(1, full + 1):
        low = m & -m
        rest = m ^ low
        sub = rest
        beste = n + 1
        while True:
            t = sub | low
            if summe[t] <= cap and g[m ^ t] + 1 < beste:
                beste = g[m ^ t] + 1
            if sub == 0:
                break
            sub = (sub - 1) & rest
        g[m] = beste
    return g[full]


def test_optimum_stimmt_mit_der_aufzaehlung_ueberein():
    for cap, sizes in instanzen(80, 1, 8):
        assert A.optimum(sizes, cap) == optimum_aufzaehlung(sizes, cap), (cap, sizes)


def test_optimum_stimmt_mit_der_untermengen_dp_ueberein():
    for cap, sizes in instanzen(40, 1, 10, seed0=1000):
        assert A.optimum(sizes, cap) == optimum_untermengen(sizes, cap), (cap, sizes)


def test_optimum_randfaelle():
    assert A.optimum([], 10) == 0 and A.optimum([10, 10, 10], 10) == 3 and A.optimum([5, 5, 5, 5], 10) == 2 and A.optimum([1] * 13, 12, limit=12) is None


# --- FFD und L2 --------------------------------------------------------------------------------------------------------------------------------


def ffd_naiv(sizes, cap):
    container = []
    for i in sorted(range(len(sizes)), key=lambda i: (-sizes[i], i)):
        for c in container:
            if sum(c) + sizes[i] <= cap:
                c.append(sizes[i])
                break
        else:
            container.append([sizes[i]])
    return sorted(sorted(c) for c in container)


def test_ffd_stimmt_mit_der_naiven_zweitumsetzung_ueberein():
    for cap, sizes in instanzen(150, 0, 14, seed0=2000):
        bins = A.ffd(sizes, cap)
        assert sorted(sorted(sizes[i] for i in b) for b in bins) == ffd_naiv(sizes, cap), (cap, sizes)
        assert A.container_pruefen(sizes, bins, cap)


def l2_alle_alpha(sizes, cap):
    best = -(-sum(sizes) // cap) if sizes else 0
    for alpha in range(0, cap // 2 + 1):
        j1 = sum(1 for s in sizes if s > cap - alpha)
        j2 = [s for s in sizes if cap - alpha >= s and 2 * s > cap]
        j3 = [s for s in sizes if 2 * s <= cap and s >= alpha]
        extra = max(0, -(-(sum(j3) - (len(j2) * cap - sum(j2))) // cap))
        best = max(best, j1 + len(j2) + extra)
    return best


def test_l2_stimmt_mit_der_rechnung_ueber_alle_alpha_ueberein():
    for cap, sizes in instanzen(200, 0, 20, seed0=3000):
        assert A.l2(sizes, cap) == l2_alle_alpha(sizes, cap), (cap, sizes)


# --- Eigenschaften mit exaktem Optimum -----------------------------------------------------------------------------------------------------------


def eingeordnet(f, s1, s2, z, opt):
    """Unabhängige Neueinordnung in anderer Reihenfolge der Prüfungen."""
    if opt is not None and opt < f and z == opt:
        return "lp_scharf" if (f != s1 and f != s2 and f != z) else ("l1" if f == s1 else "l2" if f == s2 else "lp_beweist")
    if f == s1:
        return "l1"
    if f == s2:
        return "l2"
    if f == z:
        return "lp_beweist"
    if opt is None:
        return "offen"
    return "lp_schwach"


def test_schranken_dominanz_und_ordnung_mit_exaktem_optimum():
    for cap, sizes in instanzen(80, 1, 9, cap_lo=10, cap_hi=60, seed0=4000):
        f = len(A.ffd(sizes, cap))
        opt = A.optimum(sizes, cap)
        l = A.lp_loesen(sizes, cap)
        z = A.lp_aufgerundet(l["wert"])
        s1, s2 = A.l1(sizes, cap), A.l2(sizes, cap)
        assert l["wert"] >= sum(sizes) / cap - 1e-9                      # LP >= Volumenschranke ohne Aufrunden
        assert s1 <= s2 <= z <= opt <= f, (cap, sizes, s1, s2, z, opt, f)   # Dominanz über L2 und gültige untere Schranke
        assert A.ausgang(f, s1, s2, z, opt) == eingeordnet(f, s1, s2, z, opt), (cap, sizes)


def test_rundung_gilt_an_kleinen_zufallsinstanzen():
    """Optimum gleich aufgerundetem LP-Wert (IRUP) an 150 Instanzen mit bis zu 9 Paketen; das ist eine Messung, kein Satz (Gegenbeispiele sind aus der Literatur bekannt)."""
    for cap, sizes in instanzen(150, 3, 9, cap_lo=20, cap_hi=100, seed0=5000):
        assert A.optimum(sizes, cap) == A.lp_aufgerundet(A.lp_loesen(sizes, cap)["wert"]), (cap, sizes)
