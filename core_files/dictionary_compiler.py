#!/usr/bin/python3
# - *- coding: utf- 8 - *-
import os
import sys

PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PATH)

import xml.etree.ElementTree as ET
from core_files.entry_and_inflections import *
from core_files.utils import *
from core_files.l_and_s_parser import Entry, parse_entry
from core_files import whitakers_words
from typing import Any, IO
import json
import os.path

WW_LEXICON, WW_FORMATER = whitakers_words.init(PATH, fast=False)


HTML_PREFIX_TEMP = """<!DOCTYPE html>
    <html>
    <head>
      <title>Dictionary</title>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, height=device-height, initial-scale=1">
      <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
      <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
      <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>
    <style>

    .orth {
        color: #000;
        font-weight:bold;
    }
    .itype {
        color: #000;
    }
    .gen {
        color: #000;
    }
    .pos {
        color: #000;
    }
    .etym {
        color: #304030;
    }
    .sense_block {
    }
    .sense_block_1 {
        padding-left: 10px;
    }
    .sense_block_2 {
        padding-left: 25px;
    }
    .sense_block_3 {
        padding-left: 40px;
    }
    .sense_block_4 {
        padding-left: 50px;
    }
    .sense_block_5 {
        padding-left: 60px;
    }
    .sense_heading {
        color: #000
    }
    .quote {
        color: #a09090;
    }
    .bibl {
        color: #90a090;
    }
    .foreign {
        color: #9090a0
    }
    .entryFree {
        color: #676767;
    }
    .hi_ital{
        color: #000;
    }
    </style>
    </head>
    <body>
    <h1>Lewis and Short</h1>
    <h3>Formatted by Henry Heffan</h3>
    Text provided under a CC BY-SA license by Perseus Digital Library, http://www.perseus.tufts.edu, with funding from The National Endowment for the Humanities.
<br>
Data accessed from https://github.com/PerseusDL/lexica/ [date of access].
<br>
<br>"""

# ('<', '&lt;'), # ('>', '&gt;'), #

# TODO commeneted out 'alis' line 2611
# TODO commeneted out 'quidam' lines 158038 to 158060


# THIS CODE DOES 2 THINGS
# 1) it extracts all the lewis and short entries, and classefies them according to type ==> LEWIS_SHORT.txt
# 2) it then glues the two dictionaries together ==> LSJDL.txt


def get_ls_ents():
    with open(os.path.join(PATH, 'DataFiles/lewis_and_short.xml')) as f:
        s = strip_spec_chars(f.read())


    root = ET.fromstring(s)
    text = root[1][0]
    ents = []
    for child in text:
        for ent in child:
            if ent.tag == "entryFree":
                e =  parse_entry(ent)
                if e is not None:
                    ents.append(e)
    return ents

def write_lemma_fast_cpp_format(o: IO, lemma: DictionaryLemma, only_ref_def=True):
    o.write(PartOfSpeech.str_val(lemma.part_of_speech) + " " + lemma.translation_metadata.to_str() + " "
            + str(lemma.index) + " " + str(len(lemma.dictionary_keys)))
    for key in lemma.dictionary_keys:
        o.write(" " + key.store(empty_stem="xxxxx", null_stem="zzz"))
    o.write(" ")
    o.write(lemma.definition if lemma.definition is not None else " ")
    o.write("\n")
    print(hasattr(lemma, "ent_id"), lemma.ent_id if hasattr(lemma, "ent_id") else "NO")
    o.write((lemma.ent_id if hasattr(lemma, "ent_id") else " ") if only_ref_def else
            store_utf_str(lemma.html_data if lemma.html_data is not None else ""))
    o.write("\n")

def generate_html_dic():
    l = []
    for e in ls_ents:
        l.extend(e.extract_html())
        l.append("\n")
    with open(os.path.join(PATH, "GeneratedFiles/lewis_and_short_formated.html"), "w") as o:
        o.write(HTML_PREFIX_TEMP)
        o.write("".join(l))
        o.write("""</body></html>""")



# we want to make a new dictionary file format. This will compile the old dictionary into the new one.
# This new dictionary will use 1 line to store entries from Whittickers words
# It will delimate line breaks with \n in the string. These should be replaced before displaying

# First, we will read in all the entry (above)

# then, if for any word a keyword in lewis and short exists once and a keyword

ls_ents = get_ls_ents()

# we want to glue these entries together into a DictionaryLemma
# good_ents = [ent for ent in ls_ents if ent is not None and ent.stems[0] not in {"", "-", None, "_i"}]
# good_ents.sort(key=lambda x: x.stems[0].lower())

# new_dic = list(WW_LEXICON.dictionary_list)
ENT_DIC = {}
for ent in ls_ents:
    k = (re.match(r"([a-zA-Z]*)", ent.key_word).group(1), PartOfSpeech.str_val(ent.pos))
    if k not in ENT_DIC:
        ENT_DIC[k] = []
    ENT_DIC[k].append(ent)

ND = set()
for key in WW_LEXICON.dictionary_keys:
    key.html_data = []
    k = (WW_FORMATER.dictionary_keyword(key), PartOfSpeech.str_val(key.part_of_speech))
    k2 = (WW_FORMATER.dictionary_keyword(key), PartOfSpeech.str_val(PartOfSpeech.X))
    if k in ENT_DIC:
        # assert key.html_data is None, (k, key.html_data)
        key.html_data = [ent.extract_html() for ent in ENT_DIC[k]]
        key.ent_id = [ent.id for ent in ENT_DIC[k]]
        del ENT_DIC[k]
    elif k2 in ENT_DIC:
        # assert key.html_data is None, (k2, key.lemma.html_data)
        key.html_data = [ent.extract_html() for ent in ENT_DIC[k2]]
        key.ent_id = [ent.id for ent in ENT_DIC[k2]]
        # del ENT_DIC[k2]

for lemma in WW_LEXICON.dictionary_lemmata:
    htmls = []
    ids = []
    for key in lemma.dictionary_keys:
        for html in key.html_data:
            if html not in htmls:
                htmls.append(html)
        for ent_id in (key.ent_id if hasattr(key, "ent_id") else []):
            if ent_id not in ids:
                # print(ent_id)
                ids.append(ent_id)
    # print(ids)
    lemma.html_data = "\n".join(htmls)
    lemma.ent_id = " ".join(ids)
    # print(lemma.ent_id)
    ND.add(lemma)

# Now add all the enmatched pairs. But only do this if it is NOT of type X, because those cant be conjugated
for _, ents in ENT_DIC.items():
    for ent in ents:
        if ent.pos != PartOfSpeech.X:
            ND.add(ent.make_lemma()) # (ent.header(), ent)
        else:
            pass
            # print(ent.default_keyword)


# TODO determine a better encoding (probably can save ~20 MB)


ND = list(ND)
ND.sort(key=lambda x: x.dictionary_keys[0].stems[0] if x.dictionary_keys[0].stems[0] is not None else "zzz")

for i, n in enumerate(ND):
    n.rebuild(i)

with open(os.path.join(PATH, "GeneratedFiles/JOINED.txt"), "w", encoding='utf-8') as o:
    json.dump([n.store() for n in ND], o, indent=1)

with open(os.path.join(PATH, "GeneratedFiles/JOINED_CPP_FAST.txt"), "w") as o:
    for lemma in ND:
        if lemma.part_of_speech != PartOfSpeech.X:
            write_lemma_fast_cpp_format(o, lemma)

with open(os.path.join(PATH, "GeneratedFiles/JOINED_CPP_FAST_ONLY_REF_DEF.txt"), "w") as o:
    for lemma in ND:
        if lemma.part_of_speech != PartOfSpeech.X:
            # print("REF DEF")
            write_lemma_fast_cpp_format(o, lemma, only_ref_def=True)

with open(os.path.join(PATH, "GeneratedFiles/JOINED_ONLY_REF_DEF.txt"), "w", encoding='utf-8') as o:
    json.dump([n.store(only_ref_def=True) for n in ND], o, indent=1)

with open(os.path.join(PATH, "GeneratedFiles/REF_DEF_TABLE.txt"), "w") as o:
    for ent in ls_ents:
        o.write(ent.id + " " + ("".join(ent.extract_html())))  # write_lemma_fast_cpp_format(o, lemma, only_ref_def=True)
        o.write("\n")


# with open(os.path.join(PATH, "GeneratedFiles/REF_DEF_TABLE_B64.txt"), "w") as o:
#     for ent in ls_ents:
#         o.write(ent.id + " " + store_utf_str("".join(ent.extract_html())))  # write_lemma_fast_cpp_format(o, lemma, only_ref_def=True)
#         o.write("\n")


from core_files import whitakers_words
ww, _ = whitakers_words.init(PATH, no_cache=True, fast=False)
for i, n in enumerate(ww.dictionary_lemmata):
    n.rebuild(i)
with open(os.path.join(PATH, "GeneratedFiles/DICTLINE_CPP_FAST.txt"), "w") as o:
    for lemma in ww.dictionary_lemmata:
        write_lemma_fast_cpp_format(o, lemma)

# with open(PATH + "/GeneratedFiles/JOINED_HEADERS.txt", "w", encoding='utf-8') as o:
#     json.dump([n.store(header=True) for n in ND], o, indent=1)

# TODO MAKE THESE CONNECTIONS
#  WW      L&S
#  noster binding wrong word
#  qu words
#  -que, -ve, -ne, etc.
#  Cupido & cupido CAPITAL LETTERS CAUSE BINDING ISSUES
#  ALSO STEM ADDITION HAS CAPITAL LETTER ISSUES
#  cum POS
#  ut BINDING AND INSERSION ISSUES

#  Deus, Dei NOT BINDING deus, dei
#  totus WITH totus & totus2

#  parsing of "Hippŏdămē, ēs, and Hippŏdămīa or -mēa, ae"
# contra (prep and adv)
#  'do, dare' connects to the wrong thing?


# <entryFree key="ego" type="main" id="n15326"/>
# ego                m                                                        PRON   5 1 PERS         X X X A X I, me (PERS); myself (REFLEX);

# <entryFree key="meus" type="greek" id="n28988">
# me                 me                                                       ADJ    1 1 POS          X X X A X my (personal possession); mine, of me, belonging to me; my own; to me;

# <entryFree key="tu" type="main" id="n49339"><orth lang="la" extent="full">tū</orth>
# tu                 t                                                        PRON   5 2 PERS         X X X A X you (sing.); thou/thine/thee/thy (PERS); yourself/thyself (REFLEX);

# <entryFree key="tuus" type="main" id="n49559">
# tu                 tu                                                       ADJ    1 1 POS          X X X A X your (sing.);

# ONE OF THESE, NOT SURE:
# <entryFree key="suus" type="main" id="n47174"><orth lang="la" extent="full">sŭus</orth>
# <entryFree key="sui" type="main" id="n46498"><orth lang="la" extent="full">sŭi</orth>
# su                 su                                                       ADJ    1 1 POS          X X X D X his/one's (own), her (own), hers, its (own); (pl.) their (own), theirs;


# <entryFree n="1" key="qui1" type="main" id="n40103">
# <entryFree n="2" key="qui2" type="main" id="n40104">
# <entryFree n="1" key="quis1" type="main" id="n40242">
# <entryFree n="2" key="quis2" type="main" id="n40243">

# <entryFree key="ut" type="main" id="n49975">
# ut                                                                          CONJ                    X X X A X to (+ subjunctive), in order that/to; how, as, when, while; even if;



# TODO WW add 'di' as form of 'deus'
#  I.E. IMPLEMENT UNIQUES?

# TODO L&S
#  2 word defs e.g. Bona Dea

# with open("/home/henry/Desktop/latin_website/PyWhitakersWords/GeneratedFiles/JOINED.txt", "w", encoding='utf-8') as o:
#     json.dump([n.to_dict(def_lookup=True) for n in ND], o, indent=1)


