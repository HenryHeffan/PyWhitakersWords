%module fast_dict_keys
%{ 
    /* Every thing in this file is being copied in  
     wrapper file. We include the C header files necessary 
     to compile the interface */

	#include "generated.h"
	#include "data_structures.h"
%} 

%include <std_vector.i>
%include <std_string.i>

%template(ListKeys) std::vector<DictionaryKey*>;

%rename(__add__) operator+;
%rename(__sub__) operator-;
%rename(__mult__) operator*;
%rename(__mult__) operator==;
%rename(__len__) len;
%rename(__str__) toString;
%rename(__getitem__) get;
%rename(__contains__) contains;
%ignore operator<<;
%ignore operator>>;

%include "generated.h"
%include "data_structures.h"

%pythoncode %{

StringDictKeyMapView.thisown=1

# DictionaryKeyListView.thisown=1

def make_form(self, infl, default="NULL_FORM"):
    if infl is None or self.stems[infl.stem_key - 1] is None:
        return default
    stem = self.stems[infl.stem_key - 1]
    assert stem is not None
    return stem + infl.ending

from enum import IntEnum
def enum(prefix):
    tmpD = {k:v for k,v in globals().items() if k.startswith(prefix + '_')}
    for k,v in tmpD.items():
        del globals()[k]
    tmpD = {k[len(prefix)+1:]:v for k,v in tmpD.items()}
    globals()[prefix] = IntEnum(prefix,tmpD)

%}

%pythoncode %{

DictionaryKey.verb_data = property(lambda self: self._verb_data())
DictionaryKey.noun_data = property(lambda self: self._noun_data())
DictionaryKey.pronoun_data = property(lambda self: self._pronoun_data())
DictionaryKey.adjective_data = property(lambda self: self._adjective_data())
DictionaryKey.adverb_data = property(lambda self: self._adverb_data())
DictionaryKey.conjunction_data = property(lambda self: self._conjunction_data())
DictionaryKey.preposition_data = property(lambda self: self._preposition_data())
DictionaryKey.interjection_data = property(lambda self: self._interjection_data())
DictionaryKey.number_data = property(lambda self: self._number_data())
DictionaryKey.packon_data = property(lambda self: self._packon_data())
def _get_pos_data_dict_key(key):
    if key.part_of_speech == PartOfSpeech.Verb:
        return key.verb_data
    if key.part_of_speech == PartOfSpeech.Noun:
        return key.noun_data
    if key.part_of_speech == PartOfSpeech.Pronoun:
        return key.pronoun_data
    if key.part_of_speech == PartOfSpeech.Adjective:
        return key.adjective_data
    if key.part_of_speech == PartOfSpeech.Adverb:
        return key.adverb_data
    if key.part_of_speech == PartOfSpeech.Conjunction:
        return key.conjunction_data
    if key.part_of_speech == PartOfSpeech.Preposition:
        return key.preposition_data
    if key.part_of_speech == PartOfSpeech.Interjection:
        return key.interjection_data
    if key.part_of_speech == PartOfSpeech.Number:
        return key.number_data
    if key.part_of_speech == PartOfSpeech.Packon:
        return key.packon_data
    return None
DictionaryKey.pos_data = property(lambda self: _get_pos_data_dict_key(self))

PackonDictData.accepts_tackon = lambda self, tackon: tackon is not None and tackon.tackon == self.tackon_str and tackon.pos == PartOfSpeech.Packon

DictionaryKey.make_form = make_form

StemGroup.__getitem__ = lambda self, i: self._get_elem(i) if self._get_elem(i) != "zzz" else None

from core_files.utils import load_utf_str
DictionaryLemma.html_data = property(lambda x: load_utf_str(x._stored_html_data))

# remove a bunch of unneeded constants
enum("Person"); Person.str_val=property(lambda x: str_val_Person(x))
enum("Number"); Number.str_val=property(lambda x: str_val_Number(x))
enum("Tense"); Tense.str_val=property(lambda x: str_val_Tense(x))
enum("Voice"); Voice.str_val=property(lambda x: str_val_Voice(x))
enum("Mood"); Mood.str_val=property(lambda x: str_val_Mood(x))
enum("Gender"); Gender.str_val=property(lambda x: str_val_Gender(x))
enum("Case"); Case.str_val=property(lambda x: str_val_Case(x))
enum("PartOfSpeech"); PartOfSpeech.str_val=property(lambda x: str_val_PartOfSpeech(x))
enum("VerbKind"); VerbKind.str_val=property(lambda x: str_val_VerbKind(x))
enum("NounKind"); NounKind.str_val=property(lambda x: str_val_NounKind(x))
enum("PronounKind"); PronounKind.str_val=property(lambda x: str_val_PronounKind(x))
enum("AdjectiveKind"); AdjectiveKind.str_val=property(lambda x: str_val_AdjectiveKind(x))
enum("NumberKind"); NumberKind.str_val=property(lambda x: str_val_NumberKind(x))
enum("InflectionFrequency"); InflectionFrequency.str_val=property(lambda x: str_val_InflectionFrequency(x))
enum("InflectionAge"); InflectionAge.str_val=property(lambda x: str_val_InflectionAge(x))
enum("DictionaryFrequency"); DictionaryFrequency.str_val=property(lambda x: str_val_DictionaryFrequency(x))
enum("DictionaryAge"); DictionaryAge.str_val=property(lambda x: str_val_DictionaryAge(x))

%}

