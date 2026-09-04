<?xml version="1.0" encoding="UTF-8"?>
<sch:pattern xmlns:sch="http://purl.oclc.org/dsdl/schematron" id="thermml-gas-endmember-consistency">
  <sch:title>Gas endmember consistency</sch:title>

  <!--
    Gas phases use CEFPhaseType as their storage shape in the current schema,
    but they are semantically distinct from compound-energy phases: a gas has
    one sublattice and may carry several named thermodynamic states for one
    constituent. Exact Cartesian equality and a blanket duplicate-array error
    are therefore inappropriate. These rules validate the gas mapping in both
    directions and use the normalized Gibbs expression to distinguish intentional
    state multiplicity from an apparent duplicate definition.
  -->

  <sch:rule context="t:database//t:phase[((normalize-space(@xsi:type) = 'CEFPhaseType' or substring-after(normalize-space(@xsi:type), ':') = 'CEFPhaseType') and namespace::*[name() = substring-before(normalize-space(../@xsi:type), ':')] = 'http://calphad.org/thermml/v0') and @state = 'gas']">
    <sch:let name="declared-constituents" value="normalize-space(t:structure/t:sublattices/t:site[1]/@constituents)"/>
    <sch:let name="declared-count" value="string-length($declared-constituents) - string-length(translate($declared-constituents, ' ', '')) + number(string-length($declared-constituents) &gt; 0)"/>
    <sch:assert
        id="VAL-ERR-CEF-GAS-STRUCTURE-CONSTITUENTS-DECLARED"
        role="error"
        test="$declared-count = count(t:species/t:specie[contains(concat(' ', $declared-constituents, ' '), concat(' ', normalize-space(@name), ' '))])">
      Gas phase <sch:value-of select="@name"/> has a structure constituent that is not declared in its species list.
    </sch:assert>
  </sch:rule>

  <sch:rule context="t:database//t:phase[((normalize-space(@xsi:type) = 'CEFPhaseType' or substring-after(normalize-space(@xsi:type), ':') = 'CEFPhaseType') and namespace::*[name() = substring-before(normalize-space(../@xsi:type), ':')] = 'http://calphad.org/thermml/v0') and @state = 'gas']/t:species/t:specie">
    <sch:let name="phase" value="ancestor::t:phase[1]"/>
    <sch:let name="species-name" value="normalize-space(@name)"/>
    <sch:let name="declared-constituents" value="normalize-space($phase/t:structure/t:sublattices/t:site[1]/@constituents)"/>
    <sch:assert
        id="VAL-ERR-CEF-GAS-ENDMEMBER-COVERAGE"
        role="error"
        test="not(contains(concat(' ', $declared-constituents, ' '), concat(' ', $species-name, ' '))) or $phase/t:endmembers/t:endmember/t:constituents/t:site/t:const/@species = $species-name">
      Gas constituent <sch:value-of select="$species-name"/> in phase <sch:value-of select="$phase/@name"/> has no endmember definition.
    </sch:assert>
  </sch:rule>

  <sch:rule context="t:database//t:phase[((normalize-space(@xsi:type) = 'CEFPhaseType' or substring-after(normalize-space(@xsi:type), ':') = 'CEFPhaseType') and namespace::*[name() = substring-before(normalize-space(../@xsi:type), ':')] = 'http://calphad.org/thermml/v0') and @state = 'gas']/t:endmembers/t:endmember">
    <sch:let name="phase" value="ancestor::t:phase[1]"/>
    <sch:let name="endmember-name" value="normalize-space(@name)"/>
    <sch:let name="species-name" value="normalize-space(t:constituents/t:site[1]/t:const[1]/@species)"/>
    <sch:let name="declared-constituents" value="normalize-space($phase/t:structure/t:sublattices/t:site[1]/@constituents)"/>
    <sch:let name="gibbs-expression" value="normalize-space(t:property[((normalize-space(@xsi:type) = 'G' or substring-after(normalize-space(@xsi:type), ':') = 'G') and namespace::*[name() = substring-before(normalize-space(../@xsi:type), ':')] = 'http://calphad.org/thermml/v0')][1]/t:expr)"/>
    <sch:let name="same-gibbs-state" value="preceding-sibling::t:endmember[normalize-space(@name) != $endmember-name and count(t:constituents/t:site) = 1 and count(t:constituents/t:site[1]/t:const) = 1 and normalize-space(t:constituents/t:site[1]/t:const[1]/@species) = $species-name and normalize-space(t:property[((normalize-space(@xsi:type) = 'G' or substring-after(normalize-space(@xsi:type), ':') = 'G') and namespace::*[name() = substring-before(normalize-space(../@xsi:type), ':')] = 'http://calphad.org/thermml/v0')][1]/t:expr) = $gibbs-expression][1]"/>
    <sch:assert
        id="VAL-ERR-CEF-GAS-ENDMEMBER-CONSTITUENT"
        role="error"
        test="count(t:constituents/t:site) = 1 and count(t:constituents/t:site[1]/t:const) = 1 and contains(concat(' ', $declared-constituents, ' '), concat(' ', $species-name, ' '))">
      Endmember <sch:value-of select="@name"/> in gas phase <sch:value-of select="$phase/@name"/> must reference exactly one declared structure constituent.
    </sch:assert>
    <sch:assert
        id="VAL-ERR-CEF-GAS-ENDMEMBER-NAME-UNIQUE"
        role="error"
        test="not(preceding-sibling::t:endmember[normalize-space(@name) = $endmember-name])">
      Gas phase <sch:value-of select="$phase/@name"/> contains more than one endmember named <sch:value-of select="@name"/>.
    </sch:assert>
    <sch:report
        id="VAL-WARN-CEF-GAS-ENDMEMBER-DUPLICATE-GIBBS"
        role="warning"
        test="$gibbs-expression != '' and $same-gibbs-state">
      Endmember <sch:value-of select="@name"/> in gas phase <sch:value-of select="$phase/@name"/> has the same constituent and Gibbs expression as differently named endmember <sch:value-of select="$same-gibbs-state/@name"/>.
    </sch:report>
  </sch:rule>
</sch:pattern>
