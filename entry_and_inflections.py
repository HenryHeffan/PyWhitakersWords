import re
import enum
from typing import NewType, Tuple, List, Dict, Optional, Any, Union, Generator
from abc import abstractmethod, ABCMeta


# helper functions for formatting strings

def pad_to_len(s: str, l: int) -> str:
    return s + " " * (l - len(s))


def clip_end(s: str, i: int):
    if i == 0:
        return s
    else:
        return s[:-i]


def joined(stem, ending):
    if ending != "":
        return "{}.{}".format(stem, ending)
    else:
        return stem



########################################################################################################################
########################################################################################################################
#                                             Globally Useful Constants                                                #
########################################################################################################################
########################################################################################################################

# This chunk of code creates the enumerations used by DICTLINE and INFLECTS. It uses a helper class, StringMappedEnum,
# which makes it easier to create enumeration which can decoded from strings or output easily into strings


class StringMappedEnum(enum.IntEnum):
    @staticmethod
    @abstractmethod
    def _STR_VALS():
        pass

    @property
    def str_val(self) -> str:
        return {a: b for a, b in self._STR_VALS()}[self]

    @classmethod
    def from_str(cls, s):
        return {b: a for a, b in cls._STR_VALS()}[s.upper()]


class Person(StringMappedEnum):
    X = 0
    First = 1
    Second = 2
    Third = 3

    @staticmethod
    def _STR_VALS():
        return [(Person.X, "0"), (Person.First, "1"), (Person.Second, "2"), (Person.Third, "3")]


class Number(StringMappedEnum):
    X = 0
    Singular = 1
    Plural = 2

    @staticmethod
    def _STR_VALS():
        return [(Number.Singular, "S"), (Number.Plural, "P"), (Number.X, "X")]


class Tense(StringMappedEnum):
    X = 0
    Present = 1
    Imperfect = 2
    Future = 3
    Perfect = 4
    Pluperfect = 5
    FuturePerfect = 6

    @staticmethod
    def _STR_VALS():
        return [(Tense.Present, "PRES"), (Tense.Imperfect, "IMPF"), (Tense.Future, "FUT"),
                (Tense.Perfect, "PERF"), (Tense.Pluperfect, "PLUP"), (Tense.FuturePerfect, "FUTP"), (Tense.X, "X")]


class Voice(StringMappedEnum):
    X = 0
    Active = 1
    Passive = 2

    @staticmethod
    def _STR_VALS():
        return [(Voice.Active, "ACTIVE"), (Voice.Passive, "PASSIVE"), (Voice.X, "X")]


class Mood(StringMappedEnum):
    X = 0
    Indicitive = 1
    Subjunctive = 2
    Imperative = 3
    Infinative = 4

    @staticmethod
    def _STR_VALS():
        return [(Mood.Indicitive, "IND"), (Mood.Subjunctive, "SUB"), (Mood.Imperative, "IMP"), (Mood.Infinative, "INF"), (Mood.X, "X")]


class Gender(StringMappedEnum):
    X = 0
    Male = 1
    Female = 2
    Nueter = 3
    Common = 4

    @staticmethod
    def _STR_VALS():
        return [(Gender.Male, "M"), (Gender.Female, "F"), (Gender.Nueter, "N"), (Gender.Common, "C"), (Gender.X, "X")]

    @staticmethod
    def MFN() -> List['Gender']:
        return [Gender.Male, Gender.Female, Gender.Nueter]



class Case(StringMappedEnum):
    X = 0
    Nominative = 1
    Genative = 2
    Dative = 3
    Accusitive = 4
    Ablative = 5
    Vocative = 6
    Locitive = 7

    @staticmethod
    def _STR_VALS():
        return [(Case.Nominative, "NOM"), (Case.Genative, "GEN"),
                (Case.Dative, "DAT"), (Case.Accusitive, "ACC"),
                (Case.Ablative, "ABL"), (Case.Vocative, "VOC"),
                (Case.Locitive, "LOC"),
                (Case.X, "X")]


ConjugationType = NewType("ConjugationType", int)
ConjugationSubtype = NewType("ConjugationSubtype", int)

DeclentionType = NewType("DeclentionType", int)
DeclentionSubtype = NewType("DeclentionSubtype", int)


class PartOfSpeech(StringMappedEnum):
    X = 0
    Verb = 1
    Noun = 2
    Pronoun = 3
    Adjective = 4
    Adverb = 5
    Conjunction = 6
    Preposition = 7
    Interjection = 8
    Number = 9
    Packon = 10
    Participle = 11
    Supine = 12

    @staticmethod
    def _STR_VALS():
        return [(PartOfSpeech.Verb, "V"),
                (PartOfSpeech.Noun, "N"),
                (PartOfSpeech.Preposition, "PREP"),
                (PartOfSpeech.Interjection, "INTERJ"),
                (PartOfSpeech.Adjective, "ADJ"),
                (PartOfSpeech.Adverb, "ADV"),
                (PartOfSpeech.Conjunction, "CONJ"),
                (PartOfSpeech.Pronoun, "PRON"),
                (PartOfSpeech.Number, "NUM"),
                (PartOfSpeech.Packon, "PACK"),
                (PartOfSpeech.Participle, "VPAR"),
                (PartOfSpeech.Supine, "SUPINE"),
                (PartOfSpeech.X, "X")]


class VerbKind(StringMappedEnum):
    X = 0  # all, none, or unknown
    To_Be = 1  # only the verb TO BE (esse)
    To_Being = 2  # compounds of the verb to be (esse)
    Gen = 3  # verb taking the GENitive
    Dat = 4  # verb taking the DATive
    Abl = 5  # verb taking the ABLative
    Trans = 6  # TRANSitive verb
    Intrans = 7  # INTRANSitive verb
    Impers = 8  # IMPERSonal verb (implied subject 'it', 'they', 'God')
    #  agent implied in action, subject in predicate
    Dep = 9  # DEPonent verb
    #  only passive form but with active meaning
    Semidep = 10  # SEMIDEPonent verb (forms perfect as deponent)
    #  (perfect passive has active force)
    Perfdef = 11  # PERFect DEFinite verb
    #  having only perfect stem, but with present force

    @staticmethod
    def _STR_VALS():
        return [(VerbKind.X, "X"), (VerbKind.To_Be, "TOBE"), (VerbKind.To_Being, "TO_BEING"),
                (VerbKind.Gen, "GEN"), (VerbKind.Dat, "DAT"), (VerbKind.Abl, "ABL"),
                (VerbKind.Trans, "TRANS"), (VerbKind.Intrans, "INTRANS"), (VerbKind.Impers, "IMPERS"),
                (VerbKind.Dep, "DEP"), (VerbKind.Semidep, "SEMIDEP"),(VerbKind.Perfdef, "PERFDEF")]


class NounKind(StringMappedEnum):
    X = 0
    Singular = 1
    Multiple = 2
    Abstract = 3
    Group = 4
    Name = 5
    Person = 6
    Thing = 7
    Locale = 8
    PlaceWhere = 9

    @staticmethod
    def _STR_VALS():
        return [(NounKind.X, "X"), (NounKind.Singular, "S"), (NounKind.Multiple, "M"),
                (NounKind.Abstract, "A"), (NounKind.Group, "G"), (NounKind.Name, "N"),
                (NounKind.Person, "P"), (NounKind.Thing, "T"), (NounKind.Locale, "L"),
                (NounKind.PlaceWhere, "W")]


class PronounKind(StringMappedEnum):
    X = 0
    Personal = 1
    Relative = 2
    Reflexive = 3
    Demonstrative = 4
    Interrogative = 5
    Indefinite = 6
    Adjective = 7

    @staticmethod
    def _STR_VALS():
        return [(PronounKind.X, "X"), (PronounKind.Personal, "PERS"),
                (PronounKind.Relative, "REL"), (PronounKind.Reflexive, "REFLEX"),
                (PronounKind.Demonstrative, "DEMONS"), (PronounKind.Interrogative, "INTERR"),
                (PronounKind.Indefinite, "INDEF"), (PronounKind.Adjective, "ADJECT")]


class NumberKind(StringMappedEnum):
    X = 0
    Cardinal = 1
    Ordinal = 2
    Distributive = 3
    Adverb = 4

    @staticmethod
    def _STR_VALS():
        return [(NumberKind.X, "X"), (NumberKind.Cardinal, "CARD"), (NumberKind.Ordinal, "ORD"),
                (NumberKind.Distributive, "DIST"), (NumberKind.Adverb, "ADVERB")]


class AdjectiveKind(StringMappedEnum):
    X = 0
    Positive = 1
    Compairative = 2
    Superlative = 3

    @staticmethod
    def _STR_VALS():
        return [(AdjectiveKind.X, "X"), (AdjectiveKind.Positive, "POS"), (AdjectiveKind.Compairative, "COMP"),
                (AdjectiveKind.Superlative, "SUPER")]


class InflectionFrequency(StringMappedEnum):
    X = 9  # ("        ", --  X
    A = 7  #  "mostfreq", --  A
    B = 6  #  "sometime", --  B
    C = 5  #  "uncommon", --  C
    D = 4  #  "infreq  ", --  D
    E = 3  #  "rare    ", --  E
    F = 2  #  "veryrare", --  F
    I = 1  #  "inscript", --  I
    @staticmethod
    def _STR_VALS():
        return [(InflectionFrequency.X, "X"),
                (InflectionFrequency.A, "A"),
                (InflectionFrequency.B, "B"),
                (InflectionFrequency.C, "C"),
                (InflectionFrequency.D, "D"),
                (InflectionFrequency.E, "E"),
                (InflectionFrequency.F, "F"),
                (InflectionFrequency.I, "I"),]


class InflectionAge(StringMappedEnum):
    Always = 0  # ("Always  ", --  X
    Archaic = 1  # "Archaic ", --  A
    Early = 2  # "Early   ", --  B
    Classic = 3  # "Classic ", --  C
    Late = 4  # "Late    ", --  D
    Later = 5  # "Later   ", --  E
    Medieval = 6  # "Medieval", --  F
    Scholar = 7  # "Scholar ", --  G
    Modern = 8  # "Modern  "); -- H
    @staticmethod
    def _STR_VALS():
        return [(InflectionAge.Always, "X"),
                (InflectionAge.Archaic, "A"),
                (InflectionAge.Early, "B"),
                (InflectionAge.Classic, "C"),
                (InflectionAge.Late, "D"),
                (InflectionAge.Later, "E"),
                (InflectionAge.Medieval, "F"),
                (InflectionAge.Scholar, "G"),
                (InflectionAge.Modern, "H")]


class DictionaryFrequency(StringMappedEnum):
    X = 10  # ("        ", --  X
    A = 9  #  "veryfreq", --  A
    B = 8  #  "frequent", --  B
    C = 7  #  "common  ", --  C
    D = 6  #  "lesser  ", --  D
    E = 5  #  "uncommon", --  E
    F = 4  #  "veryrare", --  F
    I = 3  #  "inscript", --  I
    J = 2  #  "graffiti", --  J
    N = 1  #  "Pliny   ");--  N
    @staticmethod
    def _STR_VALS():
        return [(DictionaryFrequency.X, "X"),
                (DictionaryFrequency.A, "A"),
                (DictionaryFrequency.B, "B"),
                (DictionaryFrequency.C, "C"),
                (DictionaryFrequency.D, "D"),
                (DictionaryFrequency.E, "E"),
                (DictionaryFrequency.F, "F"),
                (DictionaryFrequency.I, "I"),
                (DictionaryFrequency.J, "J"),
                (DictionaryFrequency.N, "N"),]


class DictionaryAge(StringMappedEnum):
    Always = 0  # ("Always  ", --  X
    Archaic = 1  # "Archaic ", --  A
    Early = 2  # "Early   ", --  B
    Classic = 3  # "Classic ", --  C
    Late = 4  # "Late    ", --  D
    Later = 5  # "Later   ", --  E
    Medieval = 6  # "Medieval", --  F
    NeoLatin = 7  # "Scholar ", --  G
    Modern = 8  # "Modern  "); -- H
    @staticmethod
    def _STR_VALS():
        return [(DictionaryAge.Always, "X"),
                (DictionaryAge.Archaic, "A"),
                (DictionaryAge.Early, "B"),
                (DictionaryAge.Classic, "C"),
                (DictionaryAge.Late, "D"),
                (DictionaryAge.Later, "E"),
                (DictionaryAge.Medieval, "F"),
                (DictionaryAge.NeoLatin, "G"),
                (DictionaryAge.Modern, "H")]


########################################################################################################################
########################################################################################################################
#                                 Classes to hold Dictionary and Inflection lines                                      #
########################################################################################################################
########################################################################################################################


# a type decliration to make code more readable later on
StemGroup = Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]

# helper functions for checking if a dic entry matches an infl
def declention_type_matches(infl: DeclentionType, dic: DeclentionType) -> bool:
    return infl == dic or infl == 0

def declention_subtype_matches(infl: DeclentionSubtype, dic: DeclentionSubtype) -> bool:
    return infl == dic or infl == 0

def conjugation_type_matches(infl: ConjugationType, dic: ConjugationType) -> bool:
    return infl == dic or infl == 0

def conjugation_subtype_matches(infl: ConjugationSubtype, dic: ConjugationSubtype) -> bool:
    return infl == dic or infl == 0

def combine_gender(infl: Gender, dic: Gender) -> Gender:
    return dic

def gender_matches(infl: Gender, dic: Gender) -> bool:
    return infl == dic or infl == Gender.X or (infl == Gender.Common and dic in {Gender.Male, Gender.Female})



# classes to store the lines loaded from DICTLINE and INFLECTS
# each InflData stores in a rule from INFLECTS, and each DictData stores the part of speach information for a line of DICTLINE
# each InflData has a function to check if it can be applied to a given DictData
# these two parrent classes handle many of the variable present in many different inflection rules
class InflDataWithDeclention:
    def __init__(self,
                 declention: DeclentionType,
                 declention_variant: DeclentionSubtype,
                 case: Case,
                 number: Number,
                 gender: Gender):
        self.declention: DeclentionType = declention
        self.declention_variant: DeclentionSubtype = declention_variant
        # self.declention_variant_set: Set[DeclentionSubtype] = {declention_variant} if declention_variant is not 0 else set(range(0,10))
        self.case: Case = case
        self.number = number
        self.gender = gender


class InflDataWithConjagation:
    def __init__(self, conjugation: ConjugationType, conjugation_variant: ConjugationSubtype):
        self.conjugation: ConjugationType = conjugation
        self.conjugation_variant: ConjugationSubtype = conjugation_variant


# Noun Entry classes

class NounDictData:
    def __init__(self,
                 declention: DeclentionType,
                 declention_variant: DeclentionSubtype,
                 gender: Gender,
                 noun_kind: NounKind):
        self.declention: DeclentionType = declention
        self.declention_variant: DeclentionSubtype = declention_variant
        self.gender: Gender = gender
        self.noun_kind: NounKind = noun_kind

    def to_dict(self) -> Dict:
        return {
            "decl": self.declention,
            "decl_var": self.declention_variant,
            "gender": self.gender.str_val,
            "noun_kind": self.noun_kind.str_val
        }
    @staticmethod
    def from_dict(data) -> 'NounDictData':
        return NounDictData(DeclentionType(data['decl']),
                            DeclentionSubtype(data['decl_var']),
                            Gender.from_str(data["gender"]),
                            NounKind.from_str(data["noun_kind"]))

    def __eq__(self, other):
        return isinstance(other, NounDictData) and \
               self.declention == other.declention and \
               self.declention_variant == other.declention_variant and \
               self.gender == other.gender and \
               self.noun_kind == other.noun_kind

    def alternate_form_match(self, other):
        return self == other

    @staticmethod
    def from_str(s: str) -> 'NounDictData':
        return NounDictData(DeclentionType(int(s[0])), DeclentionSubtype(int(s[2])), Gender.from_str(s[4]), NounKind.from_str(s[6]))


class NounInflData(InflDataWithDeclention):
    def __init__(self,
                 declention: DeclentionType,
                 declention_variant: DeclentionSubtype,
                 case: Case,
                 number: Number,
                 gender: Gender) -> None:
        InflDataWithDeclention.__init__(self, declention, declention_variant, case, number, gender)

    @staticmethod
    def from_str(s: str) -> 'NounInflData':
        m = re.match(r"(\d) +(\d) +(\S*) +(\S) +(\S) *", s)
        assert m is not None
        return NounInflData(DeclentionType(int(m.group(1))),
                                         DeclentionSubtype(int(m.group(2))),
                                         Case.from_str(m.group(3)),
                                         Number.from_str(m.group(4)),
                                         Gender.from_str(m.group(5)))

    def matches(self, dict_entry: NounDictData) -> bool:
        assert isinstance(dict_entry, NounDictData)
        return declention_type_matches(self.declention, dict_entry.declention) and \
               declention_subtype_matches(self.declention_variant, dict_entry.declention_variant) and \
               gender_matches(self.gender, dict_entry.gender)


# Preposition Entry classes

class PrepositionDictData:
    def __init__(self, case: Case) -> None:
        self.takes_case: Case = case

    def to_dict(self) -> Dict:
        return {
            "case": self.takes_case.str_val
        }
    @staticmethod
    def from_dict(data) -> 'PrepositionDictData':
        return PrepositionDictData(Case.from_str(data["case"]))

    def __eq__(self, other):
        return isinstance(other, PrepositionDictData) and \
               self.takes_case == other.takes_case

    def alternate_form_match(self, other):
        return self == other

    @staticmethod
    def from_str(s: str) -> 'PrepositionDictData':
        return PrepositionDictData(Case.from_str(s.strip()))


class PrepositionInflData:
    def __init__(self, case: Case):
        self.takes_case: Case = case

    @staticmethod
    def from_str(s: str) -> 'PrepositionInflData':
        return PrepositionInflData(Case.from_str(s.strip()))

    def matches(self, dict_entry: PrepositionDictData) -> bool:
        assert isinstance(dict_entry, PrepositionDictData)
        return self.takes_case == dict_entry.takes_case


# Adjective Entry

class AdjectiveDictData:
    def __init__(self, declention: DeclentionType, declention_variant: DeclentionSubtype, adjective_kind: AdjectiveKind):
        self.declention: DeclentionType = declention
        self.declention_variant: DeclentionSubtype = declention_variant
        self.adjective_kind: AdjectiveKind = adjective_kind

    def to_dict(self) -> Dict:
        return {
            "decl": self.declention,
            "decl_var": self.declention_variant,
            "adj_kind": self.adjective_kind.str_val
        }
    @staticmethod
    def from_dict(data) -> 'AdjectiveDictData':
        return AdjectiveDictData(DeclentionType(data['decl']),
                                 DeclentionSubtype(data['decl_var']),
                                 AdjectiveKind.from_str(data["adj_kind"]))

    def __eq__(self, other):
        return isinstance(other, AdjectiveDictData) and \
               self.declention == other.declention and \
               self.declention_variant == other.declention_variant and \
               self.adjective_kind == other.adjective_kind

    def alternate_form_match(self, other):
        return self == other

    @staticmethod
    def from_str(s: str) -> 'AdjectiveDictData':
        return AdjectiveDictData(DeclentionType(int(s[0])), DeclentionSubtype(int(s[2])), AdjectiveKind.from_str(s[4:].strip()))


class AdjectiveInflData(InflDataWithDeclention):
    def __init__(self,
                 declention: DeclentionType,
                 declention_variant: DeclentionSubtype,
                 case: Case,
                 number: Number,
                 gender: Gender,
                 adjective_kind: AdjectiveKind):
        InflDataWithDeclention.__init__(self,
                                         declention,
                                         declention_variant,
                                         case,
                                         number,
                                         gender)
        self.adjective_kind = adjective_kind

    @staticmethod
    def from_str(s: str) -> 'AdjectiveInflData':
        m = re.match(r"(\d) +(\d) +(\S*) +(\S) +(\S) +(\S*) *", s)
        assert m is not None
        return AdjectiveInflData(DeclentionType(int(m.group(1))),
                                  DeclentionSubtype(int(m.group(2))),
                                  Case.from_str(m.group(3)),
                                  Number.from_str(m.group(4)),
                                  Gender.from_str(m.group(5)),
                                  AdjectiveKind.from_str(m.group(6)))

    def matches(self, dict_entry: AdjectiveDictData) -> bool:
        assert isinstance(dict_entry, AdjectiveDictData)
        return declention_type_matches(self.declention, dict_entry.declention) and \
               declention_subtype_matches(self.declention_variant, dict_entry.declention_variant)


# Conjugation Entry classes

class ConjunctionDictData:
    def __init__(self):
        pass

    def to_dict(self) -> Dict:
        return {}

    @staticmethod
    def from_dict(data) -> 'ConjunctionDictData':
        return ConjunctionDictData()

    def __eq__(self, other):
        return isinstance(other, ConjunctionDictData)

    def alternate_form_match(self, other):
        return self == other

    @staticmethod
    def from_str(s: str) -> 'ConjunctionDictData':
        return ConjunctionDictData()


class ConjunctionInflData:
    def __init__(self):
        pass

    @staticmethod
    def from_str(s: str) -> 'ConjunctionInflData':
        return ConjunctionInflData()

    def matches(self, dict_entry: ConjunctionDictData) -> bool:
        assert isinstance(dict_entry, ConjunctionDictData)
        return True


# Packon Entry classes

class PackonDictData:
    def __init__(self, declention: DeclentionType, declention_variant: DeclentionSubtype, pronoun_kind: PronounKind):
        self.declention: DeclentionType = declention
        self.declention_variant: DeclentionSubtype = declention_variant
        self.pronoun_kind: PronounKind = pronoun_kind
        self.tackon_str: str = ""

    def to_dict(self) -> Dict:
        return {
            "decl": self.declention,
            "decl_var": self.declention_variant,
            "pronoun_kind": self.pronoun_kind.str_val,
            "tackon_str": self.tackon_str
        }
    @staticmethod
    def from_dict(data) -> 'PackonDictData':
        n = PackonDictData(DeclentionType(data['decl']),
                              DeclentionSubtype(data['decl_var']),
                              PronounKind.from_str(data["pronoun_kind"]))
        n.tackon_str = data["tackon_str"]
        return n

    def __eq__(self, other):
        return isinstance(other, PackonDictData) and \
               self.declention == other.declention and \
               self.declention_variant == other.declention_variant and \
               self.pronoun_kind == other.pronoun_kind and \
               self.tackon_str == other.tackon_str

    def alternate_form_match(self, other):
        return self == other

    @staticmethod
    def from_str(s: str):
        return PackonDictData(DeclentionType(int(s[0])),
                               DeclentionSubtype(int(s[2])),
                               PronounKind.from_str(s[4:].strip()))

    def get_required_tack_from_def(self, definition_line: str):
        assert definition_line.startswith("(w/-")
        self.tackon_str = definition_line[4:].split(" ")[0].rstrip(")")
        # print("REQ TACK", self.tackon_str)
    def accepts_tackon(self, tackon: Optional['TackonEntry']):
        return tackon is not None and tackon.tackon == self.tackon_str and tackon.pos == PartOfSpeech.Packon


class PackonInflData(InflDataWithDeclention):
    def __init__(self,
                 declention: DeclentionType,
                 declention_variant: DeclentionSubtype,
                 case: Case,
                 number: Number,
                 gender: Gender):
        InflDataWithDeclention.__init__(self, declention, declention_variant, case, number, gender)

    @staticmethod
    def from_str(s: str):
        m = re.match(r"(\d) +(\d) +(\S*) +(\S) +(\S) *", s)
        assert m is not None
        return PackonInflData(DeclentionType(int(m.group(1))),
                                DeclentionSubtype(int(m.group(2))),
                                Case.from_str(m.group(3)),
                                Number.from_str(m.group(4)),
                                Gender.from_str(m.group(5)))

    def matches(self, dict_entry: PackonDictData) -> bool:
        assert isinstance(dict_entry, PackonDictData)
        return declention_type_matches(self.declention, dict_entry.declention) and \
               declention_subtype_matches(self.declention_variant, dict_entry.declention_variant)


# Verb Entry classes

class VerbDictData:
    def __init__(self, conjugation: ConjugationType, conjugation_variant: ConjugationSubtype, verb_kind: VerbKind):
        self.conjugation: ConjugationType = conjugation
        self.conjugation_variant: ConjugationSubtype = conjugation_variant
        self.verb_kind: VerbKind = verb_kind

    def to_dict(self) -> Dict:
        return {
            "conj": self.conjugation,
            "conj_var": self.conjugation_variant,
            "verb_kind": self.verb_kind.str_val
        }
    @staticmethod
    def from_dict(data) -> 'VerbDictData':
        return VerbDictData(ConjugationType(data['conj']),
                            ConjugationSubtype(data['conj_var']),
                            VerbKind.from_str(data["verb_kind"]))

    def __eq__(self, other):
        return isinstance(other, VerbDictData) and \
               self.conjugation == other.conjugation and \
               self.conjugation_variant == other.conjugation_variant and \
               self.verb_kind == other.verb_kind

    def alternate_form_match(self, other):
        return self == other

    @staticmethod
    def from_str(s: str) -> 'VerbDictData':
        return VerbDictData(ConjugationType(int(s[0])), ConjugationSubtype(int(s[2])), VerbKind.from_str(s[3:].strip()))


class VerbInflData(InflDataWithConjagation):
    def __init__(self,
                 conjugation: ConjugationType,
                 conjugation_variant: ConjugationSubtype,
                 tense: Tense,
                 voice: Voice,
                 mood: Mood,
                 person: Person,
                 number: Number):
        InflDataWithConjagation.__init__(self, conjugation, conjugation_variant)
        self.tense: Tense = tense
        self.voice: Voice = voice
        self.mood: Mood = mood
        self.person: Person = person
        self.number: Number = number

    @staticmethod
    def from_str(s: str) -> 'VerbInflData':
        m = re.match(r"(\d) +(\d) +(\S*) +(\S*) +(\S*) +(\d) +(\S) *", s)
        assert m is not None
        return VerbInflData(ConjugationType(int(m.group(1))),
                             ConjugationSubtype(int(m.group(2))),
                             Tense.from_str(m.group(3)),
                             Voice.from_str(m.group(4)),
                             Mood.from_str(m.group(5)),
                             Person.from_str(m.group(6)),
                             Number.from_str(m.group(7)))

    def matches(self, dict_entry: VerbDictData) -> bool:
        assert isinstance(dict_entry, VerbDictData)
        return conjugation_type_matches(self.conjugation, dict_entry.conjugation) and \
               conjugation_subtype_matches(self.conjugation_variant, dict_entry.conjugation_variant) and \
               (not dict_entry.verb_kind == VerbKind.Dep or self.voice == Voice.Passive)


# Participle Entry classes

class ParticipleInflData(InflDataWithConjagation):
    def __init__(self,
                 conjugation: ConjugationType,
                 conjugation_variant: ConjugationSubtype,
                 case: Case,
                 number: Number,
                 gender: Gender,
                 tense: Tense,
                 voice: Voice):
        InflDataWithConjagation.__init__(self, conjugation, conjugation_variant)
        self.case: Case = case
        self.number: Number = number
        self.gender: Gender = gender
        self.tense: Tense = tense
        self.voice: Voice = voice

    @staticmethod
    def from_str(s: str) -> 'ParticipleInflData':
        m = re.match(r"(\d) +(\d) +(\S*) +(\S) +(\S) +(\S*) +(\S*) +PPL *", s)
        assert m is not None
        return ParticipleInflData(ConjugationType(int(m.group(1))),
                                   ConjugationSubtype(int(m.group(2))),
                                   Case.from_str(m.group(3)),
                                   Number.from_str(m.group(4)),
                                   Gender.from_str(m.group(5)),
                                   Tense.from_str(m.group(6)),
                                   Voice.from_str(m.group(7)))

    def matches(self, dict_entry: VerbDictData) -> bool:
        assert isinstance(dict_entry, VerbDictData)
        return conjugation_type_matches(self.conjugation, dict_entry.conjugation) and \
               conjugation_subtype_matches(self.conjugation_variant, dict_entry.conjugation_variant)


class SupineInflData(InflDataWithConjagation):
    def __init__(self,
                 conjugation: ConjugationType,
                 conjugation_variant: ConjugationSubtype,
                 case: Case,
                 number: Number,
                 gender: Gender):
        InflDataWithConjagation.__init__(self, conjugation, conjugation_variant)
        self.case: Case = case
        self.number: Number = number
        self.gender: Gender = gender

    @staticmethod
    def from_str(s: str):
        m = re.match(r"(\d) +(\d) +(\S*) +(\S) +(\S) *", s)
        assert m is not None
        return SupineInflData(ConjugationType(int(m.group(1))),
                               ConjugationSubtype(int(m.group(2))),
                               Case.from_str(m.group(3)),
                               Number.from_str(m.group(4)),
                               Gender.from_str(m.group(5)))

    def matches(self, dict_entry: VerbDictData) -> bool:
        assert isinstance(dict_entry, VerbDictData)
        return conjugation_type_matches(self.conjugation, dict_entry.conjugation) and \
               conjugation_subtype_matches(self.conjugation_variant, dict_entry.conjugation_variant)


# Pronoun Entry classes

class PronounDictData:
    def __init__(self, declention: DeclentionType, declention_variant: DeclentionSubtype, pronoun_kind: PronounKind):
        self.declention: DeclentionType = declention
        self.declention_variant: DeclentionSubtype = declention_variant
        self.pronoun_kind: PronounKind = pronoun_kind

    def to_dict(self) -> Dict:
        return {
            "decl": self.declention,
            "decl_var": self.declention_variant,
            "pronoun_kind": self.pronoun_kind.str_val
        }
    @staticmethod
    def from_dict(data) -> 'PronounDictData':
        return PronounDictData(DeclentionType(data['decl']),
                               DeclentionSubtype(data['decl_var']),
                               PronounKind.from_str(data["pronoun_kind"]))

    def __eq__(self, other):
        return isinstance(other, PronounDictData) and \
               self.declention == other.declention and \
               self.declention_variant == other.declention_variant and \
               self.pronoun_kind == other.pronoun_kind

    def alternate_form_match(self, other):
        return isinstance(other, PronounDictData)

    @staticmethod
    def from_str(s: str):
        return PronounDictData(DeclentionType(int(s[0])),
                               DeclentionSubtype(int(s[2])),
                               PronounKind.from_str(s[4:].strip()))


class PronounInflData(InflDataWithDeclention):
    def __init__(self,
                 declention: DeclentionType,
                 declention_variant: DeclentionSubtype,
                 case: Case,
                 number: Number,
                 gender: Gender):
        InflDataWithDeclention.__init__(self, declention, declention_variant, case, number, gender)

    @staticmethod
    def from_str(s: str):
        m = re.match(r"(\d) +(\d) +(\S*) +(\S) +(\S) *", s)
        assert m is not None
        return PronounInflData(DeclentionType(int(m.group(1))),
                                DeclentionSubtype(int(m.group(2))),
                                Case.from_str(m.group(3)),
                                Number.from_str(m.group(4)),
                                Gender.from_str(m.group(5)))

    def matches(self, dict_entry: PronounDictData) -> bool:
        assert isinstance(dict_entry, PronounDictData)
        return declention_type_matches(self.declention, dict_entry.declention) and \
               declention_subtype_matches(self.declention_variant, dict_entry.declention_variant)


# Interjection Entry classes

class InterjectionDictData:
    def __init__(self):
        pass

    def to_dict(self) -> Dict:
        return {}
    @staticmethod
    def from_dict(data) -> 'InterjectionDictData':
        return InterjectionDictData()

    def __eq__(self, other):
        return isinstance(other, InterjectionDictData)

    def alternate_form_match(self, other):
        return self == other

    @staticmethod
    def from_str(s: str):
        return InterjectionDictData()


class InterjectionInflData:
    def __init__(self):
        pass

    @staticmethod
    def from_str(s: str):
        return InterjectionInflData()

    def matches(self, dict_entry: InterjectionDictData) -> bool:
        assert isinstance(dict_entry, InterjectionDictData)
        return True


# Adverb Entry classes

class AdverbDictData:
    def __init__(self, adjective_kind: AdjectiveKind):
        self.adjective_kind: AdjectiveKind = adjective_kind

    def __eq__(self, other):
        return isinstance(other, AdverbDictData) and \
               self.adjective_kind == other.adjective_kind

    def alternate_form_match(self, other):
        return self == other

    def to_dict(self) -> Dict:
        return {
            "adj_kind": self.adjective_kind.str_val
        }
    @staticmethod
    def from_dict(data) -> 'AdverbDictData':
        return AdverbDictData(data["adj_kind"])

    @staticmethod
    def from_str(s: str):
        return AdverbDictData(AdjectiveKind.from_str(s.strip()))


class AdverbInflData:
    def __init__(self, adjective_kind_key: AdjectiveKind, adjective_kind_output: AdjectiveKind):
        self.adjective_kind_key = adjective_kind_key
        self.adjective_kind_output = adjective_kind_output

    def matches(self, dict_entry: AdverbDictData) -> bool:
        assert isinstance(dict_entry, AdverbDictData)
        return dict_entry.adjective_kind == self.adjective_kind_key

    @staticmethod
    def from_str(s: str):
        m = re.match(r" *([A-Z]+) ([A-Z]+)", s)
        assert m is not None
        return AdverbInflData(AdjectiveKind.from_str(m.group(1)), AdjectiveKind.from_str(m.group(2)))


# Number Entry classes

class NumberDictData:
    def __init__(self,
                 declention: DeclentionType,
                 declention_variant: DeclentionSubtype,
                 number_kind: NumberKind,
                 numeric_value: str):
        self.declention: DeclentionType = declention
        self.declention_variant: DeclentionSubtype = declention_variant
        self.number_kind: NumberKind = number_kind
        self.numeric_value: str = numeric_value

    def to_dict(self) -> Dict:
        return {
            "decl": self.declention,
            "decl_var": self.declention_variant,
            "number_kind": self.number_kind.str_val,
            "numeric_value": self.numeric_value
        }
    @staticmethod
    def from_dict(data) -> 'NumberDictData':
        return NumberDictData(DeclentionType(data['decl']),
                              DeclentionSubtype(data['decl_var']),
                              NumberKind.from_str(data["number_kind"]),
                              data["numeric_value"])

    def __eq__(self, other):
        return isinstance(other, NumberDictData) and \
               self.declention == other.declention and \
               self.declention_variant == other.declention_variant and \
               self.numeric_value == other.numeric_value and \
               self.number_kind == other.number_kind

    def alternate_form_match(self, other):
        return self == other

    @staticmethod
    def from_str(s: str):
        return NumberDictData(DeclentionType(int(s[0])),
                               DeclentionSubtype(int(s[2])),
                               NumberKind.from_str(s[4:-5].strip()),
                               s[-5:].strip())


class NumberInflData(InflDataWithDeclention):
    def __init__(self,
                 declention: DeclentionType,
                 declention_variant: DeclentionSubtype,
                 case: Case,
                 number: Number,
                 gender: Gender,
                 number_kind: NumberKind):
        InflDataWithDeclention.__init__(self, declention, declention_variant, case, number, gender)
        self.number_kind: NumberKind = number_kind

    @staticmethod
    def from_str(s: str):
        m = re.match(r"(\d) +(\d) +(\S*) +(\S) +(\S) +(\S*) *", s)
        assert m is not None
        return NumberInflData(DeclentionType(int(m.group(1))),
                               DeclentionSubtype(int(m.group(2))),
                               Case.from_str(m.group(3)),
                               Number.from_str(m.group(4)),
                               Gender.from_str(m.group(5)),
                               NumberKind.from_str(m.group(6)))

    def matches(self, dict_entry: NumberDictData) -> bool:
        assert isinstance(dict_entry, NumberDictData)
        return declention_type_matches(self.declention, dict_entry.declention) and \
               declention_subtype_matches(self.declention_variant, dict_entry.declention_variant)

# These maps allow for looking up 
POS_DICT_ENTRY_CLASS_MP: Dict[PartOfSpeech, Any] = {
    PartOfSpeech.Pronoun: PronounDictData,
    PartOfSpeech.Noun: NounDictData,
    PartOfSpeech.Verb: VerbDictData,
    PartOfSpeech.Preposition: PrepositionDictData,
    PartOfSpeech.Interjection: InterjectionDictData,
    PartOfSpeech.Adjective: AdjectiveDictData,
    PartOfSpeech.Adverb: AdverbDictData,
    PartOfSpeech.Conjunction: ConjunctionDictData,
    PartOfSpeech.Number: NumberDictData,
    PartOfSpeech.Packon: PackonDictData
}

POS_INFL_ENTRY_CLASS_MP: Dict[PartOfSpeech, Any] = {
    PartOfSpeech.Pronoun: PronounInflData,
    PartOfSpeech.Noun: NounInflData,
    PartOfSpeech.Verb: VerbInflData,
    PartOfSpeech.Preposition: PrepositionInflData,
    PartOfSpeech.Interjection: InterjectionInflData,
    PartOfSpeech.Adjective: AdjectiveInflData,
    PartOfSpeech.Adverb: AdverbInflData,
    PartOfSpeech.Conjunction: ConjunctionInflData,
    PartOfSpeech.Number: NumberInflData,
    PartOfSpeech.Participle: ParticipleInflData,
    PartOfSpeech.Supine: SupineInflData,
    PartOfSpeech.Packon: PackonInflData
}


# these classes store a whole row from DICTLINE and INFLECTS respectivly

class DictionaryKey:
    def __init__(self,
                 stems: StemGroup,
                 part_of_speach: PartOfSpeech,
                 pos_data,
                 lemma: 'DictionaryLemma' = None):
        # inflection stuff
        self.stems = stems
        self.part_of_speach = part_of_speach
        self.pos_data = pos_data
        self.lemma: 'DictionaryLemma' = lemma  # type: ignore  # this should be filled in by the DictionaryLemma class
        # self.lemma_index: int = 0

    def to_dict(self) -> Dict:
        return {
            'stems': self.stems,
            'pos': self.part_of_speach.str_val,
            'data': self.pos_data.to_dict(),
        }
    @staticmethod
    def from_dict(data) -> 'DictionaryKey':
        pos = PartOfSpeech.from_str(data['pos'])
        return DictionaryKey(data['stems'],
                             pos,
                             POS_DICT_ENTRY_CLASS_MP[pos].from_dict(data['data']))

    def make_form(self, infl: Optional['InflectionRule'], default="NULL_FORM") -> str:
        if infl is None or self.stems[infl.stem_key - 1] is None:
            return default
        stem = self.stems[infl.stem_key - 1]
        assert stem is not None
        return stem + infl.ending

    def alternate_form_match(self, o: 'DictionaryKey') -> bool:
        return self.part_of_speach == o.part_of_speach and self.pos_data.alternate_form_match(o.pos_data)

    @property
    def pronoun_data(self) -> PronounDictData:
        assert isinstance(self.pos_data, PronounDictData)
        return self.pos_data

    @property
    def noun_data(self) -> NounDictData:
        assert isinstance(self.pos_data, NounDictData)
        return self.pos_data

    @property
    def verb_data(self) -> VerbDictData:
        assert isinstance(self.pos_data, VerbDictData)
        return self.pos_data

    @property
    def preposition_data(self) -> PrepositionDictData:
        assert isinstance(self.pos_data, PrepositionDictData)
        return self.pos_data

    @property
    def interjection_data(self) -> InterjectionDictData:
        assert isinstance(self.pos_data, InterjectionDictData)
        return self.pos_data

    @property
    def adjective_data(self) -> AdjectiveDictData:
        assert isinstance(self.pos_data, AdjectiveDictData)
        return self.pos_data

    @property
    def adverb_data(self) -> AdverbDictData:
        assert isinstance(self.pos_data, AdverbDictData)
        return self.pos_data

    @property
    def conjunction_data(self) -> ConjunctionDictData:
        assert isinstance(self.pos_data, ConjunctionDictData)
        return self.pos_data

    @property
    def number_data(self) -> NumberDictData:
        assert isinstance(self.pos_data, NumberDictData)
        return self.pos_data

    @property
    def packon_data(self) -> PackonDictData:
        assert isinstance(self.pos_data, PackonDictData)
        return self.pos_data


class DictionaryLemma:
    def __init__(self,
                 part_of_speach: PartOfSpeech,
                 dictionary_keys: List[DictionaryKey],  # the first key is considered the main form usually, but a formatter can choose
                 translation_metadata: 'TranslationMetadata',
                 definition: 'str',
                 html_data: Optional[str],
                 index: int):
        # inflection stuff
        self.part_of_speach = part_of_speach
        self.dictionary_keys = dictionary_keys
        for key in dictionary_keys:
            assert key.part_of_speach == self.part_of_speach
            key.lemma = self
        self.translation_metadata: TranslationMetadata = translation_metadata

        # payload
        self.definition: str = definition
        self.html_data = html_data

        # formating
        self.index = index

    def to_dict(self, header=False) -> Dict:
        return {
            'pos': self.part_of_speach.str_val,
            'keys': [key.to_dict() for key in self.dictionary_keys],
            'metadata': self.translation_metadata.to_str() if not header else "",
            'def': self.definition if not header else "",
            'html': self.html_data if not header else "",
            'index': self.index
        }

    @staticmethod
    def from_dict(data) -> 'DictionaryLemma':
        return DictionaryLemma(PartOfSpeech.from_str(data['pos']),
                               [DictionaryKey.from_dict(key) for key in data['keys']],
                               TranslationMetadata(data['metadata']),
                               data['def'],
                               data['html'],
                               data['index'])

    def rebuild(self, index: int) -> None:
        for key in self.dictionary_keys:
            assert key.part_of_speach == self.part_of_speach, (key.part_of_speach, self.part_of_speach)
            key.lemma = self
        self.index = index

        # (self,
        #          stems: StemGroup,
        #          part_of_speach: PartOfSpeech,
        #          dictionary_entry,
        #          translation_metadata: 'TranslationMetadata',
        #          definition: 'Definiton',
        #          html_data: Optional[str],
        #          index: int,
        #          line: Optional[str] = None):
        #
        # # inflection stuff
        # self.stems = stems
        # self.part_of_speach = part_of_speach
        # self.dictionary_entry = dictionary_entry
        # self.translation_metadata: TranslationMetadata = translation_metadata
        #
        # # payload
        # self.definition: Definiton = definition
        # self.html_data = html_data
        # self.line=line
        #
        # # formating
        # self.index = index
    #
    # def make_form(self, infl: Optional['InflectionRule'], default="NULL_FORM") -> str:
    #     if infl is None or self.stems[infl.stem_key - 1] is None:
    #         return default
    #     stem = self.stems[infl.stem_key - 1]
    #     assert stem is not None
    #     return stem + infl.ending
    #
    # @property
    # def pronoun_data(self) -> PronounDictData:
    #     assert isinstance(self.dictionary_entry, PronounDictData)
    #     return self.dictionary_entry
    #
    # @property
    # def noun_data(self) -> NounDictData:
    #     assert isinstance(self.dictionary_entry, NounDictData)
    #     return self.dictionary_entry
    #
    # @property
    # def verb_data(self) -> VerbDictData:
    #     assert isinstance(self.dictionary_entry, VerbDictData)
    #     return self.dictionary_entry
    #
    # @property
    # def preposition_data(self) -> PrepositionDictData:
    #     assert isinstance(self.dictionary_entry, PrepositionDictData)
    #     return self.dictionary_entry
    #
    # @property
    # def interjection_data(self) -> InterjectionDictData:
    #     assert isinstance(self.dictionary_entry, InterjectionDictData)
    #     return self.dictionary_entry
    #
    # @property
    # def adjective_data(self) -> AdjectiveDictData:
    #     assert isinstance(self.dictionary_entry, AdjectiveDictData)
    #     return self.dictionary_entry
    #
    # @property
    # def adverb_data(self) -> AdverbDictData:
    #     assert isinstance(self.dictionary_entry, AdverbDictData)
    #     return self.dictionary_entry
    #
    # @property
    # def conjunction_data(self) -> ConjunctionDictData:
    #     assert isinstance(self.dictionary_entry, ConjunctionDictData)
    #     return self.dictionary_entry
    #
    # @property
    # def number_data(self) -> NumberDictData:
    #     assert isinstance(self.dictionary_entry, NumberDictData)
    #     return self.dictionary_entry
    #
    # @property
    # def packon_data(self) -> PackonDictData:
    #     assert isinstance(self.dictionary_entry, PackonDictData)
    #     return self.dictionary_entry


class InflectionRule:
    def __init__(self,
                 part_of_speach: PartOfSpeech,
                 pos_data,
                 stem_key: int,
                 ending: str,
                 age: InflectionAge,
                 frequency: InflectionFrequency,
                 index: int):
        self.part_of_speach = part_of_speach
        self.pos_data = pos_data
        self.stem_key = stem_key
        self.ending = ending
        self.metadata: Tuple[InflectionAge, InflectionFrequency] = (age, frequency)
        self.index = index

    def make_split_word_form(self, word: str):
        assert word.lower().endswith(self.ending)
        if self.ending == "":
            return word
        else:
            return word[:-len(self.ending)] + "." + self.ending

    @property
    def pronoun_data(self) -> PronounInflData:
        assert isinstance(self.pos_data, PronounInflData)
        return self.pos_data

    @property
    def noun_data(self) -> NounInflData:
        assert isinstance(self.pos_data, NounInflData)
        return self.pos_data

    @property
    def verb_data(self) -> VerbInflData:
        assert isinstance(self.pos_data, VerbInflData)
        return self.pos_data

    @property
    def preposition_data(self) -> PrepositionInflData:
        assert isinstance(self.pos_data, PrepositionInflData)
        return self.pos_data

    @property
    def interjection_data(self) -> InterjectionInflData:
        assert isinstance(self.pos_data, InterjectionInflData)
        return self.pos_data

    @property
    def adjective_data(self) -> AdjectiveInflData:
        assert isinstance(self.pos_data, AdjectiveInflData)
        return self.pos_data

    @property
    def adverb_data(self) -> AdverbInflData:
        assert isinstance(self.pos_data, AdverbInflData)
        return self.pos_data

    @property
    def conjunction_data(self) -> ConjunctionInflData:
        assert isinstance(self.pos_data, ConjunctionInflData)
        return self.pos_data

    @property
    def number_data(self) -> NumberInflData:
        assert isinstance(self.pos_data, NumberInflData)
        return self.pos_data

    @property
    def packon_data(self) -> PackonInflData:
        assert isinstance(self.pos_data, PackonInflData)
        return self.pos_data

    @property
    def participle_entry(self) -> ParticipleInflData:
        assert isinstance(self.pos_data, ParticipleInflData)
        return self.pos_data

    @property
    def supine_entry(self) -> SupineInflData:
        assert isinstance(self.pos_data, SupineInflData)
        return self.pos_data


# class Definiton:
#     def __init__(self, line: Union[str, List[str]]):
#         if not isinstance(line, list):
#            line = [line]
#         self.lines: List[str] = line
#
#     def add_definition(self, line: str):
#         self.lines.append(line)


class TranslationMetadata:
    def __init__(self, s: str):
        # Age: Age_Type := X;
        # Area: Area_Type := X;
        # Geo: Geo_Type := X;
        # Freq: Frequency_Type := X;
        # Source: Source_Type := X;
        self.age: DictionaryAge = DictionaryAge.from_str(s[0])
        self.area: str = s[2]
        self.geo: str = s[4]
        self.freqency: DictionaryFrequency = DictionaryFrequency.from_str(s[6])
        self.source: str = s[8]

    def to_str(self) -> str:
        return "{} {} {} {} {}".format(self.age.str_val, self.area, self.geo, self.freqency.str_val, self.source)

########################################################################################################################
########################################################################################################################
#                                            classes to store ADDON entrys                                             #
########################################################################################################################
########################################################################################################################


class PrefixEntry:
    def __init__(self, l1: str, l2: str, l3: str):
        m = re.match(r"PREFIX (\S*)\s*(\S?)", l1)
        assert m is not None
        self.prefix = m.group(1)
        self.connect_character = m.group(2) if len(m.group(2)) == 1 else None

        m = re.match(r"(\S*) (\S*)", l2)
        assert m is not None
        self.match_pos = m.group(1)
        self.l2_2 = m.group(2)

        self.explination = l3

    def accepts_infl(self, infl: InflectionRule) -> bool:
        return infl.part_of_speach == self.match_pos or self.match_pos == PartOfSpeech.X


class SuffixEntry:
    def __init__(self, l1: str, _l2: str, l3: str):
        m = re.match(r"SUFFIX (\S*)\s*\s*(\S?)", l1)
        assert m is not None
        self.suffix = m.group(1)
        self.connect_character = m.group(2) if len(m.group(2)) == 1 else None

        l2 = [x for x in _l2.split(" ") if x != ""]
        self.stem_pos = PartOfSpeech.from_str(l2[0])
        self.stem_key = int(l2[1])
        self.new_stem_key = int(l2[-1])

        self.explination = l3.strip()

        self.new_pos = PartOfSpeech.from_str(l2[2])
        if self.new_pos == PartOfSpeech.Noun:
            # V 4 N 3 1 F p  2
            self.decl = DeclentionType(int(l2[3]))
            self.decl_val = DeclentionSubtype(int(l2[4]))
            self.noun_gender = Gender.from_str(l2[5])
            self.noun_kind = NounKind.from_str(l2[6])
            self.fake_dictionary_entry: Union[NounDictData, AdjectiveDictData, VerbDictData, AdverbDictData, NumberDictData]\
                = NounDictData(self.decl, self.decl_val, self.noun_gender, self.noun_kind)
        elif self.new_pos == PartOfSpeech.Adjective:
            self.decl = DeclentionType(int(l2[3]))
            self.decl_val = DeclentionSubtype(int(l2[4]))
            self.new_adj_kind = AdjectiveKind.from_str(l2[5])
            self.fake_dictionary_entry = AdjectiveDictData(self.decl, self.decl_val, self.new_adj_kind)
        elif self.new_pos == PartOfSpeech.Verb:
            self.conj = ConjugationType(int(l2[3]))
            self.conj_val = ConjugationSubtype(int(l2[4]))
            self.fake_dictionary_entry = VerbDictData(self.conj, self.conj_val, VerbKind.X)
        elif self.new_pos == PartOfSpeech.Adverb:
            self.new_adv_kind = AdjectiveKind.from_str(l2[3])
            self.fake_dictionary_entry = AdverbDictData(self.new_adv_kind)
        elif self.new_pos == PartOfSpeech.Number:
            self.decl = DeclentionType(int(l2[3]))
            self.decl_val = DeclentionSubtype(int(l2[4]))
            self.new_num_kind = NumberKind.from_str(l2[5])
            self.fake_dictionary_entry = NumberDictData(self.decl, self.decl_val, self.new_num_kind, "0")
        else:
            raise ValueError()

    def accepts_infl(self, infl: InflectionRule) -> bool:
        if self.new_pos != infl.part_of_speach:
            return False
        # print("POS OK", infl, self.new_stem_key, self.stem_key, infl.stem_key)
        return infl.stem_key == self.new_stem_key or self.new_stem_key == 0

    def accepts_stem_dic_key(self, dic: DictionaryKey) -> bool:
        return dic.stems[self.stem_key - 1] is not None

    def make_fake_dic_key(self, dic: DictionaryKey) -> DictionaryKey:
        e = DictionaryKey(tuple([x + self.suffix if x is not None else None for x in dic.stems]),
                          self.new_pos,
                          self.fake_dictionary_entry,
                          lemma=dic.lemma)
        return e


class TackonEntry:
    def __init__(self, l1: str, l2: str, l3: str):
        # TACKON pte
        # ADJ 1 0 POS
        # TACKON ! (emphatic particle w/personal ADJ); (usually with ABL, suapte);
        m = re.fullmatch(r"TACKON (\S*)\s*", l1)
        assert m is not None
        self.tackon = m.group(1)

        m = re.match(r"(\S*)(.*)", l2)
        assert m is not None
        self.pos: PartOfSpeech = PartOfSpeech.from_str(m.group(1))
        if self.pos == PartOfSpeech.X:
            pass
        elif self.pos == PartOfSpeech.Adjective:
            m = re.match(r"(\S) +(\S) +(\S*)", m.group(2).strip())
            assert m is not None
            self.decl = DeclentionType(int(m.group(1)))
            self.decl_var = DeclentionSubtype(int(m.group(2)))
            self.adj_kind: AdjectiveKind = AdjectiveKind.from_str(m.group(3))
        elif self.pos == PartOfSpeech.Pronoun:
            m = re.match(r"(\S) +(\S) +(\S*)", m.group(2).strip())
            assert m is not None
            self.decl = DeclentionType(int(m.group(1)))
            self.decl_var = DeclentionSubtype(int(m.group(2)))
            self.pron_kind: PronounKind = PronounKind.from_str(m.group(3))
        elif self.pos == PartOfSpeech.Packon:
            m = re.match(r"(\S) +(\S) +(\S*)", m.group(2).strip())
            assert m is not None
            self.decl = DeclentionType(int(m.group(1)))
            self.decl_var = DeclentionSubtype(int(m.group(2)))
            self.pack_kind: PronounKind = PronounKind.from_str(m.group(3))
        elif self.pos == PartOfSpeech.Noun:
            m = re.match(r"(\S) +(\S) +(\S) +(\S)", m.group(2).strip())
            assert m is not None
            self.decl = DeclentionType(int(m.group(1)))
            self.decl_var = DeclentionSubtype(int(m.group(2)))
            self.noun_gender: Gender = Gender.from_str(m.group(3))
            self.noun_number = Number.from_str(m.group(4))
        else:
            raise ValueError(self.pos)
        self.explination = l3

    def accepts_infl(self, infl: InflectionRule) -> bool:
        def bidir_declention_type_matches(infl: DeclentionType, dic: DeclentionType) -> bool:
            return infl == dic or infl == 0 or dic == 0

        def bidir_declention_subtype_matches(infl: DeclentionSubtype, dic: DeclentionSubtype) -> bool:
            return infl == dic or infl == 0 or dic == 0

        def bidir_conjugation_type_matches(infl: ConjugationType, dic: ConjugationType) -> bool:
            return infl == dic or infl == 0 or dic == 0

        def bidir_conjugation_subtype_matches(infl: ConjugationSubtype, dic: ConjugationSubtype) -> bool:
            return infl == dic or infl == 0 or dic == 0

        if self.pos == PartOfSpeech.X:
            return True
        elif self.pos == PartOfSpeech.Adjective:
            return infl.part_of_speach == PartOfSpeech.Adjective and \
                   bidir_declention_type_matches(self.decl, infl.adjective_data.declention) and \
                   bidir_declention_subtype_matches(self.decl_var, infl.adjective_data.declention_variant) and \
                   infl.adjective_data.adjective_kind == self.adj_kind
        elif self.pos == PartOfSpeech.Pronoun:
            return infl.part_of_speach == PartOfSpeech.Pronoun and \
                   bidir_declention_type_matches(self.decl, infl.pronoun_data.declention) and \
                   bidir_declention_subtype_matches(self.decl_var, infl.pronoun_data.declention_variant) # and \
                   # TODO infl.pronoun_data.pron_kind == self.pron_kind
        elif self.pos == PartOfSpeech.Packon:
            return infl.part_of_speach == PartOfSpeech.Packon and \
                   declention_type_matches(infl.packon_data.declention, self.decl) and \
                   declention_subtype_matches(infl.packon_data.declention_variant, self.decl_var)
        elif self.pos == PartOfSpeech.Noun:
            return infl.part_of_speach == PartOfSpeech.Noun and \
                   bidir_declention_type_matches(self.decl, infl.noun_data.declention) and \
                   bidir_declention_subtype_matches(self.decl_var, infl.noun_data.declention_variant) and \
                   gender_matches(infl.noun_data.gender, self.noun_gender) and \
                   infl.noun_data.number == self.noun_number
        else:
            raise ValueError()

    def accepts_stem(self, dic: DictionaryKey) -> bool:
        if self.pos != PartOfSpeech.Packon:
            return True
        if dic.part_of_speach != PartOfSpeech.Packon:
            return False
        return self.tackon == dic.packon_data.tackon_str


class UniqueEntry:
    def __init__(self, l1: str, l2: str, l3: str):
        self.word = l1
        self.l2 = l2
        self.l3 = l3


class Lexicon(metaclass=ABCMeta):
    def __init__(self, path):
        self.inflection_list: List[InflectionRule] = []
        self.dictionary_keys: List[DictionaryKey] = []
        self.dictionary_lemmata: List[DictionaryLemma] = []
        self.prefix_list: List[Optional[PrefixEntry]] = []
        self.suffix_list: List[Optional[SuffixEntry]] = []
        self.tackon_list: List[Optional[TackonEntry]] = []
        self.uniques: Dict[str, UniqueEntry] = {}
        self.map_ending_infls: Dict[str, List[InflectionRule]] = {}
        self.stem_map: Dict[Tuple[PartOfSpeech, int], Dict[str, List[DictionaryKey]]] = {}
        self.load(path)

    @abstractmethod
    def load(self, path: str) -> None:
        pass

    def get_noun_inflection_rule(self, declention: DeclentionType, declention_varient: DeclentionSubtype, gender: Gender, case: Case, number: Number) -> Optional[InflectionRule]:
        l = [infl for infl in self.inflection_list if
             infl.part_of_speach == PartOfSpeech.Noun and
             declention_type_matches(infl.noun_data.declention, declention) and
             declention_subtype_matches(infl.noun_data.declention_variant, declention_varient) and
             gender_matches(infl.noun_data.gender, gender) and
             infl.noun_data.case == case and
             infl.noun_data.number == number]
        l.sort(key=lambda x: x.noun_data.gender != gender)
        return l[0] if len(l) > 0 else None

    def get_number_inflection_rule(self, declention: DeclentionType, declention_varient: DeclentionSubtype, gender: Gender, case: Case, number: Number, number_kind: NumberKind) -> Optional[InflectionRule]:
        l = [infl for infl in self.inflection_list if
             infl.part_of_speach == PartOfSpeech.Number and
             declention_type_matches(infl.number_data.declention, declention) and
             declention_subtype_matches(infl.number_data.declention_variant, declention_varient) and
             gender_matches(infl.number_data.gender, gender) and
             infl.number_data.case == case and
             infl.number_data.number == number and
             infl.number_data.number_kind == number_kind]
        l.sort(key=lambda x: x.number_data.gender != gender)
        return l[0] if len(l) > 0 else None

    def get_pronoun_inflection_rule(self, declention: DeclentionType, declention_varient: DeclentionSubtype, gender: Gender, case: Case, number: Number) -> Optional[InflectionRule]:
        l = [infl for infl in self.inflection_list if
             infl.part_of_speach == PartOfSpeech.Pronoun and
             declention_type_matches(infl.pronoun_data.declention, declention) and
             declention_subtype_matches(infl.pronoun_data.declention_variant, declention_varient) and
             gender_matches(infl.pronoun_data.gender, gender) and
             infl.pronoun_data.case == case and
             infl.pronoun_data.number == number]
        return l[0] if len(l) > 0 else None


    def get_adjective_inflection_rule(self, declention: DeclentionType, declention_varient: DeclentionSubtype, gender: Gender, case: Case, number: Number, adjective_kind: AdjectiveKind) -> Optional[InflectionRule]:
        l = [infl for infl in self.inflection_list if
             infl.part_of_speach == PartOfSpeech.Adjective and
             declention_type_matches(infl.adjective_data.declention, declention) and
             declention_subtype_matches(infl.adjective_data.declention_variant, declention_varient) and
             gender_matches(infl.adjective_data.gender, gender) and
             infl.adjective_data.case == case and
             infl.adjective_data.number == number and
             infl.adjective_data.adjective_kind == adjective_kind]
        l.sort(key=lambda x: x.adjective_data.gender != gender)
        return l[0] if len(l) > 0 else None

    def get_verb_inflection_rule(self, conjugation: ConjugationType, conjugation_variant: ConjugationSubtype, number: Number, person: Person, voice: Voice, tense: Tense, mood: Mood) -> Optional[InflectionRule]:
        l = sorted([infl for infl in self.inflection_list if
             infl.part_of_speach == PartOfSpeech.Verb and
             conjugation_type_matches(infl.verb_data.conjugation, conjugation) and
             conjugation_subtype_matches(infl.verb_data.conjugation_variant, conjugation_variant) and
             infl.verb_data.number == number and
             infl.verb_data.person == person and
             infl.verb_data.voice == voice and
             infl.verb_data.tense == tense and
             infl.verb_data.mood == mood],
                   key=lambda x: (-100 if x.verb_data.conjugation == 0 else 0)
                                 + (-100 if x.verb_data.conjugation_variant == 0 else 0)) # deprioritize general rules
        return l[0] if len(l) > 0 else None

    def get_participle_inflection_rule(self, conjugation: ConjugationType, conjugation_variant: ConjugationSubtype, number: Number, case: Case, voice: Voice, tense: Tense) -> Optional[InflectionRule]:
        l = [infl for infl in self.inflection_list if
             infl.part_of_speach == PartOfSpeech.Participle and
             conjugation_type_matches(infl.participle_entry.conjugation, conjugation) and
             conjugation_subtype_matches(infl.participle_entry.conjugation_variant, conjugation_variant) and
             infl.participle_entry.number == number and
             infl.participle_entry.case == case and
             infl.participle_entry.voice == voice and
             infl.participle_entry.tense == tense]
        return l[0] if len(l) > 0 else None

    def get_adverb_inflection_rule(self, adjective_kind_key: AdjectiveKind, adjective_kind_output: AdjectiveKind) -> Optional[InflectionRule]:
        l = [infl for infl in self.inflection_list if
             infl.part_of_speach == PartOfSpeech.Adverb and
             infl.adverb_data.adjective_kind_key == adjective_kind_key and
             infl.adverb_data.adjective_kind_output == adjective_kind_output]
        return l[0] if len(l) > 0 else None


class Formater(metaclass=ABCMeta):
    def __init__(self, lex: Lexicon):
        self.lex = lex

    @abstractmethod
    def parse(self, s) -> str:
        pass
