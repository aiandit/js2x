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


  <xsl:template name="replace">
    <xsl:param name="str"/>
    <xsl:param name="match" select="'abc'"/>
    <xsl:param name="repl" select="'xyz'"/>
    <xsl:choose>
      <xsl:when test="string-length($str) > 0 and contains($str, $match)">
        <xsl:variable name="nstr" select="substring-after($str, $match)"/>
        <xsl:variable name="bef" select="substring-before($str, $match)"/>
        <xsl:value-of select="$bef"/>
        <xsl:value-of select="$repl"/>
        <xsl:call-template name="replace">
          <xsl:with-param name="str" select="$nstr"/>
          <xsl:with-param name="match" select="$match"/>
          <xsl:with-param name="repl" select="$repl"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$str"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="escape-json">
    <xsl:param name="str"/>
    <xsl:call-template name="replace">
      <xsl:with-param name="str">
        <xsl:call-template name="replace">
          <xsl:with-param name="str">
            <xsl:call-template name="replace">
              <xsl:with-param name="str">
                <xsl:call-template name="replace">
                  <xsl:with-param name="str" select="$str"/>
                  <xsl:with-param name="match" select="'&#x9;'"/>
                  <xsl:with-param name="repl" select="'\t'"/>
                </xsl:call-template>
              </xsl:with-param>
              <xsl:with-param name="match">"</xsl:with-param>
              <xsl:with-param name="repl">\"</xsl:with-param>
            </xsl:call-template>
          </xsl:with-param>
          <xsl:with-param name="match" select="'&#xd;'"/>
          <xsl:with-param name="repl" select="'\r'"/>
        </xsl:call-template>
      </xsl:with-param>
      <xsl:with-param name="match" select="'&#xa;'"/>
      <xsl:with-param name="repl" select="'\n'"/>
    </xsl:call-template>
  </xsl:template>


  <xsl:template match="/">
    <xsl:apply-templates select="*" mode="top"/>
  </xsl:template>

  <xsl:template match="*" mode="top">
    <xsl:text>{</xsl:text>
    <xsl:apply-templates select="."/>
    <xsl:apply-templates select=".." mode="indent"/>
    <xsl:text>}</xsl:text>
  </xsl:template>

  <xsl:template match="num|str" mode="top">
    <xsl:apply-templates select="."/>
    <xsl:apply-templates select=".." mode="indent"/>
  </xsl:template>


  <xsl:template match="*">
    <xsl:apply-templates select="." mode="indent"/>
    <xsl:text>"</xsl:text>
    <xsl:value-of select="local-name()"/>
    <xsl:text>":</xsl:text>
    <xsl:value-of select="$spacer"/>
    <xsl:choose>
      <xsl:when test="text()">
        <xsl:text>"</xsl:text>
        <xsl:call-template name="escape-json">
          <xsl:with-param name="str" select="."/>
        </xsl:call-template>
        <xsl:text>"</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>{}</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
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

  <xsl:template match="text()" mode="in-list"/>

  <xsl:template match="item" mode="in-list">
    <xsl:apply-templates select="*" mode="in-list"/>
  </xsl:template>

  <xsl:template match="*[* or @_class]" mode="in-list">
    <xsl:text>{</xsl:text>
    <xsl:apply-templates select="*"/>
    <xsl:apply-templates select="." mode="indent"/>
    <xsl:text>}</xsl:text>
  </xsl:template>

  <xsl:template match="item[not(*)]" mode="in-list">
    <xsl:text>{}</xsl:text>
  </xsl:template>

  <xsl:template match="*" mode="in-list">
    <xsl:apply-templates select="."/>
  </xsl:template>

  <xsl:template match="*[str|num and count(*) = 1]" mode="in-list">
    <xsl:apply-templates select="*"/>
  </xsl:template>

  <xsl:template match="*[str|num and count(*) = 1]">
    <xsl:apply-templates select="." mode="indent"/>
    <xsl:text>"</xsl:text>
    <xsl:value-of select="local-name()"/>
    <xsl:text>":</xsl:text>
    <xsl:value-of select="$spacer"/>
    <xsl:apply-templates select="*"/>
    <xsl:if test="count(following-sibling::*) > 0">
      <xsl:text>,</xsl:text>
      <xsl:value-of select="$spacer"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="str[count(../*)=1]">
    <xsl:text>"</xsl:text>
    <xsl:call-template name="escape-json">
      <xsl:with-param name="str" select="."/>
    </xsl:call-template>
    <xsl:text>"</xsl:text>
  </xsl:template>

  <xsl:template match="num[count(../*)=1]">
    <xsl:value-of select="."/>
  </xsl:template>

  <xsl:template match="*[@_class = 'list']">
    <xsl:apply-templates select="." mode="indent"/>
    <xsl:text>"</xsl:text>
    <xsl:value-of select="local-name()"/>
    <xsl:text>":</xsl:text>
    <xsl:value-of select="$spacer"/>
    <xsl:text>[</xsl:text>
    <xsl:for-each select="*">
      <xsl:apply-templates select="." mode="in-list"/>
      <xsl:if test="position() != last()">
        <xsl:text>,</xsl:text>
        <xsl:value-of select="$spacer"/>
      </xsl:if>
    </xsl:for-each>
    <xsl:text>]</xsl:text>
  </xsl:template>

</xsl:stylesheet>
