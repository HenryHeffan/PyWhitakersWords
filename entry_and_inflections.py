import re
import enum
from typing import NewType, Tuple, List, Dict, Optional, Any, Union, Generator
from abc import abstractmethod, ABCMeta


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

    @classmethod
    def str_val(cls, inst) -> str:
        return {a: b for a, b in cls._STR_VALS()}[inst]

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
ALL_CONJ_VAR_PAIRS: List[Tuple[ConjugationType, ConjugationSubtype]] = \
    [(ConjugationType(i), ConjugationSubtype(j)) for i in range(10) for j in range(10)]

DeclentionType = NewType("DeclentionType", int)
DeclentionSubtype = NewType("DeclentionSubtype", int)
ALL_DECL_VAR_PAIRS: List[Tuple[ConjugationType, ConjugationSubtype]] = \
    [(DeclentionType(i), DeclentionSubtype(j)) for i in range(10) for j in range(10)]



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

    def store(self) -> str:
        return "{} {} {} {}".format(self.declention, self.declention_variant, Gender.str_val(self.gender), NounKind.str_val(self.noun_kind))
    @staticmethod
    def load(data) -> 'NounDictData':
        return NounDictData.from_str(data)

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
        # assert isinstance(dict_entry, NounDictData)
        return declention_type_matches(self.declention, dict_entry.declention) and \
               declention_subtype_matches(self.declention_variant, dict_entry.declention_variant) and \
               gender_matches(self.gender, dict_entry.gender)


# Preposition Entry classes

class PrepositionDictData:
    def __init__(self, takes_case: Case) -> None:
        self.takes_case: Case = takes_case

    def store(self) -> str:
        return "{}".format(Case.str_val(self.takes_case))
    @staticmethod
    def load(data) -> 'PrepositionDictData':
        return PrepositionDictData.from_str(data)

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
        # assert isinstance(dict_entry, PrepositionDictData)
        return self.takes_case == dict_entry.takes_case


# Adjective Entry

class AdjectiveDictData:
    def __init__(self, declention: DeclentionType, declention_variant: DeclentionSubtype, adjective_kind: AdjectiveKind):
        self.declention: DeclentionType = declention
        self.declention_variant: DeclentionSubtype = declention_variant
        self.adjective_kind: AdjectiveKind = adjective_kind

    def store(self) -> str:
        return "{} {} {}".format(self.declention, self.declention_variant, AdjectiveKind.str_val(self.adjective_kind))
    @staticmethod
    def load(data) -> 'AdjectiveDictData':
        return AdjectiveDictData.from_str(data)

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
        # assert isinstance(dict_entry, AdjectiveDictData)
        return declention_type_matches(self.declention, dict_entry.declention) and \
               declention_subtype_matches(self.declention_variant, dict_entry.declention_variant)


# Conjugation Entry classes

class ConjunctionDictData:
    def __init__(self):
        pass

    def store(self) -> str:
        return ""
    @staticmethod
    def load(data) -> 'ConjunctionDictData':
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
        # assert isinstance(dict_entry, ConjunctionDictData)
        return True


# Packon Entry classes

class PackonDictData:
    def __init__(self, declention: DeclentionType, declention_variant: DeclentionSubtype, pronoun_kind: PronounKind, tackon_str: str=""):
        self.declention: DeclentionType = declention
        self.declention_variant: DeclentionSubtype = declention_variant
        self.pronoun_kind: PronounKind = pronoun_kind
        self.tackon_str = tackon_str

    def store(self) -> str:
        return "{} {} {} {}".format(self.declention, self.declention_variant, PronounKind.str_val(self.pronoun_kind), self.tackon_str)
    @staticmethod
    def load(data) -> 'PackonDictData':
        data = data.split(" ")
        n = PackonDictData(DeclentionType(int(data[0])),
                              DeclentionSubtype(int(data[1])),
                              PronounKind.from_str(data[2]))
        n.tackon_str = data[3]
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
        # assert isinstance(dict_entry, PackonDictData)
        return declention_type_matches(self.declention, dict_entry.declention) and \
               declention_subtype_matches(self.declention_variant, dict_entry.declention_variant)


# Verb Entry classes

class VerbDictData:
    def __init__(self, conjugation: ConjugationType, conjugation_variant: ConjugationSubtype, verb_kind: VerbKind):
        self.conjugation: ConjugationType = conjugation
        self.conjugation_variant: ConjugationSubtype = conjugation_variant
        self.verb_kind: VerbKind = verb_kind

    def store(self) -> str:
        return "{} {} {}".format(self.conjugation, self.conjugation_variant, VerbKind.str_val(self.verb_kind))
    @staticmethod
    def load(data) -> 'VerbDictData':
        return VerbDictData.from_str(data)

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
        # assert isinstance(dict_entry, VerbDictData)
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
        # assert isinstance(dict_entry, VerbDictData)
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
        # assert isinstance(dict_entry, VerbDictData)
        return conjugation_type_matches(self.conjugation, dict_entry.conjugation) and \
               conjugation_subtype_matches(self.conjugation_variant, dict_entry.conjugation_variant)


# Pronoun Entry classes

class PronounDictData:
    def __init__(self, declention: DeclentionType, declention_variant: DeclentionSubtype, pronoun_kind: PronounKind):
        self.declention: DeclentionType = declention
        self.declention_variant: DeclentionSubtype = declention_variant
        self.pronoun_kind: PronounKind = pronoun_kind

    def store(self) -> str:
        return "{} {} {}".format(self.declention, self.declention_variant, PronounKind.str_val(self.pronoun_kind))
    @staticmethod
    def load(data) -> 'PronounDictData':
        return PronounDictData.from_str(data)

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
        # assert isinstance(dict_entry, PronounDictData)
        return declention_type_matches(self.declention, dict_entry.declention) and \
               declention_subtype_matches(self.declention_variant, dict_entry.declention_variant)


# Interjection Entry classes

class InterjectionDictData:
    def __init__(self):
        pass

    def store(self) -> str:
        return ""
    @staticmethod
    def load(data) -> 'InterjectionDictData':
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
        # assert isinstance(dict_entry, InterjectionDictData)
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

    def store(self) -> str:
        return "{}".format(AdjectiveKind.str_val(self.adjective_kind))
    @staticmethod
    def load(data) -> 'AdverbDictData':
        return AdverbDictData.from_str(data)

    @staticmethod
    def from_str(s: str):
        return AdverbDictData(AdjectiveKind.from_str(s.strip()))


class AdverbInflData:
    def __init__(self, adjective_kind_key: AdjectiveKind, adjective_kind_output: AdjectiveKind):
        self.adjective_kind_key = adjective_kind_key
        self.adjective_kind_output = adjective_kind_output

    def matches(self, dict_entry: AdverbDictData) -> bool:
        # assert isinstance(dict_entry, AdverbDictData)
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

    def store(self) -> str:
        return "{} {} {} {}".format(self.declention, self.declention_variant, NumberKind.str_val(self.number_kind), self.numeric_value)
    @staticmethod
    def load(data) -> 'NumberDictData':
        data = data.split(" ")
        return NumberDictData(DeclentionType(int(data[0])),
                               DeclentionSubtype(int(data[1])),
                               NumberKind.from_str(data[2]),
                               data[3])

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
        # assert isinstance(dict_entry, NumberDictData)
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
                 part_of_speech: PartOfSpeech,
                 pos_data,
                 lemma: 'DictionaryLemma' = None):
        # inflection stuff
        self.stems = stems
        self.part_of_speech = part_of_speech
        self.pos_data = pos_data
        self.lemma: 'DictionaryLemma' = lemma  # type: ignore  # this should be filled in by the DictionaryLemma class
        # self.lemma_index: int = 0

    def store(self, empty_stem="xxxxx", null_stem="zzz") -> str:
        return "{} {} {} {} {} {}".format(*[(s if s is not "" else empty_stem) if s is not None else null_stem for s in self.stems],
                                          PartOfSpeech.str_val(self.part_of_speech), self.pos_data.store())
    @staticmethod
    def load(data) -> 'DictionaryKey':
        data=data.split(" ", maxsplit=5)
        pos = PartOfSpeech.from_str(data[4])
        return DictionaryKey(tuple([None if d == "None" else d for d in data[0:4]]),
                             pos,
                             POS_DICT_ENTRY_CLASS_MP[pos].load(data[5]))

    def make_form(self, infl: Optional['InflectionRule'], default="NULL_FORM") -> str:
        if infl is None or self.stems[infl.stem_key - 1] is None:
            return default
        stem = self.stems[infl.stem_key - 1]
        assert stem is not None
        return stem + infl.ending

    def alternate_form_match(self, o: 'DictionaryKey') -> bool:
        return self.part_of_speech == o.part_of_speech and self.pos_data.alternate_form_match(o.pos_data)

    @property
    def pronoun_data(self) -> PronounDictData:
        # assert isinstance(self.pos_data, PronounDictData)
        return self.pos_data

    @property
    def noun_data(self) -> NounDictData:
        # assert isinstance(self.pos_data, NounDictData)
        return self.pos_data

    @property
    def verb_data(self) -> VerbDictData:
        # assert isinstance(self.pos_data, VerbDictData)
        return self.pos_data

    @property
    def preposition_data(self) -> PrepositionDictData:
        # assert isinstance(self.pos_data, PrepositionDictData)
        return self.pos_data

    @property
    def interjection_data(self) -> InterjectionDictData:
        # assert isinstance(self.pos_data, InterjectionDictData)
        return self.pos_data

    @property
    def adjective_data(self) -> AdjectiveDictData:
        # assert isinstance(self.pos_data, AdjectiveDictData)
        return self.pos_data

    @property
    def adverb_data(self) -> AdverbDictData:
        # assert isinstance(self.pos_data, AdverbDictData)
        return self.pos_data

    @property
    def conjunction_data(self) -> ConjunctionDictData:
        # assert isinstance(self.pos_data, ConjunctionDictData)
        return self.pos_data

    @property
    def number_data(self) -> NumberDictData:
        # assert isinstance(self.pos_data, NumberDictData)
        return self.pos_data

    @property
    def packon_data(self) -> PackonDictData:
        # assert isinstance(self.pos_data, PackonDictData)
        return self.pos_data


class DictionaryLemma:
    def __init__(self,
                 part_of_speech: PartOfSpeech,
                 dictionary_keys: List[DictionaryKey],  # the first key is considered the main form usually, but a formatter can choose
                 translation_metadata: 'TranslationMetadata',
                 definition: 'str',
                 html_data: Optional[str],
                 index: int):
        # inflection stuff
        self.part_of_speech = part_of_speech
        self.dictionary_keys = dictionary_keys
        for key in dictionary_keys:
            assert key.part_of_speech == self.part_of_speech
            key.lemma = self
        self.translation_metadata: TranslationMetadata = translation_metadata

        # payload
        self.definition: str = definition
        self.html_data = html_data

        # formating
        self.index = index

    # def get_main_key(self) -> 'DictionaryKey':
    #     return self.dictionary_keys[0]

    def store(self, header=False) -> Dict:
        return {
            'pos': PartOfSpeech.str_val(self.part_of_speech),
            'keys': [key.store() for key in self.dictionary_keys],
            'metadata': self.translation_metadata.to_str(),
            'def': self.definition if not header else "",
            'html': self.html_data if not header else "",
            'index': self.index
        }

    @staticmethod
    def load(data) -> 'DictionaryLemma':
        return DictionaryLemma(PartOfSpeech.from_str(data['pos']),
                               [DictionaryKey.load(key) for key in data['keys']],
                               TranslationMetadata(data['metadata']),
                               data['def'],
                               data['html'],
                               data['index'])

    def rebuild(self, index: int) -> None:
        for key in self.dictionary_keys:
            assert key.part_of_speech == self.part_of_speech, (key.part_of_speech, self.part_of_speech)
            key.lemma = self
        self.index = index

        # (self,
        #          stems: StemGroup,
        #          part_of_speech: PartOfSpeech,
        #          dictionary_entry,
        #          translation_metadata: 'TranslationMetadata',
        #          definition: 'Definiton',
        #          html_data: Optional[str],
        #          index: int,
        #          line: Optional[str] = None):
        #
        # # inflection stuff
        # self.stems = stems
        # self.part_of_speech = part_of_speech
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
    #     # assert isinstance(self.dictionary_entry, PronounDictData)
    #     return self.dictionary_entry
    #
    # @property
    # def noun_data(self) -> NounDictData:
    #     # assert isinstance(self.dictionary_entry, NounDictData)
    #     return self.dictionary_entry
    #
    # @property
    # def verb_data(self) -> VerbDictData:
    #     # assert isinstance(self.dictionary_entry, VerbDictData)
    #     return self.dictionary_entry
    #
    # @property
    # def preposition_data(self) -> PrepositionDictData:
    #     # assert isinstance(self.dictionary_entry, PrepositionDictData)
    #     return self.dictionary_entry
    #
    # @property
    # def interjection_data(self) -> InterjectionDictData:
    #     # assert isinstance(self.dictionary_entry, InterjectionDictData)
    #     return self.dictionary_entry
    #
    # @property
    # def adjective_data(self) -> AdjectiveDictData:
    #     # assert isinstance(self.dictionary_entry, AdjectiveDictData)
    #     return self.dictionary_entry
    #
    # @property
    # def adverb_data(self) -> AdverbDictData:
    #     # assert isinstance(self.dictionary_entry, AdverbDictData)
    #     return self.dictionary_entry
    #
    # @property
    # def conjunction_data(self) -> ConjunctionDictData:
    #     # assert isinstance(self.dictionary_entry, ConjunctionDictData)
    #     return self.dictionary_entry
    #
    # @property
    # def number_data(self) -> NumberDictData:
    #     # assert isinstance(self.dictionary_entry, NumberDictData)
    #     return self.dictionary_entry
    #
    # @property
    # def packon_data(self) -> PackonDictData:
    #     # assert isinstance(self.dictionary_entry, PackonDictData)
    #     return self.dictionary_entry


class InflectionRule:
    def __init__(self,
                 part_of_speech: PartOfSpeech,
                 pos_data,
                 stem_key: int,
                 ending: str,
                 age: InflectionAge,
                 frequency: InflectionFrequency,
                 index: int):
        self.part_of_speech = part_of_speech
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
        # assert isinstance(self.pos_data, PronounInflData)
        return self.pos_data

    @property
    def noun_data(self) -> NounInflData:
        # assert isinstance(self.pos_data, NounInflData)
        return self.pos_data

    @property
    def verb_data(self) -> VerbInflData:
        # assert isinstance(self.pos_data, VerbInflData)
        return self.pos_data

    @property
    def preposition_data(self) -> PrepositionInflData:
        # assert isinstance(self.pos_data, PrepositionInflData)
        return self.pos_data

    @property
    def interjection_data(self) -> InterjectionInflData:
        # assert isinstance(self.pos_data, InterjectionInflData)
        return self.pos_data

    @property
    def adjective_data(self) -> AdjectiveInflData:
        # assert isinstance(self.pos_data, AdjectiveInflData)
        return self.pos_data

    @property
    def adverb_data(self) -> AdverbInflData:
        # assert isinstance(self.pos_data, AdverbInflData)
        return self.pos_data

    @property
    def conjunction_data(self) -> ConjunctionInflData:
        # assert isinstance(self.pos_data, ConjunctionInflData)
        return self.pos_data

    @property
    def number_data(self) -> NumberInflData:
        # assert isinstance(self.pos_data, NumberInflData)
        return self.pos_data

    @property
    def packon_data(self) -> PackonInflData:
        # assert isinstance(self.pos_data, PackonInflData)
        return self.pos_data

    @property
    def participle_entry(self) -> ParticipleInflData:
        # assert isinstance(self.pos_data, ParticipleInflData)
        return self.pos_data

    @property
    def supine_entry(self) -> SupineInflData:
        # assert isinstance(self.pos_data, SupineInflData)
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
        self.frequency: DictionaryFrequency = DictionaryFrequency.from_str(s[6])
        self.source: str = s[8]

    def to_str(self) -> str:
        return "{} {} {} {} {}".format(DictionaryAge.str_val(self.age), self.area, self.geo, DictionaryFrequency.str_val(self.frequency), self.source)

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
        return infl.part_of_speech == self.match_pos or self.match_pos == PartOfSpeech.X


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
        if self.new_pos != infl.part_of_speech:
            return False
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
            return infl.part_of_speech == PartOfSpeech.Adjective and \
                   bidir_declention_type_matches(self.decl, infl.adjective_data.declention) and \
                   bidir_declention_subtype_matches(self.decl_var, infl.adjective_data.declention_variant) and \
                   infl.adjective_data.adjective_kind == self.adj_kind
        elif self.pos == PartOfSpeech.Pronoun:
            return infl.part_of_speech == PartOfSpeech.Pronoun and \
                   bidir_declention_type_matches(self.decl, infl.pronoun_data.declention) and \
                   bidir_declention_subtype_matches(self.decl_var, infl.pronoun_data.declention_variant) # and \
                   # TODO infl.pronoun_data.pron_kind == self.pron_kind
        elif self.pos == PartOfSpeech.Packon:
            return infl.part_of_speech == PartOfSpeech.Packon and \
                   declention_type_matches(infl.packon_data.declention, self.decl) and \
                   declention_subtype_matches(infl.packon_data.declention_variant, self.decl_var)
        elif self.pos == PartOfSpeech.Noun:
            return infl.part_of_speech == PartOfSpeech.Noun and \
                   bidir_declention_type_matches(self.decl, infl.noun_data.declention) and \
                   bidir_declention_subtype_matches(self.decl_var, infl.noun_data.declention_variant) and \
                   gender_matches(infl.noun_data.gender, self.noun_gender) and \
                   infl.noun_data.number == self.noun_number
        else:
            raise ValueError()

    def accepts_stem(self, dic: DictionaryKey) -> bool:
        if self.pos != PartOfSpeech.Packon:
            return True
        if dic.part_of_speech != PartOfSpeech.Packon:
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
        self._dictionary_keys: List[DictionaryKey] = []
        self._dictionary_lemmata: List[DictionaryLemma] = []
        self.prefix_list: List[Optional[PrefixEntry]] = []
        self.suffix_list: List[Optional[SuffixEntry]] = []
        self.tackon_list: List[Optional[TackonEntry]] = []
        self.uniques: Dict[str, UniqueEntry] = {}
        self.map_ending_infls: Dict[str, List[InflectionRule]] = {}
        self._stem_map: Dict[Tuple[PartOfSpeech, int], Dict[str, List[DictionaryKey]]] = \
            {(pos, stem_key): {} for pos in PartOfSpeech for stem_key in range(1,5)}
        self.load(path)

    def get_stem_map(self, pos: PartOfSpeech, stem_key: int) -> Dict[str, List[DictionaryKey]]:
        return self._stem_map[(pos, stem_key)]
    @property
    def dictionary_keys(self)-> List[DictionaryKey]:
        return self._dictionary_keys
    @property
    def dictionary_lemmata(self)-> List[DictionaryLemma]:
        return self._dictionary_lemmata

    @abstractmethod
    def load(self, path: str) -> None:
        pass

    def get_noun_inflection_rule(self, declention: DeclentionType, declention_varient: DeclentionSubtype, gender: Gender, case: Case, number: Number) -> Optional[InflectionRule]:
        l = [infl for infl in self.inflection_list if
             infl.part_of_speech == PartOfSpeech.Noun and
             declention_type_matches(infl.noun_data.declention, declention) and
             declention_subtype_matches(infl.noun_data.declention_variant, declention_varient) and
             gender_matches(infl.noun_data.gender, gender) and
             infl.noun_data.case == case and
             infl.noun_data.number == number]
        l.sort(key=lambda x: x.noun_data.gender != gender)
        return l[0] if len(l) > 0 else None

    def get_number_inflection_rule(self, declention: DeclentionType, declention_varient: DeclentionSubtype, gender: Gender, case: Case, number: Number, number_kind: NumberKind) -> Optional[InflectionRule]:
        l = [infl for infl in self.inflection_list if
             infl.part_of_speech == PartOfSpeech.Number and
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
             infl.part_of_speech == PartOfSpeech.Pronoun and
             declention_type_matches(infl.pronoun_data.declention, declention) and
             declention_subtype_matches(infl.pronoun_data.declention_variant, declention_varient) and
             gender_matches(infl.pronoun_data.gender, gender) and
             infl.pronoun_data.case == case and
             infl.pronoun_data.number == number]
        return l[0] if len(l) > 0 else None


    def get_adjective_inflection_rule(self, declention: DeclentionType, declention_varient: DeclentionSubtype, gender: Gender, case: Case, number: Number, adjective_kind: AdjectiveKind) -> Optional[InflectionRule]:
        l = [infl for infl in self.inflection_list if
             infl.part_of_speech == PartOfSpeech.Adjective and
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
             infl.part_of_speech == PartOfSpeech.Verb and
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
             infl.part_of_speech == PartOfSpeech.Participle and
             conjugation_type_matches(infl.participle_entry.conjugation, conjugation) and
             conjugation_subtype_matches(infl.participle_entry.conjugation_variant, conjugation_variant) and
             infl.participle_entry.number == number and
             infl.participle_entry.case == case and
             infl.participle_entry.voice == voice and
             infl.participle_entry.tense == tense]
        return l[0] if len(l) > 0 else None

    def get_adverb_inflection_rule(self, adjective_kind_key: AdjectiveKind, adjective_kind_output: AdjectiveKind) -> Optional[InflectionRule]:
        l = [infl for infl in self.inflection_list if
             infl.part_of_speech == PartOfSpeech.Adverb and
             infl.adverb_data.adjective_kind_key == adjective_kind_key and
             infl.adverb_data.adjective_kind_output == adjective_kind_output]
        return l[0] if len(l) > 0 else None


class NormalLexicon(Lexicon, metaclass=ABCMeta):
    def __init__(self, path):
        Lexicon.__init__(self, path)

    def load(self, path: str):
        self.load_inflections(path)
        self.load_dictionary(path)
        self.load_addons(path)
        self.load_uniques(path)

    def _add_inflection_rule(self, pos: PartOfSpeech, m, line, index):
        assert m is not None
        inflection_data = POS_INFL_ENTRY_CLASS_MP[pos].from_str(m.group(2))
        stem_key = int(m.group(3))
        ending_len = int(m.group(4))
        ending = m.group(5)

        assert len(ending) == ending_len, (line, ending, ending_len)

        if not ending in self.map_ending_infls:
            self.map_ending_infls[ending] = []
        rule = InflectionRule(pos,
                                inflection_data,
                                stem_key,
                                ending,
                                InflectionAge.from_str(m.group(6)),
                                InflectionFrequency.from_str(m.group(7)),
                                index)

        self.inflection_list.append(rule)
        self.map_ending_infls[ending].append(rule)

    def load_inflections(self, path):
        index = 0  # this might be useful to a formater by specifying the order that the entries are in the dictionary
        with open(path + "/DataFiles/INFLECTS.txt", encoding="ISO-8859-1") as ifile:
            for line in ifile:
                line = line.strip().split("--")[0].strip()
                if line.strip() == "":
                    continue

                m = re.match(r"(\S*) +(.*) +(\d) (\d) (\S*) +(\S) (\S)", line)
                assert m is not None
                part_of_speech = PartOfSpeech.from_str(m.group(1))
                self._add_inflection_rule(part_of_speech, m, line, index)
                index +=1
                if part_of_speech == PartOfSpeech.Pronoun:
                    # this allows us to conjugate packons as well
                    self._add_inflection_rule(PartOfSpeech.Packon, m, line, index)
                    index +=1

    def insert_lemma(self, lemma: DictionaryLemma, index: int):
        # function to generate alternate forms for each stem by applying i,j and u,v substitiutions, and
        def alternate_forms_of_stem(stem: str) -> Generator[str, None, None]:
            def subs_in_locs(stem: str, locs: Tuple[int, ...], replacement: str):
                for k in locs:
                    stem = stem[:k] + replacement + stem[k + 1:]
                return stem

            import itertools
            stem = stem.lower()
            indx_j = [i for i, c in enumerate(stem) if c == 'j']
            indx_v = [i for i, c in enumerate(stem) if c == 'v' if i > 0]
            for locs_i in itertools.chain.from_iterable(
                    itertools.combinations(indx_j, n) for n in range(len(indx_j) + 1)):
                for locs_u in itertools.chain.from_iterable(
                        itertools.combinations(indx_v, n) for n in range(len(indx_v) + 1)):
                    s = subs_in_locs(subs_in_locs(stem, locs_i, "i"), locs_u, "u")
                    if len(s) > 1 and s[0] in {'u', 'v'}:
                        yield 'u' + s[1:]
                        yield 'v' + s[1:]
                    else:
                        yield s

        lemma.rebuild(index)
        self.dictionary_lemmata.append(lemma)
        for key in lemma.dictionary_keys:
            self.dictionary_keys.append(key)
            for stem_base, i in zip(key.stems, [1, 2, 3, 4]):
                if stem_base is None:
                    continue
                for stem in alternate_forms_of_stem(stem_base):
                    if not stem in self._stem_map[(lemma.part_of_speech, i)]:
                        self._stem_map[(lemma.part_of_speech, i)][stem] = []
                    self._stem_map[(lemma.part_of_speech, i)][stem].append(key)

    @abstractmethod
    def load_dictionary(self, path: str):
        pass

    def load_addons(self, path: str):
        self.prefix_list.append(None)
        self.suffix_list.append(None)
        self.tackon_list.append(None)
        with open(path + "DataFiles/ADDONS.txt", encoding="ISO-8859-1") as ifile:
            lines = [line[:-1].split("--")[0] for line in ifile if line.split("--")[0] != ""]
        assert len(lines) % 3 == 0
        while len(lines) > 0:
            l1, l2, l3 = lines[0], lines[1], lines[2]
            lines = lines[3:]
            kind = l1[:6]
            if kind == "PREFIX":
                self.prefix_list.append(PrefixEntry(l1, l2, l3))
            elif kind == "SUFFIX":
                self.suffix_list.append(SuffixEntry(l1, l2, l3))
            elif kind == "TACKON":
                self.tackon_list.append(TackonEntry(l1, l2, l3))
            else:
                raise ValueError(lines)


    def load_uniques(self, path: str):
        with open(path + "DataFiles/UNIQUES.txt", encoding="ISO-8859-1") as ifile:
            lines = [line[:-1].split("--")[0] for line in ifile if line.split("--")[0] != ""]
        assert len(lines) % 3 == 0
        while len(lines) > 0:
            l1, l2, l3 = lines[0], lines[1], lines[2]
            lines = lines[3:]
            kind = l1[:6]
            u = UniqueEntry(l1, l2, l3)
            self.uniques[u.word] = u

# The hope is that this case silently replace normal Lexicons, which being faster to load and MUCH lower memory usage
# which is good on my server. It uses the code in low_memory_stems, which is c++ code that is backed by swig
class CppDictLexicon(NormalLexicon, metaclass=ABCMeta):
    def __init__(self, path: str, dict_file: str):
        self.dict_file = dict_file
        NormalLexicon.__init__(self, path)

    def load_dictionary(self, path: str):
        import PyWhitakersWords.low_memory_stems.fast_dict_keys as fdk
        self.dict_object = fdk.DictionaryStemCollection()
        cpp_file = path + "/" + self.dict_file
        print("LOADING CPP FILE", cpp_file)
        self.dict_object.load(cpp_file)

    def get_stem_map(self, pos: PartOfSpeech, stem_key: int) -> Dict[str, List[DictionaryKey]]:
        return self.dict_object.get_stem_dict_view_for(int(pos), stem_key)
    @property
    def dictionary_keys(self)-> List[DictionaryKey]:
        return self.dict_object.all_keys
    @property
    def dictionary_lemmata(self)-> List[DictionaryKey]:
        return self.dict_object.all_lemmata


class Formater(metaclass=ABCMeta):
    def __init__(self, lex: Lexicon):
        self.lex = lex

    @abstractmethod
    def parse(self, s) -> str:
        pass
