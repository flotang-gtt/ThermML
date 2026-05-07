<?xml version="1.0" encoding="UTF-8"?>
<sch:pattern xmlns:sch="http://purl.oclc.org/dsdl/schematron" id="thermml-rk-rank">
  <sch:title>Redlich-Kister rank diagnostics</sch:title>

  <sch:rule context="t:database//t:interaction/t:property[@xsi:type='L']/t:expr[@rank]">
    <sch:assert
        id="VAL-ERR-RK-RANK-INVALID"
        role="error"
        test="normalize-space(@rank) != '' and string(number(@rank)) != 'NaN' and not(contains(normalize-space(@rank), '.')) and not(contains(normalize-space(@rank), 'e')) and not(contains(normalize-space(@rank), 'E')) and number(@rank) &gt;= 0">
      Redlich-Kister expr rank must be a non-negative integer such as 0, 1, or 2. Found rank=<sch:value-of select="@rank"/> in phase <sch:value-of select="ancestor::t:phase[1]/@name"/> for interaction <sch:value-of select="ancestor::t:interaction[1]/@name"/>.
    </sch:assert>

    <sch:report
        id="VAL-WARN-RK-HIGH-RANK"
        role="warning"
        test="normalize-space(@rank) != '' and string(number(@rank)) != 'NaN' and not(contains(normalize-space(@rank), '.')) and not(contains(normalize-space(@rank), 'e')) and not(contains(normalize-space(@rank), 'E')) and number(@rank) &gt; 2">
      Redlich-Kister expr rank <sch:value-of select="@rank"/> in phase <sch:value-of select="ancestor::t:phase[1]/@name"/> for interaction <sch:value-of select="ancestor::t:interaction[1]/@name"/> is valid but suspicious because ranks above 2 should be reviewed.
    </sch:report>

    <sch:report
        id="VAL-WARN-RK-RANK-GAPS"
        role="warning"
        test="normalize-space(@rank) != '' and string(number(@rank)) != 'NaN' and not(contains(normalize-space(@rank), '.')) and not(contains(normalize-space(@rank), 'e')) and not(contains(normalize-space(@rank), 'E')) and number(@rank) &gt; 0 and not(../t:expr[number(@rank) = number(current()/@rank) - 1])">
      Redlich-Kister expr rank <sch:value-of select="@rank"/> in phase <sch:value-of select="ancestor::t:phase[1]/@name"/> for interaction <sch:value-of select="ancestor::t:interaction[1]/@name"/> is suspicious because a lower rank is missing in this interaction property.
    </sch:report>
  </sch:rule>
</sch:pattern>