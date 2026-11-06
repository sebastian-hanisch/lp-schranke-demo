"""Kern: FFD, die Schranken L1 und L2, die LP-Schranke (alle Muster, bis 12 Pakete), exaktes Optimum und die Einordnung des Ausgangs.

`ffd`, `l1`, `l2_detail` und `optimum` sind Kopien der Funktionen gleichen Namens aus schranken-beweis-demo/sbw_algorithm.py (Stück 2 dieser Reihe, dort gegen
Aufzählung, zweite DP und ein ganzzahliges Programm geprüft); die Orakel-Tests dieses Repos prüfen sie noch einmal. Container sind Listen von Paketnummern."""

import math

import numpy as np
from scipy.optimize import linprog

import lpb_constants as C


def ffd(sizes, cap: int) -> list[list[int]]:
    """First Fit Decreasing: größte zuerst (Gleichstand: kleinere Nummer zuerst), jedes Paket in den ersten Container mit genug Platz."""
    if any(s <= 0 or s > cap for s in sizes):
        raise ValueError("Paketgröße muss zwischen 1 und der Kapazität liegen")
    bins: list[list[int]] = []
    loads: list[int] = []
    for i in sorted(range(len(sizes)), key=lambda i: (-sizes[i], i)):
        s = sizes[i]
        for b, load in enumerate(loads):
            if load + s <= cap:
                bins[b].append(i)
                loads[b] += s
                break
        else:
            bins.append([i])
            loads.append(s)
    return bins


def container_pruefen(sizes, bins, cap: int) -> bool:
    """Unabhängiger Zulässigkeitsprüfer: jedes Paket genau einmal, keine Überfüllung, keine leeren Container."""
    gesehen = sorted(i for b in bins for i in b)
    return gesehen == list(range(len(sizes))) and all(b and sum(sizes[i] for i in b) <= cap for b in bins)


def l1(sizes, cap: int) -> int:
    """Volumenschranke: Summe der Größen durch die Kapazität, aufgerundet."""
    return -(-sum(sizes) // cap) if sizes else 0


def _l2_alpha(sizes, cap: int, alpha: int) -> int:
    j1 = [s for s in sizes if s > cap - alpha]
    j2 = [s for s in sizes if cap - alpha >= s and 2 * s > cap]
    j3 = [s for s in sizes if 2 * s <= cap and s >= alpha]
    frei = len(j2) * cap - sum(j2)
    extra = max(0, -(-(sum(j3) - frei) // cap)) if j3 else 0
    return len(j1) + len(j2) + extra


def l2(sizes, cap: int) -> int:
    """Schranke L2 nach Martello und Toth: Maximum von L1 und L(alpha) über alpha = 0 und alle Paketgrößen bis zur halben Kapazität."""
    best = l1(sizes, cap)
    for alpha in {0} | {s for s in sizes if 2 * s <= cap}:
        best = max(best, _l2_alpha(sizes, cap, alpha))
    return best


def optimum(sizes, cap: int, limit: int = 12):
    """Kleinste mögliche Containerzahl per Teilmengen-DP, oder None, wenn mehr als `limit` Pakete vorliegen."""
    n = len(sizes)
    if n > limit:
        return None
    if n == 0:
        return 0
    full = (1 << n) - 1
    inf = (n + 1, cap + 1)
    dp = [inf] * (full + 1)
    dp[0] = (1, 0)
    for mask in range(full + 1):
        b, last = dp[mask]
        if b > n:
            continue
        for i in range(n):
            if mask >> i & 1:
                continue
            s = sizes[i]
            nxt = (b, last + s) if last + s <= cap else (b + 1, s)
            m2 = mask | (1 << i)
            if nxt < dp[m2]:
                dp[m2] = nxt
    return dp[full][0]


# ------------------------------------------------------------------------------------------------------------------------------------------
# LP-Schranke


def alle_muster(sizes, cap: int) -> np.ndarray:
    """Alle nichtleeren zulässigen Teilmengen der Pakete als 0/1-Matrix (Zeile = Muster, Spalte = Paket); höchstens 14 Pakete."""
    n = len(sizes)
    if n > 14:
        raise ValueError("zu viele Pakete für die Aufzählung aller Muster")
    masken = np.arange(1, 1 << n)
    bits = (masken[:, None] >> np.arange(n)) & 1
    summen = bits @ np.asarray(sizes, dtype=np.int64)
    return bits[summen <= cap]


def lp_loesen(sizes, cap: int) -> dict:
    """LP-Schranke (Gilmore und Gomory): kleinste Summe der Mustergewichte, sodass jedes Paket mindestens einmal überdeckt ist (alle zulässigen Muster als Spalten).

    Gibt zurück: `wert` (LP-Wert), `muster` (eine optimale Lösung, zusammengefasst nach den Größen der Pakete im Muster: Liste von (Größen absteigend, Gewicht), nach Gewicht
    absteigend) und `preise` (Dualpreise der Pakete, Zertifikat: jedes zulässige Muster hat höchstens den Preis 1 und die Preise summieren sich zum LP-Wert).
    Der Wert ist eindeutig, die Muster bei Gleichständen nicht."""
    n = len(sizes)
    if n == 0:
        return {"wert": 0.0, "muster": [], "preise": []}
    p = alle_muster(sizes, cap).astype(float)
    res = linprog(np.ones(len(p)), A_ub=-p.T, b_ub=-np.ones(n), bounds=(0, None), method="highs")
    if res.status != 0:
        raise RuntimeError(f"LP nicht gelöst: {res.message}")
    zusammen: dict[tuple, float] = {}
    for gewicht, zeile in zip(res.x, p):
        if gewicht > 1e-9:
            schluessel = tuple(sorted((sizes[i] for i in range(n) if zeile[i] > 0.5), reverse=True))
            zusammen[schluessel] = zusammen.get(schluessel, 0.0) + float(gewicht)
    muster = sorted(zusammen.items(), key=lambda kv: (-kv[1], kv[0]))
    return {"wert": float(res.fun), "muster": muster, "preise": [float(-m) for m in res.ineqlin.marginals]}


def lp_aufgerundet(wert: float) -> int:
    """Aufgerundeter LP-Wert mit Toleranz für Rundungsfehler des Lösers (RUND_TOL)."""
    return math.ceil(wert - C.RUND_TOL)


def ausgang(ffd_zahl: int, schranke_l1: int, schranke_l2: int, lp_zahl: int, opt):
    """Einordnung einer Instanz: 'l1' (FFD gleich L1), 'l2' (FFD gleich L2, größer als L1), 'lp_beweist' (FFD gleich dem aufgerundeten LP-Wert, über L2: erst durch den LP bewiesen),
    'offen' (Optimum unbekannt), 'lp_scharf' (aufgerundeter LP-Wert gleich dem Optimum, FFD darüber) oder 'lp_schwach' (aufgerundeter LP-Wert unter dem Optimum, FFD darüber)."""
    if ffd_zahl == schranke_l1:
        return "l1"
    if ffd_zahl == schranke_l2:
        return "l2"
    if ffd_zahl == lp_zahl:
        return "lp_beweist"
    if opt is None:
        return "offen"
    return "lp_scharf" if lp_zahl == opt else "lp_schwach"
