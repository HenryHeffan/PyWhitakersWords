# import re
# import enum
from core_files.utils import *
from core_files.base_data_structures import *
import json
import os.path

import io
open = io.open

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
        m = re.match(r"TACKON (\S*)\s*", l1)
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


########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
#                                                    Lexicon Rules                                                     #
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################


class Lexicon(ABC):
    def __init__(self):
        pass
        # self._inflection_list: List[InflectionRule] = []
        # self._inflection_pos_map: Dict[PartOfSpeech, List[InflectionRule]] = {pos: [] for pos in PartOfSpeech}
        # self._dictionary_keys: List[DictionaryKey] = []
        # self._dictionary_lemmata: List[DictionaryLemma] = []
        self.prefix_list: List[Optional[PrefixEntry]] = []
        self.suffix_list: List[Optional[SuffixEntry]] = []
        self.tackon_list: List[Optional[TackonEntry]] = []
        self.uniques: Dict[str, UniqueEntry] = {}
        # self.map_ending_infls: Dict[str, List[InflectionRule]] = {}
        # self._stem_map: Dict[Tuple[PartOfSpeech, int], Dict[str, List[DictionaryKey]]] = \
        #     {(pos, stem_key): {} for pos in PartOfSpeech for stem_key in range(1,5)}
        # self.load(path)

    @property
    @abstractmethod
    def map_ending_infls(self) -> Dict[str, List[InflectionRule]]:
        pass

    @abstractmethod
    def get_stem_map(self, pos: PartOfSpeech, stem_key: int) -> Dict[str, List[DictionaryKey]]:
        pass

    @property
    @abstractmethod
    def dictionary_keys(self)-> List[DictionaryKey]:
        pass

    @property
    @abstractmethod
    def dictionary_lemmata(self)-> List[DictionaryLemma]:
        pass

    @abstractmethod
    def load(self, path: str) -> None:
        pass

    @abstractmethod
    def get_noun_inflection_rule(self, declention: DeclentionType, declention_varient: DeclentionSubtype,
                                 gender: Gender, case: Case, number: Number) -> Optional[InflectionRule]:
        pass
    @abstractmethod
    def get_number_inflection_rule(self, declention: DeclentionType, declention_varient: DeclentionSubtype,
                                   gender: Gender, case: Case, number: Number, number_kind: NumberKind) -> Optional[InflectionRule]:
        pass
    @abstractmethod
    def get_pronoun_inflection_rule(self, declention: DeclentionType, declention_varient: DeclentionSubtype,
                                    gender: Gender, case: Case, number: Number) -> Optional[InflectionRule]:
        pass
    @abstractmethod
    def get_adjective_inflection_rule(self, declention: DeclentionType, declention_varient: DeclentionSubtype,
                                      gender: Gender, case: Case, number: Number, adjective_kind: AdjectiveKind) -> Optional[InflectionRule]:
        pass
    @abstractmethod
    def get_verb_inflection_rule(self, conjugation: ConjugationType, conjugation_variant: ConjugationSubtype,
                                 number: Number, person: Person, voice: Voice, tense: Tense, mood: Mood) -> Optional[InflectionRule]:
        pass
    @abstractmethod
    def get_participle_inflection_rule(self, conjugation: ConjugationType, conjugation_variant: ConjugationSubtype,
                                       number: Number, case: Case, voice: Voice, tense: Tense) -> Optional[InflectionRule]:
        pass
    @abstractmethod
    def get_adverb_inflection_rule(self, adjective_kind_key: AdjectiveKind, adjective_kind_output: AdjectiveKind) -> Optional[InflectionRule]:
        pass
    @abstractmethod
    def get_preposition_inflection_rule(self):
        pass
    @abstractmethod
    def get_conjunction_inflection_rule(self):
        pass
    @abstractmethod
    def get_interjection_inflection_rule(self):
        pass

class NormalExceptInflLexicon(Lexicon):
    def __init__(self):
        Lexicon.__init__(self)

    def load_addons(self, path: str):
        self.prefix_list.append(None)
        self.suffix_list.append(None)
        self.tackon_list.append(None)
        with open(os.path.join(path, "DataFiles/ADDONS.txt"), encoding="ISO-8859-1") as ifile:
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
        with open(os.path.join(path, "DataFiles/UNIQUES.txt"), encoding="ISO-8859-1") as ifile:
            lines = [line[:-1].split("--")[0] for line in ifile if line.split("--")[0] != ""]
        assert len(lines) % 3 == 0
        while len(lines) > 0:
            l1, l2, l3 = lines[0], lines[1], lines[2]
            lines = lines[3:]
            kind = l1[:6]
            u = UniqueEntry(l1, l2, l3)
            self.uniques[u.word] = u


class NormalLexicon(NormalExceptInflLexicon):
    def __init__(self):
        Lexicon.__init__(self)
        self._inflection_list: List[InflectionRule] = []
        self._inflection_pos_map: Dict[PartOfSpeech, List[InflectionRule]] = {pos: [] for pos in PartOfSpeech}
        self._map_ending_infls: Dict[str, List[InflectionRule]] = {}
        self._map_pos_infls_lookup: Dict[Tuple, List[InflectionRule]] = {k: [] for k in
            [(pos, decl, decl_var) for pos in PartOfSpeech for decl, decl_var in ALL_DECL_VAR_PAIRS] +
            [(pos, conj, conj_var) for pos in PartOfSpeech for conj, conj_var in ALL_CONJ_VAR_PAIRS] +
            [(pos) for pos in PartOfSpeech]}

    def load_inflections(self, path):
        # print("PATH", path, os.path.join(path, "DataFiles/INFLECTS.txt"))
        index = 0  # this might be useful to a formater by specifying the order that the entries are in the dictionary
        with open(os.path.join(path, "DataFiles/INFLECTS.txt"), encoding="ISO-8859-1") as ifile:
            for line in ifile:
                line = line.strip().split("--")[0].strip()
                if line.strip() == "":
                    continue

                m = re.match(r"(\S*) +(.*) +(\d) (\d) (\S*) +(\S) (\S)", line)
                assert m is not None
                part_of_speech = PartOfSpeech.from_str(m.group(1))
                self._insert_inflection_rule(part_of_speech, m, line, index)
                index +=1
                if part_of_speech == PartOfSpeech.Pronoun:
                    # this allows us to conjugate packons as well
                    self._insert_inflection_rule(PartOfSpeech.Packon, m, line, index)
                    index +=1

    @property
    def map_ending_infls(self) -> Dict[str, List[InflectionRule]]:
        return self._map_ending_infls

    def _insert_inflection_rule(self, pos: PartOfSpeech, m, line, index):
        assert m is not None
        inflection_data = POS_INFL_ENTRY_CLASS_MP[pos].from_str(m.group(2))
        stem_key = int(m.group(3))
        ending_len = int(m.group(4))
        ending = m.group(5)

        assert len(ending) == ending_len, (line, ending, ending_len)

        if not ending in self._map_ending_infls:
            self._map_ending_infls[ending] = []
        rule = InflectionRule(pos,
                                inflection_data,
                                stem_key,
                                ending,
                                InflectionAge.from_str(m.group(6)),
                                InflectionFrequency.from_str(m.group(7)),
                                index)

        # self._inflection_list.append(rule)
        # self._inflection_pos_map   [rule.part_of_speech].append(rule)
        self._map_ending_infls[ending].append(rule)

        if pos in {PartOfSpeech.Noun, PartOfSpeech.Pronoun, PartOfSpeech.Adjective, PartOfSpeech.Number}:
            self._map_pos_infls_lookup[(pos, rule.pos_data.declention, rule.pos_data.declention_variant)].append(rule)
        elif pos in {PartOfSpeech.Verb, PartOfSpeech.Participle}:
            self._map_pos_infls_lookup[(pos, rule.pos_data.conjugation, rule.pos_data.conjugation_variant)].append(rule)
        else:
            self._map_pos_infls_lookup[pos].append(rule)

    def get_noun_inflection_rule(self, declention: DeclentionType, declention_varient: DeclentionSubtype, gender: Gender, case: Case, number: Number) -> Optional[InflectionRule]:
        l: List[InflectionRule] = [
            infl for infl in
            self._map_pos_infls_lookup[(PartOfSpeech.Noun, declention, declention_varient)] +
            self._map_pos_infls_lookup[(PartOfSpeech.Noun, declention, DeclentionSubtype(0))] +
            self._map_pos_infls_lookup[(PartOfSpeech.Noun, DeclentionType(0), DeclentionSubtype(0))]
            if infl.part_of_speech == PartOfSpeech.Noun and
            gender_matches(infl.noun_data.gender, gender) and
            infl.noun_data.case == case and
            infl.noun_data.number == number]
        if len(l) == 0:
            return None
        return max(l, key=lambda x: x.noun_data.gender != gender)

    def get_number_inflection_rule(self, declention: DeclentionType, declention_varient: DeclentionSubtype, gender: Gender, case: Case, number: Number, number_kind: NumberKind) -> Optional[InflectionRule]:
        l: List[InflectionRule] = [
            infl for infl in
            self._map_pos_infls_lookup[(PartOfSpeech.Number, declention, declention_varient)] +
            self._map_pos_infls_lookup[(PartOfSpeech.Number, declention, DeclentionSubtype(0))] +
            self._map_pos_infls_lookup[(PartOfSpeech.Number, DeclentionType(0), DeclentionSubtype(0))]
            if
            gender_matches(infl.number_data.gender, gender) and
            infl.number_data.case == case and
            infl.number_data.number == number and
            infl.number_data.number_kind == number_kind]
        if len(l) == 0:
            return None
        return max(l, key=lambda x: x.noun_data.gender != gender)

    def get_pronoun_inflection_rule(self, declention: DeclentionType, declention_varient: DeclentionSubtype, gender: Gender, case: Case, number: Number) -> Optional[InflectionRule]:
        l: List[InflectionRule] = [
            infl for infl in
            self._map_pos_infls_lookup[(PartOfSpeech.Pronoun, declention, declention_varient)] +
            self._map_pos_infls_lookup[(PartOfSpeech.Pronoun, declention, DeclentionSubtype(0))] +
            self._map_pos_infls_lookup[(PartOfSpeech.Pronoun, DeclentionType(0), DeclentionSubtype(0))]
            if
            gender_matches(infl.pronoun_data.gender, gender) and
            infl.pronoun_data.case == case and
            infl.pronoun_data.number == number]
        if len(l) == 0:
            return None
        return l[0]

    def get_adjective_inflection_rule(self, declention: DeclentionType, declention_varient: DeclentionSubtype, gender: Gender, case: Case, number: Number, adjective_kind: AdjectiveKind) -> Optional[InflectionRule]:
        l: List[InflectionRule] = [
            infl for infl in
            self._map_pos_infls_lookup[(PartOfSpeech.Adjective, declention, declention_varient)] +
            self._map_pos_infls_lookup[(PartOfSpeech.Adjective, declention, DeclentionSubtype(0))] +
            self._map_pos_infls_lookup[(PartOfSpeech.Adjective, DeclentionType(0), DeclentionSubtype(0))]
            if
            gender_matches(infl.adjective_data.gender, gender) and
            infl.adjective_data.case == case and
            infl.adjective_data.number == number and
            infl.adjective_data.adjective_kind == adjective_kind]
        if len(l) == 0:
            return None
        return max(l, key=lambda x: x.noun_data.gender != gender)

    def get_verb_inflection_rule(self, conjugation: ConjugationType, conjugation_variant: ConjugationSubtype, number: Number, person: Person, voice: Voice, tense: Tense, mood: Mood) -> Optional[InflectionRule]:
        l: List[InflectionRule] = [
            infl for infl in
            self._map_pos_infls_lookup[(PartOfSpeech.Verb, conjugation, conjugation_variant)] +
            self._map_pos_infls_lookup[(PartOfSpeech.Verb, conjugation, ConjugationSubtype(0))] +
            self._map_pos_infls_lookup[(PartOfSpeech.Verb, ConjugationType(0), ConjugationSubtype(0))]
            if
            infl.verb_data.number == number and
            infl.verb_data.person == person and
            infl.verb_data.voice == voice and
            infl.verb_data.tense == tense and
            infl.verb_data.mood == mood]
        if len(l) == 0:
            return None
        return max(l, key=lambda x: (-100 if x.verb_data.conjugation == 0 else 0) +
                                    (-100 if x.verb_data.conjugation_variant == 0 else 0))

    def get_participle_inflection_rule(self, conjugation: ConjugationType, conjugation_variant: ConjugationSubtype, number: Number, case: Case, voice: Voice, tense: Tense) -> Optional[InflectionRule]:
        l: List[InflectionRule] = [
            infl for infl in
            self._map_pos_infls_lookup[(PartOfSpeech.Participle, conjugation, conjugation_variant)] +
            self._map_pos_infls_lookup[(PartOfSpeech.Participle, conjugation, ConjugationSubtype(0))] +
            self._map_pos_infls_lookup[(PartOfSpeech.Participle, ConjugationType(0), ConjugationSubtype(0))]
            if
            infl.participle_data.number == number and
            infl.participle_data.case == case and
            infl.participle_data.voice == voice and
            infl.participle_data.tense == tense]
        if len(l) == 0:
            return None
        return l[0]

    def get_adverb_inflection_rule(self, adjective_kind_key: AdjectiveKind, adjective_kind_output: AdjectiveKind) -> Optional[InflectionRule]:
        l: List[InflectionRule] = [
            infl for infl in
            self._map_pos_infls_lookup[(PartOfSpeech.Adverb)]
            if
            infl.adverb_data.adjective_kind_key == adjective_kind_key and
            infl.adverb_data.adjective_kind_output == adjective_kind_output]
        if len(l) == 0:
            return None
        return l[0]

    def get_preposition_inflection_rule(self):
        l = self._map_pos_infls_lookup[(PartOfSpeech.Preposition)]
        return None if len(l) < 0 else l[0]

    def get_conjunction_inflection_rule(self):
        l = self._map_pos_infls_lookup[(PartOfSpeech.Conjunction)]
        return None if len(l) < 0 else l[0]

    def get_interjection_inflection_rule(self):
        l = self._map_pos_infls_lookup[(PartOfSpeech.Interjection)]
        return None if len(l) < 0 else l[0]


class PythonDictLexicon(NormalLexicon):
    def __init__(self):
        NormalLexicon.__init__(self)

        self._stem_map: Dict[Tuple[PartOfSpeech, int], Dict[str, List[DictionaryKey]]] = \
            {(pos, stem_key): {} for pos in PartOfSpeech for stem_key in range(1,5)}
        self._dictionary_keys: List[DictionaryKey] = []
        self._dictionary_lemmata: List[DictionaryLemma] = []

    def _insert_lemma(self, lemma: DictionaryLemma, index: int):
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
        self._dictionary_lemmata.append(lemma)
        for key in lemma.dictionary_keys:
            self._dictionary_keys.append(key)
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

    def load(self, path: str) -> None:
        self.load_dictionary(path)
        self.load_inflections(path)
        self.load_addons(path)
        self.load_uniques(path)

    def get_stem_map(self, pos: PartOfSpeech, stem_key: int) -> Dict[str, List[DictionaryKey]]:
        return self._stem_map[(pos, stem_key)]

    @property
    def dictionary_keys(self)-> List[DictionaryKey]:
        return self._dictionary_keys

    @property
    def dictionary_lemmata(self)-> List[DictionaryLemma]:
        return self._dictionary_lemmata


class OldStyle_DICTLINE_Lexicon(PythonDictLexicon):
    def __init__(self, file_name: str, short):
        PythonDictLexicon.__init__(self)
        self.file_name = file_name
        self.short = short

    def load_dictionary(self, path: str):
        def extract_stem_group(_stems: List, pos: PartOfSpeech, word_data) -> StemGroup:
            if pos == PartOfSpeech.Adjective and word_data.adjective_kind == AdjectiveKind.Superlative:
                _stems[3] = _stems[0]
            elif pos == PartOfSpeech.Adjective and word_data.adjective_kind == AdjectiveKind.Compairative:
                _stems[2] = _stems[0]
            stems: StemGroup = _stems  # type: ignore
            return stems

        # here is how this works
        # we read over DICTLINE in a loop. Each time we see a new line, one of three things happens
        # 1) this is a second definition of some existing entry. This will be added to the end, preceded by a '\n'
        # 2) this is actually an alternate stem for some existing word in the dictionary. this is added as such
        #       TODO maybe the alternate forms for multiline defs have multiple lines of their own
        # 3) this is a new lemma, and we add it as such

        # Participals, Supines, and Verbs all go in the Verb bin
        self.stem_map = {(pos, i): {} for pos in PartOfSpeech for i in [1, 2, 3, 4]}

        index = 0  # this might be useful to a formater by specifying the order that the entries are in the dictionary

        FILENAME = os.path.join(path, self.file_name)
        with open(FILENAME, encoding="ISO-8859-1") as ifile:
            last_lemma: Optional[DictionaryLemma] = None
            working_lemma: Optional[DictionaryLemma] = None
            for line in ifile:
                if line.startswith("--") or line in {"", "\n"}:
                    continue
                # print("LINE", line[:-1])
                if index > 1000 and self.short:
                    break
                # strip out the raw line into its groups
                __stems = [line[:19].strip(), line[19:2 * 19].strip(), line[2 * 19:3 * 19].strip(),
                           line[3 * 19:4 * 19].strip()]
                _stems = [x if x.strip() not in {"zzz", ""} else None for x in __stems]


                # print(_stems)
                # if _stems[0] == "qua":
                #     0/0
                part_of_speech = PartOfSpeech.from_str(line[76:82].strip())
                pos_data = POS_DICT_ENTRY_CLASS_MP[part_of_speech].from_str(line[82:100].strip())
                translation_metadata = TranslationMetadata(line[100:109].strip())
                definition = line[110:-1][:79].lstrip("|")

                if part_of_speech == PartOfSpeech.Packon:
                    pos_data.get_required_tack_from_def(definition)

                stems = extract_stem_group(_stems, part_of_speech, pos_data)

                new_key = DictionaryKey(stems, part_of_speech, pos_data)

                # now figure out what to do with the stem
                # we preserve the following.
                # working_lemma will always only have 1 key in it at most. This is used to collect definitions
                # last_lemma may have multiple keys. This is used to collect keys


                if working_lemma is not None and new_key == working_lemma.dictionary_keys[0]:  # and defen != working_lemma.defen:
                    working_lemma.definition += '\n' + definition
                    # print("DEF CONT!", working_lemma.dictionary_keys[0].stems)
                    continue
                # else working_lemma is None or key != working_lemma.key:
                # the we need to either merge working_lemma into last lemma or push them back
                if last_lemma is not None and working_lemma is not None and \
                        working_lemma.dictionary_keys[0].alternate_form_match(last_lemma.dictionary_keys[-1]) and \
                        working_lemma.definition == last_lemma.definition:
                    # merge them together
                    # print("MERGING!", last_lemma.dictionary_keys[-1], working_lemma.dictionary_keys[0])
                    last_lemma.dictionary_keys.append(working_lemma.dictionary_keys[0])
                    # print("AND THEN BUILDING WORKING LEMMA!", working_lemma.dictionary_keys[0].stems)
                    working_lemma = DictionaryLemma(part_of_speech, [new_key], translation_metadata, definition, None,
                                                    -1)
                    continue
                # if working_lemma is not None and key == working_lemma.dictionary_keys[0]: # and definition == working_lemma.definition.split(''):
                #     raise ValueError("repeated line")
                if working_lemma is None:
                    working_lemma = DictionaryLemma(part_of_speech, [new_key], translation_metadata, definition,
                                                    None,
                                                    -1)
                    # print("BUILDING WORKING LEMMA!", working_lemma.dictionary_keys[0].stems)
                    continue

                if last_lemma is not None:  # add the last lemma
                    index += 1
                    # print("ADDING!", last_lemma.store())
                    self._insert_lemma(last_lemma, index)

                last_lemma = working_lemma
                # print(stems, part_of_speech, new_key.part_of_speech)
                working_lemma = DictionaryLemma(part_of_speech, [new_key], translation_metadata, definition, None, -1)

            # this is hacky, but by looking in DICTLINE I know there is no merging/multiline definitions on the last 2
            # lemmata. Therefore we just manually add them in here
            index += 1
            self._insert_lemma(working_lemma, index)
            index += 1
            self._insert_lemma(last_lemma, index)

        SUM_ESSE_FUI = DictionaryLemma(PartOfSpeech.Verb,
                                       [DictionaryKey(
                                           ("s", "", "fu", "fut"),
                                           PartOfSpeech.Verb,
                                           VerbDictData(ConjugationType(5), ConjugationSubtype(1), VerbKind.To_Being)
                                       )],
                                       TranslationMetadata("X X X A X"),
                                       "be; exist; (also used to form verb perfect passive tenses) with NOM PERF PPL",
                                       None,
                                       index)
        index += 1
        self._insert_lemma(SUM_ESSE_FUI, index)


class NewStyle_Json_Lexicon(PythonDictLexicon):
    def __init__(self, file_name: str, short):
        PythonDictLexicon.__init__(self)
        self.file_name = file_name
        self.short = short

    def load_dictionary(self, path: str):
        self._stem_map = {(pos, i): {} for pos in PartOfSpeech for i in [1,2,3,4]}
        with open(os.path.join(path, self.file_name), "r", encoding='utf-8') as i:
            l = json.load(i)  # [:100]
        if self.short:
            l = l[:100]
        dictionary_lemmata = [DictionaryLemma.load(d) for d in l]
        for i, lemma in enumerate(dictionary_lemmata):
            self._insert_lemma(lemma, lemma.index)


# The hope is that this case silently replace normal Lexicons, which being faster to load and MUCH lower memory usage
# which is good on my server. It uses the code in low_memory_stems, which is c++ code that is backed by swig
class BakedLexicon(NormalExceptInflLexicon):
    def __init__(self, dict_cpp_name: str):
        NormalExceptInflLexicon.__init__(self)
        # self._inflection_list: List[InflectionRule] = []
        # self._inflection_pos_map: Dict[PartOfSpeech, List[InflectionRule]] = {pos: [] for pos in PartOfSpeech}
        # self._map_ending_infls: Dict[str, List[InflectionRule]] = {}
        # self._map_pos_infls_lookup: Dict[Tuple, List[InflectionRule]] = {k: [] for k in
        #                                                                  [(pos, decl, decl_var) for pos in PartOfSpeech
        #                                                                   for decl, decl_var in ALL_DECL_VAR_PAIRS] +
        #                                                                  [(pos, conj, conj_var) for pos in PartOfSpeech
        #                                                                   for conj, conj_var in ALL_CONJ_VAR_PAIRS] +
        #                                                                  [(pos) for pos in PartOfSpeech]}
        self.dict_cpp_name = dict_cpp_name
        self.dict_object = None
        self.infl_object = None

    def load(self, path: str) -> None:
        import low_memory_stems.fast_dict_keys
        self.fdk = low_memory_stems.fast_dict_keys.get_lib()
        self.dict_object = getattr(self.fdk, self.dict_cpp_name)
        self.infl_object = getattr(self.fdk, "BAKED_WW_INFL_RULES")

        self.load_addons(path)
        self.load_uniques(path)


    def get_stem_map(self, pos: PartOfSpeech, stem_key: int) -> Dict[str, List[DictionaryKey]]:
        return self.dict_object.get_hashtable_for(int(pos), stem_key)

    @property
    def dictionary_keys(self)-> List[DictionaryKey]:
        return self.dict_object.all_keys
    @property
    def dictionary_lemmata(self)-> List[DictionaryKey]:
        return self.dict_object.all_lemmata

    @property
    def map_ending_infls(self) -> Dict[str, List[InflectionRule]]:
        return self.infl_object.ending_rule_map

    def get_noun_inflection_rule(self, declention: DeclentionType, declention_varient: DeclentionSubtype, gender: Gender, case: Case, number: Number) -> Optional[InflectionRule]:
        return self.infl_object.get_noun_inflection_rule(int(declention), int(declention_varient), int(gender), int(case), int(number))

    def get_number_inflection_rule(self, declention: DeclentionType, declention_varient: DeclentionSubtype, gender: Gender, case: Case, number: Number, number_kind: NumberKind) -> Optional[InflectionRule]:
        return self.infl_object.get_number_inflection_rule(declention, declention_varient, gender, case, number, number_kind)

    def get_pronoun_inflection_rule(self, declention: DeclentionType, declention_varient: DeclentionSubtype, gender: Gender, case: Case, number: Number) -> Optional[InflectionRule]:
        return self.infl_object.get_pronoun_inflection_rule(declention, declention_varient, gender, case, number)

    def get_adjective_inflection_rule(self, declention: DeclentionType, declention_varient: DeclentionSubtype, gender: Gender, case: Case, number: Number, adjective_kind: AdjectiveKind) -> Optional[InflectionRule]:
        return self.infl_object.get_adjective_inflection_rule(declention, declention_varient, gender, case, number, adjective_kind)

    def get_verb_inflection_rule(self, conjugation: ConjugationType, conjugation_variant: ConjugationSubtype, number: Number, person: Person, voice: Voice, tense: Tense, mood: Mood) -> Optional[InflectionRule]:
        return self.infl_object.get_verb_inflection_rule(conjugation, conjugation_variant, number, person, voice, tense, mood)

    def get_participle_inflection_rule(self, conjugation: ConjugationType, conjugation_variant: ConjugationSubtype, number: Number, case: Case, voice: Voice, tense: Tense) -> Optional[InflectionRule]:
        return self.infl_object.get_participle_inflection_rule(conjugation, conjugation_variant, number, case, voice, tense)

    def get_adverb_inflection_rule(self, adjective_kind_key: AdjectiveKind, adjective_kind_output: AdjectiveKind) -> Optional[InflectionRule]:
        return self.infl_object.get_adverb_inflection_rule(adjective_kind_key, adjective_kind_output)

    def get_preposition_inflection_rule(self):
        return self.infl_object.get_preposition_inflection_rule()

    def get_conjunction_inflection_rule(self):
        return self.infl_object.get_conjunction_inflection_rule()

    def get_interjection_inflection_rule(self):
        return self.infl_object.get_interjection_inflection_rule()

# The hope is that this case silently replace normal Lexicons, which being faster to load and MUCH lower memory usage
# which is good on my server. It uses the code in low_memory_stems, which is c++ code that is backed by swig
# class BakedLexicon(NormalLexicon):
#     def __init__(self, dict_cpp_name: str):
#         NormalLexicon.__init__(self)
#         self.dict_cpp_name = dict_cpp_name
#         self.dict_object = None
#
#     def load(self, path: str) -> None:
#         import low_memory_stems.fast_dict_keys
#         self.fdk = low_memory_stems.fast_dict_keys.get_lib()
#         self.dict_object = getattr(self.fdk, self.dict_cpp_name)
#
#         self.load_inflections(path)
#         self.load_addons(path)
#         self.load_uniques(path)
#
#     def get_stem_map(self, pos: PartOfSpeech, stem_key: int) -> Dict[str, List[DictionaryKey]]:
#         return self.dict_object.get_hashtable_for(int(pos), stem_key)
#
#     @property
#     def dictionary_keys(self) -> List[DictionaryKey]:
#         return self.dict_object.all_keys
#
#     @property
#     def dictionary_lemmata(self) -> List[DictionaryKey]:
#         return self.dict_object.all_lemmata
