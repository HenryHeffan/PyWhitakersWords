#!/bin/share/python3

# this file is run directly, so add the proper path
import os
import sys
PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPATH = os.path.join(PATH, "low_memory_stems/build/")
sys.path.insert(0, PATH)

from core_files.entry_and_inflections import *

if len(sys.argv) >= 2:
    SHOULD_BAKE = (sys.argv[1] != "false")
else:
    SHOULD_BAKE = True


o_cpp = open(OPATH + "generated.cpp", "w")
o_h = open(OPATH + "generated.h", "w")


enum_list = []
def output_enum(c):
    enum_list.append(c)
    o_h.write("static const int MAX_{class_name} = {items_len};\n\n".format(
        class_name = c.__name__,
        items_len = len(list(c))
    ))
#     STR_CPP="""
# /*
# enum class {class_name} {lb}
#     {items}
# {rb};
# */
# static const string {class_name}Strs[] = {lb}{strs}{rb};
# string str_val_{class_name}({class_name} e)
# {lb}
#     return {class_name}Strs[static_cast<int>(e)];
# {rb}
# /*
# ostream& operator<<(ostream& os, const {class_name}& e)
# {lb}
#     os << {class_name}Strs[static_cast<int>(e)];
#     return os;
# {rb}
# istream& operator>>(istream& is, {class_name}& e) {lb}
#     // read from lhs into rhs
#     string l;
#     is >> l;
#     //cerr << ">>>"<<l <<"<<<\\n";
#     for(int i = 0; i < {items_len}; i++)
#     {lb}
#         if(l == {class_name}Strs[i])
#         {lb}
#             e = static_cast<{class_name}>(i);
#             return is;
#         {rb}
#     {rb}
#     abort();
# {rb}*/"""
#     STR_H = """
#
# enum class {class_name} {lb}
#     {items}
# {rb};
# static const int MAX_{class_name} = {items_len};
#
# //static const string {class_name}Strs[] = {lb}{strs}{rb};
# //ostream& operator<<(ostream& os, const {class_name}& e);
# //istream& operator>>(istream& is, {class_name}& e);
# string str_val_{class_name}({class_name} e);
# """
#     assert len(list(c)) == max([int(e) for e in c]) + 1, (c.__name__, len(list(c)), max([int(e) for e in c]) + 1)
#     assert len(set(list(c))) == len(list(c)) # so all the elements unque
#     assert min([int(e) for e in c]) == 0 # therefore the elemnts are 0 ... item_len-1
#
#     items_len = len(list(c))
#     o_cpp.write(STR_CPP.format(
#         class_name= c.__name__,
#         items = ", ".join(["{} = {}".format(e.name, int(e)) for e in c]),
#         strs=", ".join(['"{}"'.format(c.str_val(i)) for i in range(items_len)]),
#         items_len=items_len,
#         lb="{",
#         rb="}"
#     ))
#     o_h.write(STR_H.format(
#         class_name=c.__name__,
#         items=", ".join(["{} = {}".format(e.name, int(e)) for e in c]),
#         strs=", ".join(['"{}"'.format(c.str_val(e)) for e in c]),
#         items_len=len(list(c)),
#         lb="{",
#         rb="}"
#     ))
    # print("""enum("{class_name}"); {class_name}.str_val=property(lambda x: str_val_{class_name}(x))""".format(class_name=c.__name__))


def output_dict(c):
    STR_CPP="""
/*
class {class_name} {lb}
public:
{items}
    //friend ostream& operator<<(ostream& os, const {class_name}& dt);
    //friend istream& operator>>(istream& is, {class_name}& dt);
{rb};
*/
/*ostream& operator<<(ostream& os, const {class_name}& e)
{lb}
    os{read_out};
    return os;
{rb}
istream& operator>>(istream& is, {class_name}& e)
{lb}
    is{read_in};
    return is;
{rb}*/
bool operator==(const {class_name}& a, const {class_name}& b)
{lb}
    return {comp_code};
{rb}
"""
    STR_H = """
class {class_name}: public DictData {lb}
public:
{items}
    {class_name}({arg_items}){init_items} {lb}{rb};
    //friend ostream& operator<<(ostream& os, const {class_name}& dt);
    //friend istream& operator>>(istream& is, {class_name}& dt);
{rb};

//ostream& operator<<(ostream& os, const {class_name}& e);
//istream& operator>>(istream& is, {class_name}& e);
bool operator==(const {class_name}& a, const {class_name}& b);
"""
    MP = {c.__name__: "ENUM_VAR" for c in enum_list}
    # MP = {}
    MP["str"] = "string"
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

//#include <iostream>
#include <string>
using namespace std;

typedef unsigned char ENUM_VAR;

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

print("DONE generated.h and generated.cpp")


########################################################################################################################
########################################################################################################################
########################################################################################################################
#                                               Bake Cpp Dictionaryies                                                 #
########################################################################################################################
########################################################################################################################
########################################################################################################################


if not SHOULD_BAKE:
    exit(0)

MAX_HASHTABLE_BLOCK_SIZE_EXP = 14
MAX_HASHTABLE_BLOCK_SIZE = 2**MAX_HASHTABLE_BLOCK_SIZE_EXP

MAX_LEMMA_LIST_BLOCK_SIZE_EXP = 12
MAX_LEMMA_LIST_BLOCK_SIZE = 2**MAX_LEMMA_LIST_BLOCK_SIZE_EXP

SOFTMAX_KEY_VEC_SIZE = 2 ** 12

MAX_SMALL_VEC_SIZE = 512

SOFTMAX_KEY_VEC_SIZE = max(SOFTMAX_KEY_VEC_SIZE, MAX_SMALL_VEC_SIZE + 1)

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
""")

def add_MAX_BLOCK_SIZE(o, done=[False]):
    if not done[0]:
        done[0] = True
        o.write("const int MAX_HASHTABLE_BLOCK_SIZE_EXP = {MAX_HASHTABLE_BLOCK_SIZE_EXP};\n"
                "const int MAX_HASHTABLE_BLOCK_SIZE = {MAX_HASHTABLE_BLOCK_SIZE};\n"
                "const int MAX_LEMMA_LIST_BLOCK_SIZE_EXP = {MAX_LEMMA_LIST_BLOCK_SIZE_EXP};\n"
                "const int MAX_LEMMA_LIST_BLOCK_SIZE = {MAX_LEMMA_LIST_BLOCK_SIZE};\n"
                .format(
            MAX_HASHTABLE_BLOCK_SIZE_EXP=MAX_HASHTABLE_BLOCK_SIZE_EXP,
            MAX_HASHTABLE_BLOCK_SIZE=MAX_HASHTABLE_BLOCK_SIZE,
            MAX_LEMMA_LIST_BLOCK_SIZE_EXP=MAX_LEMMA_LIST_BLOCK_SIZE_EXP,
            MAX_LEMMA_LIST_BLOCK_SIZE=MAX_LEMMA_LIST_BLOCK_SIZE
        ))

# NOW WE GENERATE THE STATIC HASH TABLES

def add_baked_dictionary(d, name, baked_dict_index):
    b_cpp_pos_types = open(OPATH + "baked_pos_types_{}.cpp".format(name.lower()), "w")
    b_cpp_pos_types.write('\n#include "baked.h"\n')
    add_MAX_BLOCK_SIZE(b_cpp_pos_types)

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
                return str(int(at))  # at.__class__.__name__ + "::" + at.name
            if isinstance(at, str):
                return "\"{}\"".format(at)
            return str(at)

        STRS = [
            elem.__class__.__name__ + "(" +
            (", ".join([f_s(elem, name) for name, type in elem.__class__.ordered_vals]))
            + ")"
            for elem in DONE
        ]
        array_type = DONE[0].__class__.__name__
        array_name = name.upper() + "_" + pos.name + "_ARRAY"
        b_h.write("extern const " + array_type + " " + array_name + "[" + str(len(STRS)) + "];\n")
        b_cpp_pos_types.write("const " + array_type + " " + array_name + "[" + str(len(STRS)) + "] = {" + (",\n".join(STRS)) + "};\n")


    # First we will figure out the indeces and add the lemmas and keys into arrays
    LEMMATA = [[]]
    TRUE_KEYS = [[]]
    for i_lemmata, lemma in enumerate(d.dictionary_lemmata):
        # print("LEN LEM[-1]: ",len(LEMMATA[-1]), MAX_LEMMA_LIST_BLOCK_SIZE)
        if(len(LEMMATA[-1]) >= MAX_LEMMA_LIST_BLOCK_SIZE):  # TODO CHANGE WHEN ADD LEMMA BLOCKS
            # print("NEW LEMMA BLOCK")
            LEMMATA.append([])

        LEMMATA[-1].append(lemma)
        lemma.ref_str = "{}_LEMMATA_{}[{}]".format(name.upper(), len(LEMMATA) - 1, len(LEMMATA[-1]) - 1)

        if(len(TRUE_KEYS[-1]) > SOFTMAX_KEY_VEC_SIZE):
            TRUE_KEYS.append([])
        for key in lemma.dictionary_keys:
            TRUE_KEYS[-1].append(key)
            key.ref_str="{}_KEYS_{}[{}]".format(name.upper(), len(TRUE_KEYS)-1, len(TRUE_KEYS[-1])-1)
        lemma.key_arr_ref_str=lemma.dictionary_keys[0].ref_str

    for lemma_block_index, lemma_block in enumerate(LEMMATA):  # TODO CHANGE WHEN ADD BLOCKS

        b_cpp_lemmas = open(OPATH + "baked_lemmas_{}_{}.cpp".format(name.lower(), lemma_block_index), "w")
        b_cpp_lemmas.write('\n#include "baked.h"\n')

        LEMMA_VEC = []
        for lemma in lemma_block:
            LEMMA_VEC.append(
                """DictionaryLemma({part_of_speech}, {translation_metadata}, "{definition}", "{html_data}", {index}, &{keys}, {keys_len}, {baked_dict_index})""".format(
                    part_of_speech=int(lemma.part_of_speech),  # .name,
                    translation_metadata='"{}{}{}{}{}"'.format(
                        int(lemma.translation_metadata.age),
                        lemma.translation_metadata.area,
                        lemma.translation_metadata.geo,
                        int(lemma.translation_metadata.frequency),
                        lemma.translation_metadata.source),
                    definition=lemma.definition.replace("\"", "\\\""),
                    html_data=lemma.html_data if lemma.html_data else "",
                    index=lemma.index,
                    keys=lemma.key_arr_ref_str,
                    keys_len=len(lemma.dictionary_keys),
                    baked_dict_index=baked_dict_index,
                    lb="{",
                    rb="}"
                )
            )

        b_h.write(  "extern const DictionaryLemma "+name.upper() + "_LEMMATA_" + str(lemma_block_index)
                    + "[" + str(len(LEMMA_VEC)) + "];\n")
        b_cpp_lemmas.write("const DictionaryLemma "+name.upper() + "_LEMMATA_" + str(lemma_block_index)
                    + "[" + str(len(LEMMA_VEC)) + "] = {" + (",\n".join(LEMMA_VEC)) + "};\n")
        b_cpp_lemmas.close()

    # NOW PUT THE LIST OF BLOCKS DOWN HERE
    b_h.write("extern const DictionaryLemmaListBlock " + name.upper() + "_LEMMATA"
              + "[" + str(len(LEMMATA)) + "];\n")
    b_cpp_pos_types.write("const DictionaryLemmaListBlock " + name.upper() + "_LEMMATA"
                       + "[" + str(len(LEMMATA)) + "] = {" + (",\n".join([
            "DictionaryLemmaListBlock(" + name.upper() + "_LEMMATA_" + str(i) + ")" for i in range(len(LEMMATA))
        ])) + "};\n")
    b_cpp_pos_types.close()

    for key_block_index, key_block in enumerate(TRUE_KEYS):
        b_cpp_keys = open(OPATH + "baked_keys_{}_{}.cpp".format(name.lower(), key_block_index), "w")
        b_cpp_keys.write('\n#include "baked.h"\n')
        KEY_VEC = []
        for key in key_block:
            KEY_VEC.append(
                """DictionaryKey("{s1}", "{s2}", "{s3}", "{s4}", {part_of_speech}, {dict_data}, &{lemma_ptr})""".format(
                    part_of_speech=int(key.part_of_speech),
                    s1=key.stems[0] if key.stems[0] is not None else "zzz",
                    s2=key.stems[1] if key.stems[1] is not None else "zzz",
                    s3=key.stems[2] if key.stems[2] is not None else "zzz",
                    s4=key.stems[3] if key.stems[3] is not None else "zzz",
                    dict_data="&" + name.upper() + "_" + key.part_of_speech.name + "_ARRAY[" + str(key.pos_data.array_index) + "]",
                    lemma_ptr=key.lemma.ref_str,
                    lb="{",
                    rb="}"
                ))
        b_h.write("extern const DictionaryKey "+name.upper()+ "_KEYS_" + str(key_block_index) +
                  "[" + str(len(KEY_VEC))
                         + "];\n")
        b_cpp_keys.write("const DictionaryKey "+name.upper()+ "_KEYS_" + str(key_block_index) +
                         "[" + str(len(KEY_VEC))
                         + "] = {" + (", \n".join(KEY_VEC)) + "};\n")
        b_cpp_keys.close()
    # for key_vec_indx, KEY_VEC in enumerate(TRUE_KEYS):

    def hash_string(str):
        hash = 5381
        for c in str:
            hash = ((hash << 5) + hash) + ord(c)  # ; /* hash * 33 + c */
        return hash % (2 ** 32)  # // this hash should always have a 0 in the first bit

    HASH_MAPS = {}
    b_cpp_hashmaps = open(OPATH + "baked_hashmaps_{}_small.cpp".format(name.lower()), "w")
    b_cpp_hashmaps.write('\n#include "baked.h"\n')
    b_cpp_hashmaps.close()

    # NOW GENERATE ALL THE HASH TABLES
    # THE CODE BELOW BREAKS THEM INTO SECTIONS TO MAKE IT WORK MORE EASILY

    file_indx = [0]
    def dump_vector(decl, arr, l):
        if(l < MAX_SMALL_VEC_SIZE):
            b_cpp_hashmaps = open(OPATH + "baked_hashmaps_{}_small.cpp".format(name.lower()), "a")
        else:
            b_cpp_hashmaps = open(OPATH + "baked_hashmaps_{}_{}.cpp".format(name.lower(), file_indx[0]), "w")
            b_cpp_hashmaps.write('\n#include "baked.h"\n')
            file_indx[0] += 1

        b_h.write("extern ")
        b_h.write(decl)
        b_h.write(";\n")

        b_cpp_hashmaps.write(decl)
        b_cpp_hashmaps.write(" = ")
        b_cpp_hashmaps.write(arr)
        b_cpp_hashmaps.write(";\n")

        b_cpp_hashmaps.close()

    for mp_key, mp in d._stem_map.items():
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
            # if len(mp[stem]) > 5:
            #     print("TOO LONG", len(mp[stem]), [i.stems for i in mp[stem]])
            for k in mp[stem]:
                KEY_PTR_VECTOR.append("&" + k.ref_str)
                vector_i += 1
        print(pad_to_len(mp_key[0].name[:6], 6),mp_key[1], "  ", mb, "\t", badness, "\t", str(badness / len(mp) if len(mp) > 0 else badness)[:5],
              "\t", len(HASH_LIST), len(mp) / len(HASH_LIST))

        # b_h.write("const extern DictionaryKey " + name.upper() +
        #           "_KEY_[" + str(len(TRUE_KEYS)) + "];\n")
        VECTOR_NAME = name.upper() + "_" + mp_key[0].name + "_" + str(mp_key[1]) + "_KEY_VECTOR"
        dump_vector(
            "const DictionaryKey *" + VECTOR_NAME + "[" + str(len(KEY_PTR_VECTOR)) + "]",
            "{" + (", \n".join(KEY_PTR_VECTOR)) + "}",
            len(KEY_PTR_VECTOR))

        HASH_LIST_STRS = ["HashTableCell(NULL, 0, 0x80000000)" if e is None else
                          "HashTableCell(&{VECTOR_NAME}[{vec_indx}], {ct}, {hash})".format(
                              vec_indx = e[1],
                              ct = e[2],
                              hash = hash_string(e[0]),
                              lb = "{",
                              VECTOR_NAME=VECTOR_NAME,
                              rb = "}"
                          ) for e in HASH_LIST]

        import math
        BLOCK_CT = math.ceil(len(HASH_LIST_STRS) / MAX_HASHTABLE_BLOCK_SIZE)
        for block_indx in range(BLOCK_CT):
            SLICE = HASH_LIST_STRS[block_indx * MAX_HASHTABLE_BLOCK_SIZE : min((block_indx + 1) * MAX_HASHTABLE_BLOCK_SIZE, len(HASH_LIST_STRS))]
            hashmap_name = name.upper() + "_" + mp_key[0].name + "_" + str(mp_key[1]) + "_HASH_TABLE_" + str(block_indx)
            dump_vector(
                "const HashTableCell " + hashmap_name  + "[" + str(len(SLICE)) + "]",
                "{" + (", \n".join(SLICE)) + "}",
                len(SLICE))

        hashmap_name = name.upper() + "_" + mp_key[0].name + "_" + str(mp_key[1]) + "_HASH_TABLE"
        dump_vector(
            "const HashTableBlock " + hashmap_name + "[" + str(BLOCK_CT) + "]",
            "{" + (" ,".join(["HashTableBlock(" + hashmap_name + "_" + str(i) + ")" for i in range(BLOCK_CT)])) + "}",
            BLOCK_CT)

        HASH_MAPS[mp_key] = (size, hashmap_name)
        b_cpp_hashmaps.close()

    b_cpp_hashmaps = open(OPATH + "baked_hashmaps_{}_joined.cpp".format(name.lower()), "w")
    b_cpp_hashmaps.write('\n#include "baked.h"\n')
    b_h.write("const extern HashTable "+name.upper()+
                "_HASHTABLES[MAX_PartOfSpeech][4];\n")
    b_cpp_hashmaps.write("const HashTable "+name.upper()+
                "_HASHTABLES[MAX_PartOfSpeech][4] = {" + (", \n    ".join([
        "{" + (", \n        ".join([
                "HashTable({cells_ptr}, {len_log2}, {key_indx})".format(
                    cells_ptr=HASH_MAPS[(pos, stem_indx)][1],
                    len_log2=HASH_MAPS[(pos, stem_indx)][0],
                    key_indx=stem_indx - 1
                ) if (pos, stem_indx) in HASH_MAPS else "{NULL, 0, 0}"
            for stem_indx in [1, 2, 3, 4]
        ])) + "}"
    for pos in PartOfSpeech])) + "};\n")

    b_cpp_hashmaps.write("const BakedDictionaryStemCollection BAKED_" + name.upper() + " = BakedDictionaryStemCollection({tables}, {lemmas}, {baked_dict_index});\n".format(
        tables = name.upper()+ "_HASHTABLES",
        lemmas = "DictionaryLemmaListView(" + name.upper()+ "_LEMMATA," + str(sum(len(block) for block in LEMMATA)) + ")",
        baked_dict_index=baked_dict_index
    ))

    b_cpp_hashmaps.close()
    # b_cpp_lemmas.close()
    # b_cpp_keys.close()


from core_files.whitakers_words import init
ww, _ = init(PATH, fast=False)
add_baked_dictionary(ww, "WW", 0)

from core_files.joined_formater_html import init
joined, _ = init(PATH, fast=False)
add_baked_dictionary(joined, "JOINED", 1)

b_h.write("""
#endif
""")
b_h.close()
