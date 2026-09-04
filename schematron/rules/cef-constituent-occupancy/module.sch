<?xml version="1.0" encoding="UTF-8"?>
<sch:pattern xmlns:sch="http://purl.oclc.org/dsdl/schematron" id="thermml-cef-constituent-occupancy">
  <sch:title>Sublattice constituent occupancy</sch:title>

  <!-- Structural matching includes ordered CEF phases. Each reference is
       checked against its own site's token list, without a site-count ceiling. -->
  <sch:rule context="t:database//t:phase[t:structure/t:sublattices]/t:endmembers/t:endmember/t:constituents/t:site">
    <sch:assert id="VAL-ERR-CEF-ENDMEMBER-SINGLE-OCCUPANCY" role="error"
        test="count(t:const) = 1">
      Each endmember site must contain exactly one constituent.
    </sch:assert>
  </sch:rule>

  <sch:rule context="t:database//t:phase[t:structure/t:sublattices]/t:interactions/t:interaction/t:constituents">
    <sch:assert id="VAL-ERR-CEF-INTERACTION-SITE-COUNT" role="error"
        test="count(t:site) = count(ancestor::t:phase[1]/t:structure/t:sublattices/t:site)">
      Interaction constituent sites must match the phase's sublattice count.
    </sch:assert>
  </sch:rule>

  <sch:rule context="t:database//t:phase[t:structure/t:sublattices]/t:endmembers/t:endmember/t:constituents/t:site/t:const | t:database//t:phase[t:structure/t:sublattices]/t:interactions/t:interaction/t:constituents/t:site/t:const">
    <sch:let name="site-index" value="count(../preceding-sibling::t:site) + 1"/>
    <sch:let name="allowed" value="normalize-space(ancestor::t:phase[1]/t:structure/t:sublattices/t:site[$site-index]/@constituents)"/>
    <sch:assert id="VAL-ERR-CEF-CONSTITUENT-SITE-MEMBERSHIP" role="error"
        test="normalize-space(@species) != '' and contains(concat(' ', $allowed, ' '), concat(' ', normalize-space(@species), ' '))">
      Constituent <sch:value-of select="@species"/> is not declared on sublattice <sch:value-of select="$site-index"/>.
    </sch:assert>
  </sch:rule>
</sch:pattern>
