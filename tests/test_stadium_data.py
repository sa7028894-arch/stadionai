import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import stadium_data as sd


def test_get_zones_returns_all_expected_zones():
    zones = sd.get_zones()
    names = {z["zone"] for z in zones}
    assert "Gate 1" in names
    assert "Lower Bowl" in names
    assert len(zones) == 13


def test_get_zones_density_in_valid_range():
    zones = sd.get_zones()
    for z in zones:
        assert 0 <= z["density"] <= 100


def test_get_zones_status_matches_density_thresholds():
    zones = sd.get_zones()
    for z in zones:
        if z["density"] >= 85:
            assert z["status"] == "critical"
        elif z["density"] >= 60:
            assert z["status"] == "busy"
        else:
            assert z["status"] == "normal"


def test_get_incidents_returns_requested_count():
    incidents = sd.get_incidents(n=3)
    assert len(incidents) == 3


def test_get_incidents_have_required_fields():
    incidents = sd.get_incidents(n=2)
    for inc in incidents:
        assert "time" in inc
        assert "location" in inc
        assert "description" in inc
        assert inc["severity"] in ("low", "medium", "high")


def test_get_weather_has_expected_keys():
    weather = sd.get_weather()
    assert "condition" in weather
    assert "temp_c" in weather
    assert "advisory" in weather


def test_get_transport_status_nonempty():
    transport = sd.get_transport_status()
    assert len(transport) > 0
    for t in transport:
        assert "mode" in t and "status" in t


def test_build_context_block_includes_stadium_name():
    context = sd.build_context_block()
    assert sd.STADIUM_NAME in context


def test_build_context_block_includes_wayfinding_data():
    context = sd.build_context_block()
    assert "WAYFINDING KNOWLEDGE BASE" in context
    assert "Gate 1" in context


def test_locations_knowledge_base_nonempty():
    assert len(sd.LOCATIONS) > 0
    for key, value in sd.LOCATIONS.items():
        assert isinstance(key, str) and isinstance(value, str)
        assert len(value) > 0
