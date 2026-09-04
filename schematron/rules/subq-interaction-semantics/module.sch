<?xml version="1.0" encoding="UTF-8"?>
<sch:pattern xmlns:sch="http://purl.oclc.org/dsdl/schematron" id="thermml-subq-interaction-semantics">
  <sch:title>SUBQ interaction and interpolation semantics</sch:title>

  <sch:rule context="t:database//t:phase[((normalize-space(@xsi:type) = 'ModifiedQuasichemicalPhaseType' or substring-after(normalize-space(@xsi:type), ':') = 'ModifiedQuasichemicalPhaseType') and namespace::*[name() = substring-before(normalize-space(../@xsi:type), ':')] = 'http://calphad.org/thermml/v0')]//t:interaction/t:property[t:selected]">
    <sch:assert
        id="VAL-ERR-SUBQ-SELECTED-PROPERTY-TYPE"
        role="error"
        test="((normalize-space(@xsi:type) = 'MQM-L-PF' or substring-after(normalize-space(@xsi:type), ':') = 'MQM-L-PF') and namespace::*[name() = substring-before(normalize-space(../@xsi:type), ':')] = 'http://calphad.org/thermml/v0') or ((normalize-space(@xsi:type) = 'MQM-L-SP' or substring-after(normalize-space(@xsi:type), ':') = 'MQM-L-SP') and namespace::*[name() = substring-before(normalize-space(../@xsi:type), ':')] = 'http://calphad.org/thermml/v0') or ((normalize-space(@xsi:type) = 'MQM-L-Quasichemical' or substring-after(normalize-space(@xsi:type), ':') = 'MQM-L-Quasichemical') and namespace::*[name() = substring-before(normalize-space(../@xsi:type), ':')] = 'http://calphad.org/thermml/v0') or ((normalize-space(@xsi:type) = 'MQM-L-Q' or substring-after(normalize-space(@xsi:type), ':') = 'MQM-L-Q') and namespace::*[name() = substring-before(normalize-space(../@xsi:type), ':')] = 'http://calphad.org/thermml/v0') or ((normalize-space(@xsi:type) = 'MQM-L-RK' or substring-after(normalize-space(@xsi:type), ':') = 'MQM-L-RK') and namespace::*[name() = substring-before(normalize-space(../@xsi:type), ':')] = 'http://calphad.org/thermml/v0')">
      selected is valid only for PF, SP, Quasichemical, and RK SUBQ properties.
    </sch:assert>
    <sch:assert
        id="VAL-ERR-SUBQ-SELECTED-CONSTITUENT"
        role="error"
        test="t:selected = ../t:constituents/t:site/t:const/@species">
      selected must name a constituent of its interaction.
    </sch:assert>
    <sch:assert
        id="VAL-ERR-SUBQ-SELECTED-TERNARY-SITE"
        role="error"
        test="count(../t:constituents/t:site) = 2 and count(../t:constituents/t:site[count(t:const) = 3]) = 1 and count(../t:constituents/t:site[count(t:const) = 1]) = 1">
      selected requires one three-constituent ternary site and one fixed site.
    </sch:assert>
    <sch:assert
        id="VAL-ERR-SUBQ-SELECTED-K"
        role="error"
        test="not(((normalize-space(@xsi:type) = 'MQM-L-PF' or substring-after(normalize-space(@xsi:type), ':') = 'MQM-L-PF') and namespace::*[name() = substring-before(normalize-space(../@xsi:type), ':')] = 'http://calphad.org/thermml/v0') or ((normalize-space(@xsi:type) = 'MQM-L-SP' or substring-after(normalize-space(@xsi:type), ':') = 'MQM-L-SP') and namespace::*[name() = substring-before(normalize-space(../@xsi:type), ':')] = 'http://calphad.org/thermml/v0') or ((normalize-space(@xsi:type) = 'MQM-L-Quasichemical' or substring-after(normalize-space(@xsi:type), ':') = 'MQM-L-Quasichemical') and namespace::*[name() = substring-before(normalize-space(../@xsi:type), ':')] = 'http://calphad.org/thermml/v0') or ((normalize-space(@xsi:type) = 'MQM-L-Q' or substring-after(normalize-space(@xsi:type), ':') = 'MQM-L-Q') and namespace::*[name() = substring-before(normalize-space(../@xsi:type), ':')] = 'http://calphad.org/thermml/v0')) or not(t:expr[not(@k) or number(@k) &lt; 1])">
      A selected PF, SP, or Quasichemical property requires explicit k greater than or equal to one on every expression.
    </sch:assert>
  </sch:rule>

  <sch:rule context="t:database//t:phase[((normalize-space(@xsi:type) = 'ModifiedQuasichemicalPhaseType' or substring-after(normalize-space(@xsi:type), ':') = 'ModifiedQuasichemicalPhaseType') and namespace::*[name() = substring-before(normalize-space(../@xsi:type), ':')] = 'http://calphad.org/thermml/v0')]//t:interaction/t:property[((normalize-space(@xsi:type) = 'MQM-L-RM' or substring-after(normalize-space(@xsi:type), ':') = 'MQM-L-RM') and namespace::*[name() = substring-before(normalize-space(../@xsi:type), ':')] = 'http://calphad.org/thermml/v0') or ((normalize-space(@xsi:type) = 'MQM-L-RS' or substring-after(normalize-space(@xsi:type), ':') = 'MQM-L-RS') and namespace::*[name() = substring-before(normalize-space(../@xsi:type), ':')] = 'http://calphad.org/thermml/v0') or ((normalize-space(@xsi:type) = 'MQM-L-RC' or substring-after(normalize-space(@xsi:type), ':') = 'MQM-L-RC') and namespace::*[name() = substring-before(normalize-space(../@xsi:type), ':')] = 'http://calphad.org/thermml/v0') or ((normalize-space(@xsi:type) = 'MQM-L-Reciprocal' or substring-after(normalize-space(@xsi:type), ':') = 'MQM-L-Reciprocal') and namespace::*[name() = substring-before(normalize-space(../@xsi:type), ':')] = 'http://calphad.org/thermml/v0')]">
    <sch:assert
        id="VAL-ERR-SUBQ-RECIPROCAL-CARDINALITY"
        role="error"
        test="count(../t:constituents/t:site) = 2 and count(../t:constituents/t:site[count(t:const) = 2]) = 2">
      Reciprocal properties require exactly two constituents on each of two sites.
    </sch:assert>
  </sch:rule>

  <sch:rule context="t:database//t:phase[((normalize-space(@xsi:type) = 'ModifiedQuasichemicalPhaseType' or substring-after(normalize-space(@xsi:type), ':') = 'ModifiedQuasichemicalPhaseType') and namespace::*[name() = substring-before(normalize-space(../@xsi:type), ':')] = 'http://calphad.org/thermml/v0')]/t:ternaryInterpolations/t:interpolation">
    <sch:assert
        id="VAL-ERR-SUBQ-INTERPOLATION-LABELS"
        role="error"
        test="count(t:constituents/t:site) = 2 and count(t:constituents/t:site[count(t:const) = 3 and count(t:const[@site]) = 3]) = 1 and count(t:constituents/t:site[count(t:const) = 1 and not(t:const/@site)]) = 1 and count(t:constituents/t:site/t:const[@site = 'i']) = 1 and count(t:constituents/t:site/t:const[@site = 'j']) = 1 and count(t:constituents/t:site/t:const[@site = 'k']) = 1">
      A ternary interpolation requires one three-constituent site labeled exactly once with i, j, and k, plus one unlabeled fixed site.
    </sch:assert>
  </sch:rule>
</sch:pattern>
