# this file is run directly, so add the proper path
import os
import sys
PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PATH)
OPATH = os.path.join(PATH, "low_memory_stems/build/")

from core_files.entry_and_inflections import *

import sys

SHOULD_BAKE = (sys.argv[1] != "false") if len(sys.argv) >= 2 else False

o_cpp = open(OPATH + "generated.cpp", "w")
o_h = open(OPATH + "generated.h", "w")


def output_enum(c):
    STR_CPP="""
/*
enum class {class_name} {lb}
    {items}
{rb};
*/
static const string {class_name}Strs[] = {lb}{strs}{rb};
string str_val_{class_name}({class_name} e)
{lb}
    return {class_name}Strs[static_cast<int>(e)];
{rb}
ostream& operator<<(ostream& os, const {class_name}& e)
{lb}
    os << {class_name}Strs[static_cast<int>(e)];
    return os;
{rb}
istream& operator>>(istream& is, {class_name}& e) {lb}
    // read from lhs into rhs 
    string l;
    is >> l;
    //cerr << ">>>"<<l <<"<<<\\n";
    for(int i = 0; i < {items_len}; i++)
    {lb}
        if(l == {class_name}Strs[i])
        {lb}
            e = static_cast<{class_name}>(i);
            return is;
        {rb}
    {rb}
    abort();
{rb}"""
    STR_H = """

enum class {class_name} {lb}
    {items}
{rb};
static const int MAX_{class_name} = {items_len};

//static const string {class_name}Strs[] = {lb}{strs}{rb};
ostream& operator<<(ostream& os, const {class_name}& e);
istream& operator>>(istream& is, {class_name}& e);
string str_val_{class_name}({class_name} e);
"""
    assert len(list(c)) == max([int(e) for e in c]) + 1, (c.__name__, len(list(c)), max([int(e) for e in c]) + 1)
    assert len(set(list(c))) == len(list(c)) # so all the elements unque
    assert min([int(e) for e in c]) == 0 # therefore the elemnts are 0 ... item_len-1

    items_len = len(list(c))
    o_cpp.write(STR_CPP.format(
        class_name= c.__name__,
        items = ", ".join(["{} = {}".format(e.name, int(e)) for e in c]),
        strs=", ".join(['"{}"'.format(c.str_val(i)) for i in range(items_len)]),
        items_len=items_len,
        lb="{",
        rb="}"
    ))
    o_h.write(STR_H.format(
        class_name=c.__name__,
        items=", ".join(["{} = {}".format(e.name, int(e)) for e in c]),
        strs=", ".join(['"{}"'.format(c.str_val(e)) for e in c]),
        items_len=len(list(c)),
        lb="{",
        rb="}"
    ))
    # print("""enum("{class_name}"); {class_name}.str_val=property(lambda x: str_val_{class_name}(x))""".format(class_name=c.__name__))


def output_dict(c):
    STR_CPP="""
/*
class {class_name} {lb}
public:
{items}
    friend ostream& operator<<(ostream& os, const {class_name}& dt);
    friend istream& operator>>(istream& is, {class_name}& dt);
{rb};
*/
ostream& operator<<(ostream& os, const {class_name}& e)
{lb}
    os{read_out};
    return os;
{rb}
istream& operator>>(istream& is, {class_name}& e)
{lb}
    is{read_in};
    return is;
{rb}
bool operator==(const {class_name}& a, const {class_name}& b)
{lb}
    return {comp_code};
{rb}"""
    STR_H = """
class {class_name}: public DictData {lb}
public:
{items}
    {class_name}({arg_items}){init_items} {lb}{rb};
    friend ostream& operator<<(ostream& os, const {class_name}& dt);
    friend istream& operator>>(istream& is, {class_name}& dt);
{rb};

ostream& operator<<(ostream& os, const {class_name}& e);
istream& operator>>(istream& is, {class_name}& e);
bool operator==(const {class_name}& a, const {class_name}& b);
"""
    MP = {"str": "string"}
    CMPO = {"declention": "(int)", "declention_variant": "(int)", "conjugation": "(int)", "conjugation_variant": "(int)"}
    CMPI = {}  #"declention": "(DeclentionType)", "declention_variant": "(DeclentionSubtype)", "conjugation": "(ConjugationType)", "conjugation_variant": "(ConjugationSubtype)"}

    remap_type = lambda x: x if x not in MP else MP[x]
    vals = [(k, v.__name__) for k, v in c.__init__.__annotations__.items() if k!='return']
    c.ordered_vals = vals
    o_cpp.write(STR_CPP.format(
        class_name= c.__name__,
        items = "\n".join(["    {} {};".format(remap_type(type), name) for name, type in vals]),
        read_out="".join(["<<({}e.{})<<' '".format("" if name not in CMPO else CMPO[name], name) for name, _ in vals]),
        read_in="".join([">>({}e.{})".format("" if name not in CMPI else CMPI[name], name) for name, _ in vals]),
        comp_code="&&".join(["1"] + ["a.{name}==b.{name}".format(name=name) for name, _ in vals]),
        lb="{",
        rb="}"
    ))
    o_h.write(STR_H.format(
        class_name=c.__name__,
        items="\n".join(["    {} {};".format(remap_type(type), name) for name, type in vals]),
        arg_items = ",".join(["{} {}".format(remap_type(type), name) for name, type in vals]),
        init_items = ("" if len(vals) == 0 else ":") + (",".join(["{}({})".format(name, name) for name, type in vals])),
        read_out="".join(["<<({}e.{})<<' '".format("" if name not in CMPO else CMPO[name], name) for name, _ in vals]),
        read_in="".join([">>({}e.{})".format("" if name not in CMPI else CMPI[name], name) for name, _ in vals]),
        comp_code="&&".join(["a.{name}==b.{name}".format(name=name) for name, _ in vals]),
        lb="{",
        rb="}"
    ))

o_h.write("""

#ifndef SRC_GENERATED_H_
#define SRC_GENERATED_H_

#include <iostream>
#include <string>
using namespace std;

class DictData {};""")

for class_name in ["DeclentionType", "DeclentionSubtype", "ConjugationType", "ConjugationSubtype"]:
    o_h.write("""
typedef int {class_name};
""".format(class_name=class_name,
           lb="{",
           rb="}"
           ))
o_cpp.write("""#include "generated.h"
#include <stdio.h>
""")

output_enum(Person)
output_enum(Number)
output_enum(Tense)
output_enum(Voice)
output_enum(Mood)
output_enum(Gender)
output_enum(Case)
output_enum(PartOfSpeech)
output_enum(VerbKind)
output_enum(NounKind)
output_enum(PronounKind)
output_enum(AdjectiveKind)
output_enum(NumberKind)
output_enum(InflectionFrequency)
output_enum(InflectionAge)
output_enum(DictionaryFrequency)
output_enum(DictionaryAge)
#
output_dict(PronounDictData)
output_dict(NounDictData)
output_dict(VerbDictData)
output_dict(PrepositionDictData)
output_dict(InterjectionDictData)
output_dict(AdjectiveDictData)
output_dict(AdverbDictData)
output_dict(ConjunctionDictData)
output_dict(NumberDictData)
output_dict(PackonDictData)

o_h.write("""
#endif
""")

o_cpp.close()
o_h.close()



if not SHOULD_BAKE:
    exit(0)


print("DOING BAKING GENERATION")

b_h = open(OPATH + "baked.h", "w")

b_h.write("""
#ifndef SRC_BAKED_H_
#define SRC_BAKED_H_

#include <iostream>
#include <string>
#include "data_structures.h"
#include "generated.h"
using namespace std;

// """)
from time import time
b_h.write(str(time()))
b_h.write("\n\n")

# NOW WE GENERATE THE STATIC HASH TABLES


def add_baked_dictionary(d, name):
    b_cpp_keys = open(OPATH + "baked_keys_{}.cpp".format(name.lower()), "w")
    b_cpp_lemmas = open(OPATH + "baked_lemmas_{}.cpp".format(name.lower()), "w")

    b_cpp_keys.write('\n#include "baked.h"\n')
    b_cpp_lemmas.write('\n#include "baked.h"\n')

    POS_DATA_MP = {pos: [] for pos in PartOfSpeech}
    for key in d.dictionary_keys:
        POS_DATA_MP[key.part_of_speech].append(key.pos_data)
    for pos in POS_DATA_MP:
        DONE = []
        i = 0
        for pos_data in POS_DATA_MP[pos]:
            for elem in DONE:
                if elem == pos_data:
                    pos_data.array_index = elem.array_index
                    break
            else:
                DONE.append(pos_data)
                pos_data.array_index = i
                i+=1
        if len(DONE) == 0:
            continue

        def f_s(elem, name):
            at = getattr(elem, name)
            if isinstance(at, StringMappedEnum):
                return at.__class__.__name__ + "::" + at.name
            if isinstance(at, str):
                return "\"{}\"".format(at)
            return str(at)

        STRS = [
            elem.__class__.__name__ + "(" +
            (", ".join([f_s(elem, name) for name, type in elem.__class__.ordered_vals]))
            + ")"
            for elem in DONE
        ]
        b_cpp_keys.write("const " + DONE[0].__class__.__name__ + " " + name.upper() +
                    "_" + pos.name + "_ARRAY[" + str(len(STRS)) + "] = {" + (",\n".join(STRS)) + "};\n")


    LEMMATA = []
    TRUE_KEYS = []
    i_keys = 0
    for i_lemmata, l in enumerate(d.dictionary_lemmata):
        vector_index = i_keys
        for k in l.dictionary_keys:
            TRUE_KEYS.append(
                """{lb}"{s1}", "{s2}", "{s3}", "{s4}", PartOfSpeech::{part_of_speech}, {dict_data}, {lemma_ptr}{rb}""".format(
                    part_of_speech=k.part_of_speech.name,
                    s1=k.stems[0] if k.stems[0] is not None else "zzz",
                    s2=k.stems[1] if k.stems[1] is not None else "zzz",
                    s3=k.stems[2] if k.stems[2] is not None else "zzz",
                    s4=k.stems[3] if k.stems[3] is not None else "zzz",
                    dict_data="&" +  name.upper() + "_" + k.part_of_speech.name+"_ARRAY[" + str(k.pos_data.array_index) + "]",
                    lemma_ptr="&" + name.upper()+"_LEMMATA["+str(i_lemmata)+"]",
                    lb="{",
                    rb="}"
                ))
            k.array_index = i_keys
            i_keys+=1
            k.true_stem = True
        print(l.html_data)
        LEMMATA.append(
        """{lb}PartOfSpeech::{part_of_speech}, {translation_metadata}, "{definition}", "{html_data}", {index}, {keys}, {keys_len}{rb}""".format(
            part_of_speech=l.part_of_speech.name,
            translation_metadata='"{}{}{}{}{}"'.format(
                int(l.translation_metadata.age),
                l.translation_metadata.area,
                l.translation_metadata.geo,
                int(l.translation_metadata.frequency),
                l.translation_metadata.source),
            definition=l.definition.replace("\"", "\\\""),
            html_data=l.html_data if l.html_data else "",
            index=l.index,
            keys="&{}_KEYS[{}]".format(name.upper(), vector_index),
            keys_len=len(l.dictionary_keys),
            # name="LEMMA_" + str(i),
            lb="{",
            rb="}"
        ))

    b_h.write("const extern DictionaryLemma "+name.upper()+
                "_LEMMATA[" + str(len(LEMMATA)) + "];\n")
    # for i in range(len(LEMMATA) // 1000):
    #     sl_l, sl_r = i*1000, min((i+1)*1000, len(LEMMATA))
    b_cpp_lemmas.write("const DictionaryLemma "+name.upper()+
                "_LEMMATA[" + str(len(LEMMATA)) + "] = {" + (",\n".join(LEMMATA)) + "};\n")

    b_h.write("const extern DictionaryKey "+name.upper()+
                "_KEYS[" + str(len(TRUE_KEYS)) + "];\n")
    b_cpp_keys.write("const DictionaryKey "+name.upper()+
                "_KEYS[" + str(len(TRUE_KEYS)) + "] = {" + (", \n".join(TRUE_KEYS)) + "};\n")

    def hash_string(str):
        hash = 5381
        for c in str:
            hash = ((hash << 5) + hash) + ord(c)  # ; /* hash * 33 + c */
        return hash % (2 ** 32)  # // this hash should always have a 0 in the first bit

    HASH_MAPS = {}
    b_cpp_hashmaps = open(OPATH + "baked_hashmaps_{}_small.cpp".format(name.lower()), "w")
    b_cpp_hashmaps.write('\n#include "baked.h"\n')
    b_cpp_hashmaps.close()
    for key_indx_var, (mp_key, mp) in enumerate(d._stem_map.items()):
        if(len(mp) < 400):
            b_cpp_hashmaps = open(OPATH + "baked_hashmaps_{}_small.cpp".format(name.lower()), "a")
        else:
            b_cpp_hashmaps = open(OPATH + "baked_hashmaps_{}_{}.cpp".format(name.lower(), key_indx_var), "w")
            b_cpp_hashmaps.write('\n#include "baked.h"\n')
        # if len(mp) == 0:
        #     continue
        from math import log2
        size = int(2.0 + log2(len(mp) + 2))
        HASH_LIST: List[Optional[Tuple[str, List]]] = [None for _ in range(2 ** size)]

        badness = 0
        mb = 0
        KEY_PTR_VECTOR = []
        vector_i = 0
        for stem in mp:
            # assert all(k.true_stem for k in mp[stem])
            indx = hash_string(stem) % len(HASH_LIST)
            lb = 0
            while HASH_LIST[indx] is not None:
                badness += 1
                lb += 1
                indx = (indx + 1) % len(HASH_LIST)
            mb = max(mb, lb)
            HASH_LIST[indx] = (stem, vector_i, len(mp[stem]))
            for k in mp[stem]:
                KEY_PTR_VECTOR.append("&" + name.upper() + "_KEYS[" + str(k.array_index) + "]")
                vector_i += 1
        print(pad_to_len(mp_key[0].name[:6], 6),mp_key[1], "  ", mb, "\t", badness, "\t", str(badness / len(mp) if len(mp) > 0 else badness)[:5],
              "\t", len(HASH_LIST), len(mp) / len(HASH_LIST))

        # b_h.write("const extern DictionaryKey " + name.upper() +
        #           "_KEY_[" + str(len(TRUE_KEYS)) + "];\n")
        VECTOR_NAME = name.upper() + "_" + mp_key[0].name + "_" + str(mp_key[1]) + "_KEY_VECTOR"
        b_cpp_hashmaps.write("const DictionaryKey *"
                    + VECTOR_NAME + "[" + str(len(KEY_PTR_VECTOR)) + "] = {"
                    + (", \n".join(KEY_PTR_VECTOR)) + "};\n")
        HASH_LIST_STRS = ["{NULL, 0, 0x80000000}" if e is None else
                          "{lb}&{VECTOR_NAME}[{vec_indx}], {ct}, {hash}{rb}".format(
                              vec_indx = e[1],
                              ct = e[2],
                              hash = hash_string(e[0]),
                              lb = "{",
                              VECTOR_NAME=VECTOR_NAME,
                              rb = "}"
                          ) for e in HASH_LIST]
        hashmap_name = name.upper() + "_" + mp_key[0].name + "_" + str(mp_key[1]) + "_HASH_TABLE"
        b_h.write("extern const HashTableCell " + hashmap_name + "[" + str(len(HASH_LIST_STRS)) + "];\n")
        b_cpp_hashmaps.write("const HashTableCell " + hashmap_name + "[" + str(len(HASH_LIST_STRS)) + "] = {"
                    + (", \n".join(HASH_LIST_STRS)) + "};\n")
        HASH_MAPS[mp_key] = (size, hashmap_name)
        b_cpp_hashmaps.close()

    # HashTable *lookup_table[MAX_PartOfSpeech][4];
    # HashTable(const HashTableCell *cells, const unsigned long len, const int key_string_index)
    # HASH_MAP_STRS = [
    # for pos in PartOfSpeech for stem_indx in [1,2,3,4]]

    b_cpp_hashmaps = open(OPATH + "baked_hashmaps_{}_joined.cpp".format(name.lower()), "w")
    b_cpp_hashmaps.write('\n#include "baked.h"\n')
    b_h.write("const extern HashTable "+name.upper()+
                "_HASHTABLES[MAX_PartOfSpeech][4];\n")
    b_cpp_hashmaps.write("const HashTable "+name.upper()+
                "_HASHTABLES[MAX_PartOfSpeech][4] = {" + (", \n    ".join([
        "{" + (", \n        ".join([
                "{lb}{cells_ptr}, {len_log2}, {key_indx}{rb}".format(
                    lb="{",
                    rb="}",
                    cells_ptr=HASH_MAPS[(pos, stem_indx)][1],
                    len_log2=HASH_MAPS[(pos, stem_indx)][0],
                    key_indx=stem_indx - 1
                ) if (pos, stem_indx) in HASH_MAPS else "{NULL, 0, 0}"
            for stem_indx in [1, 2, 3, 4]
        ])) + "}"
    for pos in PartOfSpeech])) + "};\n")

    b_cpp_hashmaps.write("const BakedDictionaryStemCollection BAKED_" + name.upper() + " = BakedDictionaryStemCollection({tables}, {lemmas}, {ct});\n".format(
        tables = name.upper()+ "_HASHTABLES",
        lemmas = name.upper()+ "_LEMMATA",
        ct = len(LEMMATA)
    ))


    b_cpp_hashmaps.close()
    b_cpp_lemmas.close()
    b_cpp_keys.close()

    # b_h.write("const extern DictionaryKey * "+name.upper()+
    #             "_KEY_VECTORS[" + str(len(KEY_VECTOR)) + "];\n")
    # b_cpp.write("const DictionaryKey * "+name.upper()+
    #             "_KEY_VECTORS[" + str(len(KEY_VECTOR)) + "] = {" + (", \n".join(KEY_VECTOR)) + "};\n")


# CUR DictionaryKey(StemGroup stems, PartOfSpeech part_of_speech, DictData *data)
# NEW DictionaryKey(StemGroup stems, PartOfSpeech part_of_speech, DictData *data, DictionaryLemma* lemma)
# CUR DictionaryLemma(PartOfSpeech part_of_speech, TranslationMetadata translation_metadata,
#                     string definition, string html_data, int index)
# NEW DictionaryLemma(PartOfSpeech part_of_speech, TranslationMetadata translation_metadata,
#                     string definition, string html_data, int index, DictionaryKey* keys, int keys_len)

from core_files.whitakers_words import init
ww, _ = init(PATH, fast=False)
print("INITED WW")
add_baked_dictionary(ww, "WW")

from core_files.joined_formater_html import init
joined, _ = init(PATH, fast=False)
print("INITED JOINED")
# for e in joined.dictionary_lemmata:
#     print(e.html_data)
add_baked_dictionary(joined, "JOINED")

# for k in ww._stem_map:
#     ls = ww._stem_map[k]
#     print(k, len(mp))

# CPP_REF = os.path.join(PATH, "GeneratedFiles/JOINED_CPP_FAST_ONLY_REF_DEF.txt")
# WW = os.path.join(PATH, "GeneratedFiles/DICTLINE_CPP_FAST.txt")
# if os.path.isfile(CPP_REF):
#     with open(CPP_REF) as ifile:
#         s = ifile.read()
#         o_h.write('\nstatic const string CPP_STR = "{}";\n'.format(s.replace("\n", "\\n").replace("\"", "\\\"")))
#     with open(WW) as ifile:
#         s = ifile.read()
#         o_h.write('\nstatic const string WW_STR = "{}";\n'.format(s.replace("\n", "\\n").replace("\"", "\\\"")))

b_h.write("""
#endif
""")
b_h.close()
# b_cpp.close()
