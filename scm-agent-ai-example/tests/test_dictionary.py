from tools.dictionary_lookup import lookup


def test_dictionary_lookup_term():
    results, related = lookup("OTIF")
    assert results
    assert "OTIF" in related


def test_dictionary_lookup_synonym():
    results, related = lookup("on time in full")
    assert results
