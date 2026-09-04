<?xml version="1.0" encoding="UTF-8"?>
<sch:pattern xmlns:sch="http://purl.oclc.org/dsdl/schematron" id="thermml-expression-range-consistency">
  <sch:title>Expression range bounds, order and overlap</sch:title>
  <!-- Applies to inline and global expressions, including H-S-Cp ranges.
       Positive-width intervals are [low, high). Zero-width records and gaps
       are allowed; all records are sorted by nondecreasing lower bound. -->
  <sch:rule context="t:database//t:range[@low and @high]">
    <sch:let name="low" value="number(@low)"/>
    <sch:let name="high" value="number(@high)"/>
    <sch:assert id="VAL-ERR-EXPRESSION-RANGE-BOUNDS" role="error"
        test="$low &lt;= $high">
      Range lower bound <sch:value-of select="@low"/> must not exceed upper bound <sch:value-of select="@high"/>.
    </sch:assert>
    <sch:assert id="VAL-ERR-EXPRESSION-RANGE-ORDER" role="error"
        test="not(preceding-sibling::t:range[number(@low) &gt; $low])">
      Expression ranges must be listed in nondecreasing order of lower bound.
    </sch:assert>
    <sch:assert id="VAL-ERR-EXPRESSION-RANGE-OVERLAP" role="error"
        test="$low &gt;= $high or not(preceding-sibling::t:range[number(@low) &lt; number(@high) and number(@low) &lt; $high and number(@high) &gt; $low])">
      Positive-width expression ranges must not overlap. Shared boundaries and zero-width records are allowed.
    </sch:assert>
  </sch:rule>
</sch:pattern>
