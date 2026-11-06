"""Gemeinsame Fixtures: Mini-Instanzen (Kapazität 10) mit Handrechnung (DEMO-PLAYBOOK §1b).

* mini_lp (4, 4, 4, 4, 3), Summe 19: L1 = 2, L2 = 2 (kein Paket über 5). FFD: 4 + 4 in C1 (8); die dritte 4 in C2; die vierte 4 in C2 (8); die 3 passt in keinen (11): C3. FFD = 3, Optimum 3
  (zwei Container bräuchten eine Teilmenge mit Summe 9 oder 10; die Summen sind 3, 4, 7, 8, 11, 12, 15, 16, 19). LP: Muster {4, 4} (Summe 8), {4, 3} (7), Einzelpakete. Die 3 braucht ein
  Muster mit ihr, kleinstes Gewicht 1 auf {4, 3}, das deckt eine Vier; die übrigen drei Vieren deckt {4, 4} mit Gewicht 1,5. LP = 1 + 1,5 = 2,5, aufgerundet 3. Ausgang 'lp_beweist'.
* mini_scharf (4, 4, 3, 3, 3, 3), Summe 20: L1 = L2 = 2, FFD 3 (4 + 4; 3 + 3 + 3; 3), Optimum 2 durch {4, 3, 3} zweimal. LP = 2 (nicht unter L1 = 2, und zweimal {4, 3, 3} deckt alles).
  Aufgerundet 2 = Optimum < FFD. Ausgang 'lp_scharf'.
* mini_l1 (5, 5, 4, 3, 3), Summe 20: L1 = 2; FFD: 5 + 5 füllt C1; 4 + 3 + 3 füllt C2: 2 Container. LP = 2. Ausgang 'l1'.
* mini_l2 (6, 6, 6, 2), Summe 20: L1 = 2, L2 = 3 (drei Pakete über 5), FFD 3. LP = 3: Jedes Paket zu 6 braucht ein eigenes Muster (zwei Sechsen passen nicht), also Gewicht mindestens 3.
  Ausgang 'l2'.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lpb_scenario import Instance  # noqa: E402


@pytest.fixture
def mini_lp():
    return Instance((4, 4, 4, 4, 3), 10)


@pytest.fixture
def mini_scharf():
    return Instance((4, 4, 3, 3, 3, 3), 10)


@pytest.fixture
def mini_l1():
    return Instance((5, 5, 4, 3, 3), 10)


@pytest.fixture
def mini_l2():
    return Instance((6, 6, 6, 2), 10)
