<?xml version="1.0" encoding="UTF-8"?>
<sch:pattern xmlns:sch="http://purl.oclc.org/dsdl/schematron" id="thermml-endmember-constituent-site-count">
  <sch:title>Endmember constituent site count matches phase sublattices</sch:title>

  <!--
    Rejects an endmember whose constituent site array has a different count than the
    number of sublattices declared by the phase. An endmember is a specific compound that
    occupies each sublattice site with exactly one species (or vacancy); the number of
    constituent sites must therefore match the number of sublattices.

    This rule applies only to phases that declare a structure with sublattices (CEF and
    related models). Phases without structure (e.g., quasichemical/MQM models) are excluded
    and not checked by this rule.
  -->

  <sch:rule context="t:database//t:phase[t:structure/t:sublattices/t:site]/t:endmembers/t:endmember">
    <sch:let name="expected-site-count" value="count(ancestor::t:phase[1]/t:structure/t:sublattices/t:site)"/>
    <sch:let name="actual-site-count" value="count(t:constituents/t:site)"/>
    <sch:assert
        id="VAL-ERR-ENDMEMBER-CONSTITUENT-SITE-COUNT-MISMATCH"
        role="error"
        test="$actual-site-count = $expected-site-count">
      Endmember <sch:value-of select="@name"/> in phase <sch:value-of select="ancestor::t:phase[1]/@name"/> has <sch:value-of select="$actual-site-count"/> constituent site(s), but phase declares <sch:value-of select="$expected-site-count"/> sublattice(s).
    </sch:assert>
  </sch:rule>
</sch:pattern>
