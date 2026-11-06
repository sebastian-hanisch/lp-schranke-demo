"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen; jedes Preset liefert den erwarteten Ausgang und die Art des Verdikts."""

import pytest

import lpb_constants as C
import lpb_evaluation as ev
import lpb_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_regler_bounds():
    for preset in C.PRESETS.values():
        for key, state_key in P.PRESET_KEYS.items():
            lo, hi = P.bounds(state_key)
            assert lo <= preset[key] <= hi, (key, preset)


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**next(iter(C.PRESETS.values()))) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS) and set(P.PRESET_KEYS_INV) == set(P.SETTING_SPECS)


def test_beispielauswahl_deckt_alle_beispiele_und_die_zufallsinstanz_ab():
    assert set(C.BEISPIEL_NAMEN) == set(C.BEISPIELE) | {C.ZUFALL} and P.bounds("beispiel_select") == (0, C.ZUFALL)


ERWARTET = {
    "Kleines Beispiel (LP 2,5)": ("lp_beweist", "success"),
    "Bewiesen durch L2, LP gleich": ("l2", "success"),
    "LP beweist FFD": ("lp_beweist", "success"),
    "LP trifft das Optimum": ("lp_scharf", "warning"),
}


@pytest.mark.parametrize("name", list(ERWARTET))
def test_jedes_beispiel_preset_liefert_den_erwarteten_ausgang_und_die_art(name):
    a = ev.analyse(ev.Settings(**C.PRESETS[name]))
    assert a.ausgang == ERWARTET[name][0] and ev.verdict_ausgang(a)[0] == ERWARTET[name][1]


def test_zufallspreset_liefert_eine_zulaessige_instanz_mit_optimum_und_ordnung_der_schranken():
    a = ev.analyse(ev.Settings(**C.PRESETS["Zufällige Instanz (mittlere Teile)"]))
    assert a.inst.n == C.DEFAULT_N and a.opt is not None
    assert a.schranke_l1 <= a.schranke_l2 <= a.lp_zahl <= a.opt <= a.ffd
    assert a.ausgang in ("l1", "l2", "lp_beweist", "lp_scharf")
