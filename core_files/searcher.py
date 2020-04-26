from core_files.entry_and_inflections import *
from core_files.utils import *
import io
open = io.open
import re


########################################################################################################################
########################################################################################################################
#                                     classes to store the results from queries                                        #
########################################################################################################################
########################################################################################################################


class POSFormater:
    def __init__(self, lex: Lexicon):
        self.inflection_table = {}
        self.lex = lex

    @abstractmethod
    def setup(self) -> None:
        pass

    def sort_infls_key(self, infl: Tuple[DictionaryKey, InflectionRule]):
        key, rule = infl
        return 0

    @abstractmethod
    def make_cannon_form_str(self, dic: DictionaryKey) -> str:
        pass

    def dictionary_key_form(self, dic: DictionaryKey) -> str:
        # print(self.__class__)
        # print(self.make_cannon_form_str(dic))
        return self.make_cannon_form_str(dic).split(',')[0]


class NounFormater(POSFormater):
    def get_key(self, dic: DictionaryKey):
        return dic.noun_data.declention, dic.noun_data.declention_variant, dic.noun_data.gender

    SORT_ORDER = [Case.Nominative, Case.Vocative, Case.Genative, Case.Locitive, Case.Dative, Case.Accusitive,
                  Case.Ablative, Case.X]

    def sort_infls_key(self, infl: Tuple[DictionaryKey, InflectionRule]):
        key, rule = infl
        return self.SORT_ORDER.index(rule.noun_data.case) + 10 * rule.noun_data.number

    def setup(self) -> None:
        # called once on each class. Use to setup noun formating rules
        # for decl, decl_var, gender) in set([self.get_key(dic)
        #                                      for i in range(1, 5)
        #                                      for (stem, l) in self.lex.stem_map[(PartOfSpeech.Noun, i)].items()
        #                                      for dic in l]):
        for decl in range(10):
            for decl_var in range(10):
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


class VerbFormater(POSFormater):
    def filter_verb_kind(self, vk: VerbKind) -> VerbKind:
        return vk if vk in {VerbKind.Impers, VerbKind.Dep, VerbKind.Semidep, VerbKind.Perfdef} else VerbKind.X

    def get_key(self, dic: DictionaryKey):
        return dic.verb_data.conjugation, dic.verb_data.conjugation_variant, self.filter_verb_kind(
            dic.verb_data.verb_kind)

    def setup(self) -> None:
        pass
        # for Verb:
        for conj, conj_var in ALL_CONJ_VAR_PAIRS:
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


    def sort_infls_key_verb(self, infl: Tuple[DictionaryKey, InflectionRule]):
        key, rule = infl
        SORT_ORDER_TENSE = [Tense.Present, Tense.Imperfect, Tense.Future, Tense.Perfect, Tense.Pluperfect,
                            Tense.FuturePerfect, Tense.X]
        SORT_ORDER_VOICE = [Voice.Active, Voice.Passive, Voice.X]
        SORT_ORDER_MOOD = [Mood.Indicitive, Mood.Subjunctive, Mood.Imperative, Mood.Infinative, Mood.X]
        if rule.part_of_speech != PartOfSpeech.Verb:
            return 0
        else:
            return SORT_ORDER_TENSE.index(rule.verb_data.tense) * 100 + SORT_ORDER_VOICE.index(
                rule.verb_data.voice) * 10 + SORT_ORDER_MOOD.index(rule.verb_data.mood)

    SORT_ORDER_VPAR = [Case.Nominative, Case.Vocative, Case.Genative, Case.Locitive, Case.Dative, Case.Accusitive,
                       Case.Ablative, Case.X]

    def sort_infls_key_part(self, infl: Tuple[DictionaryKey, InflectionRule]):
        key, rule = infl
        if rule.part_of_speech != PartOfSpeech.Participle:
            return 0
        else:
            return self.SORT_ORDER_VPAR.index(rule.participle_data.case) + 10 * rule.participle_data.number


# TODO: this one needs work
class AdjectiveFormater(POSFormater):
    def get_key(self, dic: DictionaryKey):
        return dic.adjective_data.declention, dic.adjective_data.declention_variant

    def setup(self) -> None:
        for decl in range(10):
            for decl_var in range(10):
                # (decl, decl_var) in set([self.get_key(dic)
                #                      for i in range(1, 5)
                #                      for (stem, l) in self.lex.stem_map[(PartOfSpeech.Adjective, i)].items()
                #                      for dic in l]):
                pos = [self.lex.get_adjective_inflection_rule(decl, decl_var, g, Case.Nominative, Number.Singular,
                                                     AdjectiveKind.Positive)
                       for g in Gender.MFN()]
                comp = [self.lex.get_adjective_inflection_rule(decl, decl_var, g, Case.Nominative, Number.Singular,
                                                      AdjectiveKind.Compairative)
                        for g in Gender.MFN()]
                sup = [self.lex.get_adjective_inflection_rule(decl, decl_var, g, Case.Nominative, Number.Singular,
                                                     AdjectiveKind.Superlative)
                       for g in Gender.MFN()]
                x = [self.lex.get_adjective_inflection_rule(decl, decl_var, g, Case.Nominative, Number.Singular,
                                                     AdjectiveKind.X)
                       for g in Gender.MFN()]

                self.inflection_table[(decl, decl_var)] = [pos, comp, sup, x]
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
            elif self.get_key(dic) == (2, 6):
                return "{}, {}".format(dic.make_form(infls[3][0], default="*"),
                                       dic.make_form(infls[3][1], default="*"))
            elif self.get_key(dic) in {(2, 7), (2, 8)}:
                return "{}".format(dic.make_form(infls[3][2], default="*"))
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

    def sort_infls_key(self, infl: Tuple[DictionaryKey, InflectionRule]):
        key, rule = infl
        return self.SORT_ORDER.index(rule.adjective_data.case) + 10 * rule.adjective_data.number


# TODO: this one needs some work
class AdverbFormater(POSFormater):
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


class PrepositionFormater(POSFormater):
    def setup(self) -> None:
        self.inflection_rule = self.lex.get_preposition_inflection_rule()

    def make_cannon_form_str(self, dic: DictionaryKey) -> str:
        return dic.make_form(self.inflection_rule)


class ConjunctionFormater(POSFormater):
    def setup(self) -> None:
        self.inflection_rule = self.lex.get_conjunction_inflection_rule()

    def make_cannon_form_str(self, dic: DictionaryKey) -> str:
        return dic.make_form(self.inflection_rule)


class InterjectionFormater(POSFormater):
    def setup(self) -> None:
        self.inflection_rule = self.lex.get_interjection_inflection_rule()

    def make_cannon_form_str(self, dic: DictionaryKey) -> str:
        return dic.make_form(self.inflection_rule)


class NumberFormater(POSFormater):
    def get_key(self, dic: DictionaryKey):
        return dic.number_data.declention, dic.number_data.declention_variant

    SORT_ORDER = [Case.Nominative, Case.Vocative, Case.Genative, Case.Locitive, Case.Dative, Case.Accusitive,
                  Case.Ablative, Case.X]

    def sort_infls_key(self, infl: Tuple[DictionaryKey, InflectionRule]):
        key, rule = infl
        return self.SORT_ORDER.index(rule.number_data.case) + 10 * rule.number_data.number

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


class ProPackFormater(POSFormater):
    def get_key(self, dic: DictionaryKey):
        return dic.pro_pack_data.declention, dic.pro_pack_data.declention_variant

    @abstractmethod
    def make_form(self, dic: DictionaryKey, infl: InflectionRule):
        pass

    SORT_ORDER = [Case.Nominative, Case.Vocative, Case.Genative, Case.Dative, Case.Ablative, Case.Accusitive,
                  Case.Locitive, Case.X]

    def sort_infls_key(self, infl: Tuple[DictionaryKey, InflectionRule]):
        key, rule = infl
        return self.SORT_ORDER.index(rule.packon_data.case) + 10 * rule.packon_data.number

    def setup(self) -> None:
        for (decl, decl_var) in ALL_DECL_VAR_PAIRS:
            self.inflection_table[(decl, decl_var)] = [
                (
                    self.lex.get_pronoun_inflection_rule(decl, decl_var, gender, Case.Nominative, Number.Singular),
                    self.lex.get_pronoun_inflection_rule(decl, decl_var, gender, Case.Genative, Number.Singular)
                )
                for gender in Gender.MFN()
            ]

    def make_cannon_form_str(self, dic: DictionaryKey) -> str:
        infls = self.inflection_table[self.get_key(dic)]
        if (dic.pronoun_data.declention, dic.pronoun_data.declention_variant) in {(3, 1), (3, 2), (4, 1),
                                                                                  (4, 2), (6, 1), (6, 2)}:
            return "{}, {}, {}".format(
                self.make_form(dic, infls[0][0]),
                self.make_form(dic, infls[1][0]),
                self.make_form(dic, infls[2][0]))
        elif dic.pronoun_data.declention == 1:  # qui/quis, quae/qua, quod/quid
            arr = [None, None, None]
            INDEX_MP = {1:0, 2:0, 3:1, 4:1, 6:2, 7:2}
            for k in dic.lemma.dictionary_keys:
                decl_var = k.pronoun_data.declention_variant
                if decl_var in INDEX_MP:
                    rule = self.inflection_table[self.get_key(k)][INDEX_MP[decl_var]][0]
                    if rule is not None:
                        arr[INDEX_MP[decl_var]] = rule
            return "{}, {}, {}".format(
                self.make_form(dic, arr[0]),
                self.make_form(dic, arr[1]),
                self.make_form(dic, arr[2]))
        elif dic.pronoun_data.declention == 5:  # ego, mei
            return "{}, {}".format(
                self.make_form(dic, infls[0][0]),
                self.make_form(dic, infls[0][1]))
        else:
            raise ValueError()


class PronounFormater(ProPackFormater):
    def make_form(self, dic: DictionaryKey, infl: InflectionRule):
        return dic.make_form(infl, default="-")


class PackonFormater(ProPackFormater):
    def make_form(self, dic: DictionaryKey, infl: InflectionRule):
        form = dic.make_form(infl, default="-")
        if form == "-":
            return form
        form += dic.packon_data.tackon_str
        return form

class Formater(ABC):
    def __init__(self,
                 lex: Lexicon):
        self.lex = lex

    @abstractmethod
    def display_entry_query(self, query: 'EntryQuery') -> str:
        pass

    def parse(self, s: str) -> str:
        return self.display_entry_query(get_matches(self.lex, s))


class FormGroup:
    def __init__(self,
                 lemma: DictionaryLemma,
                 key_infl_pairs: List[Tuple[DictionaryKey, InflectionRule]],
                 prefix: Optional[PrefixEntry],
                 suffix: Optional[SuffixEntry],
                 tackon: Optional[TackonEntry]):
        self.lemma = lemma
        self.key_infl_pairs = key_infl_pairs
        self.prefix = prefix
        self.suffix = suffix
        self.tackon = tackon

class FormGroupS:
    def __init__(self,
                 lemma: DictionaryLemma,
                 key_infl_pairs: List[Tuple[DictionaryKey, InflectionRule, str, bool]],  # word_form, is_syncopy
                 prefix: Optional[PrefixEntry],
                 suffix: Optional[SuffixEntry],
                 tackon: Optional[TackonEntry]):
        self.lemma = lemma
        self.key_infl_pairs = key_infl_pairs
        self.prefix = prefix
        self.suffix = suffix
        self.tackon = tackon


class EntryQuery:
    def __init__(self,
                 is_match: bool,
                 unsyncopated_form_groups: List[FormGroup],
                 unsyncopated_word: str,
                 syncopated_form_groups: List[FormGroup],
                 syncopated_why: Optional[str],
                 syncopated_word: Optional[str],
                 two_words: bool,
                 two_words_query1: Optional['EntryQuery'],
                 two_words_query2: Optional['EntryQuery']):
        self.is_match = is_match
        self.unsyncopated_form_groups = unsyncopated_form_groups
        self.unsyncopated_word = unsyncopated_word
        self.syncopated_form_groups = syncopated_form_groups
        self.syncopated_why = syncopated_why
        self.syncopated_word = syncopated_word
        self.two_words = two_words
        self.two_words_query1 = two_words_query1
        self.two_words_query2 = two_words_query2

    @staticmethod
    def make_normal(unsyncopated_form_groups: List[FormGroup],
                    unsyncopated_word: str,
                    syncopated_form_groups: List[FormGroup],
                    syncopated_why: Optional[str],
                    syncopated_word: Optional[str]) -> 'EntryQuery':
        return EntryQuery(True, unsyncopated_form_groups, unsyncopated_word, syncopated_form_groups, syncopated_why, syncopated_word, False, None, None)

    @staticmethod
    def make_two_words(two_words_query1: 'EntryQuery',
                       two_words_query2: 'EntryQuery') -> 'EntryQuery':
        return EntryQuery(True, [], "NONE", [], None, "NONE", True, two_words_query1, two_words_query2)

    @staticmethod
    def make_no_match(word: str) -> 'EntryQuery':
        return EntryQuery(False, [], word, [], None, "NONE", False, None, None)

    def sync_marked_form_groups(self) -> List[FormGroupS]:
        form_group_map: Dict[str, Tuple[DictionaryLemma, List[Optional[FormGroup]]]] = \
            {str(group.lemma): (group.lemma, [None, None])
             for group in self.unsyncopated_form_groups + self.syncopated_form_groups}

        for group in self.unsyncopated_form_groups:
            if form_group_map[str(group.lemma)][1][0] is None:
                form_group_map[str(group.lemma)][1][0] = group
            else:
                # TODO assert matches suffix, prefix tackon
                form_group_map[str(group.lemma)][1][0].key_infl_pairs.extend(group.key_infl_pairs)
        for group in self.syncopated_form_groups:
            if form_group_map[str(group.lemma)][1][1] is None:
                form_group_map[str(group.lemma)][1][1] = group
            else:
                # TODO assert matches suffix, prefix tackon
                form_group_map[str(group.lemma)][1][1].key_infl_pairs.extend(group.key_infl_pairs)

        format_groups = []
        for lemma, fgs in form_group_map.values():
            unsync, sync = fgs[0], fgs[1]
            assert unsync is None or sync is None or \
                   (unsync.suffix == sync.suffix and unsync.prefix == sync.prefix and unsync.tackon == sync.tackon)
            format_groups.append(FormGroupS(
                lemma,
                ([(key, rule, self.unsyncopated_word, False) for key, rule in unsync.key_infl_pairs] if unsync is not None else []) +
                ([(key, rule, self.syncopated_word, True) for key, rule in sync.key_infl_pairs] if sync is not None else []),
                unsync.prefix if unsync is not None else sync.prefix,
                unsync.suffix if unsync is not None else sync.suffix,
                unsync.tackon if unsync is not None else sync.tackon
            ))
        return format_groups

# TODO: I really hate this function. Is there a way to make it seem less hacky
def group_dic_infl_pairs(matched_dic_key_infl_rule_pairs: List[Tuple[DictionaryKey, InflectionRule]],
                         prefix: Optional[PrefixEntry],
                         suffix: Optional[SuffixEntry],
                         tackon: Optional[TackonEntry]) -> List[FormGroup]:
    KEYS = {}  # 'qu', 'aliqu', "cum", "cumque", "piam", "que", "dam", "lubet", "libet", "nam", "quam", "vis"}
    lemma_forms_map: Dict[str, Tuple[DictionaryLemma, List[Tuple[DictionaryKey, InflectionRule]]]] = {k: (None, []) for k in KEYS}  # gather the inflection for each dictionary entry
    for dic_key, infl_rule in matched_dic_key_infl_rule_pairs:
        # print("KEY",dic_key.lemma.dictionary_keys[0].stems[0],dic_key.lemma.dictionary_keys[0].stems[1])
        # if dic_key.lemma.dictionary_keys[0].stems[0] == 'qu' and dic_key.lemma.dictionary_keys[0].stems[1] in {None, 'cu'}\
        #         and dic_key.part_of_speech == PartOfSpeech.Pronoun:
        #     # print("QU")
        #     lemma_forms_map['qu'][1].append((dic_key, infl_rule))
        # elif dic_key.lemma.dictionary_keys[0].stems[0] == 'qu' and dic_key.lemma.dictionary_keys[0].stems[1] in {None, 'cu'}\
        #         and dic_key.part_of_speech == PartOfSpeech.Packon:
        #     lemma_forms_map[dic_key.packon_data.tackon_str][1].append((dic_key, infl_rule))
        # elif dic_key.lemma.dictionary_keys[0].stems[0] == 'aliqu' and dic_key.lemma.dictionary_keys[0].stems[1] in {None, 'alicu'}:
        #     lemma_forms_map['aliqu'][1].append((dic_key, infl_rule))
        # else:
        if not dic_key.lemma.index in lemma_forms_map:
            lemma_forms_map[dic_key.lemma.index] = (dic_key.lemma, [])
        lemma_forms_map[dic_key.lemma.index][1].append((dic_key, infl_rule))

    grouped_list = []
    for k, (lemma, forms) in lemma_forms_map.items():
        if len(forms) == 0:
            continue
        # if k in KEYS:
        #     # print("GATHERING", k)
        #     defs = sorted(list({key.lemma.definition for key, _ in forms if key.lemma.definition}))
        #     htmls = sorted(list({key.lemma.html_data for key, _ in forms if key.lemma.html_data}))
            # if k == 'aliqu':
            #     fake_key = DictionaryKey(('aliqu', 'alicu', None, None),
            #                          PartOfSpeech.Pronoun,
            #                          PronounDictData(DeclentionType(1), DeclentionSubtype(0), PronounKind.X))
            # elif k == 'qu':
            #     fake_key = DictionaryKey(('qu', 'cu', None, None),
            #                          PartOfSpeech.Pronoun,
            #                          PronounDictData(DeclentionType(1), DeclentionSubtype(0), PronounKind.X))
            # else:  # then k == 'PACK str':
            # d = PackonDictData(DeclentionType(1), DeclentionSubtype(0), PronounKind.X)
            # d.tackon_str = forms[0][0].packon_data.tackon_str
            # fake_key = DictionaryKey(('qu', 'cu', None, None),
            #                      PartOfSpeech.Packon,
            #                      d)
        #     cut_forms = []
        #     for _, form in forms:
        #         if not (fake_key, form) in cut_forms:
        #             cut_forms.append((fake_key, form))
        #     pos = PartOfSpeech.Pronoun if k in {'qu', 'aliqu'} else PartOfSpeech.Packon
        #     grouped_list.append(FormGroup(DictionaryLemma(
        #         pos,
        #         [fake_key],
        #         TranslationMetadata("X X X A O"),
        #         "\n".join(defs),
        #         "\n".join(htmls),
        #         0
        #     ), cut_forms, prefix, suffix, tackon))
        # else:
        grouped_list.append(FormGroup(lemma, sorted(forms, key=lambda x: x[1].index), prefix, suffix, tackon))

    grouped_list.sort(key=lambda group: group.lemma.index)
    return grouped_list


def get_inner_matches(lex: Lexicon,
                      word: str,
                      tackon: Optional[TackonEntry],
                      prefix: Optional[PrefixEntry],
                      suffix: Optional[SuffixEntry]) -> List[Tuple[DictionaryKey, InflectionRule]]:
    # if tackon is None or tackon.tackon != "cumque" or prefix is not None or suffix is not None:
    #     return []
    # print("{}:{}:{}".format(tackon.tackon if tackon else "", prefix.prefix if prefix else "", suffix.suffix if suffix else ""))
    # TODO
    #   if prefix is None and suffix is None and word in lex.uniques:
    #       return [(lex.uniques[word], None)]

    matched_dic_infl_pairs = []
    suffix_ending = suffix.suffix if suffix is not None else ""
    for inflection_index in range(len(word) + 1):
        if inflection_index - len(suffix_ending) < 0:
            continue
        potential_suffix = word[inflection_index - len(suffix_ending): inflection_index]
        if potential_suffix != suffix_ending:
            continue
        potential_inflection_ending = word[inflection_index:]
        if potential_inflection_ending not in lex.map_ending_infls:
            continue

        # print("HI:{}".format(potential_inflection_ending))

        for infl in lex.map_ending_infls[potential_inflection_ending]:
            assert word.endswith(infl.ending)

            if tackon is not None and not tackon.accepts_infl(infl):
                continue
            # print("- TACKON APPROVES", infl)
            if prefix is not None and not prefix.accepts_infl(infl):
                continue
            if suffix is not None and not suffix.accepts_infl(infl):
                continue

            # check that inflection rule matches the TACKON and SUFFIX, and PREFIX
            # search for stems of the proper PartOfSpeach based on suffix

            possible_stem = clip_end(word, len(infl.ending) + len(suffix_ending))
            if suffix is None:
                stem_pos = PartOfSpeech.Verb if infl.part_of_speech in \
                                                {PartOfSpeech.Supine,
                                                 PartOfSpeech.Participle} else infl.part_of_speech
                stem_key = infl.stem_key
            else:
                stem_pos = suffix.stem_pos
                stem_key = suffix.stem_key


            # THIS CODE IS CLUNKY, BUT MAKES CODING THE C++ EASIER
            # print(stem_pos, stem_key)
            stem_map = lex.get_stem_map(stem_pos, stem_key)
            if possible_stem in stem_map:
                possible_entrys = stem_map[possible_stem]
                for i in range(len(possible_entrys)):
                    entry = possible_entrys[i]
                    # print(entry, entry.part_of_speech)
                    # DONE WITH CLUNKY PART

                    if tackon is not None and not tackon.accepts_stem(entry):
                        continue
                    if entry.part_of_speech == PartOfSpeech.Packon and not entry.packon_data.accepts_tackon(tackon):
                        continue  # we cant have a PACKON without a TACKON
                    if suffix is None:
                        # print(entry.__class__)
                        # print(list(entry.__class__.__dict__))
                        # print(entry.pos_data)
                        if infl.pos_data.matches(entry.pos_data):
                            matched_dic_infl_pairs.append((entry, infl))
                    elif suffix.accepts_stem_dic_key(entry):
                        if infl.pos_data.matches(suffix.fake_dictionary_entry):
                            matched_dic_infl_pairs.append((entry, infl))

    return matched_dic_infl_pairs


def get_syncopy_matches(lex: Lexicon,
                        word: str,
                        tackon: Optional[TackonEntry],
                        prefix: Optional[PrefixEntry],
                        suffix: Optional[SuffixEntry]) -> Tuple[List[Tuple[DictionaryKey, InflectionRule]],
                                                      Optional[str],
                                                      Optional[str]]:
    #  This one has to go first #  special for 3 4
    #  ivi  => ii ,  in perfect  (esp. for V 3 4)
    #  This is handled in WORDS as syncope
    #  It seems to appear in texts as alternative stems  ii and ivi
    for i in [i for i in range(len(word)-1) if word.lower()[i: i+2] == "ii"]:
        word_prime = word[:i] + "ivi" + word[i+2:]
        matches = [(dic, infl) for dic, infl in get_inner_matches(lex, word_prime.lower(), tackon, prefix, suffix)
                   if infl.part_of_speech == PartOfSpeech.Verb and
                   (dic.verb_data.conjugation, dic.verb_data.conjugation_variant) in {(3,4), (6,1)} and
                   infl.stem_key == 3]
        if len(matches) > 0:
            return matches, "Syncope  ii => ivi\nSyncopated perfect ivi can drop 'v' without contracting vowel", word_prime

    # avis => as, evis => es, ivis => is, ovis => os   in perfect
    for i in [i for i in range(len(word)-1) if word.lower()[i: i+2] in {"as", "es", "is", "os"}]:
        word_prime = word[:i+1] + "vi" + word[i+1:]
        # print("WORDPRIME2", word, word_prime)
        matches = [(dic, infl) for dic, infl in get_inner_matches(lex, word_prime.lower(), tackon, prefix, suffix) if
                   infl.part_of_speech == PartOfSpeech.Verb and infl.stem_key == 3]
        if len(matches) > 0:
            return matches, "Syncope  *vis => *s\nSyncopated perfect often drops the 'v' and contracts vowel", word_prime

    # aver => ar, ever => er, in perfect
    for i in [i for i in range(len(word)-1) if word.lower()[i: i+2] in {"ar", "er", "or"}]:
        word_prime = word[:i+1] + "ve" + word[i+1:]
        # print("WORDPRIME3", word, word_prime)
        inner = get_inner_matches(lex, word_prime.lower(), tackon, prefix, suffix)
        # print(len(inner), inner)
        matches = [(dic, infl) for dic, infl in inner if
                   infl.part_of_speech == PartOfSpeech.Verb] # and infl.stem_key == 3], because we want to accept

        if all(infl.stem_key != 3 for dic, infl in matches):
            matches = []

        if len(matches) > 0:
            return matches, "Syncope   r => v.r   \nSyncopated perfect often drops the 'v' and contracts vowel", word_prime

    # iver => ier,  in perfect
    for i in [i for i in range(len(word)-2) if word.lower()[i: i+3] == "ier"]:
        word_prime = word[:i] + "iver" + word[i+3:]

        matches = [(dic, infl) for dic, infl in get_inner_matches(lex, word_prime.lower(), tackon, prefix, suffix) if
                   infl.part_of_speech == PartOfSpeech.Verb and infl.stem_key == 3]
        if len(matches) > 0:
            return matches, "Syncope  iver => ier\nSyncopated perfect often drops the 'v' and contracts vowel", word_prime

    # sis => s, xis => x, in perfect
    for i in [i for i in range(len(word)-2) if word.lower()[i] in {"s", "x"}]:
        word_prime = word[:i+1] + "is" + word[i+1:]
        matches = [(dic, infl) for dic, infl in get_inner_matches(lex, word_prime.lower(), tackon, prefix, suffix) if
                   infl.part_of_speech == PartOfSpeech.Verb and infl.stem_key == 3]
        if len(matches) > 0:
            return matches, "Syncope  [s|x]is => [s|x]\nSyncopated perfect sometimes drops the 'is' after 's' or 'x'", word_prime

    return [], None, None

def get_matches(lex: Lexicon,
                input_word: str,
                allow_two_words: bool = True,
                allow_syncopy: bool = True,
                allow_suffix: bool = True,
                allow_prefix: bool = True,
                allow_tackon: bool = True) -> EntryQuery:
    m = re.match(r"""([\[\]"'\n ,.)(;:\s]*)([A-Za-z]*)""", input_word)
    assert m is not None
    input_word = m.group(2)

    # unsynced_fg = []
    # synced_fg = []
    for prefix in (lex.prefix_list if allow_prefix else [None]):
        # TODO continue these two loops, only terminate outermost loop if valuen is found
        for suffix in (lex.suffix_list if allow_suffix else [None]):
            prefix_str = "" if prefix is None else prefix.prefix
            prefix_match = prefix_str + (prefix.connect_character if (prefix is not None and prefix.connect_character is not None) else "")

            if not input_word.lower().startswith(prefix_match):
                continue

            for tackon in (lex.tackon_list if allow_tackon else [None]):
                # TODO implement tackon PACKON combinations
                tackon_ending = "" if tackon is None else tackon.tackon
                if not input_word.lower().endswith(tackon_ending):
                    continue
                # DO THE SEARCH

                word = clip_end(input_word, len(tackon_ending))[len(prefix_str):]

                unsyncopated_dic_infl_pairs = get_inner_matches(lex, word.lower(), tackon, prefix, suffix)

                if allow_syncopy:
                    # Try Syncopy
                    syncopated_dic_infl_pairs, why, word_syncopy = get_syncopy_matches(lex, word, tackon, prefix, suffix)
                else:
                    syncopated_dic_infl_pairs, why, word_syncopy = [], None, None

                if len(unsyncopated_dic_infl_pairs) > 0 or len(syncopated_dic_infl_pairs) > 0:
                    return EntryQuery.make_normal(group_dic_infl_pairs(unsyncopated_dic_infl_pairs, prefix, suffix, tackon), word,
                                                  group_dic_infl_pairs(syncopated_dic_infl_pairs, prefix, suffix, tackon), why, word_syncopy)

    if allow_two_words:
        COMMON_PREFIXES = {"dis", "ex", "in", "per", "prae", "pro", "re", "si", "sub", "super", "trans"}
        for i in range(2, len(input_word)-2):
            if input_word[:i] in COMMON_PREFIXES:
                continue
            m1 = get_matches(lex, input_word[:i], allow_two_words=False, allow_syncopy=False,
                             allow_suffix=False, allow_prefix=False)
            m2 = get_matches(lex, input_word[i:], allow_two_words=False, allow_syncopy=False,
                             allow_suffix=False, allow_prefix=False, allow_tackon=False)
            if len(m1.unsyncopated_form_groups) + len(m1.syncopated_form_groups) > 0 and \
               len(m2.unsyncopated_form_groups) + len(m2.syncopated_form_groups) > 0:
                return EntryQuery.make_two_words(m1, m2)
    return EntryQuery.make_no_match(input_word)
