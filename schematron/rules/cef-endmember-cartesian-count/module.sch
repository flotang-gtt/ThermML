<?xml version="1.0" encoding="UTF-8"?>
<sch:pattern xmlns:sch="http://purl.oclc.org/dsdl/schematron" id="thermml-cef-endmember-count">
  <sch:title>CEF endmember cartesian-count completeness</sch:title>

  <!--
    This rule is written for the current XPath 1.0 / XSLT-style Schematron binding used by
    lxml.isoschematron. That environment does not offer a clean generic product operator over an
    arbitrary-length sequence of sublattice constituent counts, so the expected endmember total
    is computed as a bounded case split over explicit site positions.

    The current formulation supports up to 8 declared sublattice sites. That is intentional and
    acceptable for the current ThermML domain, where practical CEF models are comfortably below
    that ceiling.
  -->

  <sch:rule context="t:database//t:phase[@xsi:type='CEFPhaseType' and count(t:structure/t:sublattices/t:site[@constituents]) &gt;= 1 and count(t:structure/t:sublattices/t:site[@constituents]) &lt;= 8 and t:endmembers]">
    <sch:let name="site-count" value="count(t:structure/t:sublattices/t:site[@constituents])"/>
    <sch:let name="actual-endmember-count" value="count(t:endmembers/t:endmember)"/>
    <sch:let name="site1-count" value="string-length(normalize-space(t:structure/t:sublattices/t:site[1]/@constituents)) - string-length(translate(normalize-space(t:structure/t:sublattices/t:site[1]/@constituents), ' ', '')) + number(boolean(t:structure/t:sublattices/t:site[1]))"/>
    <sch:let name="site2-count" value="string-length(normalize-space(t:structure/t:sublattices/t:site[2]/@constituents)) - string-length(translate(normalize-space(t:structure/t:sublattices/t:site[2]/@constituents), ' ', '')) + number(boolean(t:structure/t:sublattices/t:site[2]))"/>
    <sch:let name="site3-count" value="string-length(normalize-space(t:structure/t:sublattices/t:site[3]/@constituents)) - string-length(translate(normalize-space(t:structure/t:sublattices/t:site[3]/@constituents), ' ', '')) + number(boolean(t:structure/t:sublattices/t:site[3]))"/>
    <sch:let name="site4-count" value="string-length(normalize-space(t:structure/t:sublattices/t:site[4]/@constituents)) - string-length(translate(normalize-space(t:structure/t:sublattices/t:site[4]/@constituents), ' ', '')) + number(boolean(t:structure/t:sublattices/t:site[4]))"/>
    <sch:let name="site5-count" value="string-length(normalize-space(t:structure/t:sublattices/t:site[5]/@constituents)) - string-length(translate(normalize-space(t:structure/t:sublattices/t:site[5]/@constituents), ' ', '')) + number(boolean(t:structure/t:sublattices/t:site[5]))"/>
    <sch:let name="site6-count" value="string-length(normalize-space(t:structure/t:sublattices/t:site[6]/@constituents)) - string-length(translate(normalize-space(t:structure/t:sublattices/t:site[6]/@constituents), ' ', '')) + number(boolean(t:structure/t:sublattices/t:site[6]))"/>
    <sch:let name="site7-count" value="string-length(normalize-space(t:structure/t:sublattices/t:site[7]/@constituents)) - string-length(translate(normalize-space(t:structure/t:sublattices/t:site[7]/@constituents), ' ', '')) + number(boolean(t:structure/t:sublattices/t:site[7]))"/>
    <sch:let name="site8-count" value="string-length(normalize-space(t:structure/t:sublattices/t:site[8]/@constituents)) - string-length(translate(normalize-space(t:structure/t:sublattices/t:site[8]/@constituents), ' ', '')) + number(boolean(t:structure/t:sublattices/t:site[8]))"/>
    <sch:let name="expected-endmember-count" value="
      ($site-count = 1) * $site1-count +
      ($site-count = 2) * ($site1-count * $site2-count) +
      ($site-count = 3) * ($site1-count * $site2-count * $site3-count) +
      ($site-count = 4) * ($site1-count * $site2-count * $site3-count * $site4-count) +
      ($site-count = 5) * ($site1-count * $site2-count * $site3-count * $site4-count * $site5-count) +
      ($site-count = 6) * ($site1-count * $site2-count * $site3-count * $site4-count * $site5-count * $site6-count) +
      ($site-count = 7) * ($site1-count * $site2-count * $site3-count * $site4-count * $site5-count * $site6-count * $site7-count) +
      ($site-count = 8) * ($site1-count * $site2-count * $site3-count * $site4-count * $site5-count * $site6-count * $site7-count * $site8-count)
    "/>

    <sch:assert
        id="VAL-ERR-CEF-ENDMEMBER-CARTESIAN-COUNT-MISMATCH"
        role="error"
        test="$actual-endmember-count = $expected-endmember-count">
      CEF phase <sch:value-of select="@name"/> declares <sch:value-of select="$site-count"/> sublattices; the constituent lists imply <sch:value-of select="$expected-endmember-count"/> endmembers, but found <sch:value-of select="$actual-endmember-count"/>.
    </sch:assert>
  </sch:rule>
</sch:pattern>