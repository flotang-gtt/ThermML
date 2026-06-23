<?xml version="1.0" encoding="UTF-8"?>
<sch:pattern xmlns:sch="http://purl.oclc.org/dsdl/schematron" id="thermml-cef-magnetic-consistency">
  <sch:title>CEF magnetic structure and parameter consistency</sch:title>

  <!--
    Cross-checks the two places magnetic information lives in a CEF phase:
      - a magnetic model in the phase <structure> (the <magnetic> element), and
      - magnetic parameters (xsi:type 'M' on endmembers, 'BML'/'TCL' on
        interactions).
    If one side is present without the other, the phase description is most
    likely incomplete, so each direction emits a warning.

    Scope is intentionally limited to xsi:type='CEFPhaseType', mirroring the
    cef-endmember-cartesian-count family. Ordered phases (CEFOrderedPhaseType)
    routinely inherit a magnetic model from their parent disordered phase while
    declaring no magnetic parameters of their own, so including them here would
    raise false positives.
  -->

  <sch:rule context="t:database//t:phase[@xsi:type='CEFPhaseType']">
    <sch:let name="has-magnetic-structure" value="boolean(t:structure/t:magnetic)"/>
    <sch:let name="magnetic-parameter-count" value="count(.//t:property[@xsi:type='M' or @xsi:type='BML' or @xsi:type='TCL'])"/>

    <sch:report
        id="VAL-WARN-CEF-MAGNETIC-STRUCTURE-WITHOUT-PARAMETERS"
        role="warning"
        test="$has-magnetic-structure and $magnetic-parameter-count = 0">
      CEF phase <sch:value-of select="@name"/> declares a magnetic model in its structure, but no endmember or interaction carries magnetic parameters (xsi:type M, BML, or TCL). Verify that the magnetic data is intentionally omitted.
    </sch:report>

    <sch:report
        id="VAL-WARN-CEF-MAGNETIC-PARAMETERS-WITHOUT-STRUCTURE"
        role="warning"
        test="$magnetic-parameter-count &gt; 0 and not($has-magnetic-structure)">
      CEF phase <sch:value-of select="@name"/> carries <sch:value-of select="$magnetic-parameter-count"/> magnetic parameter(s) (xsi:type M, BML, or TCL), but its structure declares no magnetic model. Add a magnetic model to the phase structure.
    </sch:report>
  </sch:rule>
</sch:pattern>
