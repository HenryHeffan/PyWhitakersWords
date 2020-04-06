# -*- coding: utf-8 -*-

# import os
# import sys
# import base64
# import enum
# import io
# import re
# import time
# import low_memory_stems.fast_dict_keys
# low_memory_stems.fast_dict_keys.get_lib()
# if __name__ == "__main__":
#
#     PATH = os.path.dirname(os.path.abspath(__file__))
#     sys.path.insert(0, PATH)
#     print(PATH)
#
#     import os
#     import sys
#
#     sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
#     from strip_hints import strip_on_import
#
#     strip_on_import(__file__, to_empty=False, no_ast=False, no_colon_move=False,
#                     only_assigns_and_defs=False, py3_also=False)
#
#     # import test
#     import searcher
# else:

# print(os.path.dirname(os.path.realpath(__file__)))
# from strip_hints import strip_on_import
# strip_on_import(__file__, to_empty=False, no_ast=False, no_colon_move=False,
#                 only_assigns_and_defs=False, py3_also=False)

# from utils import *
# for file in os.listdir(PATH):
#     if os.path.isfile(file) and os.path.splitext(file)[1] == ".py":
#         strip_on_import(os.path.join(PATH, file), to_empty=False, no_ast=False, no_colon_move=False,
#                         only_assigns_and_defs=False, py3_also=False)

# from . import PATH
# def run():
from core_files.searcher import get_matches

import core_files.whitakers_words as ww
import core_files.joined_formater_html as jd
PATH="/home/henry/Desktop/PyWhitakersWords/"

print("LOADING", PATH)
J_LEX, J_FORM = jd.init(PATH)
print("LOADED JOINED")
WW_LEX, WW_FORM = ww.init(PATH)
print("LOADED WW")

for word in ["hi", "a", "qui", "quicumque", "quibus", "praecanto", ""]:
    J_FORM.display_entry_query(get_matches(J_LEX, word))
    WW_FORM.display_entry_query(get_matches(WW_LEX, word))

print(WW_FORM.display_entry_query(get_matches(WW_LEX, "qui")))
# print(WW_FORM.display_entry_query(get_matches(WW_LEX, "quae")))
# print(WW_FORM.display_entry_query(get_matches(WW_LEX, "quod")))
