from lark import Lark

parser = Lark.open("grammar.lark", rel_to=__file__, start="start")