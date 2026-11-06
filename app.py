"""LP-Schranke: was Brüche beweisen - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 4 der Reihe „Packen: Reihenfolge und Platzierungsregel“. Die LP-Schranke (Gilmore und Gomory) gegen FFD, L1, L2 und das exakte Optimum: Was beweist sie über L1 und L2
hinaus? Live bis 12 Pakete (alle Muster, scipy), das Raster mit denselben Instanzen wie Stück 2 und die Suche nach Gegenbeispielen sind vorberechnet (lpb_precomputed.json).

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import lpb_constants as C
from lpb_evaluation import Settings, analyse, suche_zeile, verdict_ausgang, verdict_raster, verdict_suche, zeile
from lpb_layout import dunkles_design, kopf_css
from lpb_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from lpb_visualization import build_container, build_lp, build_raster

st.set_page_config(page_title="LP-Schranke – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in lpb_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧮 LP-Schranke: was Brüche beweisen")
st.markdown(
    """
FFD ist **bewiesen optimal**, wenn seine Containerzahl gleich einer unteren Schranke ist. Die Volumenschranke **L1** und die Schranke **L2** reichen dafür oft nicht. Die **LP-Schranke** erlaubt, ein **Muster** (eine Gruppe von Paketen, die in einen Container passt) auch zu einem Bruchteil zu benutzen: Die kleinste Summe der Gewichte, mit der jedes Paket überdeckt wird, ist der **LP-Wert**. Aufgerundet ist er eine untere Schranke. Die Demo zeigt, was sie über L1 und L2 hinaus beweist und wo sie das Optimum trifft.

Weiter unten: die Abschnitte **🔬 Experiment** (Raster mit denselben Instanzen wie Stück 2, Suche nach Gegenbeispielen), **🚧 Wo die Annahmen enden**, der Expander **⚠️ Annahmen, Grenzen und bekannte Probleme** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert die LP-Schranke", expanded=True):
    st.markdown(
        """
1. **Muster:** Jede Gruppe von Paketen, die zusammen in einen Container passt, ist ein Muster.
2. **Brüche zulassen:** Jedes Muster bekommt ein Gewicht, auch ein Bruch wie 0,5. Jedes Paket muss insgesamt mindestens einmal überdeckt sein. Die kleinste Summe der Gewichte ist der **LP-Wert**.
3. **Aufrunden:** Jede echte Packung ist eine Lösung mit ganzen Gewichten, also ist der LP-Wert höchstens so groß wie das Optimum, und aufgerundet bleibt er eine untere Schranke.
4. **Vergleich:** Ist FFD gleich dem aufgerundeten LP-Wert, ist FFD bewiesen optimal. Ist der aufgerundete LP-Wert gleich dem Optimum und FFD darüber, verliert FFD, und die LP-Schranke zeigt es.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Instanz**")
    beispiel = st.selectbox("Pakete", list(C.BEISPIEL_NAMEN), format_func=C.BEISPIEL_NAMEN.get, key="beispiel_select",
                            help="Vier feste Beispiele (das erste mit Kapazität 10, die anderen mit Kapazität 100) oder eine zufällige Instanz.")
    st.markdown("**Zufällige Instanz**")
    verteilung = st.selectbox("Größen der Pakete", list(range(len(C.VERTEILUNGEN))), format_func=lambda i: C.VERTEILUNGEN[i][1], key="verteilung_select",
                              help="Wirkt nur bei der zufälligen Instanz.")
    n = st.slider("Zahl der Pakete n", *bounds("n_slider"), key="n_slider", help="Wirkt nur bei der zufälligen Instanz.")
    seed = st.number_input("Startzahl der zufälligen Instanz", *bounds("seed_input"), key="seed_input", step=1, help="Wirkt nur bei der zufälligen Instanz.")
    st.button("🎲 Neue zufällige Instanz würfeln", width="stretch", on_click=randomize_seed)

sync_query_params({"beispiel_select": int(beispiel), "verteilung_select": int(verteilung), "n_slider": int(n), "seed_input": int(seed)})

settings = Settings(int(beispiel), int(verteilung), int(n), int(seed))
a = _analysis(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3 = st.columns(3)
# Delta immer als „mein Wert minus Referenz“; die Farbe regelt delta_color="inverse" (Vorzeichen-Falle, DEMO-PLAYBOOK §2).
m1.metric("FFD braucht", a.ffd, delta=a.ffd - a.opt, delta_color="inverse", help="Delta: FFD minus exaktes Optimum.")
m2.metric("Optimum (exakt)", a.opt, delta="Referenz", delta_color="off")
m3.metric("Volumenschranke L1", a.schranke_l1, delta="Summe durch Kapazität, aufgerundet", delta_color="off")
m4, m5, m6 = st.columns(3)
m4.metric("Schranke L2", a.schranke_l2, delta="stärker bei großen Paketen", delta_color="off")
m5.metric("LP-Wert", f"{a.lp['wert']:.4f}", delta="Muster dürfen Brüche sein", delta_color="off")
m6.metric("LP-Wert aufgerundet", a.lp_zahl, delta="untere Schranke", delta_color="off")
st.caption("Pakete nach Größe geordnet: " + ", ".join(str(s) for s in sorted(a.inst.sizes, reverse=True)) + f"  (Summe {sum(a.inst.sizes)}, Kapazität {a.inst.cap}).")
c1, c2 = st.columns(2)
with c1:
    st.markdown(f"**FFD: {a.ffd} Container**")
    st.plotly_chart(build_container(a.inst.sizes, a.bins, a.inst.cap), width="stretch", key="chart_ffd")
with c2:
    st.markdown(f"**LP-Lösung: Gesamtbreite {a.lp['wert']:.2f}**")
    st.plotly_chart(build_lp(a.lp["muster"], a.inst.cap), width="stretch", key="chart_lp")
st.caption("Links die FFD-Packung. Rechts eine optimale Lösung des LP: Jedes Muster ist ein Balken, seine Breite ist sein Gewicht (Breite 1 = ein ganzer Container). Bei Gleichständen gibt es mehrere optimale Lösungen, der LP-Wert ist eindeutig.")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wer beweist hier, dass FFD optimal ist, und woran scheitert es sonst?")
kind, text = verdict_ausgang(a)
getattr(st, kind)(text)

st.markdown("---")

# --- Experiment 1: Raster ------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Was beweist die LP-Schranke zusätzlich?")
st.caption(
    f"Dasselbe Raster wie in Stück 2 dieser Reihe: je {C.INSTANZEN} feste Zufallsinstanzen pro Zelle (Kapazität {C.MESS_CAP}, Größen gleichverteilt im gewählten Bereich), dieselben Seeds. "
    f"Den LP-Wert rechnet ein Generator vorab (Spaltenerzeugung); ob eine Packung mit einem Container weniger als FFD existiert, kommt bei 12 Paketen aus der Teilmengen-DP, "
    f"bei 20 und 30 aus einem ganzzahligen Programm mit {C.ILP_ZEITLIMIT:.0f} Sekunden Zeitlimit."
)
e1, e2 = st.columns(2)
exp_v = e1.selectbox("Größen der Pakete", list(range(len(C.VERTEILUNGEN))), index=0, format_func=lambda i: C.VERTEILUNGEN[i][1], key="exp_verteilung")
exp_n = e2.selectbox("Zahl der Pakete n (für das Verdikt)", list(range(len(C.MESS_N))), index=1, format_func=lambda i: str(C.MESS_N[i]), key="exp_n")
zeilen = [zeile(int(exp_v), ni) for ni in range(len(C.MESS_N))]
st.plotly_chart(build_raster(zeilen), width="stretch", key="exp_chart")
tabelle = ["| n | L1 | L2 | LP | scharf | offen |", "|---|---|---|---|---|---|"]
for z in zeilen:
    tabelle.append(f"| {z['n']} | {z['l1']} | {z['l2']} | {z['lp_beweist']} | {z['lp_scharf']} | {z['offen_unentschieden']} |")
st.markdown("\n".join(tabelle))
st.caption(
    f"Anzahl der Instanzen von je {zeilen[0]['instanzen']}. **L1, L2, LP:** FFD ist durch die Volumenschranke, erst durch L2 oder erst durch den aufgerundeten LP-Wert bewiesen optimal. "
    "**scharf:** der aufgerundete LP-Wert ist gleich dem Optimum, FFD braucht einen Container mehr. **offen:** der aufgerundete LP-Wert liegt einen Container unter FFD, das Optimum ist nicht entschieden. "
    "Fälle, in denen die Rundung verletzt ist oder der LP-Wert mehr als einen Container unter FFD liegt, stehen im Verdikt."
)
kind, text = verdict_raster(zeilen[int(exp_n)])
getattr(st, kind)(text)

st.markdown("---")

# --- Experiment 2: Suche nach Gegenbeispielen ---------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Verfehlt der aufgerundete LP-Wert das Optimum je?")
st.caption(
    f"Je Größe feste Zufallsinstanzen (Kapazität {C.SUCHE_CAP}, Größen {C.SUCHE_MIN} bis {C.SUCHE_MAX}); Optimum per Teilmengen-DP, LP-Wert mit allen Mustern; vorberechnet. "
    "Gezählt wird, ob das Optimum gleich dem aufgerundeten LP-Wert ist oder größer."
)
such = [suche_zeile(nn) for nn in C.SUCHE_N]
tab = ["| n | Instanzen | gleich | größer |", "|---|---|---|---|"]
for z in such:
    tab.append(f"| {z['n']} | {z['instanzen']} | {z['gleich']} | {z['verletzt']} |")
st.markdown("\n".join(tab))
kind, text = verdict_suche(such)
getattr(st, kind)(text)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Der aufgerundete LP-Wert trifft das Optimum** | In der Literatur gibt es Instanzen, bei denen das Optimum darüber liegt (Suchtreffer, ab etwa zehn Paketen); die Suche dieser Demo hat in zufälligen kleinen Instanzen keine gefunden, das beweist nichts für gezielt gebaute. | - |
| **Nur L1, L2 und der LP-Wert** | Stärkere Schranken sind nicht gemessen; wie viele der 8 Fälle im Raster, die offen bleiben, sie entscheiden würden, ist unbekannt. | spätere Stücke dieser Reihe |
| **Der LP-Wert ist berechenbar** | Live rechnet die Demo ihn bis 12 Pakete mit allen Mustern; bei 20 und 30 Paketen stammt er aus einem Generator mit Spaltenerzeugung, die diese Demo nicht erklärt. | [Exakte Suche](https://sebastianhanisch.net/konzepte-exakte-suche.html) |
| **Die Pakete sind zufällig und gleichverteilt** | Gezielt gebaute Instanzen verhalten sich anders (etwa Triplets: Dort kennt schon L1 das Optimum). | Stück 3 dieser Reihe |
"""
)

with st.expander("⚠️ Annahmen, Grenzen und bekannte Probleme"):
    st.markdown(C.ASSUMPTIONS_MARKDOWN)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Lesehilfe.** *Gegeben:* Pakete mit ganzzahligen Größen und Container einer festen Kapazität. *Gesucht:* die kleinste Zahl von Containern und ein Beweis, dass FFD sie erreicht.

| Symbol | Bedeutung |
|---|---|
| $s_i$ | Größe von Paket $i$, $1 \le s_i \le C$ |
| $C$ | Kapazität eines Containers |
| $\mathcal{P}$ | Menge der Muster: Teilmengen $p$ der Pakete mit $\sum_{i \in p} s_i \le C$ |
| $x_p$ | Gewicht des Musters $p$ |
| $y_i$ | Dualpreis von Paket $i$ |
| $\mathrm{LP}$ | LP-Wert |
| $\mathrm{OPT}$, $\mathrm{FFD}$ | Optimum, Containerzahl von FFD |

**LP-Schranke** (Gilmore und Gomory). $\mathrm{LP} = \min \sum_{p \in \mathcal{P}} x_p$ unter $\sum_{p \ni i} x_p \ge 1$ für jedes Paket $i$ und $x_p \ge 0$. Jede Packung ist eine Lösung mit $x_p \in \{0, 1\}$, also gilt $\sum_i s_i / C \le \mathrm{LP} \le \mathrm{OPT} \le \mathrm{FFD}$ und, weil $\mathrm{OPT}$ ganz ist, $L_1 \le \lceil \mathrm{LP} \rceil \le \mathrm{OPT}$ (der ungerundete LP-Wert kann unter $L_1$ liegen, etwa bei vier Paketen der Größe 3 und $C = 10$).

**Dualzertifikat.** Das duale Programm $\max \sum_i y_i$ unter $\sum_{i \in p} y_i \le 1$ für jedes Muster $p$ und $y \ge 0$ hat denselben Wert. Jedes zulässige $y$ beweist eine untere Schranke; die Tests der Demo prüfen es an den Beispielen.

**Beispiel (4, 4, 4, 4, 3), $C = 10$.** Muster sind $\{4,4\}$ (Summe 8), $\{4,3\}$ (7) und Einzelpakete. Die 3 braucht ein Muster mit ihr: Gewicht mindestens 1 auf $\{4,3\}$ (das deckt auch eine Vier); die übrigen drei Vieren deckt $\{4,4\}$ mit Gewicht $1{,}5$: $\mathrm{LP} = 1 + 1{,}5 = 2{,}5$, aufgerundet $3$. FFD braucht 3 Container, also ist FFD bewiesen optimal, obwohl $L_1 = L_2 = 2$.

**Rundung.** Dass $\mathrm{OPT} = \lceil \mathrm{LP} \rceil$ gilt (Rundungseigenschaft), ist in allen Messungen dieser Demo so, in denen das Optimum bekannt ist (im Raster sind 8 Instanzen unentschieden), aber nicht allgemein: Aus der Literatur (Suchtreffer, Originale nicht gelesen) sind Instanzen mit $\mathrm{OPT} > \lceil \mathrm{LP} \rceil$ bekannt, die kleinsten ab etwa zehn Paketen, und die größte bekannte Lücke $\mathrm{OPT} - \mathrm{LP}$ liegt bei etwa 1,1.

**Wie die Demo rechnet.** Bis 12 Pakete mit allen Mustern (höchstens $2^{12} - 1$ Spalten) und dem Löser HiGHS (`scipy.optimize.linprog`); die Muster der Anzeige sind nach den Größen der Pakete zusammengefasst. Bei 20 und 30 Paketen stammt der Wert aus einem Generator mit Spaltenerzeugung (Preisproblem: beschränkter Rucksack per DP, jedes Paket höchstens einmal).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
