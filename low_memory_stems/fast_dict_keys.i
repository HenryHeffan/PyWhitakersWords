%module fast_dict_keys
%{ 
    /* Every thing in this file is being copied in  
     wrapper file. We include the C header files necessary 
     to compile the interface */

	#include "generated.h"
	#include "baked.h"
	#include "data_structures.h"
	#include "generic_data_structures.h"
%} 

%include <std_string.i>

%rename(__add__) operator+;
%rename(__sub__) operator-;
%rename(__mult__) operator*;
%rename(__mult__) operator==;
%rename(__len__) len;
%rename(__str__) toString;
%rename(__getitem__) get;
%rename(__contains__) contains;
%rename(__contains__) has;

%ignore operator<<;
%ignore operator>>;
%ignore StemGroup(const char*, const char*, const char*, const char*);
%ignore HashTable(const HashTableCell **, const unsigned long, const int);

%include "generated.h"
%include "generic_data_structures.h"

%template(ArrayViewDictionaryKey)     ArrayView<DictionaryKey>;
%template(ArrayViewInflectionRule)    ArrayView<InflectionRule>;

%template(PtrArrayViewDictionaryKey)  PtrArrayView<DictionaryKey>;
%template(PtrArrayViewInflectionRule) PtrArrayView<InflectionRule>;

%template(BlockedLemmaArrayView)   BlockedArrayView<DictionaryLemma>;
%template(BlockedInflectionRuleArrayView)   BlockedArrayView<InflectionRule>;

%template(HashTable_to_DictionaryKeyList)    HashTable<DictionaryKey>;
%template(HashTable_to_InflectionRuleList)   HashTable<InflectionRule>;

%include "data_structures.h"



%pythoncode %{

def implement_properties(c):
    for k in list(c.__dict__):
        if k.startswith("_property_"):
            f = getattr(c, k)
            delattr(c, k)
            setattr(c, k[len("_property_"):], property(f) )

implement_properties(DictionaryKey)
implement_properties(DictionaryLemma)
implement_properties(InflectionRule)

# SETUP DICTIONARY_KEY

def make_form(self, infl, default="NULL_FORM"):
    if infl is None or self.stems[infl.stem_key - 1] is None:
        return default
    stem = self.stems[infl.stem_key - 1]
    assert stem is not None
    return stem + infl.ending

def _get_pos_data_dict_key(key):
    import core_files.entry_and_inflections
    if key.part_of_speech == core_files.entry_and_inflections.PartOfSpeech.Verb:
        return key.verb_data
    if key.part_of_speech == core_files.entry_and_inflections.PartOfSpeech.Noun:
        return key.noun_data
    if key.part_of_speech == core_files.entry_and_inflections.PartOfSpeech.Pronoun:
        return key.pronoun_data
    if key.part_of_speech == core_files.entry_and_inflections.PartOfSpeech.Adjective:
        return key.adjective_data
    if key.part_of_speech == core_files.entry_and_inflections.PartOfSpeech.Adverb:
        return key.adverb_data
    if key.part_of_speech == core_files.entry_and_inflections.PartOfSpeech.Conjunction:
        return key.conjunction_data
    if key.part_of_speech == core_files.entry_and_inflections.PartOfSpeech.Preposition:
        return key.preposition_data
    if key.part_of_speech == core_files.entry_and_inflections.PartOfSpeech.Interjection:
        return key.interjection_data
    if key.part_of_speech == core_files.entry_and_inflections.PartOfSpeech.Number:
        return key.number_data
    if key.part_of_speech == core_files.entry_and_inflections.PartOfSpeech.Packon:
        return key.packon_data
    return None

DictionaryKey.pos_data = property(lambda self: _get_pos_data_dict_key(self))
DictionaryKey.pro_pack_data = property(lambda self: self.pos_data)
setattr(DictionaryKey, "make_form", make_form)

# SETUP INFLECTION_RULE

def _get_pos_data_infl_rule(inlf):
    import core_files.entry_and_inflections
    if inlf.part_of_speech == core_files.entry_and_inflections.PartOfSpeech.Verb:
        return inlf.verb_data
    if inlf.part_of_speech == core_files.entry_and_inflections.PartOfSpeech.Noun:
        return inlf.noun_data
    if inlf.part_of_speech == core_files.entry_and_inflections.PartOfSpeech.Pronoun:
        return inlf.pronoun_data
    if inlf.part_of_speech == core_files.entry_and_inflections.PartOfSpeech.Adjective:
        return inlf.adjective_data
    if inlf.part_of_speech == core_files.entry_and_inflections.PartOfSpeech.Adverb:
        return inlf.adverb_data
    if inlf.part_of_speech == core_files.entry_and_inflections.PartOfSpeech.Conjunction:
        return inlf.conjunction_data
    if inlf.part_of_speech == core_files.entry_and_inflections.PartOfSpeech.Preposition:
        return inlf.preposition_data
    if inlf.part_of_speech == core_files.entry_and_inflections.PartOfSpeech.Interjection:
        return inlf.interjection_data
    if inlf.part_of_speech == core_files.entry_and_inflections.PartOfSpeech.Number:
        return inlf.number_data
    if inlf.part_of_speech == core_files.entry_and_inflections.PartOfSpeech.Packon:
        return inlf.packon_data
    if inlf.part_of_speech == core_files.entry_and_inflections.PartOfSpeech.Participle:
        return inlf.participle_data
    if inlf.part_of_speech == core_files.entry_and_inflections.PartOfSpeech.Supine:
        return inlf.supine_data
    return None

InflectionRule.pos_data = property(lambda self: _get_pos_data_infl_rule(self))
InflectionRule.pro_pack_data = property(lambda self: self.pos_data)

def make_split_word_form(inlf, word):
    assert word.lower().endswith(inlf.ending)
    if inlf.ending == "":
        return word
    else:
        return word[:-len(inlf.ending)] + "." + inlf.ending
setattr(InflectionRule, "make_split_word_form", make_split_word_form)


#def _PACKON_accepts_tackon(packon, tackon):
#    return tackon is not None and tackon.tackon == packon.tackon_str and tackon.pos == core_files.entry_and_inflections.PartOfSpeech.Packon

import core_files.entry_and_inflections
setattr(PackonDictData, "accepts_tackon",
        lambda self, tackon: core_files.entry_and_inflections.PackonDictData.accepts_tackon(self, tackon))

def _get_stem_stem_group(stem_group, indx):
    if indx not in {0,1,2,3}:
        raise ValueError()
    e = stem_group._get_elem(indx)
    return e if e != "zzz" else None

setattr(StemGroup, "__getitem__", _get_stem_stem_group)
setattr(StemGroup, "__iter__", lambda s: iter([s[i] for i in [0,1,2,3]]))


class MyListIterator:
    def __init__(self, arr, l):
        self.arr = arr
        self.l = l
        self.i = 0

    def __next__(self):
        i = self.i
        if i >= self.l:
            raise StopIteration()
        self.i +=1
        return self.arr[i]

    next = __next__

    def __iter__(self):
        return self

def initialize_arrayview(c):
    def _get_item_helper(inst, i):
        if isinstance(i, int):
            return inst._get_index(i)
        elif isinstance(i, slice) and hasattr(inst, "_get_sub_to_end_array"):
            assert i.stop is None and i.step is None
            return getattr(inst, "_get_sub_to_end_array")(i.start)
        else:
            raise ValueError()
    c.__iter__ = lambda self: MyListIterator(self, len(self))
    setattr(c, "__getitem__", _get_item_helper)

for c in [ArrayViewDictionaryKey, ArrayViewInflectionRule, PtrArrayViewDictionaryKey,
          PtrArrayViewInflectionRule, BlockedLemmaArrayView, BlockedInflectionRuleArrayView]:
    initialize_arrayview(c)

from core_files.base_data_structures import POS_DICT_ENTRY_CLASS_MP, POS_INFL_ENTRY_CLASS_MP

for c in list(POS_DICT_ENTRY_CLASS_MP.values()) + list(POS_INFL_ENTRY_CLASS_MP.values()):
    c = globals()[c.__name__]
    if hasattr(c, "_case"):
        setattr(c, "case", getattr(c, "_case"))
        delattr(c, "_case")

for c in POS_INFL_ENTRY_CLASS_MP.values():
    nc = globals()[c.__name__]
    for name in c.__dict__:
        if not hasattr(nc, name):
            setattr(nc, name, getattr(c, name))

%}

