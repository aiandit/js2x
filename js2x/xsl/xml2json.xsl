<!--
 Transform arbitrary XML to JSON.
 (c) 2023-2025 Johannes Willkomm

 #TODO: Proper pretty printing
-->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="text"/>
  <xsl:param name="indent" select="0"/>
  <xsl:param name="indentstr" select="''"/>
  <xsl:param name="spacer" select="substring($indentstr, 1, 1)"/>

  <xsl:template match="/" mode="indentstr"/>
  <xsl:template match="*" mode="indentstr">
    <xsl:value-of select="$indentstr"/>
    <xsl:apply-templates select=".." mode="indentstr"/>
  </xsl:template>

  <xsl:template match="/" mode="indent">
    <xsl:if test="$indent">
      <xsl:text>&#xa;</xsl:text>
    </xsl:if>
  </xsl:template>

  <xsl:template match="*|@*" mode="indent">
    <xsl:if test="$indent and ..">
      <xsl:text>&#xa;</xsl:text>
      <xsl:apply-templates select="." mode="indentstr"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="/">
    <xsl:text>{</xsl:text>
    <xsl:apply-templates/>
    <xsl:apply-templates select="." mode="indent"/>
    <xsl:text>}</xsl:text>
  </xsl:template>

  <xsl:template match="*">
    <xsl:apply-templates select="." mode="indent"/>
    <xsl:text>"</xsl:text>
    <xsl:value-of select="local-name()"/>
    <xsl:text>":</xsl:text>
    <xsl:value-of select="$spacer"/>
    <xsl:text>"</xsl:text>
    <xsl:value-of select="."/>
    <xsl:text>"</xsl:text>
    <xsl:if test="count(following-sibling::*) > 0">
      <xsl:text>,</xsl:text>
      <xsl:if test="not($indent)">
        <xsl:value-of select="$spacer"/>
      </xsl:if>
    </xsl:if>
  </xsl:template>

  <xsl:template match="*[* or @_class]">
    <xsl:apply-templates select="." mode="indent"/>
    <xsl:text>"</xsl:text>
    <xsl:value-of select="local-name()"/>
    <xsl:text>":</xsl:text>
    <xsl:value-of select="$spacer"/>
    <xsl:text>{</xsl:text>
    <xsl:apply-templates select="*"/>
    <xsl:apply-templates select="." mode="indent"/>
    <xsl:text>}</xsl:text>
    <xsl:if test="@_class">
      <xsl:if test="*">
        <xsl:text>,</xsl:text>
      </xsl:if>
      <xsl:apply-templates select="." mode="indent"/>
      <xsl:text>"_class":</xsl:text>
      <xsl:value-of select="$spacer"/>
      <xsl:text>"</xsl:text>
      <xsl:value-of select="@_class"/>
      <xsl:text>"</xsl:text>
    </xsl:if>
    <xsl:if test="count(following-sibling::*) > 0">
      <xsl:text>,</xsl:text>
      <xsl:if test="not($indent)">
        <xsl:value-of select="$spacer"/>
      </xsl:if>
    </xsl:if>
  </xsl:template>

  <xsl:template match="*[str|num and count(*) = 1]">
    <xsl:apply-templates select="*"/>
  </xsl:template>

  <xsl:template match="*[@_class = 'list']">
    <xsl:apply-templates select="." mode="indent"/>
    <xsl:text>[</xsl:text>
    <xsl:for-each select="*">
      <xsl:apply-templates select="."/>
      <xsl:if test="position() != last()">
        <xsl:text>,</xsl:text>
      </xsl:if>
    </xsl:for-each>
    <xsl:text>]</xsl:text>
  </xsl:template>

</xsl:stylesheet>
