#!/bin/share/python3

# this file is run directly, so add the proper path
import os
import sys
PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPATH = os.path.join(PATH, "low_memory_stems/build/")
sys.path.insert(0, PATH)

from typing import IO

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

def output_dict(c):
    STR_H = """
class {class_name}: public DictData {lb}
public:
{items}
    {class_name}({arg_items}){init_items} {lb}{rb};
{rb};

bool operator==(const {class_name}& a, const {class_name}& b);
    """
    STR_CPP="""
bool operator==(const {class_name}& a, const {class_name}& b)
{lb}
    return {comp_code};
{rb}
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
# DONE OUTPUT DICT


def output_infl(c):
    STR_H = """
class {class_name}: public InflData {lb}
public:
{items}
    {class_name}({arg_items}){init_items} {lb}{rb};
{rb};

//bool operator==(const {class_name}& a, const {class_name}& b);
    """
    STR_CPP="""
/*bool operator==(const {class_name}& a, const {class_name}& b)
{lb}
    return {comp_code};
{rb}*/
"""

    MP = {c.__name__: "ENUM_VAR" for c in enum_list}
    # MP = {}
    MP["str"] = "string"
    CMPO = {"declention": "(int)", "declention_variant": "(int)", "conjugation": "(int)", "conjugation_variant": "(int)"}
    CMPI = {}  #"declention": "(DeclentionType)", "declention_variant": "(DeclentionSubtype)", "conjugation": "(ConjugationType)", "conjugation_variant": "(ConjugationSubtype)"}

    NAME_MP = {"case": "_case"}

    remap_type = lambda x: x if x not in MP else MP[x]
    remap_name = lambda x: x if x not in NAME_MP else NAME_MP[x]
    vals = [(remap_name(k), v.__name__) for k, v in c.__init__.__annotations__.items() if k!='return']
    c.ordered_vals = vals
    # print(c, vals)
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
# DONE OUTPUT INFL



o_h.write("""

#ifndef SRC_GENERATED_H_
#define SRC_GENERATED_H_

#include <string>
using namespace std;

typedef unsigned char ENUM_VAR;

class DictData {};
class InflData {};
""")

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
for _, dict in POS_DICT_ENTRY_CLASS_MP.items():
    output_dict(dict)
for _, infl in POS_INFL_ENTRY_CLASS_MP.items():
    output_infl(infl)
# output_dict(NounDictData)
# output_dict(VerbDictData)
# output_dict(PrepositionDictData)
# output_dict(InterjectionDictData)
# output_dict(AdjectiveDictData)
# output_dict(AdverbDictData)
# output_dict(ConjunctionDictData)
# output_dict(NumberDictData)
# output_dict(PackonDictData)

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


MAX_HASHTABLE_BLOCK_SIZE_EXP = 10
MAX_LEMMA_LIST_BLOCK_SIZE_EXP = 9
MAX_INFL_LIST_BLOCK_SIZE_EXP = 9

print("DOING BAKING GENERATION")

class BakedOutput:
    def __init__(self):
        self.CPP_LEN_THRESH = 2**19
        self.header: IO = open(OPATH + "TEMPbaked.h", "w")
        self.cpp_output: Optional[IO] = None
        self.index: int = 0
        self.cur_len: int = 0
        self._new_cpp_file()
        self._inserted_vectors: List[Tuple[str, str, List, Callable[[Any], str]]] = []

    def _new_cpp_file(self):
        if self.cpp_output is not None:
            self.cpp_output.close()
        self.cpp_output = open(OPATH + "baked_{}.cpp".format(self.index), "w")
        self.cpp_output.write('\n#include "baked.h"\n')
        self.index += 1
        self.cur_len = 0

    def add_exact_vector_2d(self, array_type: str, array_name: str, strs: List[List[str]]):
        assert all(len(strs[0]) == len(strs[i]) for i in range(len(strs)))

        self.header.write("extern const {} {}[{}][{}];\n"
                          .format(array_type, array_name, len(strs), len(strs[0])))

        content = ",\n".join(["{\n    " + (",\n    ".join(l)) + "\n}" for l in strs])

        self.add_cpp(
            "const {array_type} {array_name}[{array_len_1}][{array_len_2}] = {lb}{content}{rb};\n".format(
                array_type=array_type,
                array_name=array_name,
                array_len_1=len(strs),
                array_len_2=len(strs[0]),
                content=content,
                lb="{",
                rb="}"
            )
        )

    def add_exact_multidim_array(self, array_type: str, array_name: str, strs: List[List]):
        # print(strs)
        # assert all(len(strs[0]) == len(strs[i]) for i in range(len(strs)))
        dims = []
        p = strs
        while isinstance(p, list):
            dims.append(len(p))
            p = p[0]

        dims_str="".join(["[{}]".format(dim) for dim in dims])

        self.header.write("extern const {} {}{};\n"
                          .format(array_type, array_name, dims_str))

        l_to_s = lambda l: ("{" + (",\n".join([l_to_s(e) for e in l])) + "}" ) if isinstance(l, list) else l
        content = l_to_s(strs)
        #",\n".join(["{\n    " + (",\n    ".join(l)) + "\n}" for l in strs])

        self.add_cpp(
            "const {array_type} {array_name}{array_dims} = {content};\n".format(
                array_type=array_type,
                array_name=array_name,
                array_dims=dims_str,
                content=content,
                lb="{",
                rb="}"
            )
        )
    def add_cpp(self, string: str):
        if(self.cur_len + len(string) > self.CPP_LEN_THRESH):
            self._new_cpp_file()
        self.cur_len += len(string)
        self.cpp_output.write(string)

    def add_header(self, string: str):
        self.header.write(string)

    def insert_vector(self, array_type: str, array_name: str, ls: List, elem_to_str: Callable, do_labeling=False):
        if do_labeling:
            # print("DOING LABELING", ls)
            for i, elem in enumerate(ls):
                if elem is not None and not isinstance(elem, str):
                    # print("ASSIGNED LABEL", elem)
                    elem.cpp_ref_str = "&{array_name}[{index}]".format(array_name=array_name, index=i)
        self._inserted_vectors.append((array_type, array_name, ls, elem_to_str))
        # self.header.write("extern const {} {}[{}];\n".format(array_type, array_name, len(ls)))
        # content = ",\n".join([elem_to_str(elem) for elem in ls])
        #
        # self.add_cpp("const {} {}[{}] = {lb}{}{rb};\n"
        #              .format(array_type, array_name, len(ls), content, lb="{", rb="}"))

    def close(self):
        for (array_type, array_name, ls, elem_to_str) in self._inserted_vectors:
            self.header.write("extern const {} {}[{}];\n".format(array_type, array_name, len(ls)))
            content = ",\n".join([elem_to_str(elem) for elem in ls])

            self.add_cpp("const {} {}[{}] = {lb}{}{rb};\n"
                         .format(array_type, array_name, len(ls), content, lb="{", rb="}"))

        self.header.write("\n#endif\n")
        self.header.close()
        self.cpp_output.close()
        import shutil
        shutil.move(OPATH + "TEMPbaked.h", OPATH + "baked.h")

    def insert_blocked_array(self,
                             array_type: str,
                             array_name: str,
                             ls: List,
                             elem_to_str: Callable,
                             max_block_size_exp: int,
                             do_labeling=False):
        max_block_size = 2 ** max_block_size_exp
        item_ct = len(ls)
        block_ct=0
        block_refs = []
        while len(ls) > 0:
            block_name = array_name+"_"+str(block_ct)
            block_ct += 1
            block = ls[:max_block_size]
            ls = ls[max_block_size:]
            # print("BLOKC", block)
            self.insert_vector(array_type, block_name, block, elem_to_str, do_labeling=do_labeling)
            block_refs.append(block_name)

        baked_output.insert_vector(
            "BlockedArrayItemBlock< {array_type} >".format(array_type=array_type),
            array_name,
            block_refs,
            lambda ref: "BlockedArrayItemBlock< {array_type} >({block_name})"
                        .format(array_type=array_type, block_name=ref)
        )
        return "BlockedArrayView< {array_type} >({blocks}, {item_ct}, {block_size_exp})".format(
            array_type=array_type,
            blocks=array_name,
            item_ct=item_ct,
            block_size_exp=max_block_size_exp
        )

    def insert_multivector(self,
                           array_type: str,
                           array_name: str,
                           vectors: List[List],
                           elem_to_str: Callable,
                           max_block_size: int = 2**8,
                           do_labeling=False):
        # returns a list of strings, which are the references to each vector created in the same order as vectors
        # ls is a list of vectors
        references = []
        blocks = []
        for ls in vectors:
            if len(blocks) == 0 or (len(ls) + len(blocks[-1][1]) > max_block_size):
                vec_name = array_name + "_" + str(len(blocks))
                blocks.append((vec_name, []))
            references.append("&{block_name}[{block_index}]".format(
                block_name=blocks[-1][0], block_index=str(len(blocks[-1][1]))
            ))
            blocks[-1][1].extend(ls)
        for vec_name, block in blocks:
            self.insert_vector(array_type, vec_name, block, elem_to_str, do_labeling=do_labeling)
        return(references)

    # hashmap_name = name.upper() + "_" + mp_key[0].name + "_" + str(mp_key[1]) + "_HASH_TABLE"
    def build_and_insert_hashmap(self,
                                 hashmap_name: str,
                                 payload_array_type: str,
                                 mp: Dict,
                                 hash_string: Callable[[str], int],
                                 stem_key_index:int=0):
        # assert that it is a map from strings to lists
        assert all(isinstance(k, str) and isinstance(mp[k], list) for k in mp)

        from math import log2
        size = int(2.0 + log2(len(mp) + 2))
        TABLE: List[Optional[Tuple[str, List]]] = [None for _ in range(2 ** size)]

        for string in mp:
            indx = hash_string(string) % len(TABLE)
            while TABLE[indx] is not None:
                indx = (indx + 1) % len(TABLE)
            TABLE[indx] = (string, mp[string])

        strings = list(mp)
        payload_vectors = [mp[string] for string in strings]
        payload_name = hashmap_name + "_PAYLOAD_VECTOR"

        references = baked_output.insert_multivector(
            payload_array_type + "*",
            payload_name,
            payload_vectors,
            lambda key:  key.cpp_ref_str,
            do_labeling=False
        )
        references = {string: reference for string, reference in zip(strings, references)}

        hashtable_block_array_str = baked_output.insert_blocked_array(
            "HashTableCell< {payload_array_type} >".format(payload_array_type=payload_array_type),
            hashmap_name,
            TABLE,
            lambda cell:
            "HashTableCell< {payload_array_type} >(NULL, 0, 0x80000000)".format(
                payload_array_type=payload_array_type
            )
            if cell is None else
            "HashTableCell< {payload_array_type} >({payload_ptr}, {payload_len}, {hash}U)".format(
                payload_array_type=payload_array_type,
                payload_ptr=references[cell[0]],
                payload_len=len(cell[1]),
                hash=hash_string(cell[0])
            ),
            max_block_size_exp=MAX_HASHTABLE_BLOCK_SIZE_EXP,
            do_labeling=False
        )
        return "HashTable< {payload_array_type} >({array}, {item_ct_log2}, {key_indx})".format(
            payload_array_type=payload_array_type,
            array=hashtable_block_array_str,
            item_ct_log2=size,
            key_indx=stem_key_index,
        )


def hash_string(string):
    hash = 5381
    for c in string:
        hash = ((hash << 5) + hash) + ord(c)  # ; /* hash * 33 + c */
    return hash % (2 ** 32)  # // this hash should always have a 0 in the first bit

baked_output = BakedOutput()
baked_output.header.write('#ifndef SRC_BAKED_H_\n#define SRC_BAKED_H_\n#include <string>\n'
                          '#include "data_structures.h"\n#include "generated.h"\n'
                          'using namespace std;\n')
# we will add the atrribute .cpp_str_ref to get refer to a pointer to an elemnt in an array
# for example, if Lemma.cpp_str_ref would be "$LEMMA_ARRAY_3[100] if i

def add_baked_dictionary(d, name):
    POS_DATA_MP = {pos: [] for pos in PartOfSpeech}
    for key in d.dictionary_keys:
        POS_DATA_MP[key.part_of_speech].append(key.pos_data)

    # glue together the repeated elements
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
        POS_DATA_MP[pos] = DONE

    for pos in POS_DATA_MP:
        if len(POS_DATA_MP[pos]) == 0:
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
            for elem in POS_DATA_MP[pos]
        ]
        array_type = POS_DATA_MP[pos][0].__class__.__name__
        array_name = name.upper() + "_" + pos.name + "_ARRAY"
        baked_output.insert_vector(array_type, array_name, STRS, lambda s:s)

    references = baked_output.insert_multivector(
        "DictionaryKey",
        "{}_KEYS".format(name.upper()),
        [lemma.dictionary_keys for lemma in d.dictionary_lemmata],
        lambda key: 'DictionaryKey("{s1}", "{s2}", "{s3}", "{s4}", '
                    '{part_of_speech}, {dict_data}, {lemma_ptr})'.format(
            part_of_speech=int(key.part_of_speech),
            s1=key.stems[0] if key.stems[0] is not None else "zzz",
            s2=key.stems[1] if key.stems[1] is not None else "zzz",
            s3=key.stems[2] if key.stems[2] is not None else "zzz",
            s4=key.stems[3] if key.stems[3] is not None else "zzz",
            dict_data="&" + name.upper() + "_" + key.part_of_speech.name + "_ARRAY[" + str(key.pos_data.array_index) + "]",
            lemma_ptr=key.lemma.cpp_ref_str,
            lb="{",
            rb="}"
        ),
        do_labeling=True
    )
    for lemma, key_vec_ref in zip(d.dictionary_lemmata, references):
        lemma.key_vec_ref=key_vec_ref

    lemmata_array_st = baked_output.insert_blocked_array(
        "DictionaryLemma",
        "{}_LEMMATA".format(name.upper()),
        d.dictionary_lemmata,
        lambda lemma: 'DictionaryLemma({part_of_speech}, {translation_metadata}, "{definition}", '
                      '"{extra_def}", {index}, {keys}, {keys_len})'.format(
            part_of_speech=int(lemma.part_of_speech),  # .name,
            translation_metadata='"{}{}{}{}{}"'.format(
                int(lemma.translation_metadata.age),
                lemma.translation_metadata.area,
                lemma.translation_metadata.geo,
                int(lemma.translation_metadata.frequency),
                lemma.translation_metadata.source),
            definition=lemma.definition.replace("\"", "\\\"").replace("\n", "\\n"),
            extra_def=lemma.extra_def if lemma.extra_def else "",
            index=lemma.index,
            keys=lemma.key_vec_ref,
            keys_len=len(lemma.dictionary_keys),
            lb="{",
            rb="}"
        ),
        MAX_LEMMA_LIST_BLOCK_SIZE_EXP,
        do_labeling=True
    )

    table_content = [["HashTable<DictionaryKey>()" for stem_index in [1,2,3,4]] for pos in PartOfSpeech]
    for (pos, stem_key_indx), mp in d._stem_map.items():
        hashmap_name = name.upper() + "_" + pos.name + "_" + str(stem_key_indx) + "_HASH_TABLE"
        hash_table_setup_str = baked_output.build_and_insert_hashmap(
            hashmap_name, "DictionaryKey", mp, hash_string, stem_key_indx-1)
        table_content[pos][stem_key_indx-1] = hash_table_setup_str

    baked_output.add_exact_vector_2d(
        "HashTable<DictionaryKey>",
        "{}_HASHTABLES".format(name.upper()),
        table_content
    )
    baked_output.add_cpp("const BakedDictionaryStemCollection BAKED_" + name.upper() + " = BakedDictionaryStemCollection({tables}, {lemmas});\n".format(
        tables = name.upper()+ "_HASHTABLES",
        lemmas = lemmata_array_st
    ))


def add_baked_inflection_rules(d, name):
    POS_DATA_MP = {pos: [] for pos in PartOfSpeech}
    # print(d._map_ending_infls)
    for ending in d._map_ending_infls:  # d._inflection_pos_map
        for key in d._map_ending_infls[ending]:
            POS_DATA_MP[key.part_of_speech].append(key.pos_data)

    # glue together the repeated elements
    for pos in POS_DATA_MP:
        DONE = []
        i = 0
        for pos_data in POS_DATA_MP[pos]:
            # print(pos_data.__dict__)
            for elem in DONE:
                if elem == pos_data:
                    pos_data.array_index = elem.array_index
                    break
            else:
                DONE.append(pos_data)
                pos_data.array_index = i
                i+=1
        POS_DATA_MP[pos] = DONE

    # print(POS_DATA_MP)
    #
    for pos in POS_DATA_MP:
        if len(POS_DATA_MP[pos]) == 0:
            continue

        def f_s(elem, name):
            at = getattr(elem, name.lstrip("_"))
            if isinstance(at, StringMappedEnum):
                return str(int(at))  # at.__class__.__name__ + "::" + at.name
            if isinstance(at, str):
                return "\"{}\"".format(at)
            return str(at)

        STRS = [
            elem.__class__.__name__ + "(" +
            (", ".join([f_s(elem, name) for name, type in elem.__class__.ordered_vals]))
            + ")"
            for elem in POS_DATA_MP[pos]
        ]
        array_type = POS_DATA_MP[pos][0].__class__.__name__
        array_name = name.upper() + "_INFL_" + pos.name + "_ARRAY"
        baked_output.insert_vector(array_type, array_name, STRS, lambda s:s)

    # we want the following
    # a list of all inflections
    # a hash table maping endings to inflections
    # for each pos, a multidimentional arrays maping tuples to inflection rules
    # infl_rule = InflectionRule()

    array_name = name.upper() + "_INFLECTION_RULES"
    inflection_rules = []
    for ending in d._map_ending_infls:  # d._inflection_pos_map
        for rule in d._map_ending_infls[ending]:
            inflection_rules.append(rule)
    inflection_rule_array_str = baked_output.insert_blocked_array(
        "InflectionRule",
        array_name,
        inflection_rules,
        lambda infl_rule: 'InflectionRule("{ending}", {pos}, {pos_data}, {stem_key}, {index}, "{age}{frequency}")'.format(
            ending=infl_rule.ending,
            pos = int(infl_rule.part_of_speech),
            pos_data = "&" + name.upper() + "_INFL_" + infl_rule.part_of_speech.name + "_ARRAY[" + str(infl_rule.pos_data.array_index) + "]",
            stem_key=infl_rule.stem_key,
            index=infl_rule.index,
            age=int(infl_rule.metadata[0]),
            frequency=int(infl_rule.metadata[1])
        ),
        max_block_size_exp=MAX_INFL_LIST_BLOCK_SIZE_EXP,
        do_labeling=True
    )
    hashmap_name = name.upper() + "_INFLECTION_RULE_ENDING_LOOKUP"
    inflection_hashtable_ending_rules_str = baked_output.build_and_insert_hashmap(
        hashmap_name,
        "InflectionRule",
        d._map_ending_infls,
        hash_string
    )

    ref_str  = lambda infl: "NULL" if infl is None else infl.cpp_ref_str

    noun_rules = [[[[[
        ref_str(d.get_noun_inflection_rule(declention, declention_varient, gender, _case,number))
        for number in Number] for _case in Case] for gender in Gender]
        for declention_varient in range(10)] for declention in range(10)]
    number_rules = [[[[[[
        ref_str(d.get_number_inflection_rule(declention, declention_varient, gender, _case, number, number_kind))
        for number_kind in NumberKind] for number in Number] for _case in Case] for gender in Gender]
        for declention_varient in range(10)] for declention in range(10)]
    pronoun_rules = [[[[[
        ref_str(d.get_pronoun_inflection_rule(declention, declention_varient, gender, _case,number))
        for number in Number] for _case in Case] for gender in Gender]
        for declention_varient in range(10)] for declention in range(10)]
    # const InflectionRule *number_rules[10][10][MAX_Gender][MAX_Case][MAX_Number][MAX_NumberKind];
    # const InflectionRule *pronoun_rules[10][10][MAX_Gender][MAX_Case][MAX_Number];
    adjective_rules = [[[[[[
        ref_str(d.get_adjective_inflection_rule(declention, declention_varient, gender, _case,number, adjective_kind))
        for adjective_kind in AdjectiveKind] for number in Number] for _case in Case] for gender in Gender]
        for declention_varient in range(10)] for declention in range(10)]
    verb_rules = [[[[[[[
        ref_str(d.get_verb_inflection_rule(conjugation, conjugation_varient, number, person, voice, tense, mood))
        for mood in Mood] for tense in Tense] for voice in Voice] for person in Person] for number in Number]
        for conjugation_varient in range(10)] for conjugation in range(10)]
    # const InflectionRule *adjective_rules[10][10][MAX_Gender][MAX_Case][MAX_Number][MAX_AdjectiveKind];
    # const InflectionRule *verb_rules[10][10][MAX_Number][MAX_Person][MAX_Voice][MAX_Tense][MAX_Mood];
    participle_rules = [[[[[[
        ref_str(d.get_participle_inflection_rule(conjugation, conjugation_varient, number, _case, voice, tense))
        for tense in Tense] for voice in Voice] for _case in Case] for number in Number]
        for conjugation_varient in range(10)] for conjugation in range(10)]
    # const InflectionRule *participle_rules[10][10][MAX_Number][MAX_Case][MAX_Voice][MAX_Tense];
    adverb_rules = [[
        ref_str(d.get_adverb_inflection_rule(adj_kind1, adj_kind2))
        for adj_kind2 in AdjectiveKind] for adj_kind1 in AdjectiveKind]
    # const InflectionRule *adverb_rules[MAX_AdjectiveKind][MAX_AdjectiveKind];
    preposition_rule = ref_str(d.get_preposition_inflection_rule())
    conjunction_rule = ref_str(d.get_conjunction_inflection_rule())
    interjection_rule = ref_str(d.get_interjection_inflection_rule())

    # noun_rules,number_rules ,pronoun_rules,adjective_rules,verb_rules,participle_rules,adverb_rules, preposition_rule, conjunction_rule, interjection_rule
    # baked_output.add_exact_multidim_array("InflectionRule *",
    #                                       name.upper() + "_BAKED_NOUN_RULES",
    #                                       noun_rules)
    flatten = lambda l: [item for sublist in l for item in flatten(sublist)] if isinstance(l[0], list) else l

    # print(len(flatten(noun_rules[0])), len(flatten(noun_rules[1][0])), len(flatten(noun_rules[1][1][0]))
    #       , len(flatten(noun_rules[1][1][1][0])))
    # print(flatten(noun_rules[1][1][1]))
    # print(noun_rules[1][1][1])
    # ,"\n",noun_rules[1][1][1],"\n",noun_rules[1][1][2])  #, len(flatten(adverb_rules)), [len(flatten(sublist)) for sublist in adverb_rules])
    # 0/0
    baked_output.insert_vector("InflectionRule *",
                               name.upper() + "_BAKED_NOUN_RULES",
                               flatten(noun_rules), lambda s: s)
    baked_output.insert_vector("InflectionRule *",
                               name.upper() + "_BAKED_NUMBER_RULES",
                               flatten(number_rules), lambda s: s)
    baked_output.insert_vector("InflectionRule *",
                               name.upper() + "_BAKED_PRONOUN_RULES",
                               flatten(pronoun_rules), lambda s: s)
    baked_output.insert_vector("InflectionRule *",
                               name.upper() + "_BAKED_ADJECTIVE_RULES",
                               flatten(adjective_rules), lambda s: s)
    baked_output.insert_vector("InflectionRule *",
                               name.upper() + "_BAKED_VERB_RULES",
                               flatten(verb_rules), lambda s: s)
    baked_output.insert_vector("InflectionRule *",
                               name.upper() + "_BAKED_PARTICIPLE_RULES",
                               flatten(participle_rules), lambda s: s)
    baked_output.insert_vector("InflectionRule *",
                                          name.upper() + "_BAKED_ADVERB_RULES",
                                          flatten(adverb_rules), lambda s:s)

    baked_output.add_cpp("const BakedInflectionRuleCollection BAKED_" + name.upper() +
                         " = BakedInflectionRuleCollection({mp}, {ls},{noun_rules}, {number_rules},"
                         "{pronoun_rules},{adjective_rules},{verb_rules},{participle_rules},"
                         "{adverb_rules},{preposition_rule},{conjunction_rule},{interjection_rule});\n".format(
        mp = inflection_hashtable_ending_rules_str,
        ls = inflection_rule_array_str,
        noun_rules=name.upper() + "_BAKED_NOUN_RULES",
        number_rules=name.upper() + "_BAKED_NUMBER_RULES",
        pronoun_rules=name.upper() + "_BAKED_PRONOUN_RULES",
        adjective_rules= name.upper() + "_BAKED_ADJECTIVE_RULES",
        verb_rules= name.upper() + "_BAKED_VERB_RULES",
        participle_rules= name.upper() + "_BAKED_PARTICIPLE_RULES",
        adverb_rules= name.upper() + "_BAKED_ADVERB_RULES",  # "NULL",
        preposition_rule=preposition_rule,
        conjunction_rule=conjunction_rule,
        interjection_rule=interjection_rule,
    ))
    # references = baked_output.insert_multivector(
    #     "DictionaryKey",
    #     "{}_KEYS".format(name.upper()),
    #     [lemma.dictionary_keys for lemma in d.dictionary_lemmata],
    #     lambda key: 'DictionaryKey("{s1}", "{s2}", "{s3}", "{s4}", '
    #                 '{part_of_speech}, {dict_data}, {lemma_ptr})'.format(
    #         part_of_speech=int(key.part_of_speech),
    #         s1=key.stems[0] if key.stems[0] is not None else "zzz",
    #         s2=key.stems[1] if key.stems[1] is not None else "zzz",
    #         s3=key.stems[2] if key.stems[2] is not None else "zzz",
    #         s4=key.stems[3] if key.stems[3] is not None else "zzz",
    #         dict_data="&" + name.upper() + "_" + key.part_of_speech.name + "_ARRAY[" + str(key.pos_data.array_index) + "]",
    #         lemma_ptr=key.lemma.cpp_ref_str,
    #         lb="{",
    #         rb="}"
    #     ),
    #     do_labeling=True
    # )
    # for lemma, key_vec_ref in zip(d.dictionary_lemmata, references):
    #     lemma.key_vec_ref=key_vec_ref
    #
    # lemmata_array_st = baked_output.insert_blocked_array(
    #     "DictionaryLemma",
    #     "{}_LEMMATA".format(name.upper()),
    #     d.dictionary_lemmata,
    #     lambda lemma: 'DictionaryLemma({part_of_speech}, {translation_metadata}, "{definition}", '
    #                   '"{extra_def}", {index}, {keys}, {keys_len})'.format(
    #         part_of_speech=int(lemma.part_of_speech),  # .name,
    #         translation_metadata='"{}{}{}{}{}"'.format(
    #             int(lemma.translation_metadata.age),
    #             lemma.translation_metadata.area,
    #             lemma.translation_metadata.geo,
    #             int(lemma.translation_metadata.frequency),
    #             lemma.translation_metadata.source),
    #         definition=lemma.definition.replace("\"", "\\\"").replace("\n", "\\n"),
    #         extra_def=lemma.extra_def if lemma.extra_def else "",
    #         index=lemma.index,
    #         keys=lemma.key_vec_ref,
    #         keys_len=len(lemma.dictionary_keys),
    #         lb="{",
    #         rb="}"
    #     ),
    #     MAX_LEMMA_LIST_BLOCK_SIZE_EXP,
    #     do_labeling=True
    # )
    #
    # def hash_string(str):
    #     hash = 5381
    #     for c in str:
    #         hash = ((hash << 5) + hash) + ord(c)  # ; /* hash * 33 + c */
    #     return hash % (2 ** 32)  # // this hash should always have a 0 in the first bit
    #
    # table_content = [["HashTable<DictionaryKey>()" for stem_index in [1,2,3,4]] for pos in PartOfSpeech]
    # for (pos, stem_key_indx), mp in d._stem_map.items():
    #     hashmap_name = name.upper() + "_" + pos.name + "_" + str(stem_key_indx) + "_HASH_TABLE"
    #     hash_table_setup_str = baked_output.build_and_insert_hashmap(
    #         hashmap_name, "DictionaryKey", mp, hash_string, stem_key_indx-1)
    #     table_content[pos][stem_key_indx-1] = hash_table_setup_str
    #
    # baked_output.add_exact_vector_2d(
    #     "HashTable<DictionaryKey>",
    #     "{}_HASHTABLES".format(name.upper()),
    #     table_content
    # )
    # baked_output.add_cpp("const BakedDictionaryStemCollection BAKED_" + name.upper() + " = BakedDictionaryStemCollection({tables}, {lemmas});\n".format(
    #     tables = name.upper()+ "_HASHTABLES",
    #     lemmas = lemmata_array_st
    # ))

short=True

from core_files.whitakers_words import init
ww, _ = init(PATH, fast=False, short=short)
add_baked_dictionary(ww, "WW")
add_baked_inflection_rules(ww, "WW_INFL_RULES")

from core_files.joined_formater_html import init
joined, _ = init(PATH, fast=False, short=short)
add_baked_dictionary(joined, "JOINED")

baked_output.close()
