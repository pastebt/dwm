
import re
import sys
import cgi
from itertools import chain
from gettext import gettext
try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser

from comm import echo


"""
.class              .intro
    Selects all elements with class="intro"
#id                 #firstname
    Selects the element with id="firstname"
element             p
    Selects all <p> elements
element,element     div,p
    Selects all <div> elements and all <p> elements
element element     div p
    Selects all <p> elements inside <div> elements
element>element     div>p
    Selects all <p> elements where the parent is a <div> element
:first-child        p:first-child
    Selects every <p> element that is the first child of its parent
:enabled            input:enabled
    Selects every enabled <input> element
:disabled           input:disabled
    Selects every disabled <input> element
:checked            input:checked
    Selects every checked <input> element
[attribute]         [target]
    Selects all elements with a target attribute
[attribute=value]   [target=_blank]
    Selects all elements with target="_blank"
[attribute^=value]  a[src^="https"]
    Selects every <a> element whose src attribute value begins with "https"
[attribute$=value]  a[src$=".pdf"]
    Selects every <a> element whose src attribute value ends with ".pdf"
[attribute*=value]  a[src*="w3schools"]
    Selects every <a> element whose src attribute value contains the
    substring "w3schools"
"""

"""
elm has "class", "tag", "id", "attrs"
elm has fedc
"""


def select_fedc(elm, sel):
    if sel == 'first-child':
        return elm.parent and elm.parent.children[0] == elm
    if elm.tag != 'input':
        return False
    if sel == 'enabled':
        return 'enabled' in elm or 'disabled' not in elm
    if sel == 'disabled':
        return 'disabled' in elm
    if sel == 'checked':
        if elm.get('type', 'text').lower() in ("checkbox", "radio"):
            return 'checked' in elm
    return False


def select_one(act, sel, elms):
    #if sel == ' ':      # space, all descendant elements
    if len(sel) > 0 and len(sel.strip()) == 0:
        return (c for e in elms for c in e.descendants)
    if sel.strip() == '>':      # children
        return (c for e in elms for c in e.children)

    if act == '':
        #return (e for e in elms if e.tag == sel)
        return (e for e in elms if e.tag in sel.split(',')) # this will keep order
    if act == '.':
        #return (e for e in elms if e.get('class') == sel)
        return (e for e in elms if sel in e.get('class', '').split())
    if act == '#':
        return (e for e in elms if e.get('id') == sel)
    if act == '[' and sel[-1] == ']':
        dat = sel[:-1].split('=', 1)
        if len(dat) == 1:
            return (e for e in elms if dat[0] in e)
        nm, value = dat
        if value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        name = nm[:-1]
        if nm[-1] == '^':
            return (e for e in elms for n, v in e
                    if name == n and v and v.startswith(value))
        if nm[-1] == '*':
            return (e for e in elms for n, v in e
                    if name == n and v and value in v)
        if nm[-1] == '$':
            return (e for e in elms for n, v in e
                    if name == n and v and v.endswith(value))
        return (e for e in elms for n, v in e
                if nm == n and value == v)
    if act == ':':
        return (e for e in elms if select_fedc(e, sel))

    raise Exception("bad format, act=[%s], sel=[%s]" % (act, sel))


def select(sel, get_elems):
    # because we should support "element,element",
    # source elements should reset, and we are using iter-list,
    # so we should use function who will give a iter as return
    ##sels = re.split("([\.\#\[\: ,\>])", sel)
    sel = ",".join(re.split("\s*,\s*", sel))
    sels = re.split("([\.\#\[\:]|\s*\>\s*| +)", sel)
    #sels = re.split("([\.\#\[\:]|\s*,\s*|\s*\>\s*| +)", sel)
    ##sels = re.split("([\.\#\:]|\s*,\s*|\s*\>\s*|\[.+\]|\s+)", sel)
    #print sels
    es = get_elems()
    act = sel = ''
    ret = []
    for s in sels:
        if not s:   # s may == ''
            act = ''
            continue
        if s in ".#[":
            act = s
            continue
        if s == ':':
            if act == '[':
                # handle a[_stat="videolist:click"]
                sel = sel + s
                continue
            else:
                act = s
        if act == '[' and s[-1] != ']':
            # handle "a[name='a b']"
            sel = sel + s
            continue
        es = select_one(act, sel + s, es)
        #print 'act = [%s], s = [%s]' % (act, s)
        act = sel = ''
    ret.append(es)
    return [y for y in chain(*ret)]


class Node(object):
    def __init__(self, parent):
        self.parent = p = parent
        self.children = []
        # don't use index, otherwise you have to maintain it when del
        #self.index = 0      # index in parent children
        self.tag = ''
        self.attrs_dict = {}
        if p:
            p.children.append(self)

    @property
    def descendants(self):
        return self.get_descendants()

    def get_descendants(self):
        for c in self.children:
            yield c
            for y in c.descendants:
                yield y

    def get(self, key, default=None):
        return self.attrs_dict.get(key, default)

    def select(self, sel):
        return select(sel, self.get_descendants)

    def show(self):
        # this works like root node
        return (y for c in self.children for y in c.show())

    @property
    def text(self):     # follow BeautifulSoup use 'text'
        return "".join(y for c in self.children for y in c.show(textonly=True))

    def __str__(self):
        return "".join(self.show())

    def __call__(self, sel):
        return self.select(sel)

    def __iter__(self):
        return self.attrs_dict.iteritems()

    def gettext_helper(self):
        return (y for c in self.children for y in c.gettext_helper())


class DataNode(Node):
    def __init__(self, parent, data):
        if parent.children and isinstance(parent.children[-1], DataNode):
            parent.children[-1].append(data)
        else:
            Node.__init__(self, parent)
            self.data = data

    def append(self, data):
        self.data += data

    def show(self, textonly=False):
        yield self.data

    def gettext_show(self):
        yield gettext(self.data)

    def gettext_helper(self):
        yield '_("""' + self.data + '""")\n'


class TagNode(Node):
    def __init__(self, parent, tag, attrs, raw_text=None):
        Node.__init__(self, parent)
        self.tag = tag
        self.attrs_dict = dict(attrs)
        self.raw_text = raw_text

    def __getitem__(self, key):
        return self.attrs_dict[key]

    def __setitem__(self, key, value):
        self.attrs_dict[key] = value
        self.raw_text = None

    def __delitem__(self, key):
        if key in self.attrs_dict:
            del self.attrs_dict[key]
            self.raw_text = None

    def __contains__(self, key):
        return key in self.attrs_dict

    def set_inner_text(self, text):
        del self.children[::]
        self.children = [DataNode(self, cgi.escape(text))]

    def show(self, textonly=False):
        if not textonly:
            if self.raw_text and (not self.children 
                                  or self.raw_text[-2] != '/'):
                yield self.raw_text
                if self.raw_text[-2] == '/':
                    return
            else:
                yield "<%s" % self.tag
                for n, v in self:
                    yield ' %s="%s"' % (n, cgi.escape(v))
                yield ">"
        for c in self.children:
            for y in c.show(textonly):
                yield y
        if not textonly:
            yield "</%s>" % self.tag


class CommNode(Node):
    def __init__(self, parent, comm):
        Node.__init__(self, parent)
        self.comm = comm

    def show(self, textonly=False):
        yield "<!--%s-->" % self.comm if not textonly else ""


class DeclNode(Node):
    def __init__(self, parent, decl):
        Node.__init__(self, parent)
        self.decl = decl

    def show(self, textonly=False):
        yield "<!%s>" % self.decl if not textonly else ""


class PiNode(Node):
    def __init__(self, parent, pi):
        Node.__init__(self, parent)
        self.pi = pi

    def show(self, textonly=False):
        yield "<?%s>" % self.pi if not textonly else ""


class MyHtmlParser(HTMLParser):
    def __init__(self, fin=None, tidy=True):
        HTMLParser.__init__(self)
        if tidy:
            self.handle_endtag = self._handle_endtag_tidy
        else:
            self.handle_endtag = self._handle_endtag
        self.root_node = self.now_node = Node(None)

        #if filename:
        #    with open(filename) as fin:
        #        self.feed(fin.read().decode('utf8', 'ignore'))
        if hasattr(fin, 'read'):
            self.feed(fin.read().decode('utf8', 'ignore'))

    def handle_starttag(self, tag, attrs):
        #print "start:", tag, attrs
        self.now_node = TagNode(self.now_node, tag, attrs,
                                self.get_starttag_text())

    def _handle_endtag(self, tag):
        ns = self.now_node
        while isinstance(self.now_node, TagNode):
            n = self.now_node
            self.now_node = self.now_node.parent
            if n.tag == tag:
                return
        self.now_node = ns

    def _handle_endtag_tidy(self, tag):
        #print "end:", tag
        if isinstance(self.now_node, TagNode) and self.now_node.tag == tag:
            self.now_node = self.now_node.parent
            return
        #print "now_node.tag = [%s]" % self.now_node.tag
        #print str(self.now_node)
        raise Exception("tag pair miss match: %s %s" % (
                         self.now_node.tag, tag))

    def handle_data(self, data):
        #print "data:", data
        #if isinstance(self.now_node.last_child, DataNode):
        #    self.now_node.last_child.append(data)
        #else:
        DataNode(self.now_node, data)

    def handle_entityref(self, name):
        self.handle_data("&%s;" % name)

    def handle_charref(self, name):
        self.handle_data("&#%s;" % name)

    def handle_comment(self, data):
        #print "data: <!--%s-->" % data
        CommNode(self.now_node, data)

    def handle_decl(self, decl):
        #print "data: <!%s>" % decl
        DeclNode(self.now_node, decl)

    def handle_pi(self, data):
        #print "data: <?%s>" % decl
        PiNode(self.now_node, data)

    def unknown_decl(self, data):
        #print "data: <!%s>" % data
        DeclNode(self.now_node, data)

    def select(self, sel):
        return select(sel, self.root_node.get_descendants)


def MyBS(fin):
    mp = MyHtmlParser(tidy=False)
    mp.feed(fin.read().decode('utf8', 'ignore'))
    return mp.root_node


def SelStr(sel, data):
    mp = MyHtmlParser(tidy=False)
    mp.feed(data)
    return mp.select(sel)


#mp = MyHtmlParser()
#mp.feed("""<html><head></head><body>
#           <a a='1'  b='2'>12&gt;</ a></body></html>""")
#
#print str(mp.root_node)
##print "".join(mp.root_node.show())
##print [x for x in mp.root_node.children()]
##print "".join(mp.root_node.first_child.show())
#
##print str(next(select("a", mp.root_node.descendants())))
#ns = select("a", mp.root_node.descendants())
#print map(str, ns)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        echo('Usage: ', sys.argv[0], 'selector html_file')
        sys.exit(1)

    html = open(sys.argv[2]).read().decode('utf8', 'ignore')
    mp = MyHtmlParser(tidy=False)
    mp.feed(html)
    nodes = mp.select(sys.argv[1])
    echo(nodes)
    for n in nodes:
        echo(n.tag, n.text.strip())

