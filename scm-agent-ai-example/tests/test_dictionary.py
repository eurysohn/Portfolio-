from tools.dictionary_lookup import lookup_terms


def test_dictionary_lookup_otif():
    results = lookup_terms("define OTIF", top_n=3)
    assert results
    assert results[0]["term"] == "OTIF"


def test_dictionary_synonym_lookup():
    results = lookup_terms("what is on-time in-full", top_n=3)
    assert results
    assert results[0]["term"] == "OTIF"
