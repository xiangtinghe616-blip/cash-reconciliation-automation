from splink import DuckDBAPI, Linker, SettingsCreator, block_on
import splink.comparison_library as cl
import splink.comparison_level_library as cll


def test_splink_core_api_imports():
    assert DuckDBAPI is not None
    assert Linker is not None
    assert SettingsCreator is not None
    assert block_on is not None
    assert cl.ExactMatch is not None
    assert cll.ExactMatchLevel is not None
