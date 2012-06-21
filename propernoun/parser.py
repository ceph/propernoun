from pyparsing import (
    CharsNotIn,
    Combine,
    Keyword,
    Literal,
    ParseSyntaxException,
    TokenConverter,
    Word,
    alphas,
    hexnums,
    nestedExpr,
    nums,
    quotedString,
    )


# ungroup is only available in pyparsing >=1.5.6
try:
    from pyparsing import ungroup
    _ungroup = ungroup
except ImportError:
    def _ungroup(expr):
        return TokenConverter(expr).setParseAction(lambda t: t[0])


def dictify(s, loc, toks):
    return dict(toks)

_p_ip_address = Combine(Word(nums) - ('.' + Word(nums)) * 3)

_p_lease_deleted = Literal("deleted")
_p_lease_deleted.setParseAction(lambda s, loc, toks: True)

_p_hex_digit = Word(hexnums, exact=2)
_p_mac = Combine(
    _p_hex_digit + ':' + _p_hex_digit + ':' + _p_hex_digit + ':'
    + _p_hex_digit + ':' + _p_hex_digit + ':' + _p_hex_digit)

_p_lease_hardware_ethernet = _ungroup(
    Keyword("hardware").suppress()
    + Keyword("ethernet").suppress()
    + _p_mac
    )

_p_lease_junk = (
    Word(alphas)
    # if we include { } ; here, they become greedy and eat the closing
    # brace or semicolon
    + CharsNotIn('{};')
    ).suppress()

_p_lease_decl = (
    _p_lease_deleted.setResultsName('deleted')
    | _p_lease_hardware_ethernet.setResultsName('mac')
    | _p_lease_junk
    ) + Literal(';').suppress()

_p_lease = (
    Keyword("lease").suppress()
    + _p_ip_address.setResultsName('ip')
    + _ungroup(
        nestedExpr(
            opener='{',
            closer='}',
            content=_p_lease_decl,
            ignoreExpr=quotedString,
            ),
        )
    ).setParseAction(dictify)


def parse(s):
    g = _p_lease.scanString(s)
    while True:
        try:
            (toks, start, end) = next(g)
        except StopIteration:
            break
        except ParseSyntaxException:
            # hide errors from callers; probably encountered the last,
            # partial statement while dhcpd is appending to the file;
            # stop here, inotify will wake up the caller as the next
            # chunk arrives
            break
        else:
            (tok,) = toks
            yield tok
