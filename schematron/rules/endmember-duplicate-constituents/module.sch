<?xml version="1.0" encoding="UTF-8"?>
<sch:pattern xmlns:sch="http://purl.oclc.org/dsdl/schematron" id="thermml-endmember-duplicate-constituents">
  <sch:title>Duplicate endmember constituent arrays within a phase</sch:title>

  <!--
    Rejects two endmembers in the same phase that occupy the sublattice sites with the
    identical constituent array, i.e. the same species on every site, in order. The
    comparison is a literal string compare of a per-site species signature; it does not
    parse species or canonicalize anything. Site order is significant: [Fe|Va] and
    [Va|Fe] are different endmembers.

    Like the CEF endmember-count rule, the signature is built as a bounded concat over
    explicit site positions, because the XPath 1.0 / XSLT Schematron binding used here has
    no string-join over an arbitrary-length sequence. Up to 8 sublattice sites are
    supported, matching the ceiling used elsewhere in this rule set. Endmembers are
    expected to carry exactly one constituent per site (standard CEF endmember); only the
    first constituent of each site participates in the signature.

    Scope is a single phase's <endmembers> block; the same constituent array may appear in
    a different phase without being flagged.
  -->

  <sch:rule context="t:database//t:phase/t:endmembers/t:endmember">
    <sch:let name="signature" value="concat(
      count(t:constituents/t:site), '#',
      normalize-space(t:constituents/t:site[1]/t:const/@species), '#',
      normalize-space(t:constituents/t:site[2]/t:const/@species), '#',
      normalize-space(t:constituents/t:site[3]/t:const/@species), '#',
      normalize-space(t:constituents/t:site[4]/t:const/@species), '#',
      normalize-space(t:constituents/t:site[5]/t:const/@species), '#',
      normalize-space(t:constituents/t:site[6]/t:const/@species), '#',
      normalize-space(t:constituents/t:site[7]/t:const/@species), '#',
      normalize-space(t:constituents/t:site[8]/t:const/@species))"/>
    <sch:let name="duplicate" value="preceding-sibling::t:endmember[concat(
      count(t:constituents/t:site), '#',
      normalize-space(t:constituents/t:site[1]/t:const/@species), '#',
      normalize-space(t:constituents/t:site[2]/t:const/@species), '#',
      normalize-space(t:constituents/t:site[3]/t:const/@species), '#',
      normalize-space(t:constituents/t:site[4]/t:const/@species), '#',
      normalize-space(t:constituents/t:site[5]/t:const/@species), '#',
      normalize-space(t:constituents/t:site[6]/t:const/@species), '#',
      normalize-space(t:constituents/t:site[7]/t:const/@species), '#',
      normalize-space(t:constituents/t:site[8]/t:const/@species)) = $signature][1]"/>
    <sch:assert
        id="VAL-ERR-ENDMEMBER-DUPLICATE-CONSTITUENTS"
        role="error"
        test="not($duplicate)">
      Endmember <sch:value-of select="@name"/> in phase <sch:value-of select="ancestor::t:phase[1]/@name"/> has the same constituent array as endmember <sch:value-of select="$duplicate/@name"/>.
    </sch:assert>
  </sch:rule>
</sch:pattern>
