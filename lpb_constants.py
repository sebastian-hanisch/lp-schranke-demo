"""Konstanten: Regler-Grenzen, Beispiele, Raster, Suche, Farben und Presets."""

CAP = 100                 # Kapazität der Beispiele 1 bis 3 und der zufälligen Live-Instanz
OPT_LIMIT = 12            # so viele Pakete darf das exakte Optimum und der LP mit allen Mustern live höchstens haben
N_MIN, N_MAX, DEFAULT_N = 6, 12, 12
SEED_MAX, DEFAULT_SEED = 999999, 7
RUND_TOL = 1e-6           # Toleranz beim Aufrunden des LP-Wertes (Rundungsfehler des Lösers)

# --- Beispiele (Größen, Kapazität) ----------------------------------------------------------------------------------------------------------
# 0: das kleine Beispiel, von Hand lösbar (LP 2,5); 1 bis 3: Beispiele aus Stück 2 dieser Reihe (zwölf Pakete, Kapazität 100).
BEISPIELE = {
    0: ((4, 4, 4, 4, 3), 10),
    1: ((90, 88, 85, 81, 75, 75, 70, 69, 67, 67, 34, 33), 100),     # FFD 11, L1 9, L2 11, LP 11, Optimum 11: bewiesen durch L2, LP gleich
    2: ((89, 86, 77, 69, 40, 34, 30, 18, 17, 14, 13, 11), 100),     # FFD 6, L1 5, L2 5, LP 36/7, Optimum 6: LP beweist FFD
    3: ((73, 70, 67, 54, 45, 45, 31, 27, 27, 24, 18, 15), 100),     # FFD 6, L1 5, L2 5, LP 5, Optimum 5: LP trifft das Optimum, FFD verliert
}
BEISPIEL_NAMEN = {
    0: "Kleines Beispiel (4, 4, 4, 4, 3)",
    1: "Beispiel 2 (bewiesen durch L2)",
    2: "Beispiel 3 (LP beweist FFD)",
    3: "Beispiel 4 (LP trifft das Optimum)",
    4: "Zufällige Instanz",
}
ZUFALL = 4

VERTEILUNGEN = (
    ("mittel", "mittlere Teile (10 bis 50 % der Kapazität)", 0.10, 0.50),
    ("gross", "große Teile (20 bis 80 %)", 0.20, 0.80),
    ("breit", "breit gestreute Teile (1 bis 90 %)", 0.01, 0.90),
)

# --- Raster (dasselbe wie Stück 2: gleiche Zellen, gleiche Seeds), vorberechnet in lpb_precomputed.json -----------------------------------------
MESS_CAP = 1000
MESS_N = (12, 20, 30)
INSTANZEN = 100
ILP_ZEITLIMIT = 60.0      # Sekunden je ILP-Aufruf im Generator (nur für die Fälle „LP gleich FFD minus 1“); darüber gilt die Instanz als „nicht entschieden“

# Ausgangscodes je Instanz: 1 FFD = L1; 2 FFD = L2 (> L1); P aufgerundeter LP-Wert = FFD (erst durch LP bewiesen); T LP = FFD - 1 und eine Packung mit FFD - 1 Containern
# existiert (LP scharf, FFD verliert); U LP = FFD - 1, ILP nach dem Zeitlimit nicht entschieden; V LP = FFD - 1, aber keine Packung mit FFD - 1 Containern (Rundung verletzt);
# X aufgerundeter LP-Wert um mehr als 1 unter FFD.
AUSGANG_CODES = {"1": "l1", "2": "l2", "P": "lp_beweist", "T": "lp_scharf", "U": "offen_unentschieden", "V": "rundung_verletzt", "X": "lp_weit_unter"}
AUSGANG_TEXTE = {
    "l1": "bewiesen durch L1",
    "l2": "erst durch L2 bewiesen",
    "lp_beweist": "erst durch LP bewiesen",
    "lp_scharf": "LP trifft das Optimum, FFD verliert",
    "offen_unentschieden": "offen (nicht entschieden)",
    "rundung_verletzt": "Rundung verletzt",
    "lp_weit_unter": "LP mehr als 1 unter FFD",
}

# --- Suche nach Gegenbeispielen zur Rundung (Optimum gegen aufgerundeten LP-Wert), vorberechnet -------------------------------------------------
SUCHE_N = (8, 9, 10, 11)
SUCHE_INSTANZEN = {8: 1500, 9: 1500, 10: 1500, 11: 600}
SUCHE_CAP = 100
SUCHE_MIN, SUCHE_MAX = 10, 60     # Paketgrößen gleichverteilt

COLOR_FILL = "#2F6B65"
COLOR_FREE = "rgba(150,150,150,0.35)"
COLOR_LINE = "#c0392b"
COLOR_L1 = "#2F6B65"
COLOR_L2 = "#4c78a8"
COLOR_LP = "#e0a030"
COLOR_SCHARF = "#7b5ea7"
COLOR_OFFEN = "#9e9e9e"
COLOR_BAD = "#c0392b"

PRESETS = {
    "Kleines Beispiel (LP 2,5)": {"beispiel": 0, "verteilung": 0, "n": DEFAULT_N, "seed": DEFAULT_SEED},
    "Bewiesen durch L2, LP gleich": {"beispiel": 1, "verteilung": 0, "n": DEFAULT_N, "seed": DEFAULT_SEED},
    "LP beweist FFD": {"beispiel": 2, "verteilung": 0, "n": DEFAULT_N, "seed": DEFAULT_SEED},
    "LP trifft das Optimum": {"beispiel": 3, "verteilung": 0, "n": DEFAULT_N, "seed": DEFAULT_SEED},
    "Zufällige Instanz (mittlere Teile)": {"beispiel": ZUFALL, "verteilung": 0, "n": DEFAULT_N, "seed": DEFAULT_SEED},
}
PRESET_HELP = {
    "Kleines Beispiel (LP 2,5)": "Fünf Pakete, bei denen der LP-Wert 2,5 ist: anderthalb Container mit zwei Vieren und ein Container mit einer Vier und einer Drei. Aufgerundet 3.",
    "Bewiesen durch L2, LP gleich": "Zwölf große Pakete: FFD ist schon durch L2 bewiesen optimal, der LP-Wert bestätigt es.",
    "LP beweist FFD": "FFD braucht mehr Container als L1 und L2 verlangen. Der aufgerundete LP-Wert ist gleich FFD: Damit ist FFD bewiesen optimal.",
    "LP trifft das Optimum": "FFD braucht einen Container mehr als das Optimum. Der aufgerundete LP-Wert ist gleich dem Optimum: Die LP-Schranke ist hier scharf.",
    "Zufällige Instanz (mittlere Teile)": "Eine zufällige Instanz mit mittleren Paketgrößen; Größenbereich, Paketzahl und Startzahl in der Seitenleiste.",
}

# Text des Expanders „Annahmen, Grenzen und bekannte Probleme“; derselbe Wortlaut steht in der README (tests/test_claims.py vergleicht beide).
ASSUMPTIONS_MARKDOWN = f"""**Annahmen.** Ganzzahlige Paketgrößen; eine Sorte Container mit fester Kapazität; alle Pakete sind vor dem Packen bekannt; keine Geometrie, nur Größen. Die LP-Schranke ist die Relaxation, in der jede zulässige Teilmenge von Paketen ein Muster ist, die Gewichte der Muster Brüche sein dürfen und jedes Paket mindestens einmal überdeckt wird. Verglichen wird nur FFD (First Fit, größte zuerst).

**Grenzen.** Live rechnet die Demo den LP-Wert und das Optimum bis {OPT_LIMIT} Pakete. Das Raster hat drei Größenbereiche und drei Paketzahlen (12, 20, 30) mit je {INSTANZEN} Instanzen und dieselben Instanzen wie Stück 2 dieser Reihe; über 30 Pakete ist nichts gemessen. Die Suche nach Gegenbeispielen zur Rundung deckt {sum(SUCHE_INSTANZEN.values())} zufällige Instanzen mit 8 bis 11 Paketen ab: Dass sie keines fand, heißt nicht, dass es keine gibt. Stärkere Schranken als die LP-Schranke sind nicht gemessen. Wie der LP-Wert bei vielen Paketen berechnet wird (Spaltenerzeugung), erklärt diese Demo nicht.

**Bekannte Probleme und Unsicherheiten.** Die Muster und Gewichte, die die Demo als LP-Lösung zeigt, sind eine optimale Lösung unter mehreren; der LP-Wert selbst ist eindeutig. Bei den Rasterinstanzen mit 20 und 30 Paketen kommt die Aussage „es gibt eine Packung mit einem Container weniger als FFD“ aus einem ganzzahligen Programm mit {ILP_ZEITLIMIT:.0f} Sekunden Zeitlimit; Instanzen, die es in dieser Zeit nicht entschieden hat, stehen in einer eigenen Spalte. {INSTANZEN} Instanzen je Zelle sind wenig, eine einzelne Zelle ist kein Gesetz. Dass kleinste Instanzen mit einem Optimum über dem aufgerundeten LP-Wert existieren (ab etwa zehn Paketen), steht nur aus Suchtreffern und Sekundärquellen, die Originale wurden nicht gelesen. Die App wurde im Browser bedient (Presets, Würfel-Button und Ausklapper auf Desktopbreite; auf Telefonbreite wurde nur das Layout geprüft), nicht auf einem echten Touch-Gerät."""
