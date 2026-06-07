<?xml version="1.0" encoding="UTF-8"?>
<sch:pattern xmlns:sch="http://purl.oclc.org/dsdl/schematron" id="thermml-species-duplicate-stoichiometry">
  <sch:title>Duplicate species stoichiometry within a phase</sch:title>

  <!--
    Rejects two species in the same phase that share the same stoichiometric identity.
    "Same stoichiometric formula" is compared literally as a string: the normalized
    composition attribute together with the normalized charge.

    Charge is part of the comparison on purpose. Ions such as Cu[1+]/Cu[2+] or
    Fe[2+]/Fe[3+] legitimately share a composition string ("Cu1", "Fe1") and must not
    be reported as duplicates; they are distinct species precisely because of charge.

    The check is intentionally syntactic. It does not canonicalize chemical formulas
    (e.g. "Fe1" vs "Fe", or reordered constituents like "Al2Si1" vs "Si1Al2") and does
    not attempt to parse them. Species without a composition are not compared, because
    there is no formula to compare. The scope is a single phase's <species> block; the
    same formula may reappear in a different phase without being flagged.
  -->

  <sch:rule context="t:database//t:phase/t:species/t:specie[normalize-space(@composition) != '']">
    <sch:let name="composition" value="normalize-space(@composition)"/>
    <sch:let name="charge" value="normalize-space(@charge)"/>
    <sch:assert
        id="VAL-ERR-SPECIES-DUPLICATE-STOICHIOMETRY"
        role="error"
        test="not(preceding-sibling::t:specie[normalize-space(@composition) = $composition and normalize-space(@charge) = $charge])">
      Species <sch:value-of select="@name"/> in phase <sch:value-of select="ancestor::t:phase[1]/@name"/> duplicates the stoichiometric formula already declared by species <sch:value-of select="preceding-sibling::t:specie[normalize-space(@composition) = $composition and normalize-space(@charge) = $charge][1]/@name"/> (composition "<sch:value-of select="$composition"/>", charge "<sch:value-of select="$charge"/>").
    </sch:assert>
  </sch:rule>
</sch:pattern>
