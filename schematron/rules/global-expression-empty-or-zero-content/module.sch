<?xml version="1.0" encoding="UTF-8"?>
<sch:pattern xmlns:sch="http://purl.oclc.org/dsdl/schematron" id="thermml-global-expression-empty-or-zero-content">
  <sch:title>Global expression content that is empty or zero</sch:title>

  <sch:rule context="t:database/t:globalExpressions/t:expression[@xsi:type='RangedTemperatureExpr' or @xsi:type='FunctionTypeExpr']/t:range | t:database/t:globalExpressions/t:expression/t:tdb | t:database/t:globalExpressions/t:expression/t:chemsage">
    <sch:report
        id="VAL-WARN-GLOBAL-EXPRESSION-EMPTY-OR-ZERO-CONTENT"
        role="warning"
        test="normalize-space(.) = '' or (string(number(normalize-space(.))) != 'NaN' and number(normalize-space(.)) = 0)">
      Global expression <sch:value-of select="ancestor::t:expression[1]/@name"/> has content in <sch:value-of select="local-name()"/> that is empty or a numeric zero literal, which may indicate a missing or null function body.
    </sch:report>
  </sch:rule>
</sch:pattern>