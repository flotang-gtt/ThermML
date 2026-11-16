<?xml version="1.0" encoding="UTF-8"?>
<sch:pattern xmlns:sch="http://purl.oclc.org/dsdl/schematron" id="thermml-species-duplicate-stoichiometry">
  <sch:title>Shared species composition and charge within a phase</sch:title>

  <!--
    Species names identify distinct model entities. Matching composition and charge
    do not establish identity: native assessments may assign independent parameters
    to such species, and MQM charge records formal model valence rather than
    necessarily physical oxidation state. This is an advisory review aid only.

    Comparison is deliberately literal after whitespace normalization. It does not
    canonicalize formulas (Fe1 versus Fe) or charges (+1 versus 1). Missing or empty
    compositions are not compared. Scope is one phase's species block; name
    uniqueness and reference integrity remain XSD constraints.
  -->

  <sch:rule context="t:database//t:phase/t:species/t:specie[normalize-space(@composition) != '']">
    <sch:let name="composition" value="normalize-space(@composition)"/>
    <sch:let name="charge" value="normalize-space(@charge)"/>
    <sch:report
        id="VAL-WARN-SPECIES-DUPLICATE-STOICHIOMETRY"
        role="warning"
        test="preceding-sibling::t:specie[normalize-space(@composition) = $composition and normalize-space(@charge) = $charge]">
      Species <sch:value-of select="@name"/> in phase <sch:value-of select="ancestor::t:phase[1]/@name"/> shares composition "<sch:value-of select="$composition"/>" and charge "<sch:value-of select="$charge"/>" with species <sch:value-of select="preceding-sibling::t:specie[normalize-space(@composition) = $composition and normalize-space(@charge) = $charge][1]/@name"/>. Distinct model identities may be intentional; review the source assessment without automatically merging species or changing model charges.
    </sch:report>
  </sch:rule>
</sch:pattern>
