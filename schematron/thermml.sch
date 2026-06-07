<?xml version="1.0" encoding="UTF-8"?>
<sch:schema
    xmlns:sch="http://purl.oclc.org/dsdl/schematron"
    xmlns:t="http://calphad.org/thermml/0.1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    queryBinding="xslt">

  <sch:title>ThermML Schematron Sample Rule Set</sch:title>

  <sch:ns prefix="t" uri="http://calphad.org/thermml/0.1"/>
  <sch:ns prefix="xsi" uri="http://www.w3.org/2001/XMLSchema-instance"/>

  <sch:include href="rules/ternary-interpolation-locator-aliases/module.sch"/>
  <sch:include href="rules/redlich-kister-rank/module.sch"/>
  <sch:include href="rules/cef-endmember-cartesian-count/module.sch"/>
  <sch:include href="rules/global-expression-empty-or-zero-content/module.sch"/>
  <sch:include href="rules/species-duplicate-stoichiometry/module.sch"/>
  <sch:include href="rules/endmember-duplicate-constituents/module.sch"/>
  <sch:include href="rules/endmember-constituent-site-count/module.sch"/>
</sch:schema>