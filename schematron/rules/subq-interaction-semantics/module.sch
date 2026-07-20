<?xml version="1.0" encoding="UTF-8"?>
<sch:pattern xmlns:sch="http://purl.oclc.org/dsdl/schematron" id="thermml-subq-interaction-semantics">
  <sch:title>SUBQ interaction and interpolation semantics</sch:title>

  <sch:rule context="t:database//t:phase[@xsi:type = 'ModifiedQuasichemicalPhaseType']//t:interaction/t:property[t:selected]">
    <sch:assert
        id="VAL-ERR-SUBQ-SELECTED-PROPERTY-TYPE"
        role="error"
        test="@xsi:type = 'MQM-L-PF' or @xsi:type = 'MQM-L-SP' or @xsi:type = 'MQM-L-Quasichemical' or @xsi:type = 'MQM-L-Q' or @xsi:type = 'MQM-L-RK'">
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
        test="not(@xsi:type = 'MQM-L-PF' or @xsi:type = 'MQM-L-SP' or @xsi:type = 'MQM-L-Quasichemical' or @xsi:type = 'MQM-L-Q') or not(t:expr[not(@k) or number(@k) &lt; 1])">
      A selected PF, SP, or Quasichemical property requires explicit k greater than or equal to one on every expression.
    </sch:assert>
  </sch:rule>

  <sch:rule context="t:database//t:phase[@xsi:type = 'ModifiedQuasichemicalPhaseType']//t:interaction/t:property[@xsi:type = 'MQM-L-RM' or @xsi:type = 'MQM-L-RS' or @xsi:type = 'MQM-L-RC' or @xsi:type = 'MQM-L-Reciprocal']">
    <sch:assert
        id="VAL-ERR-SUBQ-RECIPROCAL-CARDINALITY"
        role="error"
        test="count(../t:constituents/t:site) = 2 and count(../t:constituents/t:site[count(t:const) = 2]) = 2">
      Reciprocal properties require exactly two constituents on each of two sites.
    </sch:assert>
  </sch:rule>

  <sch:rule context="t:database//t:phase[@xsi:type = 'ModifiedQuasichemicalPhaseType']/t:ternaryInterpolations/t:interpolation">
    <sch:assert
        id="VAL-ERR-SUBQ-INTERPOLATION-LABELS"
        role="error"
        test="count(t:constituents/t:site) = 2 and count(t:constituents/t:site[count(t:const) = 3 and count(t:const[@site]) = 3]) = 1 and count(t:constituents/t:site[count(t:const) = 1 and not(t:const/@site)]) = 1 and count(t:constituents/t:site/t:const[@site = 'i']) = 1 and count(t:constituents/t:site/t:const[@site = 'j']) = 1 and count(t:constituents/t:site/t:const[@site = 'k']) = 1">
      A ternary interpolation requires one three-constituent site labeled exactly once with i, j, and k, plus one unlabeled fixed site.
    </sch:assert>
  </sch:rule>
</sch:pattern>
