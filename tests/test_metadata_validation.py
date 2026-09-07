from pathlib import Path

import pytest
from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
URI = "http://calphad.org/thermml/v0"
NS = {"t": URI}


@pytest.mark.parametrize(
    "fixture",
    ["tests/fixtures/ionic-liquid-minimal.xml", "examples/simple_solution.xml"],
)
def test_assessed_systems_belong_to_database_metadata(fixture):
    schema = etree.XMLSchema(etree.parse(str(ROOT / "schema/thermml-schema.xsd")))
    doc = etree.parse(str(ROOT / fixture))
    metadata = doc.find("t:metadata", NS)
    note = etree.Element(f"{{{URI}}}assessedSystems")
    note.text = "Al-Fe Al-O Fe-O"
    license_element = metadata.find("t:license", NS)
    metadata.insert(metadata.index(license_element), note)
    assert schema.validate(doc), str(schema.error_log)

    metadata.remove(note)
    phase = doc.find("t:phases/t:phase", NS)
    endmembers = phase.find("t:endmembers", NS)
    phase.insert(phase.index(endmembers), note)
    assert not schema.validate(doc)
    assert "assessedSystems" in str(schema.error_log)
