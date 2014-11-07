from pixie.vm.code import as_var, affirm, extend
from pixie.vm.object import Object, Type
from pixie.vm.string import String
from pixie.vm.primitives import nil
import pixie.vm.stdlib as proto
import pixie.vm.rt as rt

import rpython.rlib.rsre.rsre_re as rpy_re

class Regex(Object):
    _type = Type(u"pixie.stdlib.Regex")
    _immutable_fields_ = ["_str", "_regex"]

    def __init__(self, s):
        assert isinstance(s, String)

        self._str = s._str
        self._regex = rpy_re.compile(self._str)

    def type(self):
        return self._type

@extend(proto._str, Regex)
def _str(re):
    assert(isinstance(re, Regex))
    return rt.wrap("#\"" + re._str + "\"")

def groups_as_vector(gs):
    v = rt.vector()
    for g in gs:
        v = rt.conj(v, rt.wrap(unicode(g)))
    return v

class RegexMatcher(Object):
    _type = Type(u"pixie.stdlib.RegexMatcher")

    def __init__(self, re, s):
        self._regex = re._regex
        self._str = s._str
        self._pos = 0

    def find_next(self):
        m = self._regex.search(self._str, self._pos)
        if m is None:
            return nil
        self._pos = m.end()
        return groups_as_vector(m.groups())

    def type(self):
        return self._type

@as_var("re-pattern")
def re_pattern(s):
    affirm(isinstance(s, String), u"can only construct a regex from a string")

    return Regex(s)

@as_var("re-matcher")
def re_matcher(re, s):
    affirm(isinstance(re, Regex), u"First argument must be a regex")
    affirm(isinstance(s, String), u"Second argument must be a string")
    return RegexMatcher(re, s)

# re-groups

@as_var("re-matches")
def re_matches(re, s):
    return rt.re_matcher(re, s).find_next()

@as_var("re-find")
def re_find(m):
    affirm(isinstance(m, RegexMatcher), u"First argument must be a regex matcher")
    return m.find_next()
