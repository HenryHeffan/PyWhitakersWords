import os
import sys

abs_pth = os.path.abspath(__file__)
PATH = os.path.split(abs_pth)[0]
PATH_UP = os.path.split(PATH)[0]
PATH += "/"
PATH_UP += "/"
sys.path.insert(0, PATH_UP)
from PyWhitakersWords.entry_and_inflections import *

from PyWhitakersWords.searcher import get_matches
from time import time
from memory_profiler import memory_usage, profile
from random import randint

@profile
def test():
    import os
    import sys

    import PyWhitakersWords.whitakers_words as ww
    import PyWhitakersWords.joined_formater_html as jd
    from PyWhitakersWords import searcher
    from PyWhitakersWords.entry_and_inflections import DictionaryLemma

    print("LOADING", PATH)
    J_LEX, J_FORM = jd.init(PATH)
    print("LOADED JOINED")
    WW_LEX, WW_FORM = ww.init(PATH)
    print("LOADED WW")



test()
# mem = max(memory_usage(proc=test))
# import sys
# print("Maximum memory used: {} MiB".format(mem))
# profile(test)

# import PyWhitakersWords.whitakers_words as ww
# WW, _ = ww.init("/home/henry/Desktop/latin_website/PyWhitakersWords/")
# print(sys.getsizeof(WW.dictionary_keys) + sum([sys.getsizeof(key) + sys.getsizeof(key.pos_data) + sys.getsizeof(key.part_of_speech) + sys.getsizeof(key.pos_data) for key in WW.dictionary_keys]),
#       sys.getsizeof(WW.dictionary_lemmata) + sum([sys.getsizeof(lem) + sys.getsizeof(lem.dictionary_keys) for lem in WW.dictionary_lemmata]))
#

