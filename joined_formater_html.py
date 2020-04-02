from QuickLatin.entry_and_inflections import *
from QuickLatin.whitakers_words import WW_FORMATER
from QuickLatin.searcher import get_matches, FormGroup, EntryQuery
from typing import List, Tuple, Optional, Dict
from abc import abstractmethod


PATH = "/home/henry/Desktop/latin_website/QuickLatin/"

class JoinedLexicon(Lexicon):
    def load(self):
        self.load_inflections()
        self.load_dictionary()
        self.load_addons()
        self.load_uniques()

    def _add_inflection_rule(self, pos: PartOfSpeech, m, line, index):
        assert m is not None
        inflection_data = POS_INFL_ENTRY_CLASS_MP[pos].from_str(m.group(2))
        stem_key = int(m.group(3))
        ending_len = int(m.group(4))
        ending = m.group(5)

        assert len(ending) == ending_len, (line, ending, ending_len)

        if not ending in self.map_ending_infls:
            self.map_ending_infls[ending] = []
        entry = InflectionRule(pos,
                                inflection_data,
                                stem_key,
                                ending,
                                InflectionAge.from_str(m.group(6)),
                                InflectionFrequency.from_str(m.group(7)),
                                index)

        self.inflection_list.append(entry)
        self.map_ending_infls[ending].append(entry)

    def load_inflections(self):
        index = 0  # this might be useful to a formater by specifying the order that the entries are in the dictionary
        with open(PATH + "/DataFiles/INFLECTS.txt", encoding="ISO-8859-1") as ifile:
            for line in ifile:
                line = line.strip().split("--")[0].strip()
                if line.strip() == "":
                    continue

                m = re.match(r"(\S*) +(.*) +(\d) (\d) (\S*) +(\S) (\S)", line)
                assert m is not None
                part_of_speach = PartOfSpeech.from_str(m.group(1))
                self._add_inflection_rule(part_of_speach, m, line, index)
                index +=1
                if part_of_speach == PartOfSpeech.Pronoun:
                    # this allows us to conjugate packons as well
                    self._add_inflection_rule(PartOfSpeech.Packon, m, line, index)
                    index +=1

    def insert_lemma(self, lemma: DictionaryLemma):
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

        lemma.rebuild(lemma.index)  # keep the index
        self.dictionary_lemmata.append(lemma)
        for key in lemma.dictionary_keys:
            self.dictionary_keys.append(key)
            for stem_base, i in zip(key.stems, [1, 2, 3, 4]):
                if stem_base is None:
                    continue
                for stem in alternate_forms_of_stem(stem_base):
                    if not stem in self.stem_map[(lemma.part_of_speach, i)]:
                        self.stem_map[(lemma.part_of_speach, i)][stem] = []
                    self.stem_map[(lemma.part_of_speach, i)][stem].append(key)

    def load_dictionary(self):
        self.stem_map = {(pos, i): {} for pos in PartOfSpeech for i in [1,2,3,4]}
        import json
        with open("/home/henry/Desktop/latin_website/QuickLatin/DataFiles/JOINED.txt", "r", encoding='utf-8') as i:
            l = json.load(i)
        print("FILE READ")
        dictionary_lemmata = [DictionaryLemma.from_dict(d) for d in l]
        print("LEMATA DECODED")
        for i, lemma in enumerate(dictionary_lemmata):
            self.insert_lemma(lemma)
            # print("{}/{}".format(i, len(dictionary_lemmata)))

    def load_addons(self):
        self.prefix_list.append(None)
        self.suffix_list.append(None)
        self.tackon_list.append(None)
        with open(PATH + "DataFiles/ADDONS.LAT", encoding="ISO-8859-1") as ifile:
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


    def load_uniques(self):
        with open(PATH + "DataFiles/UNIQUES.LAT", encoding="ISO-8859-1") as ifile:
            lines = [line[:-1].split("--")[0] for line in ifile if line.split("--")[0] != ""]
        assert len(lines) % 3 == 0
        while len(lines) > 0:
            l1, l2, l3 = lines[0], lines[1], lines[2]
            lines = lines[3:]
            kind = l1[:6]
            u = UniqueEntry(l1, l2, l3)
            self.uniques[u.word] = u


J_LEX = JoinedLexicon()

TWO_WORD_TEMP = """
<div class="two_word_group">
    <div class="two_word_header">
        {header_slot}
    </div>
    {word_1_slot}
    {word_2_slot}
</div>
"""

TACKON_TEMP = """
<div class="tackon_group">
    <div class="row cannon_form_row">
        <div class="col-sm-12">
            {tackon_str}
        </div>
    </div>
    <div class="definition_group">
        {tackon_meaning}
    </div>
</div>
"""



PREFIX_TEMP = """
<div class="prefix_group row">
    <div class="col-sm-3 cannon_form_row">
        Prefix: {prefix_str}
    </div>
    <div class="col-sm-9 definition_group">
        {prefix_meaning}
    </div>
</div>
"""

SUFFIX_TEMP = """
<div class="suffix_group row">
    <div class="col-sm-3 cannon_form_row">
        Suffix: {suffix_str}
    </div>
    <div class="col-sm-9 definition_group">
        {suffix_meaning}
    </div>
</div>
"""

METADATA_TEMP = """
<div class="row metadata_row">
    <div class="col-sm-6 metadata_row_slot1">
        {metadata_slot_1}
    </div>
    <div class="col-sm-6 metadata_row_slot2">
        {metadata_slot_2}
    </div>
</div>
"""

DEFINITION_ROW_TEMP = """
<div class="row definition_row">
    <div class="col-sm-12">
        {definition_row_slot}
    </div>
</div>
"""

FORM_ROW_TEMP = """
<div class="row form_row">
    <div class="col-sm-4">
        {form_row_word_slot}
    </div>
    <div class="col-sm-8">
        {form_row_form_slot}
    </div>
</div>
"""

CANNON_MAIN_ROW_TEMP = """
<div class="row cannon_form_main_row">
    <div class="col-sm-10">
        {cannon_form_slot}
    </div>
    <!--<div class="col-sm-2 cannon_form_main_row_suffix">
        {cannon_form_suffix}
    </div>-->
    <div class="col-sm-2">
        {button_space}
    </div>
</div>
"""
CANNON_ALT_ROW_TEMP = """
<div class="row cannon_form_alt_row">
    <div class="col-sm-12">
        {cannon_form_slot}
    </div>
</div>
"""

HTML_SPACE_TEMP = """<div class="collapse" id="collapseSpot{id_slot}"><div class="panel panel-default"><div class="panel-body">
    {html_slot}
</div></div></div>"""

WORD_GROUP_TEMP = """
<div class="word_group" id="{id_slot}">
    <div class="cannon_rows_group">
        {cannon_rows_space}
    </div>
    {metadata_space}
    <div class="definition_group">
        {definition_rows_space}
    </div>
    {prefix_space}
    {suffix_space}
    <div class="forms_group">
        {form_rows_space}
    </div>
    {html_space}
</div>
"""

for gen in Gender:
    gen.alt_str_val = {
            Gender.Male: "masc",
            Gender.Female: "fem",
            Gender.Nueter: "neut",
            Gender.Common: "common",
            Gender.X: "X"
        }[gen]

for num in Number:
    num.alt_str_val = {
        Number.Singular: "sg",
        Number.Plural: "pl",
        Number.X: "X"
    }[num]

for voice in Voice:
    voice.alt_str_val = {
        Voice.Active: "act",
        Voice.Passive: "pass",
        Voice.X: "X"
    }[voice]

for mood in Mood:
    mood.alt_str_val = {
        Mood.X: "X",
        Mood.Subjunctive: "subj",
        Mood.Infinative: "inf",
        Mood.Imperative: "imp",
        Mood.Indicitive: "ind"
    }[mood]

for person in Person:
    person.alt_str_val = {
        Person.X: "X",
        Person.First: "1st",
        Person.Second: "2nd",
        Person.Third: "3rd",
    }[person]


class FormaterBase:
    def __init__(self, lex: Lexicon):
        self.inflection_table = {}
        self.lex = lex

    @abstractmethod
    def setup(self) -> None:
        pass

    def sort_infls_key(self, infl: InflectionRule):
        return 0

    def format_infl_metadata(self, metadata: Tuple[InflectionAge, InflectionFrequency]) -> str:
        age, freq = metadata
        age_str = {InflectionAge.Always: "",
                   InflectionAge.Archaic: "  Archaic ",
                   InflectionAge.Early: "  Early   ",
                   InflectionAge.Classic: "  Classic ",
                   InflectionAge.Late: "  Late    ",
                   InflectionAge.Later: "  Later   ",
                   InflectionAge.Medieval: "  Medieval",
                   InflectionAge.Scholar: "  Scholar ",
                   InflectionAge.Modern: "  Modern  "}[age]
        freq_str = {InflectionFrequency.X: "",
                    InflectionFrequency.A: "",
                    InflectionFrequency.B: "",
                    InflectionFrequency.C: "  uncommon",
                    InflectionFrequency.D: "  infreq  ",
                    InflectionFrequency.E: "  rare    ",
                    InflectionFrequency.F: "  veryrare",
                    InflectionFrequency.I: "  inscript", }[freq]
        return age_str + freq_str

    def dic_metadata_frequency(self, dic: DictionaryLemma):
        return {
            DictionaryFrequency.A: "",
            DictionaryFrequency.B: "",
            DictionaryFrequency.C: "",
            DictionaryFrequency.D: "  lesser",
            DictionaryFrequency.E: "  uncommon",
            DictionaryFrequency.F: "  veryrare",
            DictionaryFrequency.N: "  Pliny",
            DictionaryFrequency.I: "  inscript",
            DictionaryFrequency.X: "",
        }[dic.translation_metadata.freqency]
    def dic_metadata_age(self, dic: DictionaryLemma) -> str:
        return {
            DictionaryAge.Always: "  ",
            DictionaryAge.Archaic: "    Archaic",
            DictionaryAge.Early: "    Early",
            DictionaryAge.Classic: "  ",
            DictionaryAge.Late: "    Late",
            DictionaryAge.Later: "    Later",
            DictionaryAge.Medieval: "    Medieval",
            DictionaryAge.NeoLatin: "    NeoLatin",
            DictionaryAge.Modern: "    Modern"
        }[dic.translation_metadata.age]

    # def format_group(self, dic: DictionaryKey, infls: List[InflectionRule], word: str) -> Tuple[str, str, str]:
    #     before = "\n".join(
    #         [pad_to_len(self.infl_entry_line(dic, infl, word), 56) + self.format_infl_metadata(infl.metadata)
    #          for infl in sorted(infls, key=self.sort_infls_key)])
    #     cannon = self.dic_entry_line(dic) + "\n"  # cannon_form
    #     defen = "\n".join([l[:79] if len(l) >= 79 else l for l in dic.definition.lines])
    #     return before, cannon, defen

    def make_infl_row_str(self, dic: DictionaryKey, infl: InflectionRule, is_syncopy: bool) -> str:
        return self.infl_entry_line(dic, infl, "") + ("" if not is_syncopy else " (syncopated)")

    @abstractmethod
    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        pass

    # @abstractmethod
    # def dic_entry_line(self, dic: DictionaryKey) -> str:
    #     pass

    @abstractmethod
    def make_cannon_form_str(self, dic: DictionaryKey) -> str:
        pass

    @abstractmethod
    def get_extra_info_spot(self, dic: DictionaryKey) -> str:
        pass

    def dictionary_key_form(self, dic: DictionaryKey) -> str:
        return self.make_cannon_form_str(dic).split(',')[0]


class NounFormater(FormaterBase):
    def get_key(self, dic: DictionaryKey):
        return dic.noun_data.declention, dic.noun_data.declention_variant, dic.noun_data.gender

    SORT_ORDER = [Case.Nominative, Case.Vocative, Case.Genative, Case.Locitive, Case.Dative, Case.Accusitive,
                  Case.Ablative, Case.X]

    def sort_infls_key(self, infl):
        return self.SORT_ORDER.index(infl.noun_data.case) + 10 * infl.noun_data.number

    def setup(self) -> None:
        # called once on each class. Use to setup noun formating rules
        for (decl, decl_var, gender) in set([self.get_key(dic)
                                             for i in range(1, 5)
                                             for (stem, l) in self.lex.stem_map[(PartOfSpeech.Noun, i)].items()
                                             for dic in l]):
            nom = self.lex.get_noun_inflection_rule(decl, decl_var, gender, Case.Nominative, Number.Singular)
            gen = self.lex.get_noun_inflection_rule(decl, decl_var, gender, Case.Genative, Number.Singular)
            self.inflection_table[(decl, decl_var, gender)] = [nom, gen]

    def make_cannon_form_str(self, dic: DictionaryKey) -> str:
        infls = self.inflection_table[self.get_key(dic)]
        nom = dic.make_form(infls[0], default="-")
        gen = dic.make_form(infls[1], default="-")
        if (dic.noun_data.declention, dic.noun_data.declention_variant) == (2, 4):
            gen = gen[:-1] + "(i)"
        elif (dic.noun_data.declention, dic.noun_data.declention_variant) in {(3, 7), (3, 9)}:
            gen = gen[:-2] + "os/is"
        elif (dic.noun_data.declention, dic.noun_data.declention_variant) == (9, 8):
            stem = dic.stems[0]
            assert stem is not None
            nom = stem + "."
            gen = "abb."
        elif (dic.noun_data.declention, dic.noun_data.declention_variant) == (9, 9):
            stem = dic.stems[0]
            assert stem is not None
            nom = stem
            gen = "undeclined"
        return "{}, {}".format(nom, gen)

    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        return "noun {case} {number} {gender}".format(
            case=infl.noun_data.case.str_val.lower(),
            number=infl.noun_data.number.alt_str_val,
            gender=combine_gender(infl.noun_data.gender, dic.noun_data.gender).alt_str_val
        )

    # def dic_entry_line(self, dic: DictionaryKey) -> str:
    #     decl = {1: "(1st decl.) ", 2: "(2nd decl.) ", 3: "(3rd decl.) ", 4: "(4th decl.) ", 5: "(5th decl.) ", 9: ""}[dic.noun_data.declention]
    #     # if dic.noun_data.declention == 3 and dic.noun_data.declention_variant not in {1, 2, 3, 4}:
    #     #     decl = ""
    #     if dic.noun_data.declention_variant > 5:
    #         decl = ""
    #     return "{cannon_form}  N {decl}{gender}   {metadata}".format(
    #         cannon_form=self.make_cannon_form_str(dic),
    #         decl=decl,
    #         gender=dic.noun_data.gender.str_val.upper(),
    #         metadata=self.format_dic_metadata(dic.translation_metadata)
    #     )

    def get_extra_info_spot(self, dic: DictionaryKey) -> str:
        decl = {1: "(1st decl.) ", 2: "(2nd decl.) ", 3: "(3rd decl.) ", 4: "(4th decl.) ", 5: "(5th decl.) ", 9: ""}[
            dic.noun_data.declention]
        # if dic.noun_data.declention == 3 and dic.noun_data.declention_variant not in {1, 2, 3, 4}:
        #     decl = ""
        if dic.noun_data.declention_variant > 5:
            decl += " greek"
        return decl


# TODO: this one needs work
class PronounFormater(FormaterBase):
    def get_key(self, dic: DictionaryKey):
        return dic.pronoun_data.declention, dic.pronoun_data.declention_variant

    SORT_ORDER = [Case.Nominative, Case.Vocative, Case.Genative, Case.Dative, Case.Ablative, Case.Accusitive,
                  Case.Locitive, Case.X]

    def sort_infls_key(self, infl):
        return self.SORT_ORDER.index(infl.pronoun_data.case) + 10 * infl.pronoun_data.number

    def setup(self) -> None:
        # for Pronoun: nom, gen
        for (decl, decl_var) in set([self.get_key(dic)
                                     for i in range(1, 5)
                                     for (stem, l) in self.lex.stem_map[(PartOfSpeech.Pronoun, i)].items()
                                     for dic in l]):
            self.inflection_table[(decl, decl_var)] = \
                [self.lex.get_pronoun_inflection_rule(decl, decl_var, gender, Case.Nominative, Number.Singular)
                 for gender in Gender.MFN()]

    def make_cannon_form_str(self, dic: DictionaryKey) -> str:
        # print(dic.part_of_speach)
        infls = self.inflection_table[self.get_key(dic)]
        if (dic.pronoun_data.declention, dic.pronoun_data.declention_variant) in {(3, 1), (4, 1), (6, 1)}:
            return "{}, {}, {}".format(
                dic.make_form(infls[0], default="-"),
                dic.make_form(infls[1], default="-"),
                dic.make_form(infls[2], default="-"))
        else:
            return ""

    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        # h.ic                 PRON   3 1 NOM S M
        return "pronoun {case} {number} {gender}".format(
            case=infl.pronoun_data.case.str_val.lower(),
            number=infl.pronoun_data.number.alt_str_val,
            gender=infl.pronoun_data.gender.alt_str_val
        )

    # def dic_entry_line(self, dic: DictionaryKey) -> str:
    #     # hic, haec, hoc  PRON   [XXXAX]
    #     cannon_form = self.make_cannon_form_str(dic)
    #     return "{cannon_form}{pos} {metadata}".format(
    #         cannon_form=cannon_form,
    #         pos="" if cannon_form == "" else "  PRON  ",
    #         metadata=self.format_dic_metadata(dic.translation_metadata)
    #     )

    def get_extra_info_spot(self, dic: DictionaryKey) -> str:
        return ""


class VerbFormater(FormaterBase):
    def filter_verb_kind(self, vk: VerbKind) -> VerbKind:
        return vk if vk in {VerbKind.Impers, VerbKind.Dep, VerbKind.Semidep, VerbKind.Perfdef} else VerbKind.X

    def get_key(self, dic: DictionaryKey):
        return dic.verb_data.conjugation, dic.verb_data.conjugation_variant, self.filter_verb_kind(
            dic.verb_data.verb_kind)

    def setup(self) -> None:
        pass
        # for Verb:
        for (conj, conj_var, vk) in set([self.get_key(dic)
                                         for i in range(1, 5)
                                         for stem, l in self.lex.stem_map[(PartOfSpeech.Verb, i)].items()
                                         for dic in l]):
            if vk == VerbKind.X:
                pp1 = self.lex.get_verb_inflection_rule(conj, conj_var, Number.Singular, Person.First, Voice.Active,
                                               Tense.Present,
                                               Mood.Indicitive)
                pp2 = self.lex.get_verb_inflection_rule(conj, conj_var, Number.X, Person.X, Voice.Active, Tense.Present,
                                               Mood.Infinative)
                pp3 = self.lex.get_verb_inflection_rule(conj, conj_var, Number.Singular, Person.First, Voice.Active,
                                               Tense.Perfect,
                                               Mood.Indicitive)
                pp4 = self.lex.get_participle_inflection_rule(conj, conj_var, Number.Singular, Case.Nominative, Voice.Passive,
                                                     Tense.Perfect)
                if (conj, conj_var) == (5, 1):
                    pp4 = self.lex.get_participle_inflection_rule(conj, conj_var, Number.Singular, Case.Nominative, Voice.Active,
                                                         Tense.Future)
                self.inflection_table[(conj, conj_var, vk)] = [pp1, pp2, pp3, pp4]
            elif vk == VerbKind.Impers:
                pp1 = self.lex.get_verb_inflection_rule(conj, conj_var, Number.Singular, Person.Third, Voice.Active,
                                               Tense.Present,
                                               Mood.Indicitive)
                pp2 = self.lex.get_verb_inflection_rule(conj, conj_var, Number.X, Person.X, Voice.Active, Tense.Present,
                                               Mood.Infinative)
                pp3 = self.lex.get_verb_inflection_rule(conj, conj_var, Number.Singular, Person.Third, Voice.Active,
                                               Tense.Perfect,
                                               Mood.Indicitive)
                pp4 = self.lex.get_participle_inflection_rule(conj, conj_var, Number.Singular, Case.Nominative, Voice.Passive,
                                                     Tense.Perfect)
                self.inflection_table[(conj, conj_var, vk)] = [pp1, pp2, pp3, pp4]
            elif vk == VerbKind.Semidep:
                pp1 = self.lex.get_verb_inflection_rule(conj, conj_var, Number.Singular, Person.First, Voice.Active,
                                               Tense.Present,
                                               Mood.Indicitive)
                # if (conj, conj_var) == (3, 3):
                pp2 = self.lex.get_verb_inflection_rule(conj, conj_var, Number.X, Person.X, Voice.Active, Tense.Present,
                                               Mood.Infinative)
                # else:
                #     pp2 = self.lex.get_verb_inflection_rule(conj, conj_var, Number.X, Person.X, Voice.Active, Tense.Present, Mood.Infinative)
                pp4 = self.lex.get_participle_inflection_rule(conj, conj_var, Number.Singular, Case.Nominative, Voice.Passive,
                                                     Tense.Perfect)
                self.inflection_table[(conj, conj_var, vk)] = [pp1, pp2, pp4]
            elif vk == VerbKind.Dep:
                pp1 = self.lex.get_verb_inflection_rule(conj, conj_var, Number.Singular, Person.First, Voice.Passive,
                                               Tense.Present,
                                               Mood.Indicitive)
                pp2 = self.lex.get_verb_inflection_rule(conj, conj_var, Number.X, Person.X, Voice.Passive, Tense.Present,
                                               Mood.Infinative)
                pp4 = self.lex.get_participle_inflection_rule(conj, conj_var, Number.Singular, Case.Nominative, Voice.Passive,
                                                     Tense.Perfect)
                self.inflection_table[(conj, conj_var, vk)] = [pp1, pp2, pp4]
            elif vk == VerbKind.Perfdef:
                pp1 = self.lex.get_verb_inflection_rule(conj, conj_var, Number.Singular, Person.First, Voice.Active,
                                               Tense.Perfect,
                                               Mood.Indicitive)
                pp2 = self.lex.get_verb_inflection_rule(conj, conj_var, Number.X, Person.X, Voice.Active, Tense.Perfect,
                                               Mood.Infinative)
                pp4 = self.lex.get_participle_inflection_rule(conj, conj_var, Number.Singular, Case.Nominative, Voice.Passive,
                                                     Tense.Perfect)
                self.inflection_table[(conj, conj_var, vk)] = [pp1, pp2, pp4]
            else:
                raise ValueError()

    def make_cannon_form_str(self, dic: DictionaryKey) -> str:
        infls = self.inflection_table[self.get_key(dic)]
        if dic.verb_data.verb_kind == VerbKind.Perfdef:
            return "{}, {}, {}".format(dic.make_form(infls[0], default="-"),
                                       dic.make_form(infls[1], default="-"),
                                       dic.make_form(infls[2], default="-"))
        elif dic.verb_data.verb_kind in {VerbKind.Dep, VerbKind.Semidep}:
            return "{}, {}, {} sum".format(dic.make_form(infls[0], default="-"),
                                           dic.make_form(infls[1], default="-"),
                                           dic.make_form(infls[2], default="-"))
        elif dic.verb_data.verb_kind == VerbKind.Impers:
            return "{}, {}, {}, {} est".format(dic.make_form(infls[0], default="-"),
                                               dic.make_form(infls[1], default="-"),
                                               dic.make_form(infls[2], default="-"),
                                               dic.make_form(infls[3], default="-"))
        else:
            return "{}, {}, {}, {}".format(dic.make_form(infls[0], default="-"),
                                           dic.make_form(infls[1], default="-"),
                                           dic.make_form(infls[2], default="-")
                                           + ("(ii)" if (dic.verb_data.conjugation,
                                                         dic.verb_data.conjugation_variant) == (
                                                            6, 1) else ""),
                                           dic.make_form(infls[3], default="-"))

    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        if infl.part_of_speach == PartOfSpeech.Verb:
            return self.infl_entry_line_verb(dic, infl, word)
        elif infl.part_of_speach == PartOfSpeech.Supine:
            return self.infl_entry_line_suppine(dic, infl, word)
        elif infl.part_of_speach == PartOfSpeech.Participle:
            return self.infl_entry_line_participle(dic, infl, word)
        else:
            raise ValueError()

    def infl_entry_line_verb(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        # conj = dic.verb_data.conjugation
        # conj_var = dic.verb_data.conjugation_variant
        # if (conj, conj_var) == (3, 4):
        #     conj, conj_var = ConjugationType(4), ConjugationSubtype(1)
        return "verb {tense} {voice} {mood} {person} {number}".format(
            tense=infl.verb_data.tense.str_val.lower(),
            voice=infl.verb_data.voice.alt_str_val if dic.verb_data.verb_kind != VerbKind.Dep else "deponent",
            mood=pad_to_len(infl.verb_data.mood.str_val.lower(), 3),
            person=infl.verb_data.person.alt_str_val,
            number=infl.verb_data.number.alt_str_val,
        )

    def infl_entry_line_suppine(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        return "supine {case} {number} {gender}".format(
            case=infl.supine_entry.case.str_val.lower(),
            number=infl.supine_entry.number.alt_str_val,
            gender=infl.supine_entry.gender.alt_str_val,
        )

    def infl_entry_line_participle(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        return "participle {case} {number} {gender} {tense} {voice}".format(
            case=infl.participle_entry.case.str_val.lower(),
            number=infl.participle_entry.number.alt_str_val,
            gender=infl.participle_entry.gender.alt_str_val,
            tense=infl.participle_entry.tense.str_val.lower(),
            voice=infl.participle_entry.voice.alt_str_val if dic.verb_data.verb_kind != VerbKind.Dep else "deponent",
        )

    # def dic_entry_line(self, dic: DictionaryKey) -> str:
    #     conj_str = ""
    #     if dic.verb_data.conjugation == 1:
    #         conj_str = " (1st)"
    #     elif dic.verb_data.conjugation == 2:
    #         conj_str = " (2nd)"
    #     elif dic.verb_data.conjugation == 3 and dic.verb_data.conjugation_variant == 1:
    #         conj_str = " (3rd)"
    #     elif dic.verb_data.conjugation == 3 and dic.verb_data.conjugation_variant == 4:
    #         conj_str = " (4th)"
    #
    #     return "{cannon_form}  V{conj_str}{verb_kind}   {metadata}".format(
    #         cannon_form=self.make_cannon_form_str(dic),
    #         conj_str=conj_str,
    #         verb_kind=(" " + dic.verb_data.verb_kind.str_val.upper()) if dic.verb_data.verb_kind in
    #                                                                      {VerbKind.Trans, VerbKind.Intrans,
    #                                                                       VerbKind.Dep,
    #                                                                       VerbKind.Semidep, VerbKind.Impers,
    #                                                                       VerbKind.Perfdef,
    #                                                                       VerbKind.Dat, VerbKind.Abl} else "",
    #         metadata=self.format_dic_metadata(dic.translation_metadata)
    #     )

    def get_extra_info_spot(self, dic: DictionaryKey) -> str:
        conj_str = ""
        if dic.verb_data.conjugation == 1:
            conj_str = " (1st conj.)"
        elif dic.verb_data.conjugation == 2:
            conj_str = " (2nd conj.)"
        elif dic.verb_data.conjugation == 3 and dic.verb_data.conjugation_variant == 1:
            conj_str = " (3rd conj.)"
        elif dic.verb_data.conjugation == 3 and dic.verb_data.conjugation_variant == 4:
            conj_str = " (4th conj.)"
        return conj_str

    def sort_infls_key_verb(self, infl: InflectionRule):
        # return 0
        # 	argu.it              V      3 1 PRES ACTIVE  IND 3 S
        # 	argu.it              V      3 1 PERF ACTIVE  IND 3 S

        #  	carp.ere             V      3 1 PRES ACTIVE  INF 0 X
        # 	carp.ere             V      3 1 PRES PASSIVE IMP 2 S
        # 	carp.ere             V      3 1 FUT  PASSIVE IND 2 S

        SORT_ORDER_TENSE = [Tense.Present, Tense.Imperfect, Tense.Future, Tense.Perfect, Tense.Pluperfect,
                            Tense.FuturePerfect, Tense.X]
        SORT_ORDER_VOICE = [Voice.Active, Voice.Passive, Voice.X]
        SORT_ORDER_MOOD = [Mood.Indicitive, Mood.Subjunctive, Mood.Imperative, Mood.Infinative, Mood.X]
        if infl.part_of_speach != PartOfSpeech.Verb:
            return 0
        else:
            return SORT_ORDER_TENSE.index(infl.verb_data.tense) * 100 + SORT_ORDER_VOICE.index(
                infl.verb_data.voice) * 10 + SORT_ORDER_MOOD.index(infl.verb_data.mood)

    SORT_ORDER_VPAR = [Case.Nominative, Case.Vocative, Case.Genative, Case.Locitive, Case.Dative, Case.Accusitive,
                       Case.Ablative, Case.X]

    def sort_infls_key_part(self, infl: InflectionRule):
        if infl.part_of_speach != PartOfSpeech.Participle:
            return 0
        else:
            return self.SORT_ORDER_VPAR.index(infl.participle_entry.case) + 10 * infl.participle_entry.number

    # def format_group(self, dic: DictionaryKey, infls: List[InflectionRule], word: str) -> Tuple[str, str, str]:
    #     verbs = [pad_to_len(self.infl_entry_line(dic, infl, word), 56) + self.format_infl_metadata(infl.metadata)
    #              for infl in sorted(infls, key=self.sort_infls_key_verb) if infl.part_of_speach == PartOfSpeech.Verb]
    #     vpars = [pad_to_len(self.infl_entry_line(dic, infl, word), 56) + self.format_infl_metadata(infl.metadata)
    #              for infl in sorted(infls, key=self.sort_infls_key_part) if
    #              infl.part_of_speach == PartOfSpeech.Participle]
    #     sups = [pad_to_len(self.infl_entry_line(dic, infl, word), 56) + self.format_infl_metadata(infl.metadata)
    #             for infl in sorted(infls, key=self.sort_infls_key) if infl.part_of_speach == PartOfSpeech.Supine]
    #     forms = "\n".join(verbs + vpars + sups)
    #     cannon = self.dic_entry_line(dic) + "\n"  # cannon_form
    #     defen = "\n".join([l[:79] if len(l) >= 79 else l for l in dic.definition.lines])
    #     return forms, cannon, defen


# TODO: this one needs work
class AdjectiveFormater(FormaterBase):
    def get_key(self, dic: DictionaryKey):
        return dic.adjective_data.declention, dic.adjective_data.declention_variant

    def setup(self) -> None:
        for (decl, decl_var) in set([self.get_key(dic)
                                     for i in range(1, 5)
                                     for (stem, l) in self.lex.stem_map[(PartOfSpeech.Adjective, i)].items()
                                     for dic in l]):
            pos = [self.lex.get_adjective_inflection_rule(decl, decl_var, g, Case.Nominative, Number.Singular,
                                                 AdjectiveKind.Positive)
                   for g in Gender.MFN()]
            comp = [self.lex.get_adjective_inflection_rule(decl, decl_var, g, Case.Nominative, Number.Singular,
                                                  AdjectiveKind.Compairative)
                    for g in Gender.MFN()]
            sup = [self.lex.get_adjective_inflection_rule(decl, decl_var, g, Case.Nominative, Number.Singular,
                                                 AdjectiveKind.Superlative)
                   for g in Gender.MFN()]

            self.inflection_table[(decl, decl_var)] = [pos, comp, sup]
        self.inflection_gen_3_1_pos = self.lex.get_adjective_inflection_rule(DeclentionType(3), DeclentionSubtype(1), Gender.X,
                                                                    Case.Genative, Number.Singular,
                                                                    AdjectiveKind.Positive)

    def make_cannon_form_str(self, dic: DictionaryKey) -> str:
        # pos, comp, sup = "", "", ""
        infls = self.inflection_table[self.get_key(dic)]
        # pos = "{} -{} -{}"
        if dic.stems[2] is None and dic.stems[3] is None:
            # This means that it is either just POS, just COMP, or just SUPER
            # therefore just show all the genders of this word
            s1 = dic.make_form(infls[0][0], default="*")
            if self.get_key(dic) == (3, 1):
                s2 = "(gen.)"
                s3 = dic.make_form(self.inflection_gen_3_1_pos, default="*")
            elif self.get_key(dic) == (1, 3):
                s2 = dic.make_form(infls[0][1], default="*")
                s3 = dic.make_form(infls[0][2], default="*") + " (gen -ius)"
            else:
                s2 = dic.make_form(infls[0][1], default="*")
                s3 = dic.make_form(infls[0][2], default="*")

            return "{}, {}, {}".format(s1, s2, s3)

        # Otherwise, this has multiple stems. Therefore show all the stems, and within all the genders
        s1 = dic.make_form(infls[0][0], default="*")

        if self.get_key(dic) == (3, 2):
            s2 = dic.make_form(infls[0][2], default="*")
        elif self.get_key(dic) == (3, 1):
            s2 = dic.make_form(self.inflection_gen_3_1_pos) + " (gen.)"
        else:
            s2 = "{} -{}".format(
                dic.make_form(infls[0][1], default="*"),
                "*" if infls[0][2] is None else infls[0][2].ending
            )

        comp_str = "{} -{} -{}".format(
            dic.make_form(infls[1][0], default="*"),
            "*" if infls[1][1] is None else infls[1][1].ending,
            "*" if infls[1][2] is None else infls[1][2].ending
        )
        if comp_str[0] == "*":
            comp_str = "-"

        sup_str = "{} -{} -{}".format(
            dic.make_form(infls[2][0], default="*"),
            "*" if infls[2][1] is None else infls[2][1].ending[1:],  # -a instead of -ma
            "*" if infls[2][2] is None else infls[2][2].ending[1:]  # -a instead of -ma
        )
        if sup_str[0] == "*":
            sup_str = "-"

        if dic.adjective_data.adjective_kind == AdjectiveKind.Compairative:
            return "{}, {}, {}".format(
                dic.make_form(infls[1][0], default="*"),
                dic.make_form(infls[1][1], default="*"),
                dic.make_form(infls[1][2], default="*")
            )
        elif dic.adjective_data.adjective_kind == AdjectiveKind.Superlative:
            return "{}, {}, {}".format(
                dic.make_form(infls[2][0], default="*"),
                dic.make_form(infls[2][1], default="*"),
                dic.make_form(infls[2][2], default="*")
            )
        else:
            return "{}, {}, {}, {}".format(
                s1, s2, comp_str, sup_str
            )

    SORT_ORDER = [Case.Nominative, Case.Vocative, Case.Genative, Case.Dative, Case.Ablative, Case.Accusitive,
                  Case.Locitive, Case.X]

    def sort_infls_key(self, infl):
        return self.SORT_ORDER.index(infl.adjective_data.case) + 10 * infl.adjective_data.number

    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        # grav.i               ADJ    3 2 DAT S X POS
        # grav.i               ADJ    3 2 ABL S X POS
        return "adj {case} {number} {gender} {adj_kind}".format(
            case=infl.adjective_data.case.str_val.lower(),
            number=infl.adjective_data.number.alt_str_val,
            gender=infl.adjective_data.gender.alt_str_val,
            adj_kind=infl.adjective_data.adjective_kind.str_val.lower()
        )

    # def dic_entry_line(self, dic: DictionaryKey) -> str:
    #     # gravis, grave, gravior -or -us, gravissimus -a -um  ADJ   [XXXAX]
    #     return "{cannon_form}  ADJ   {metadata}".format(
    #         cannon_form=self.make_cannon_form_str(dic),
    #         metadata=self.format_dic_metadata(dic.translation_metadata)
    #     )

    def get_extra_info_spot(self, dic: DictionaryKey) -> str:
        return ""


# TODO: this one needs some work
class AdverbFormater(FormaterBase):
    def setup(self) -> None:
        pass

        for k in [AdjectiveKind.Positive, AdjectiveKind.Compairative, AdjectiveKind.Superlative]:
            self.inflection_table[k] = [self.lex.get_adverb_inflection_rule(k, k)]  # there is only 1
        self.inflection_table[AdjectiveKind.X] = \
            [self.lex.get_adverb_inflection_rule(AdjectiveKind.X, AdjectiveKind.Positive),
             self.lex.get_adverb_inflection_rule(AdjectiveKind.X, AdjectiveKind.Compairative),
             self.lex.get_adverb_inflection_rule(AdjectiveKind.X, AdjectiveKind.Superlative)]

    def make_cannon_form_str(self, dic: DictionaryKey) -> str:
        infls = self.inflection_table[dic.adverb_data.adjective_kind]
        if dic.adverb_data.adjective_kind == AdjectiveKind.X:
            return "{}, {}, {}".format(
                dic.make_form(infls[0]),
                dic.make_form(infls[1]),
                dic.make_form(infls[2])
            )
        else:
            return "{}".format(dic.make_form(infls[0]))

    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        return "adv {adj_kind}".format(
            adj_kind=infl.adverb_data.adjective_kind_output.str_val.lower()
        )

    # def dic_entry_line(self, dic: DictionaryKey) -> str:
    #     return "{cannon_form}  ADV   {metadata}".format(
    #         cannon_form=self.make_cannon_form_str(dic),
    #         metadata=self.format_dic_metadata(dic.translation_metadata)
    #     )
    def get_extra_info_spot(self, dic: DictionaryKey) -> str:
        return ""


class PrepositionFormater(FormaterBase):
    def setup(self) -> None:
        self.inflection_rule = [infl for infl in self.lex.inflection_list if infl.part_of_speach == PartOfSpeech.Preposition][0]

    def make_cannon_form_str(self, dic: DictionaryKey) -> str:
        return dic.make_form(self.inflection_rule)

    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        # cum                  PREP   ABL
        return "prep w/ {case}".format(
            case=dic.preposition_data.takes_case.str_val.lower()
        )

    # def dic_entry_line(self, dic: DictionaryKey) -> str:
    #     # cum  PREP  ABL   [XXXAO]
    #     return "{cannon_form}  PREP  {case}   {metadata}".format(
    #         cannon_form=self.make_cannon_form_str(dic),
    #         case=dic.preposition_data.takes_case.str_val.upper(),
    #         metadata=self.format_dic_metadata(dic.translation_metadata)
    #     )

    def get_extra_info_spot(self, dic: DictionaryKey) -> str:
        return "+ {}".format(dic.preposition_data.takes_case.str_val.lower())


class ConjunctionFormater(FormaterBase):
    def setup(self) -> None:
        self.inflection_rule = [infl for infl in self.lex.inflection_list if infl.part_of_speach == PartOfSpeech.Conjunction][0]

    def make_cannon_form_str(self, dic: DictionaryKey) -> str:
        return dic.make_form(self.inflection_rule)

    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        # at                   CONJ
        return "conj"

    # def dic_entry_line(self, dic: DictionaryKey) -> str:
    #     # at  CONJ   [XXXAO]
    #     return "{cannon_form}  CONJ   {metadata}".format(
    #         cannon_form=self.make_cannon_form_str(dic),
    #         metadata=self.format_dic_metadata(dic.translation_metadata)
    #     )

    def get_extra_info_spot(self, dic: DictionaryKey) -> str:
        return ""


class InterjectionFormater(FormaterBase):
    def setup(self) -> None:
        self.inflection_rule = [infl for infl in self.lex.inflection_list if infl.part_of_speach == PartOfSpeech.Interjection][0]

    def make_cannon_form_str(self, dic: DictionaryKey) -> str:
        return dic.make_form(self.inflection_rule)

    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        # heu                  INTERJ
        return "interj"

    # def dic_entry_line(self, dic: DictionaryKey) -> str:
    #     # heu  INTERJ   [XXXAX]
    #     return "{cannon_form}  INTERJ   {metadata}".format(
    #         cannon_form=self.make_cannon_form_str(dic),
    #         metadata=self.format_dic_metadata(dic.translation_metadata)
    #     )
    def get_extra_info_spot(self, dic: DictionaryKey) -> str:
        return ""


class NumberFormater(FormaterBase):
    def get_key(self, dic: DictionaryKey):
        return dic.number_data.declention, dic.number_data.declention_variant

    SORT_ORDER = [Case.Nominative, Case.Vocative, Case.Genative, Case.Locitive, Case.Dative, Case.Accusitive,
                  Case.Ablative, Case.X]

    def sort_infls_key(self, infl):
        return self.SORT_ORDER.index(infl.number_data.case) + 10 * infl.number_data.number

    def setup(self) -> None:
        for (decl, decl_var) in set([self.get_key(dic)
                                     for i in range(1, 5)
                                     for (stem, l) in self.lex.stem_map[(PartOfSpeech.Number, i)].items()
                                     for dic in l]):
            card = [self.lex.get_number_inflection_rule(decl, decl_var, g, Case.Nominative, Number.Singular, NumberKind.Cardinal)
                    for
                    g in Gender.MFN()]
            ordinal = [
                self.lex.get_number_inflection_rule(decl, decl_var, g, Case.Nominative, Number.Singular, NumberKind.Ordinal)
                for g in Gender.MFN()]
            dist = [
                self.lex.get_number_inflection_rule(decl, decl_var, g, Case.Nominative, Number.Plural, NumberKind.Distributive)
                for g in Gender.MFN()]
            adverb = self.lex.get_number_inflection_rule(decl, decl_var, Gender.X, Case.X, Number.X, NumberKind.Adverb)
            self.inflection_table[(decl, decl_var)] = [card, ordinal, dist, [adverb]]

    def make_cannon_form_str(self, dic: DictionaryKey) -> str:
        infls = self.inflection_table[self.get_key(dic)]
        return "{} -{} -{}, {} -{} -{}, {} -{} -{}, {}".format(
            dic.make_form(infls[0][0], default="*"),
            "*" if infls[0][1] is None else infls[0][1].ending,
            "*" if infls[0][2] is None else infls[0][2].ending,
            dic.make_form(infls[1][0], default="*"),
            "*" if infls[1][1] is None else infls[1][1].ending,
            "*" if infls[1][2] is None else infls[1][2].ending,
            dic.make_form(infls[2][0], default="*"),
            "*" if infls[2][1] is None else infls[2][1].ending,
            "*" if infls[2][2] is None else infls[2][2].ending,
            dic.make_form(infls[3][0], default="*")
        )

    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        # un.a                 NUM    1 1 NOM S F CARD
        # un.a                 NUM    1 1 VOC S F CARD
        # un.a                 NUM    1 1 ABL S F CARD
        return "num {case} {number} {gender} {num_kind}".format(
            case=infl.number_data.case.str_val.lower(),
            number=infl.number_data.number.alt_str_val,
            gender=infl.number_data.gender.alt_str_val,
            num_kind=infl.number_data.number_kind.str_val.lower()
        )

    # def dic_entry_line(self, dic: DictionaryKey) -> str:
    #     # unus -a -um, primus -a -um, singuli -ae -a, semel  NUM   [XXXAX]
    #     return "{cannon_form}  NUM   {metadata}".format(
    #         cannon_form=self.make_cannon_form_str(dic),
    #         metadata=self.format_dic_metadata(dic.translation_metadata)
    #     )

    def get_extra_info_spot(self, dic: DictionaryKey) -> str:
        return ""

    # def format_group(self, dic: DictionaryKey, infls: List[InflectionRule], word: str) -> Tuple[str, str, str]:
    #     before = "\n".join(
    #         [pad_to_len(self.infl_entry_line(dic, infl, word), 56) + self.format_infl_metadata(infl.metadata)
    #          for infl in sorted(infls, key=self.sort_infls_key)])
    #     cannon = self.dic_entry_line(dic) + "\n"  # cannon_form
    #     defen = "\n".join([l[:79] if len(l) >= 79 else l for l in dic.definition.lines])
    #     if all(infl.number_data.number_kind == NumberKind.Ordinal for infl in infls):
    #         defen = pad_to_len(
    #             " {number}th - (ORD, 'in series'); (a/the) {number}th (part) (fract w/pars?);                  ".format(
    #                 number=dic.number_data.numeric_value), 80)
    #     elif all(infl.number_data.number_kind == NumberKind.Cardinal for infl in infls):
    #         defen = pad_to_len(" {number} - (CARD answers 'how many');".format(number=dic.number_data.numeric_value),
    #                            80)
    #     return before, cannon, defen


class PackonFormater(FormaterBase):
    def get_key(self, dic: DictionaryKey):
        return dic.packon_data.declention, dic.packon_data.declention_variant

    SORT_ORDER = [Case.Nominative, Case.Vocative, Case.Genative, Case.Dative, Case.Ablative, Case.Accusitive,
                  Case.Locitive, Case.X]

    def sort_infls_key(self, infl):
        return self.SORT_ORDER.index(infl.packon_data.case) + 10 * infl.packon_data.number

    def setup(self) -> None:
        # for Packon: nom, gen
        for (decl, decl_var) in set([self.get_key(dic)
                                     for i in range(1, 5)
                                     for (stem, l) in self.lex.stem_map[(PartOfSpeech.Packon, i)].items()
                                     for dic in l]):
            self.inflection_table[(decl, decl_var)] = \
                [self.lex.get_pronoun_inflection_rule(decl, decl_var, gender, Case.Nominative, Number.Singular)
                 for gender in Gender.MFN()]

    def make_cannon_form_str(self, dic: DictionaryKey) -> str:
        # print(dic.part_of_speach)
        infls = self.inflection_table[self.get_key(dic)]
        if (dic.packon_data.declention, dic.packon_data.declention_variant) in {(3, 1), (4, 1), (6, 1)}:
            return "{}, {}, {}".format(
                dic.make_form(infls[0], default="-"),
                dic.make_form(infls[1], default="-"),
                dic.make_form(infls[2], default="-"))
        else:
            return ""

    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        # h.ic                 PRON   3 1 NOM S M
        return "pron {case} {number} {gender}".format(
            case=infl.packon_data.case.str_val.lower(),
            number=infl.packon_data.number.alt_str_val,
            gender=infl.packon_data.gender.alt_str_val
        )

    # def dic_entry_line(self, dic: DictionaryKey) -> str:
    #     # hic, haec, hoc  PRON   [XXXAX]
    #     cannon_form = self.make_cannon_form_str(dic)
    #     return "{cannon_form}{pos} {metadata}".format(
    #         cannon_form=cannon_form,
    #         pos="" if cannon_form == "" else "  PRON  ",
    #         metadata=self.format_dic_metadata(dic.translation_metadata)
    #     )
    def get_extra_info_spot(self, dic: DictionaryKey) -> str:
        return ""


class Formater:
    def __init__(self,
                 lex: Lexicon,
                 noun: NounFormater,
                 pronoun: PronounFormater,
                 verb: VerbFormater,
                 adjective: AdjectiveFormater,
                 adverb: AdverbFormater,
                 preposition: PrepositionFormater,
                 conjunction: ConjunctionFormater,
                 interjection: InterjectionFormater,
                 number: NumberFormater,
                 packon: PackonFormater):
        self.lex = lex
        self.map = {
            PartOfSpeech.Noun: noun,
            PartOfSpeech.Pronoun: pronoun,
            PartOfSpeech.Verb: verb,
            PartOfSpeech.Adjective: adjective,
            PartOfSpeech.Adverb: adverb,
            PartOfSpeech.Preposition: preposition,
            PartOfSpeech.Conjunction: conjunction,
            PartOfSpeech.Interjection: interjection,
            PartOfSpeech.Number: number,
            PartOfSpeech.Packon: packon
        }
        for formater in self.map.values():
            formater.setup()

    def dictionary_keyword(self, dic: DictionaryKey) -> str:
        return self.map[dic.part_of_speach].dictionary_key_form(dic)

    # def format_suffix_group(self, form_group: FormGroup, word: str) -> Tuple[str, str, str]:
    #     assert form_group.suffix is not None
    #     formater_pos_infl = self.map[form_group.suffix.new_pos]
    #     formater_pos_stem = self.map[form_group.suffix.stem_pos]
    #     dic = form_group.suffix.make_fake_dic_key(form_group.dic)
    #     before = "\n".join([pad_to_len(formater_pos_infl.infl_entry_line(dic, infl, word),
    #                                    56) + formater_pos_infl.format_infl_metadata(infl.metadata)
    #                         for infl in sorted(form_group.infls, key=formater_pos_infl.sort_infls_key)])
    #     cannon = formater_pos_stem.dic_entry_line(form_group.dic) + "\n"  # cannon_form
    #     defen = "\n".join([l[:79] if len(l) >= 79 else l for l in form_group.dic.definition.lines])
    #     return before, cannon, defen

    def display_entry_query(self, query: EntryQuery, no_newline=False) -> str:
        if query.two_words:
            assert query.two_words_query1 is not None
            assert query.two_words_query2 is not None
            return TWO_WORD_TEMP.format(
                header_slot="2 words ({}+{})?"
                          .format(query.two_words_query1.unsyncopated_word, query.two_words_query2.unsyncopated_word),
                word_1_slot=self.display_entry_query(query.two_words_query1),
                word_2_slot=self.display_entry_query(query.two_words_query2),
            )

        # first, clean up the FormGroups from the Query to form FormatFormGroups

        # class SyncopyMetadata:
        #     def __init__(self, word: str, is_syncopy: bool, why: Optional[str]):
        #         self.word = word
        #         self.is_syncopy = is_syncopy
        #         self.why = why

        # class FormatFormGroup:
        #     def __init__(self,
        #                  dic: DictionaryKey,
        #                  infls_is_sync_pairs: List[Tuple[InflectionRule, SyncopyMetadata]],
        #                  alt_dic: List[DictionaryKey],
        #                  prefix: Optional[PrefixEntry],
        #                  suffix: Optional[SuffixEntry],
        #                  tackon: Optional[TackonEntry]):
        #         self.dic = dic
        #         self.infls_is_sync_pairs = infls_is_sync_pairs
        #         self.alt_dic = alt_dic
        #         self.prefix = prefix
        #         self.suffix = suffix
        #         # not actually dispalyed, except for a note in the metadata.
        #         # The tackon is shared, and so will have its own row
        #         self.tackon = tackon

        # format_groups = []
        #
        # form_group_map: Dict[str, List[Tuple[FormGroup, bool, str, Optional[str]]]]= {}
        # for group in query.unsyncopated_form_groups:
        #     if not str(group.dic) in form_group_map:
        #         form_group_map[str(group.dic)] = []
        #     form_group_map[str(group.dic)].append((group, False, query.unsyncopated_word, None))
        # for group in query.syncopated_form_groups:
        #     if not str(group.dic) in form_group_map:
        #         form_group_map[str(group.dic)] = []
        #     form_group_map[str(group.dic)].append((group, True, query.syncopated_word, query.syncopated_why))
        #
        # for key in form_group_map:
        #     # form_group_map[key].sort(key=lambda x: x[0].dic.index)
        #     main_group = form_group_map[key][0]
        #     for form_group in form_group_map[key][1:]:
        #         assert form_group[0].suffix == main_group[0].suffix and \
        #                form_group[0].tackon == main_group[0].tackon and \
        #                form_group[0].prefix == main_group[0].prefix
        #     infls = []
        #     for form_group in form_group_map[key]:
        #         for infl in form_group[0].infls:
        #             ent = (infl, SyncopyMetadata(form_group[2], form_group[1], query.syncopated_why if form_group[1] else None))
        #             if not any(i == ent for i in infls):
        #                 infls.append(ent)
        #     format_group = FormatFormGroup(main_group[0].dic, infls, [],  # the next step is to join groups which share both the forms and definitions
        #                                    form_group[0].prefix, form_group[0].suffix, form_group[0].tackon)
        #     format_groups.append(format_group)
        #
        # nls: List[FormatFormGroup] = []
        # for format_group_pos in format_groups:
        #     for format_group in nls:
        #         if format_group.dic.part_of_speach == format_group_pos.dic.part_of_speach and\
        #                 format_group.dic.definition.lines == format_group_pos.dic.definition.lines and\
        #                 format_group.infls_is_sync_pairs == format_group_pos.infls_is_sync_pairs and\
        #                 format_group.tackon == format_group_pos.tackon and\
        #                 format_group.prefix == format_group_pos.prefix and\
        #                 format_group.suffix == format_group_pos.suffix:
        #             format_group.alt_dic.append(format_group_pos.dic)
        #             break
        #     else:
        #         nls.append(format_group_pos)
        #
        # # now all groups with shared dictionary and inflections have been changed over to be alternate stems
        # format_groups = nls

        format_groups = query.sync_marked_form_groups()

        tackons = []
        for format_group in format_groups:
            if format_group.tackon is not None and not any(format_group.tackon is tackon for tackon in tackons):
                tackons.append(format_group.tackon)

        # NOW OUTPUT THE DICTIONARY

        output = []
        # first output tackons at the top
        for tackon in tackons:
            output.append(TACKON_TEMP.format(
                tackon_str="-"+tackon.tackon,
                tackon_meaning=tackon.explination
            ))

        # (lemma, [(key, infl, syncopy_q, word)])

        # then output each of the format_groups
        for format_group in format_groups:
            group_id = format_group.lemma.index
            # TODO TEST alternate forms
            if format_group.suffix is None:
                infl_formater = self.map[format_group.lemma.part_of_speach]
                dic_formater = self.map[format_group.lemma.part_of_speach]
                inflectable_dic = format_group.lemma
            else:
                infl_formater = self.map[format_group.suffix.new_pos]
                dic_formater = self.map[format_group.suffix.stem_pos]
                inflectable_dic = format_group.suffix.make_fake_dic_key(format_group.lemma.dictionary_keys[0])


            cannon_form_rows = [CANNON_MAIN_ROW_TEMP.format(
                cannon_form_slot=dic_formater.make_cannon_form_str(format_group.lemma.dictionary_keys[0]),
                cannon_form_suffix=(" +" + format_group.tackon.tackon) if format_group.tackon is not None else "",
                button_space=("""<button class="btn btn-secondary" type="button"
				data-toggle="collapse" data-target="#collapseSpot{id}"
				aria-expanded="false" aria-controls="collapseSpot">L&S</button>""".format(id=group_id)) if format_group.lemma.html_data else ""
            )]
            for key in format_group.lemma.dictionary_keys[1:]:
                cannon_form_rows.append(CANNON_ALT_ROW_TEMP.format(cannon_form_slot=dic_formater.make_cannon_form_str(key)))
            # [DEFINITION_ROW_TEMP.format(definition_row_slot=line) for line in
            definition_rows = format_group.lemma.definition

            # print(format_group.dic.part_of_speach, [infl.part_of_speach for infl, sync_data in format_group.infls_is_sync_pairs ], format_group.suffix)
            # print(format_group.suffix, [((key.part_of_speach, key.stems), form.part_of_speach, word, is_sync) for key, form, word, is_sync in format_group.key_infl_pairs])
            form_rows = [FORM_ROW_TEMP.format(
                form_row_word_slot=form.make_split_word_form(word),
                form_row_form_slot=infl_formater.make_infl_row_str(
                    format_group.suffix.make_fake_dic_key(key) if format_group.suffix is not None else key,
                    form,
                    is_sync)
            ) for key, form, word, is_sync in format_group.key_infl_pairs]

            output.append(WORD_GROUP_TEMP.format(
                id_slot=group_id,
                cannon_rows_space="".join(cannon_form_rows),
                prefix_space = PREFIX_TEMP.format(
                    prefix_str=format_group.prefix.prefix + "-",
                    prefix_meaning=format_group.prefix.explination
                ) if format_group.prefix is not None else "",
                suffix_space = SUFFIX_TEMP.format(
                    suffix_str="-"+format_group.suffix.suffix+"-",
                    suffix_meaning=format_group.suffix.explination
                ) if format_group.suffix is not None else "",
                metadata_space=METADATA_TEMP.format(
                    metadata_slot_1=format_group.lemma.part_of_speach.name + " &nbsp; &nbsp; &nbsp; " +
                                    dic_formater.get_extra_info_spot(format_group.lemma.dictionary_keys[0]),
                    metadata_slot_2=dic_formater.dic_metadata_frequency(format_group.lemma) + " &nbsp; &nbsp; &nbsp; " +
                                    dic_formater.dic_metadata_age(format_group.lemma)
                ),
                definition_rows_space="".join(definition_rows),
                html_space=HTML_SPACE_TEMP.format(
                    id_slot=group_id,
                    html_slot=format_group.lemma.html_data
                ) if format_group.lemma.html_data else "",
                form_rows_space="".join(form_rows)
            ))
        return "".join(output)


formater = Formater(J_LEX,
                    NounFormater(J_LEX),
                    PronounFormater(J_LEX),
                    VerbFormater(J_LEX),
                    AdjectiveFormater(J_LEX),
                    AdverbFormater(J_LEX),
                    PrepositionFormater(J_LEX),
                    ConjunctionFormater(J_LEX),
                    InterjectionFormater(J_LEX),
                    NumberFormater(J_LEX),
                    PackonFormater(J_LEX))

def set_formater(_formater: Formater) -> None:
    global formater
    formater = _formater


def parse(s) -> str:
    m = get_matches(J_LEX, s)
    # print(m)
    return formater.display_entry_query(m)


def parse_and_def(s) -> Tuple[str, str]:
    m = get_matches(J_LEX, s)

    def extract(fgs: List[FormGroup]):
        r = []
        for fg in fgs:
            r.append("\n".join([WW_FORMATER.map[fg.lemma.part_of_speach].dic_entry_line(fg.lemma.dictionary_keys[0])]
                               + ["    " + line for line in fg.lemma.definition.split("\n")]))
        return r

    l = extract(m.unsyncopated_form_groups) + extract(m.syncopated_form_groups) + (
        [] if not m.two_words else
        extract(m.two_words_query1.unsyncopated_form_groups) + extract(m.two_words_query2.syncopated_form_groups))
    # print("\n".join(l))
    r = "\n".join(l)
    if r != "":
        r += "\n"
    # print(">>>{}<<<".format(r))
    return formater.display_entry_query(m), r


def parse_document(filename, encoding="utf-8"):
    lines_raw = []
    with open(filename, encoding=encoding) as inp:
        for line in inp:
            lines_raw.append(line.split("--")[0])
    lines = []
    endings = []
    for i in range(150):  # len(l)):
        if lines_raw[i].strip() == "":
            if i > 0:
                endings[-1] = "\n=>Blank exits =>"
        else:
            lines.append(lines_raw[i].strip())
            endings.append("\n=>")
    # print(lines, endings)
    for line, ending in zip(lines, endings):
        for word in line.split(" "):
            word = word.strip()
            if word is not "":
                print(parse(word))
        print(ending)


# parse_document("/home/henry/Desktop/latin_website/QuickLatin/aeneid_bk4.txt")
print(parse("qui"))


# e                    SUFFIX
# make of;
# sature.o             ADJ    1 1 DAT S M POS
# sature.o             ADJ    1 1 DAT S N POS
# sature.o             ADJ    1 1 ABL S M POS
# sature.o             ADJ    1 1 ABL S N POS
# satura, saturae  N  F   [XXXCX]
# satire;


# print(parse("Uxor"))
# print(parse("Vxor"))
# print(parse("eadem"))
# print(parse("Olidissimis"))
# print(parse("  die'"))
#
#   di.e                 N      2 1 VOC S M
# 	dius, dii  N (2nd) M   [DEXFS]    Late  veryrare
# 	god;
# 	di.e                 N      5 1 GEN S C                   Early
# 	di.e                 N      5 1 ABL S C
# 	dies, diei  N (5th) C   [XXXAO]
# 	day; daylight; (sunlit hours); (24 hours from midnight); open sky; weather;
# 	specific day; day in question; date of letter; festival; lifetime, age; time;
# 	di.e                 ADJ    1 1 VOC S M POS
# 	dius, dia, dium  ADJ   [XEXDO]    lesser
# 	divine; w/supernatural radiance; divinely inspired; blessed, saint (Latham);
# 	daylit; charged with brightness of day/daylight;
# 	e                    SUFFIX
# 	-ly; -ily;  Converting ADJ to ADV
# 	di.e                 ADV    POS
# 	dius, dia, dium  ADJ   [XEXDO]    lesser
# 	divine; w/supernatural radiance; divinely inspired; blessed, saint (Latham);
# 	e                    SUFFIX
# 	di.e                 ADV    POS
# 	dius, dia, dium  ADJ   [XEXDO]    lesser
# 	divine; w/supernatural radiance; divinely inspired; blessed, saint (Latham);
# 	*

# 	Syncope   r => v.r
# 	Syncopated perfect often drops the 'v' and contracts vowel
# 	nov.eris             V      3 1 PERF ACTIVE  SUB 2 S
# 	nov.eris             V      3 1 FUTP ACTIVE  IND 2 S
# 	nosco, noscere, novi, notus  V (3rd) TRANS   [XXXAO]
# 	get to know; learn, find out; become cognizant of/acquainted/familiar with;
# 	examine, study, inspect; try (case); recognize, accept as valid/true; recall;
# 	nov.eris             V      1 1 PRES PASSIVE SUB 2 S
# 	novo, novare, novavi, novatus  V (1st)   [XXXDX]    lesser
# 	make new, renovate; renew, refresh, change;
# 	nov.eris             V      3 1 PERF ACTIVE  SUB 2 S
# 	nov.eris             V      3 1 FUTP ACTIVE  IND 2 S
# 	novi, novisse, notus  V (3rd) PERFDEF   [XXXDX]    lesser
# 	know, know of; know how, be able (to); experience;  (PERF form, PRES force);
# 	know; be familiar/acquainted/conversant with/aware of; accept, recognize;


# def make_qu_lookup_table(word: str, prefix, suffix, tackon):
#     # qui, quis, quid, quae, quod
#     # cuius, cui, quem, quam, quo, qua
#     # quibus, quorum, quarum, quos, quas
#     pass
#
#     L1 = "who; that; which, what; of which kind/degree; person/thing/time/point that;"
#     L2 = "who/what/which?, what/which one/man/person/thing? what kind/type of?;"
#     L3 = "who/whatever, everyone who, all that, anything that;"
#     L4 = "any; anyone/anything, any such; unspecified some; (after si/sin/sive/ne);"
#     L5 = "who?, which?, what?; what kind of?;"
#     L6 = "anyone/anybody/anything; whoever you pick; something (or other); any (NOM S);"
#
#     LINES = {1: L1, 2: L2, 3: L3, 4: L4, 5: L5, 6: L6}
#     MP: Dict[str, List[Tuple[List[Tuple[Case, Number, Gender]], List[int]]]] = {
#         "qui": [([(Case.Nominative, Number.Plural, Gender.Male)], [1, 2, 3, 4, 5]),
#                 ([(Case.Nominative, Number.Singular, Gender.Male)], [1, 3, 4, 5])],
#         "quid": [(
#                  [(Case.Nominative, Number.Singular, Gender.Nueter), (Case.Accusitive, Number.Singular, Gender.Nueter)],
#                  [2, 6])],
#         "quis": [([(Case.Dative, Number.Plural, Gender.X), (Case.Ablative, Number.Plural, Gender.X)], [1, 2, 3, 4, 5]),
#                  ([(Case.Nominative, Number.Singular, Gender.Common)], [2, 6])],
#         "quibus": [
#             ([(Case.Dative, Number.Plural, Gender.X), (Case.Ablative, Number.Plural, Gender.X)], [1, 2, 3, 4, 5])],
#         "quae": [([(Case.Nominative, Number.Plural, Gender.Female)], [1, 2, 3, 4, 5]),
#                  ([(Case.Nominative, Number.Singular, Gender.Female)], [1, 6, 3, 4, 5]),
#                  ([(Case.Nominative, Number.Plural, Gender.Nueter), (Case.Accusitive, Number.Plural, Gender.Nueter)],
#                   [6, 4])],
#         "quod": [(
#                  [(Case.Nominative, Number.Singular, Gender.Nueter), (Case.Accusitive, Number.Singular, Gender.Nueter)],
#                  [1, 3, 4, 5])],
#         "quem": [([(Case.Accusitive, Number.Singular, Gender.Male)], [1, 2, 3, 4, 5])],
#         "quos": [([(Case.Accusitive, Number.Plural, Gender.Male)], [1, 2, 3, 4, 5])],
#         "quas": [([(Case.Accusitive, Number.Plural, Gender.Female)], [1, 2, 3, 4, 5])],
#         "quam": [([(Case.Accusitive, Number.Singular, Gender.Female)], [1, 2, 3, 4, 5])],
#         "quo": [([(Case.Ablative, Number.Singular, Gender.Male), (Case.Ablative, Number.Singular, Gender.Nueter)],
#                  [1, 2, 3, 4, 5])],
#         "qua": [([(Case.Nominative, Number.Singular, Gender.Female), (Case.Ablative, Number.Singular, Gender.Female)],
#                  [6, 4]),
#                 ([(Case.Ablative, Number.Singular, Gender.Female)], [1, 6, 3, 4, 5]),
#                 ([(Case.Nominative, Number.Plural, Gender.Nueter), (Case.Accusitive, Number.Plural, Gender.Nueter)],
#                  [1, 2, 3, 4, 5])],
#         "quorum": [([(Case.Genative, Number.Plural, Gender.Male), (Case.Genative, Number.Plural, Gender.Nueter)],
#                     [1, 2, 3, 4, 5])],
#         "quarum": [([(Case.Genative, Number.Plural, Gender.Female)], [1, 2, 3, 4, 5])],
#         "cujus": [([(Case.Genative, Number.Singular, Gender.X)], [1, 2, 3, 4, 5])],
#         "cui": [([(Case.Dative, Number.Singular, Gender.X)], [1, 2, 3, 4, 5])],
#     }
#
#     pairs: List[Tuple[List[Tuple[Case, Number, Gender]], List[int]]] = MP[word.lower()]
#     form_groups = []
#     for pair in pairs:
#         keys, lines = pair
#         lines = [LINES[i] for i in lines]
#         dic = DictionaryKey(("qu", "cu", None, None),
#                               PartOfSpeech.Pronoun,
#                               PronounDictData(DeclentionType(1), DeclentionSubtype(0), PronounKind.X),
#                               TranslationMetadata("X X X A O"),
#                               Definiton(lines),
#                               -1)
#         infls = [InflectionRule(PartOfSpeech.Pronoun,
#                                  PronounInflData(DeclentionType(1), DeclentionSubtype(0), key[0], key[1], key[2]),
#                                  1 if word.lower()[0] == "q" else 2,
#                                  word[2:],
#                                  InflectionAge.Always,
#                                  InflectionFrequency.A)
#                  for key in keys]
#         form_group = FormGroup(dic, infls, prefix, suffix, tackon)
#         form_groups.append(form_group)
#     return form_groups