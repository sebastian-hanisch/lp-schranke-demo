"""Ganzzahliges Programm (scipy.optimize.milp) für die Frage „gibt es eine Packung mit m Containern?“: nur für Generator und Tests, nie für die App. Kopie aus schranken-beweis-demo/dev/ilp.py."""


def ilp_machbar(sizes, m: int, cap: int, zeitlimit: float):
    """Gibt es eine Packung mit höchstens m Containern? True / False, None bei Zeitüberschreitung (Zuordnungsmodell, größtes Paket fest in Container 0)."""
    import numpy as np
    from scipy.optimize import Bounds, LinearConstraint, milp

    n = len(sizes)
    nv = n * m
    a_eq = np.zeros((n, nv))
    for i in range(n):
        a_eq[i, i * m:(i + 1) * m] = 1
    a_cap = np.zeros((m, nv))
    for j in range(m):
        for i in range(n):
            a_cap[j, i * m + j] = sizes[i]
    ub = np.ones(nv)
    big = max(range(n), key=lambda i: sizes[i])
    ub[big * m + 1:big * m + m] = 0
    res = milp(np.zeros(nv), constraints=[LinearConstraint(a_eq, 1, 1), LinearConstraint(a_cap, -np.inf, cap)], integrality=np.ones(nv),
               bounds=Bounds(np.zeros(nv), ub), options={"time_limit": zeitlimit})
    if res.status == 0 and res.x is not None:
        return True
    if res.status == 2:
        return False
    return None


def optimum_ilp(sizes, cap: int, untergrenze: int, obergrenze: int, zeitlimit: float):
    """Kleinstes m zwischen Untergrenze und Obergrenze mit Packung (Obergrenze = FFD, immer machbar); None, wenn ein Aufruf das Zeitlimit erreicht."""
    best = obergrenze
    for m in range(obergrenze - 1, untergrenze - 1, -1):
        r = ilp_machbar(sizes, m, cap, zeitlimit)
        if r is None:
            return None
        if not r:
            break
        best = m
    return best
