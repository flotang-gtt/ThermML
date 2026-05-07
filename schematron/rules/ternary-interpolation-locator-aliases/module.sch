<?xml version="1.0" encoding="UTF-8"?>
<sch:pattern xmlns:sch="http://purl.oclc.org/dsdl/schematron" id="thermml-ternary-interpolation">
  <sch:title>Ternary interpolation alias consistency</sch:title>

  <sch:rule context="t:database//t:ternaryInterpolations/t:interpolation//t:const[@site and @siteIndex]">
    <sch:assert
        id="VAL-ERR-TERNARY-INTERPOLATION-LOCATOR-ALIASES-MISMATCH"
        role="error"
        test="@site = @siteIndex">
      Ternary interpolation locator aliases disagree for constituent <sch:value-of select="@name"/> in phase <sch:value-of select="ancestor::t:phase[1]/@name"/>: site=<sch:value-of select="@site"/> and siteIndex=<sch:value-of select="@siteIndex"/> must carry the same locator value.
    </sch:assert>
  </sch:rule>
</sch:pattern>