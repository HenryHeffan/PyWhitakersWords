# - *- coding: utf- 8 - *-

from core_files.utils import *
import io
open = io.open
from core_files.entry_and_inflections import *
from core_files.searcher import EntryQuery
from core_files import searcher




TWO_WORD_TEMP = u"""
<div class="two_word_group">
    <div class="two_word_header">
        {header_slot}
    </div>
    {word_1_slot}
    {word_2_slot}
</div>
"""

TACKON_TEMP = u"""
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



PREFIX_TEMP = u"""
<div class="prefix_group row">
    <div class="col-sm-3 cannon_form_row">
        Prefix: {prefix_str}
    </div>
    <div class="col-sm-9 definition_group">
        {prefix_meaning}
    </div>
</div>
"""

SUFFIX_TEMP = u"""
<div class="suffix_group row">
    <div class="col-sm-3 cannon_form_row">
        Suffix: {suffix_str}
    </div>
    <div class="col-sm-9 definition_group">
        {suffix_meaning}
    </div>
</div>
"""

METADATA_TEMP = u"""
<div class="row metadata_row">
    <div class="col-sm-6 metadata_row_slot1">
        {metadata_slot_1}
    </div>
    <div class="col-sm-6 metadata_row_slot2">
        {metadata_slot_2}
    </div>
</div>
"""

DEFINITION_ROW_TEMP = u"""
<div class="row definition_row">
    <div class="col-sm-12">
        {definition_row_slot}
    </div>
</div>
"""

FORM_ROW_TEMP = u"""
<div class="row form_row">
    <div class="col-sm-4">
        {form_row_word_slot}
    </div>
    <div class="col-sm-8">
        {form_row_form_slot}
    </div>
</div>
"""

CANNON_MAIN_ROW_TEMP = u"""
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
CANNON_ALT_ROW_TEMP = u"""
<div class="row cannon_form_alt_row">
    <div class="col-sm-12">
        {cannon_form_slot}
    </div>
</div>
"""

HTML_SPACE_TEMP = u"""<div class="collapse" id="collapseSpot{id_slot}"><div class="panel panel-default"><div class="panel-body">
    {html_slot}
</div></div></div>"""

WORD_GROUP_TEMP = u"""
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

Gender.alt_str_val = classmethod(lambda cls, gen: {
            Gender.Male: "masc",
            Gender.Female: "fem",
            Gender.Nueter: "neut",
            Gender.Common: "common",
            Gender.X: "X"
        }[Gender(gen)])

Number.alt_str_val = classmethod(lambda cls, num: {
        Number.Singular: "sg",
        Number.Plural: "pl",
        Number.X: "X"
    }[Number(num)])

Voice.alt_str_val = classmethod(lambda cls, voice: {
        Voice.Active: "act",
        Voice.Passive: "pass",
        Voice.X: "X"
    }[Voice(voice)])

Mood.alt_str_val = classmethod(lambda cls, mood: {
        Mood.X: "X",
        Mood.Subjunctive: "subj",
        Mood.Infinative: "inf",
        Mood.Imperative: "imp",
        Mood.Indicitive: "ind"
    }[Mood(mood)])

Person.alt_str_val = classmethod(lambda cls, person: {
        Person.X: "X",
        Person.First: "1st",
        Person.Second: "2nd",
        Person.Third: "3rd",
    }[Person(person)])


class FormaterBase:
    def __init__(self, lex: Lexicon):
        self.inflection_table = {}
        self.lex = lex

    @abstractmethod
    def setup(self) -> None:
        pass

    def sort_infls_key(self, infl: InflectionRule):
        return 0

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
        }[dic.translation_metadata.frequency]

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

    def make_infl_row_str(self, dic: DictionaryKey, infl: InflectionRule, is_syncopy: bool) -> str:
        return self.infl_entry_line(dic, infl, "") + ("" if not is_syncopy else " (syncopated)")

    @abstractmethod
    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        pass

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
        for decl, decl_var in ALL_DECL_VAR_PAIRS:
            for gender in Gender:
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
            case=Case.str_val(infl.noun_data.case).lower(),
            number=Number.alt_str_val(infl.noun_data.number),
            gender=Gender.alt_str_val(combine_gender(infl.noun_data.gender, dic.noun_data.gender))
        )

    def get_extra_info_spot(self, dic: DictionaryKey) -> str:
        decl = {1: "(1st decl.) ", 2: "(2nd decl.) ", 3: "(3rd decl.) ", 4: "(4th decl.) ", 5: "(5th decl.) ", 9: ""}[
            dic.noun_data.declention]
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
        for (decl, decl_var) in ALL_DECL_VAR_PAIRS:
            self.inflection_table[(decl, decl_var)] = \
                [(self.lex.get_pronoun_inflection_rule(decl, decl_var, gender, Case.Nominative, Number.Singular),
                  self.lex.get_pronoun_inflection_rule(decl, decl_var, gender, Case.Genative, Number.Singular))
                 for gender in Gender.MFN()]

    def make_cannon_form_str(self, dic: DictionaryKey) -> str:
        infls = self.inflection_table[self.get_key(dic)]
        if (dic.pronoun_data.declention, dic.pronoun_data.declention_variant) in {(1,0), (3, 1), (3, 2), (4, 1), (4, 2), (6, 1), (6, 2)}:
            return "{}, {}, {}".format(
                dic.make_form(infls[0][0], default="-"),
                dic.make_form(infls[1][0], default="-"),
                dic.make_form(infls[2][0], default="-"))
        else:

            # --  Ex: ego mei    =>       ego   m
            # --  Ex: tu tui    =>        tu   t
            # --  Ex: tui       =>        zzz  t      reflexive
            # --  Ex: nos nostrum       =>  n nostr
            # --  Ex: sui       =>        zzz  s      reflexive

            return "{}, {}".format(
                dic.make_form(infls[0][0], default="-"),
                dic.make_form(infls[0][1], default="-"))


    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        return "pronoun {case} {number} {gender}".format(
            case=Case.str_val(infl.pronoun_data.case).lower(),
            number=Number.alt_str_val(infl.pronoun_data.number),
            gender=Gender.alt_str_val(infl.pronoun_data.gender)
        )

    def get_extra_info_spot(self, dic: DictionaryKey) -> str:
        return ""


class VerbFormater(FormaterBase):
    def filter_verb_kind(self, vk: VerbKind) -> VerbKind:
        return vk if vk in {VerbKind.Impers, VerbKind.Dep, VerbKind.Semidep, VerbKind.Perfdef} else VerbKind.X

    def get_key(self, dic: DictionaryKey):
        return dic.verb_data.conjugation, dic.verb_data.conjugation_variant, self.filter_verb_kind(
            dic.verb_data.verb_kind)

    def setup(self) -> None:
        for (conj, conj_var) in ALL_CONJ_VAR_PAIRS:
            for vk in VerbKind:
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
                    continue

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
        if infl.part_of_speech == PartOfSpeech.Verb:
            return self.infl_entry_line_verb(dic, infl, word)
        elif infl.part_of_speech == PartOfSpeech.Supine:
            return self.infl_entry_line_suppine(dic, infl, word)
        elif infl.part_of_speech == PartOfSpeech.Participle:
            return self.infl_entry_line_participle(dic, infl, word)
        else:
            raise ValueError()

    def infl_entry_line_verb(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        return "verb {tense} {voice} {mood} {person} {number}".format(
            tense=Tense.str_val(infl.verb_data.tense).lower(),
            voice=Voice.alt_str_val(infl.verb_data.voice) if dic.verb_data.verb_kind != VerbKind.Dep else "deponent",
            mood=pad_to_len(Mood.str_val(infl.verb_data.mood).lower(), 3),
            person=Person.alt_str_val(infl.verb_data.person),
            number=Number.alt_str_val(infl.verb_data.number),
        )

    def infl_entry_line_suppine(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        return "supine {case} {number} {gender}".format(
            case=Case.str_val(infl.supine_entry.case).lower(),
            number=Number.alt_str_val(infl.supine_entry.number),
            gender=Gender.alt_str_val(infl.supine_entry.gender),
        )

    def infl_entry_line_participle(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        return "participle {case} {number} {gender} {tense} {voice}".format(
            case=Case.str_val(infl.participle_entry.case).lower(),
            number=Number.alt_str_val(infl.participle_entry.number),
            gender=Gender.alt_str_val(infl.participle_entry.gender),
            tense=Tense.str_val(infl.participle_entry.tense).lower(),
            voice=Voice.alt_str_val(infl.participle_entry.voice) if dic.verb_data.verb_kind != VerbKind.Dep else "deponent",
        )

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
        SORT_ORDER_TENSE = [Tense.Present, Tense.Imperfect, Tense.Future, Tense.Perfect, Tense.Pluperfect,
                            Tense.FuturePerfect, Tense.X]
        SORT_ORDER_VOICE = [Voice.Active, Voice.Passive, Voice.X]
        SORT_ORDER_MOOD = [Mood.Indicitive, Mood.Subjunctive, Mood.Imperative, Mood.Infinative, Mood.X]
        if infl.part_of_speech != PartOfSpeech.Verb:
            return 0
        else:
            return SORT_ORDER_TENSE.index(infl.verb_data.tense) * 100 + SORT_ORDER_VOICE.index(
                infl.verb_data.voice) * 10 + SORT_ORDER_MOOD.index(infl.verb_data.mood)

    SORT_ORDER_VPAR = [Case.Nominative, Case.Vocative, Case.Genative, Case.Locitive, Case.Dative, Case.Accusitive,
                       Case.Ablative, Case.X]

    def sort_infls_key_part(self, infl: InflectionRule):
        if infl.part_of_speech != PartOfSpeech.Participle:
            return 0
        else:
            return self.SORT_ORDER_VPAR.index(infl.participle_entry.case) + 10 * infl.participle_entry.number

# TODO: this one needs work
class AdjectiveFormater(FormaterBase):
    def get_key(self, dic: DictionaryKey):
        return dic.adjective_data.declention, dic.adjective_data.declention_variant

    def setup(self) -> None:
        for (decl, decl_var) in ALL_DECL_VAR_PAIRS:
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
                                                                    Case.Genative, Number.Singular, AdjectiveKind.Positive)

    def make_cannon_form_str(self, dic: DictionaryKey) -> str:
        infls = self.inflection_table[self.get_key(dic)]
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
        return "adj {case} {number} {gender} {adj_kind}".format(
            case=Case.str_val(infl.adjective_data.case).lower(),
            number=Number.alt_str_val(infl.adjective_data.number),
            gender=Gender.alt_str_val(infl.adjective_data.gender),
            adj_kind=AdjectiveKind.str_val(infl.adjective_data.adjective_kind).lower()
        )

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
            adj_kind=AdjectiveKind.str_val(infl.adverb_data.adjective_kind_output).lower()
        )

    def get_extra_info_spot(self, dic: DictionaryKey) -> str:
        return ""


class PrepositionFormater(FormaterBase):
    def setup(self) -> None:
        self.inflection_rule = self.lex.get_preposition_inflection_rule()

    def make_cannon_form_str(self, dic: DictionaryKey) -> str:
        return dic.make_form(self.inflection_rule)

    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        return "prep w/ {case}".format(
            case=Case.str_val(dic.preposition_data.takes_case).lower()
        )

    def get_extra_info_spot(self, dic: DictionaryKey) -> str:
        return "+ {}".format(Case.str_val(dic.preposition_data.takes_case).lower())


class ConjunctionFormater(FormaterBase):
    def setup(self) -> None:
        self.inflection_rule = self.lex.get_conjunction_inflection_rule()

    def make_cannon_form_str(self, dic: DictionaryKey) -> str:
        return dic.make_form(self.inflection_rule)

    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        # at                   CONJ
        return "conj"

    def get_extra_info_spot(self, dic: DictionaryKey) -> str:
        return ""


class InterjectionFormater(FormaterBase):
    def setup(self) -> None:
        self.inflection_rule = self.lex.get_interjection_inflection_rule()
    def make_cannon_form_str(self, dic: DictionaryKey) -> str:
        return dic.make_form(self.inflection_rule)

    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        return "interj"

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
        for (decl, decl_var) in ALL_DECL_VAR_PAIRS:
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
        return "num {case} {number} {gender} {num_kind}".format(
            case=Case.str_val(infl.number_data.case).lower(),
            number=Number.alt_str_val(infl.number_data.number),
            gender=Gender.alt_str_val(infl.number_data.gender),
            num_kind=NumberKind.str_val(infl.number_data.number_kind).lower()
        )

    def get_extra_info_spot(self, dic: DictionaryKey) -> str:
        return ""


class PackonFormater(FormaterBase):
    def get_key(self, dic: DictionaryKey):
        return dic.packon_data.declention, dic.packon_data.declention_variant

    SORT_ORDER = [Case.Nominative, Case.Vocative, Case.Genative, Case.Dative, Case.Ablative, Case.Accusitive,
                  Case.Locitive, Case.X]


    def sort_infls_key(self, infl):
        return self.SORT_ORDER.index(infl.packon_data.case) + 10 * infl.packon_data.number

    def setup(self) -> None:
        # for Packon: nom, gen
        for (decl, decl_var) in ALL_DECL_VAR_PAIRS:
            self.inflection_table[(decl, decl_var)] = \
                [(self.lex.get_pronoun_inflection_rule(decl, decl_var, gender, Case.Nominative, Number.Singular),
                  self.lex.get_pronoun_inflection_rule(decl, decl_var, gender, Case.Genative, Number.Singular))
                 for gender in Gender.MFN()]

    def make_packon_form(self, dic: DictionaryKey, infl: InflectionRule):
        form = dic.make_form(infl, default="-")
        if form == "-":
            return form
        form += dic.packon_data.tackon_str
        return form

    def make_cannon_form_str(self, dic: DictionaryKey) -> str:
        infls = self.inflection_table[self.get_key(dic)]

        if (dic.pronoun_data.declention, dic.pronoun_data.declention_variant) in {(1, 0), (3, 1), (3, 2), (4, 1),
                                                                                  (4, 2), (6, 1), (6, 2)}:
            return "{}, {}, {}".format(
                self.make_packon_form(dic, infls[0][0]),
                self.make_packon_form(dic, infls[1][0]),
                self.make_packon_form(dic, infls[2][0]))
        elif dic.pronoun_data.declention == 5:  # ego, mei
            return "{}, {}".format(
                self.make_packon_form(dic, infls[0][0]),
                self.make_packon_form(dic, infls[0][1]))
        else:
            return ""

    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        return "pron {case} {number} {gender}".format(
            case=Case.str_val(infl.packon_data.case).lower(),
            number=Number.alt_str_val(infl.packon_data.number),
            gender=Gender.alt_str_val(infl.packon_data.gender)
        )

    def get_extra_info_spot(self, dic: DictionaryKey) -> str:
        return ""


class JoinedFormater(searcher.Formater):
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
        searcher.Formater.__init__(self, lex)
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
        return self.map[dic.part_of_speech].dictionary_key_form(dic)

    def display_entry_query(self, query: EntryQuery) -> str:
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

        # then output each of the format_groups
        for format_group in format_groups:
            group_id = format_group.lemma.index
            # TODO TEST alternate forms
            if format_group.suffix is None:
                infl_formater = self.map[format_group.lemma.part_of_speech]
                dic_formater = self.map[format_group.lemma.part_of_speech]
                # inflectable_dic = format_group.lemma
            else:
                infl_formater = self.map[format_group.suffix.new_pos]
                dic_formater = self.map[format_group.suffix.stem_pos]
                # inflectable_dic = format_group.suffix.make_fake_dic_key(format_group.lemma.dictionary_keys[0])

            cannon_form_rows = [CANNON_MAIN_ROW_TEMP.format(
                cannon_form_slot=dic_formater.make_cannon_form_str(format_group.lemma.dictionary_keys[0]),
                cannon_form_suffix=(" +" + format_group.tackon.tackon) if format_group.tackon is not None else "",
                button_space=("""<button class="btn btn-secondary" type="button"\ndata-toggle="collapse" data-target="#collapseSpot{id}"\naria-expanded="false" aria-controls="collapseSpot">L&S</button>"""
                              .format(id=group_id)) if format_group.lemma.html_data else ""
            )]
            for key in format_group.lemma.dictionary_keys[1:]:
                cannon_form_rows.append(CANNON_ALT_ROW_TEMP.format(cannon_form_slot=dic_formater.make_cannon_form_str(key)))
            definition_rows = format_group.lemma.definition

            form_rows = [FORM_ROW_TEMP.format(
                form_row_word_slot=form.make_split_word_form(word),
                form_row_form_slot=infl_formater.make_infl_row_str(
                    format_group.suffix.make_fake_dic_key(key) if format_group.suffix is not None else key,
                    form,
                    is_sync)
            ) for key, form, word, is_sync in format_group.key_infl_pairs]

            # print(format_group.lemma.dictionary_keys[0].stems, format_group.lemma.html_data)

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
                    metadata_slot_1=PartOfSpeech.get_name(format_group.lemma.part_of_speech) + " &nbsp; &nbsp; &nbsp; " +
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


def init(path: str, fast: bool = True, load_html_def_dict: bool = False, decode_func=None) -> Tuple[NewStyle_Json_Lexicon, JoinedFormater]:
    # One of three should be the case
    # BOTH load_html_def_dict == False and decode_func == None, then do nothing
    # BOTH load_html_def_dict == True and decode_func == None, then load REF_DEF_TABLE.txt and return decoded from this
    # BOTH load_html_def_dict == False and decode_func == some function f, then use f to get the html value lazily as needed
    if load_html_def_dict:
        assert decode_func is None
        import json
        table = {"": ""}
        with open(os.path.join(path, "GeneratedFiles/REF_DEF_TABLE.txt")) as ifile:
            for line in ifile:
                line = line[:-1].split(" ")
                table[line[0]] = line[1]
        decode_func = lambda html_data: "\n".join([load_utf_str(table[k]) for k in html_data.split(" ")])
    elif decode_func is None:
        decode_func = lambda s: ""

    J_LEX = (BakedLexicon("BAKED_JOINED", decode_func)
             if fast else
             NewStyle_Json_Lexicon("GeneratedFiles/JOINED_ONLY_REF_DEF.txt", decode_func))  #"GeneratedFiles/JOINED.txt" if not self.ref_def else
    J_LEX.load(path)
    formater = JoinedFormater(J_LEX,
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

    return J_LEX, formater
