# - *- coding: utf- 8 - *-

from core_files.utils import *
import io
open = io.open
from core_files.entry_and_inflections import *
from core_files.searcher import *
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

HTML_SPACE_TEMP = u"""<div class="collapse" id="collapseSpot{id_slot}">
  <div class="card">
    <div class="card-body">
      {content}
    </div>
  </div>
</div>"""

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


class JPOSFormater:
    def __init__(self, lex: Lexicon):
        self.inflection_table = {}
        self.lex = lex

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
        # print(self.__class__)
        return self.infl_entry_line(dic, infl, "") + ("" if not is_syncopy else " (syncopated)")

    @abstractmethod
    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        pass

    @abstractmethod
    def get_extra_info_spot(self, dic: DictionaryKey) -> str:
        pass

    def dictionary_key_form(self, dic: DictionaryKey) -> str:
        assert isinstance(self, POSFormater)
        return self.make_cannon_form_str(dic).split(',')[0]

    def get_cannon_row_keys(self, keys: List[DictionaryKey]) -> List[DictionaryKey]:
        return keys

    def filter_infl_rules(self, rules: List[Tuple[DictionaryKey, InflectionRule, str, bool]]) -> List[Tuple[DictionaryKey, InflectionRule, str, bool]]:
        return rules


class JNounFormater(NounFormater, JPOSFormater):
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
class JPronounFormater(PronounFormater, JPOSFormater):
    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        return "pronoun {case} {number} {gender}".format(
            case=Case.str_val(infl.pronoun_data.case).lower(),
            number=Number.alt_str_val(infl.pronoun_data.number),
            gender=Gender.alt_str_val(infl.pronoun_data.gender)
        )

    def get_extra_info_spot(self, dic: DictionaryKey) -> str:
        return ""

    def get_cannon_row_keys(self, keys: List[DictionaryKey]):
        return [keys[0]]

    def filter_infl_rules(self, rules: List[Tuple[DictionaryKey, InflectionRule, str, bool]]) -> List[
        Tuple[DictionaryKey, InflectionRule, str, bool]]:
        _infls = []
        for key, rule, s, b in rules:
            if not any(_rule == rule and _s == s and _b == b for _, _rule, _s, _b in _infls):
                _infls.append((key, rule, s, b))
        return _infls

class JVerbFormater(VerbFormater, JPOSFormater):
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

# TODO: this one needs work
class JAdjectiveFormater(AdjectiveFormater, JPOSFormater):
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
class JAdverbFormater(AdverbFormater, JPOSFormater):
    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        return "adv {adj_kind}".format(
            adj_kind=AdjectiveKind.str_val(infl.adverb_data.adjective_kind_output).lower()
        )

    def get_extra_info_spot(self, dic: DictionaryKey) -> str:
        return ""


class JPrepositionFormater(PrepositionFormater, JPOSFormater):
    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        return "prep w/ {case}".format(
            case=Case.str_val(dic.preposition_data.takes_case).lower()
        )

    def get_extra_info_spot(self, dic: DictionaryKey) -> str:
        return "+ {}".format(Case.str_val(dic.preposition_data.takes_case).lower())


class JConjunctionFormater(ConjunctionFormater, JPOSFormater):
    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        # at                   CONJ
        return "conj"

    def get_extra_info_spot(self, dic: DictionaryKey) -> str:
        return ""


class JInterjectionFormater(InterjectionFormater, JPOSFormater):
    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        return "interj"

    def get_extra_info_spot(self, dic: DictionaryKey) -> str:
        return ""


class JNumberFormater(NumberFormater, JPOSFormater):
    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        return "num {case} {number} {gender} {num_kind}".format(
            case=Case.str_val(infl.number_data.case).lower(),
            number=Number.alt_str_val(infl.number_data.number),
            gender=Gender.alt_str_val(infl.number_data.gender),
            num_kind=NumberKind.str_val(infl.number_data.number_kind).lower()
        )

    def get_extra_info_spot(self, dic: DictionaryKey) -> str:
        return ""


class JPackonFormater(PackonFormater, JPOSFormater):
    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        return "pron {case} {number} {gender}".format(
            case=Case.str_val(infl.packon_data.case).lower(),
            number=Number.alt_str_val(infl.packon_data.number),
            gender=Gender.alt_str_val(infl.packon_data.gender)
        )

    def get_extra_info_spot(self, dic: DictionaryKey) -> str:
        return ""

    def get_cannon_row_keys(self, keys: List[DictionaryKey]):
        return [keys[0]]

    def filter_infl_rules(self, rules: List[Tuple[DictionaryKey, InflectionRule, str, bool]]) -> List[
        Tuple[DictionaryKey, InflectionRule, str, bool]]:
        _infls = []
        for key, rule, s, b in rules:
            if not any(_rule == rule and _s == s and _b == b for _, _rule, _s, _b in _infls):
                _infls.append((key, rule, s, b))
        return _infls


class JFormater(searcher.Formater):
    def __init__(self, lex: Lexicon, make_LAS_content=Optional[Callable[[str], str]]):
        searcher.Formater.__init__(self, lex)
        self.map = {
            PartOfSpeech.Noun: JNounFormater(lex),
            PartOfSpeech.Pronoun: JPronounFormater(lex),
            PartOfSpeech.Verb: JVerbFormater(lex),
            PartOfSpeech.Adjective: JAdjectiveFormater(lex),
            PartOfSpeech.Adverb: JAdverbFormater(lex),
            PartOfSpeech.Preposition: JPrepositionFormater(lex),
            PartOfSpeech.Conjunction: JConjunctionFormater(lex),
            PartOfSpeech.Interjection: JInterjectionFormater(lex),
            PartOfSpeech.Number: JNumberFormater(lex),
            PartOfSpeech.Packon: JPackonFormater(lex)
        }
        for formater in self.map.values():
            formater.setup()
        self.make_LAS_content = make_LAS_content if make_LAS_content else \
            lambda las_id: "<div class=\"las-def-spot\" def_id=\"" + las_id + "\"></div>"

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
            ids_for_LAS_entries = [i for i in format_group.lemma.extra_def.split(" ") if i not in {" ", ""}]
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

            cannon_row_keys = dic_formater.get_cannon_row_keys(format_group.lemma.dictionary_keys)
            cannon_form_rows = [CANNON_MAIN_ROW_TEMP.format(
                cannon_form_slot=dic_formater.make_cannon_form_str(cannon_row_keys[0]),
                cannon_form_suffix=(" +" + format_group.tackon.tackon) if format_group.tackon is not None else "",
                button_space=("""<button class="btn btn-outline-secondary" type="button"\ndata-toggle="collapse" data-target="#collapseSpot{id}"\naria-expanded="false" aria-controls="collapseSpot">L&S</button>"""
                              .format(id=group_id)) if len(ids_for_LAS_entries) > 0 else ""
            )]
            for key in cannon_row_keys[1:]:
                cannon_form_rows.append(CANNON_ALT_ROW_TEMP.format(cannon_form_slot=dic_formater.make_cannon_form_str(key)))
            definition_rows = format_group.lemma.definition

            _infls = infl_formater.filter_infl_rules(format_group.key_infl_pairs)
            form_rows = [FORM_ROW_TEMP.format(
                form_row_word_slot=form.make_split_word_form(word),
                form_row_form_slot=infl_formater.make_infl_row_str(
                    format_group.suffix.make_fake_dic_key(key) if format_group.suffix is not None else key,
                    form,
                    is_sync)
            ) for key, form, word, is_sync in _infls]

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
                html_space="".join([HTML_SPACE_TEMP.format(
                    id_slot=group_id,
                    content=self.make_LAS_content(LAS_id)
                ) for LAS_id in ids_for_LAS_entries]),
                form_rows_space="".join(form_rows)
            ))
        return "".join(output)


def init(path: str,
         fast: bool = True,
         load_html_def_dict: bool = False,
         las_id_to_content: Optional[Callable[[str], str]]=None) -> Tuple[NewStyle_Json_Lexicon, JFormater]:
    # One of three should be the case
    # BOTH load_html_def_dict == False and decode_func == None, then do nothing
    # BOTH load_html_def_dict == True and decode_func == None, then load REF_DEF_TABLE.txt and return decoded from this
    # BOTH load_html_def_dict == False and decode_func == some function f, then use f to get the html value lazily as needed
    if load_html_def_dict:
        assert las_id_to_content is None
        import json
        table = {"": ""}
        with open(os.path.join(path, "GeneratedFiles/REF_DEF_TABLE.txt")) as ifile:
            for line in ifile:
                line = line[:-1].split(" ")
                table[line[0]] = line[1]
        las_id_to_content = lambda html_data: "\n".join([load_utf_str(table[k]) for k in html_data.split(" ")])

    J_LEX = (BakedLexicon("BAKED_JOINED")
             if fast else
             NewStyle_Json_Lexicon("GeneratedFiles/JOINED_ONLY_REF_DEF.txt"))  #"GeneratedFiles/JOINED.txt" if not self.ref_def else
    J_LEX.load(path)

    return J_LEX, JFormater(J_LEX, las_id_to_content)
