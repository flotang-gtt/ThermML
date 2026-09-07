<?xml version="1.0" encoding="UTF-8"?>
<sch:pattern xmlns:sch="http://purl.oclc.org/dsdl/schematron" id="thermml-ionic-liquid-constituents">
  <sch:title>Ionic-liquid constituent identity and site membership</sch:title>

  <!-- Group shape is unique to the ionic model. XSD checks charge signs,
       non-empty compositions, one or two sites, and single endmember occupancy. -->
  <sch:rule context="t:database//t:phase/t:constituents/*/t:specie">
    <sch:let name="composition" value="normalize-space(@composition)"/>
    <sch:let name="charge" value="normalize-space(@charge)"/>
    <sch:assert id="VAL-ERR-IONIC-DUPLICATE-SPECIES" role="error"
        test="not(preceding-sibling::t:specie[normalize-space(@composition) = $composition and normalize-space(@charge) = $charge])">
      Ionic species <sch:value-of select="@name"/> duplicates a species with the same composition and charge in its group.
    </sch:assert>
  </sch:rule>

  <sch:rule context="t:database//t:phase[t:constituents/t:cations]/t:endmembers/t:endmember/t:constituents/t:site/t:const | t:database//t:phase[t:constituents/t:cations]/t:interactions/t:interaction/t:constituents/t:site/t:const">
    <sch:let name="phase" value="ancestor::t:phase[1]"/>
    <sch:let name="site-index" value="count(../preceding-sibling::t:site) + 1"/>
    <sch:assert id="VAL-ERR-IONIC-CONSTITUENT-SITE-MEMBERSHIP" role="error"
        test="(count(../../t:site) = 1 and @species = $phase/t:constituents/t:neutrals/t:specie[translate(@name, 'va', 'VA') != 'VA' and translate(normalize-space(@composition), 'va', 'VA') != 'VA']/@name) or (count(../../t:site) = 2 and (($site-index = 1 and @species = $phase/t:constituents/t:cations/t:specie/@name) or ($site-index = 2 and (@species = $phase/t:constituents/t:anions/t:specie/@name or @species = $phase/t:constituents/t:neutrals/t:specie/@name))))">
      Ionic constituent <sch:value-of select="@species"/> is not allowed on site <sch:value-of select="$site-index"/>: a single site requires non-vacancy neutrals; with two sites, site 1 requires cations and site 2 requires anions or neutrals.
    </sch:assert>
  </sch:rule>
</sch:pattern>
