<?xml version="1.0" encoding="UTF-8"?>
<sch:pattern xmlns:sch="http://purl.oclc.org/dsdl/schematron" id="thermml-sublattice-multiplicities">
  <sch:title>Sublattice multiplicity count</sch:title>
  <!-- XSD validates a non-empty list of positive decimals. -->
  <sch:rule context="t:database//t:phase/t:structure/t:sublattices">
    <sch:let name="values" value="normalize-space(@multiplicities)"/>
    <sch:let name="value-count" value="string-length($values) - string-length(translate($values, ' ', '')) + number($values != '')"/>
    <sch:assert id="VAL-ERR-SUBLATTICE-MULTIPLICITY-COUNT" role="error"
        test="$value-count = count(t:site)">
      Expected one multiplicity per sublattice: found <sch:value-of select="$value-count"/> values for <sch:value-of select="count(t:site)"/> sites.
    </sch:assert>
  </sch:rule>
</sch:pattern>
