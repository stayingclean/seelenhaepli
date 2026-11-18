from buechlein.buch import buch_laden, ordnen


def test_reihenfolge_gemaess_buch():
    ergebnis = ordnen(["a", "b", "c"], ["c", "a", "b"])
    assert ergebnis.namen == ["c", "a", "b"]
    assert ergebnis.nicht_aufgefuehrt == []
    assert ergebnis.ohne_datei == []


def test_nicht_aufgefuehrte_alphabetisch_ans_ende():
    ergebnis = ordnen(["Zeller_Z", "meier_m", "Abt_A", "Huber_H"], ["Huber_H"])
    assert ergebnis.namen == ["Huber_H", "Abt_A", "meier_m", "Zeller_Z"]
    assert ergebnis.nicht_aufgefuehrt == ["Abt_A", "meier_m", "Zeller_Z"]


def test_eintrag_ohne_datei_wird_gemeldet_und_uebersprungen():
    ergebnis = ordnen(["a"], ["fehlt", "a"])
    assert ergebnis.namen == ["a"]
    assert ergebnis.ohne_datei == ["fehlt"]


def test_doppelter_eintrag_erscheint_einmal():
    assert ordnen(["a", "b"], ["a", "b", "a"]).namen == ["a", "b"]


def test_buch_laden(tmp_path):
    datei = tmp_path / "buch.yaml"
    datei.write_text(
        "titel: Probe\nherausgeber: Jemand\nreihenfolge:\n  - a\n  - b\n", encoding="utf-8"
    )
    buch = buch_laden(datei)
    assert buch.titel == "Probe"
    assert buch.sprache == "de-CH"
    assert buch.max_zeichen == 4500
    assert buch.reihenfolge == ["a", "b"]
    assert buch.ordner == tmp_path
