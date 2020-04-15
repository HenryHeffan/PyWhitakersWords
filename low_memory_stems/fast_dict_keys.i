%module fast_dict_keys
%{ 
    /* Every thing in this file is being copied in  
     wrapper file. We include the C header files necessary 
     to compile the interface */

	#include "generated.h"
	#include "baked.h"
	#include "data_structures.h"
%} 

%include <std_vector.i>
%include <std_string.i>

%template(ListKeys) std::vector<DictionaryKey*>;
%template(ListLemmas) std::vector<DictionaryLemma*>;

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
%include "data_structures.h"


%pythoncode %{

# StringDictKeyMapView.thisown=1

# DictionaryKeyListView.thisown=1

def make_form(self, infl, default="NULL_FORM"):
    if infl is None or self.stems[infl.stem_key - 1] is None:
        return default
    stem = self.stems[infl.stem_key - 1]
    assert stem is not None
    return stem + infl.ending

#from enum import IntEnum
#def enum(prefix):
#    tmpD = {k:v for k,v in globals().items() if k.startswith(prefix + '_')}
#    for k,v in tmpD.items():
#        del globals()[k]
#    tmpD = {k[len(prefix)+1:]:v for k,v in tmpD.items()}
#    globals()[prefix] = IntEnum(prefix,tmpD)


def implement_properties(c):
    for k in list(c.__dict__):
        if k.startswith("_property_"):
            f = getattr(c, k)
            delattr(c, k)
            setattr(c, k[len("_property_"):], property(f) )
            # print("ADDED",c, k[len("_property_"):])
        # else:
        # print("SKIPPED",c, k)

implement_properties(DictionaryKey)
implement_properties(DictionaryLemma)

# DictionaryKey.verb_data = property(lambda self: self._property_verb_data())
# DictionaryKey.noun_data = property(lambda self: self._property_noun_data())
# DictionaryKey.pronoun_data = property(lambda self: self._property_pronoun_data())
# DictionaryKey.adjective_data = property(lambda self: self._property_adjective_data())
# DictionaryKey.adverb_data = property(lambda self: self._property_adverb_data())
# DictionaryKey.conjunction_data = property(lambda self: self._property_conjunction_data())
# DictionaryKey.preposition_data = property(lambda self: self._property_preposition_data())
# DictionaryKey.interjection_data = property(lambda self: self._property_interjection_data())
# DictionaryKey.number_data = property(lambda self: self._property_number_data())
# DictionaryKey.packon_data = property(lambda self: self._property_packon_data())

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
# ("POS_DATA", DictionaryKey.pos_data)
setattr(DictionaryKey, "make_form", make_form)

def _PACKON_accepts_tackon(packon, tackon):
    import core_files.entry_and_inflections
    return tackon is not None and tackon.tackon == packon.tackon_str and tackon.pos == core_files.entry_and_inflections.PartOfSpeech.Packon
setattr(PackonDictData, "accepts_tackon", _PACKON_accepts_tackon)

def _get_stem_stem_group(stem_group, indx):
    if indx not in {0,1,2,3}:
        raise ValueError()
    e = stem_group._get_elem(indx)
    return e if e != "zzz" else None

setattr(StemGroup, "__getitem__", _get_stem_stem_group)
setattr(StemGroup, "__iter__", lambda s: iter([s[i] for i in [0,1,2,3]]))


extract_html_data_func = lambda s: s
def set_extract_html_data_func(func):
    # the function should take in a string, _stored_html_data, and output a string
    assert func is not None
    global extract_html_data_func
    extract_html_data_func = func
setattr(DictionaryLemma, "html_data", property(lambda x: extract_html_data_func(x.stored_html_data)))

from core_files.utils import load_utf_str
DictionaryLemma.html_data = property(lambda x: x.stored_html_data)
# print("HAS ATTR", hasattr(DictionaryLemma, "html_data"))
# remove a bunch of unneeded constants
# enum("Person"); Person.str_val=property(lambda x: str_val_Person(x))
# enum("Number"); Number.str_val=property(lambda x: str_val_Number(x))
# enum("Tense"); Tense.str_val=property(lambda x: str_val_Tense(x))
# enum("Voice"); Voice.str_val=property(lambda x: str_val_Voice(x))
# enum("Mood"); Mood.str_val=property(lambda x: str_val_Mood(x))
# enum("Gender"); Gender.str_val=property(lambda x: str_val_Gender(x))
# enum("Case"); Case.str_val=property(lambda x: str_val_Case(x))
# enum("PartOfSpeech"); PartOfSpeech.str_val=property(lambda x: str_val_PartOfSpeech(x))
# enum("VerbKind"); VerbKind.str_val=property(lambda x: str_val_VerbKind(x))
# enum("NounKind"); NounKind.str_val=property(lambda x: str_val_NounKind(x))
# enum("PronounKind"); PronounKind.str_val=property(lambda x: str_val_PronounKind(x))
# enum("AdjectiveKind"); AdjectiveKind.str_val=property(lambda x: str_val_AdjectiveKind(x))
# enum("NumberKind"); NumberKind.str_val=property(lambda x: str_val_NumberKind(x))
# enum("InflectionFrequency"); InflectionFrequency.str_val=property(lambda x: str_val_InflectionFrequency(x))
# enum("InflectionAge"); InflectionAge.str_val=property(lambda x: str_val_InflectionAge(x))
# enum("DictionaryFrequency"); DictionaryFrequency.str_val=property(lambda x: str_val_DictionaryFrequency(x))
# enum("DictionaryAge"); DictionaryAge.str_val=property(lambda x: str_val_DictionaryAge(x))


class DictionaryKeyListIterator:
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

DictionaryKeyView.__iter__ = lambda self: DictionaryKeyListIterator(self, len(self))
DictionaryKeyPtrView.__iter__ = lambda self: DictionaryKeyListIterator(self, len(self))
def _get_item_DictionaryKeyPtrView_HELPER(keyview, i):
    if isinstance(i, int):
        return keyview._get_index(i)
    elif isinstance(i, slice):
        assert i.stop is None and i.step is None
        return keyview._get_sub_to_end_array(i.start)
    else:
        raise ValueError()
DictionaryKeyPtrView.__getitem__ = _get_item_DictionaryKeyPtrView_HELPER
DictionaryKeyView.__getitem__ = _get_item_DictionaryKeyPtrView_HELPER

%}

