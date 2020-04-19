
from core_files.entry_and_inflections import *

from core_files.utils import *
import io
open = io.open
from core_files.searcher import *  # FormGroup, EntryQuery, get_matches
from core_files import searcher


class WWPOSFormater:  # but everyone that inherit from this must also inherit for POSFormater
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

    def format_dic_metadata(self, metadata: TranslationMetadata):
        return "[{}{}{}{}{}]{}{}".format(DictionaryAge.str_val(metadata.age), metadata.area, metadata.geo, DictionaryFrequency.str_val(metadata.frequency),
                                         metadata.source,
                                         {DictionaryAge.Always: "  ",
                                          DictionaryAge.Archaic: "    Archaic",
                                          DictionaryAge.Early: "    Early",
                                          DictionaryAge.Classic: "  ",
                                          DictionaryAge.Late: "    Late",
                                          DictionaryAge.Later: "    Later",
                                          DictionaryAge.Medieval: "    Medieval",
                                          DictionaryAge.NeoLatin: "    NeoLatin",
                                          DictionaryAge.Modern: "    Modern"}[metadata.age],
                                         {DictionaryFrequency.A: "",
                                          DictionaryFrequency.B: "",
                                          DictionaryFrequency.C: "",
                                          DictionaryFrequency.D: "  lesser",
                                          DictionaryFrequency.E: "  uncommon",
                                          DictionaryFrequency.F: "  veryrare",
                                          DictionaryFrequency.N: "  Pliny",
                                          DictionaryFrequency.X: "",
                                          DictionaryFrequency.I: "  inscript"}[metadata.frequency])

    def format_group(self, dic: DictionaryLemma, forms: List[Tuple[DictionaryKey, InflectionRule]], word: str) -> Tuple[str, str, str]:
        assert isinstance(self, POSFormater) and isinstance(self, WWPOSFormater)
        before = "\n".join(
            [pad_to_len(self.infl_entry_line(key, rule, word), 56) + self.format_infl_metadata(rule.metadata)
             for key, rule in sorted(forms, key=self.sort_infls_key)])
        cannon = "\n".join([self.dic_entry_line(key) for key in dic.dictionary_keys]) + "\n"  # cannon_form
        return before, cannon, dic.definition

    @abstractmethod
    def infl_entry_line(self, key: DictionaryKey, rule: InflectionRule, word: str) -> str:
        pass

    @abstractmethod
    def dic_entry_line(self, dic: DictionaryKey) -> str:
        pass



class WWNounFormater(NounFormater, WWPOSFormater):
    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        return "{form}N      {decl} {decl_val} {case} {number} {gender}".format(
            form=pad_to_len(infl.make_split_word_form(word), 21),
            decl=dic.noun_data.declention,
            decl_val=dic.noun_data.declention_variant,
            case=pad_to_len(Case.str_val(infl.noun_data.case).upper(), 3),
            number=Number.str_val(infl.noun_data.number).upper(),
            gender=Gender.str_val(combine_gender(infl.noun_data.gender, dic.noun_data.gender)).upper()
        )

    def dic_entry_line(self, dic: DictionaryKey) -> str:
        decl = {1: "(1st) ", 2: "(2nd) ", 3: "(3rd) ", 4: "(4th) ", 5: "(5th) ", 9: ""}[dic.noun_data.declention]
        # if dic.noun_data.declention == 3 and dic.noun_data.declention_variant not in {1, 2, 3, 4}:
        #     decl = ""
        if dic.noun_data.declention_variant > 5:
            decl = ""
        # print(dic.part_of_speech)
        return "{cannon_form}  N {decl}{gender}   {metadata}".format(
            cannon_form=self.make_cannon_form_str(dic),
            decl=decl,
            gender=Gender.str_val(dic.noun_data.gender).upper(),
            metadata=self.format_dic_metadata(dic.lemma.translation_metadata)
        )


# TODO: this one needs work
class WWPronounFormater(PronounFormater, WWPOSFormater):
    def format_group(self, dic: DictionaryLemma, forms: List[Tuple[DictionaryKey, InflectionRule]], word: str) -> Tuple[str, str, str]:
        if dic.dictionary_keys[0].pronoun_data.declention != 1:
            return WWPOSFormater.format_group(self, dic, forms, word)
        _forms = []
        for key, rule in forms:
            if not any(_rule == rule for _, _rule in _forms):
                _forms.append((key, rule))
        before = "\n".join(
            [pad_to_len(self.infl_entry_line(key, rule, word), 56) + self.format_infl_metadata(rule.metadata)
             for key, rule in sorted(_forms, key=self.sort_infls_key)])

        cannon = self.dic_entry_line(dic.dictionary_keys[0]) + "\n"  # cannon_form
        return before, cannon, dic.definition

    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        # h.ic                 PRON   3 1 NOM S M
        return "{form}PRON   {decl} {decl_var} {case} {number} {gender}".format(
            form=pad_to_len(infl.make_split_word_form(word), 21),
            decl=dic.pronoun_data.declention,
            decl_var=dic.pronoun_data.declention_variant,
            case=pad_to_len(Case.str_val(infl.pronoun_data.case).upper(), 3),
            number=Number.str_val(infl.pronoun_data.number).upper(),
            gender=Gender.str_val(infl.pronoun_data.gender).upper()
        )

    def dic_entry_line(self, dic: DictionaryKey) -> str:
        # hic, haec, hoc  PRON   [XXXAX]
        cannon_form = self.make_cannon_form_str(dic)
        return "{cannon_form}{pos} {metadata}".format(
            cannon_form=cannon_form,
            pos="" if cannon_form == "" else "  PRON  ",
            metadata=self.format_dic_metadata(dic.lemma.translation_metadata)
        )


class WWVerbFormater(VerbFormater, WWPOSFormater):
    def filter_verb_kind(self, vk: VerbKind) -> VerbKind:
        return vk if vk in {VerbKind.Impers, VerbKind.Dep, VerbKind.Semidep, VerbKind.Perfdef} else VerbKind.X

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
        conj = dic.verb_data.conjugation
        conj_var = dic.verb_data.conjugation_variant
        if (conj, conj_var) == (3, 4):
            conj, conj_var = ConjugationType(4), ConjugationSubtype(1)
        return "{form}V      {conj} {conj_var} {tense} {voice} {mood} {person} {number}".format(
            form=pad_to_len(infl.make_split_word_form(word), 21),
            conj=conj,
            conj_var=conj_var,
            tense=pad_to_len(Tense.str_val(infl.verb_data.tense).upper(), 4),
            voice=pad_to_len(Voice.str_val(infl.verb_data.voice).upper() if dic.verb_data.verb_kind != VerbKind.Dep else "",
                             7),
            mood=pad_to_len(Mood.str_val(infl.verb_data.mood).upper(), 3),
            person=Person.str_val(infl.verb_data.person).upper(),
            number=Number.str_val(infl.verb_data.number).upper(),
        )

    def infl_entry_line_suppine(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        conj = dic.verb_data.conjugation
        conj_var = dic.verb_data.conjugation_variant
        if (conj, conj_var) == (3, 4):
            conj, conj_var = ConjugationType(4), ConjugationSubtype(1)
        return "{form}SUPINE {conj} {conj_var} {case} {number} {gender}".format(
            form=pad_to_len(infl.make_split_word_form(word), 21),
            conj=conj,
            conj_var=conj_var,
            case=pad_to_len(Case.str_val(infl.supine_entry.case).upper(), 3),
            number=Number.str_val(infl.supine_entry.number).upper(),
            gender=Gender.str_val(infl.supine_entry.gender).upper(),
        )

    def infl_entry_line_participle(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        conj = dic.verb_data.conjugation
        conj_var = dic.verb_data.conjugation_variant
        # if (conj, conj_var) == (3, 4):
        #     conj, conj_var = 4, 1
        return "{form}VPAR   {conj} {conj_var} {case} {number} {gender} {tense} {voice} PPL".format(
            form=pad_to_len(infl.make_split_word_form(word), 21),
            conj=conj,
            conj_var=conj_var,
            case=pad_to_len(Case.str_val(infl.participle_entry.case).upper(), 3),
            number=Number.str_val(infl.participle_entry.number).upper(),
            gender=Gender.str_val(infl.participle_entry.gender).upper(),
            tense=pad_to_len(Tense.str_val(infl.participle_entry.tense).upper(), 4),
            voice=pad_to_len(
                Voice.str_val(infl.participle_entry.voice).upper() if dic.verb_data.verb_kind != VerbKind.Dep else "", 7),
        )

    def dic_entry_line(self, dic: DictionaryKey) -> str:
        conj_str = ""
        if dic.verb_data.conjugation == 1:
            conj_str = " (1st)"
        elif dic.verb_data.conjugation == 2:
            conj_str = " (2nd)"
        elif dic.verb_data.conjugation == 3 and dic.verb_data.conjugation_variant == 1:
            conj_str = " (3rd)"
        elif dic.verb_data.conjugation == 3 and dic.verb_data.conjugation_variant == 4:
            conj_str = " (4th)"

        return "{cannon_form}  V{conj_str}{verb_kind}   {metadata}".format(
            cannon_form=self.make_cannon_form_str(dic),
            conj_str=conj_str,
            verb_kind=(" " + VerbKind.str_val(dic.verb_data.verb_kind).upper()) if dic.verb_data.verb_kind in
                                                                         {VerbKind.Trans, VerbKind.Intrans,
                                                                          VerbKind.Dep,
                                                                          VerbKind.Semidep, VerbKind.Impers,
                                                                          VerbKind.Perfdef,
                                                                          VerbKind.Dat, VerbKind.Abl} else "",
            metadata=self.format_dic_metadata(dic.lemma.translation_metadata)
        )

    def format_group(self, dic: DictionaryLemma, forms: List[Tuple[DictionaryKey, InflectionRule]], word: str) -> Tuple[str, str, str]:
        verbs = [pad_to_len(self.infl_entry_line(key, rule, word), 56) + self.format_infl_metadata(rule.metadata)
                 for key, rule in sorted(forms, key=self.sort_infls_key_verb) if rule.part_of_speech == PartOfSpeech.Verb]
        vpars = [pad_to_len(self.infl_entry_line(key, rule, word), 56) + self.format_infl_metadata(rule.metadata)
                 for key, rule in sorted(forms, key=self.sort_infls_key_part) if rule.part_of_speech == PartOfSpeech.Participle]
        sups = [pad_to_len(self.infl_entry_line(key, rule, word), 56) + self.format_infl_metadata(rule.metadata)
                 for key, rule in sorted(forms, key=self.sort_infls_key) if rule.part_of_speech == PartOfSpeech.Supine]
        forms = "\n".join(verbs + vpars + sups)
        cannon = "\n".join([self.dic_entry_line(key) for key in dic.dictionary_keys]) + "\n"  # cannon_form
        defen = dic.definition
        return forms, cannon, defen


# TODO: this one needs work
class WWAdjectiveFormater(AdjectiveFormater, WWPOSFormater):
    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        # grav.i               ADJ    3 2 DAT S X POS
        # grav.i               ADJ    3 2 ABL S X POS
        return "{form}ADJ    {decl} {decl_var} {case} {number} {gender} {adj_kind}".format(
            form=pad_to_len(infl.make_split_word_form(word), 21),
            decl=dic.adjective_data.declention,
            decl_var=dic.adjective_data.declention_variant,
            case=pad_to_len(Case.str_val(infl.adjective_data.case).upper(), 3),
            number=Number.str_val(infl.adjective_data.number).upper(),
            gender=Gender.str_val(infl.adjective_data.gender).upper(),
            adj_kind=AdjectiveKind.str_val(infl.adjective_data.adjective_kind).upper()
        )

    def dic_entry_line(self, dic: DictionaryKey) -> str:
        # gravis, grave, gravior -or -us, gravissimus -a -um  ADJ   [XXXAX]
        return "{cannon_form}  ADJ   {metadata}".format(
            cannon_form=self.make_cannon_form_str(dic),
            metadata=self.format_dic_metadata(dic.lemma.translation_metadata)
        )


# TODO: this one needs some work
class WWAdverbFormater(AdverbFormater, WWPOSFormater):
    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        return "{form}ADV    {adj_kind}".format(
            form=pad_to_len(infl.make_split_word_form(word), 21),
            adj_kind=AdjectiveKind.str_val(infl.adverb_data.adjective_kind_output).upper()
        )

    def dic_entry_line(self, dic: DictionaryKey) -> str:
        return "{cannon_form}  ADV   {metadata}".format(
            cannon_form=self.make_cannon_form_str(dic),
            metadata=self.format_dic_metadata(dic.lemma.translation_metadata)
        )


class WWPrepositionFormater(PrepositionFormater, WWPOSFormater):
    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        # cum                  PREP   ABL
        return "{form}PREP   {case}".format(
            form=pad_to_len(infl.make_split_word_form(word), 21),
            case=Case.str_val(dic.preposition_data.takes_case).upper()
        )

    def dic_entry_line(self, dic: DictionaryKey) -> str:
        # cum  PREP  ABL   [XXXAO]
        return "{cannon_form}  PREP  {case}   {metadata}".format(
            cannon_form=self.make_cannon_form_str(dic),
            case=Case.str_val(dic.preposition_data.takes_case).upper(),
            metadata=self.format_dic_metadata(dic.lemma.translation_metadata)
        )


class WWConjunctionFormater(ConjunctionFormater, WWPOSFormater):
    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        # at                   CONJ
        return "{form}CONJ".format(form=pad_to_len(infl.make_split_word_form(word), 21))

    def dic_entry_line(self, dic: DictionaryKey) -> str:
        # at  CONJ   [XXXAO]
        return "{cannon_form}  CONJ   {metadata}".format(
            cannon_form=self.make_cannon_form_str(dic),
            metadata=self.format_dic_metadata(dic.lemma.translation_metadata)
        )


class WWInterjectionFormater(InterjectionFormater, WWPOSFormater):
    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        # heu                  INTERJ
        return "{form}INTERJ".format(form=pad_to_len(infl.make_split_word_form(word), 21))

    def dic_entry_line(self, dic: DictionaryKey) -> str:
        # heu  INTERJ   [XXXAX]
        return "{cannon_form}  INTERJ   {metadata}".format(
            cannon_form=self.make_cannon_form_str(dic),
            metadata=self.format_dic_metadata(dic.lemma.translation_metadata)
        )


class WWNumberFormater(NumberFormater, WWPOSFormater):
    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        # un.a                 NUM    1 1 NOM S F CARD
        # un.a                 NUM    1 1 VOC S F CARD
        # un.a                 NUM    1 1 ABL S F CARD
        return "{form}NUM    {decl} {decl_var} {case} {number} {gender} {num_kind}".format(
            form=pad_to_len(infl.make_split_word_form(word), 21),
            decl=dic.number_data.declention,
            decl_var=dic.number_data.declention_variant,
            case=pad_to_len(Case.str_val(infl.number_data.case).upper(), 3),
            number=Number.str_val(infl.number_data.number).upper(),
            gender=Gender.str_val(infl.number_data.gender).upper(),
            num_kind=NumberKind.str_val(infl.number_data.number_kind).upper()
        )

    def dic_entry_line(self, dic: DictionaryKey) -> str:
        # unus -a -um, primus -a -um, singuli -ae -a, semel  NUM   [XXXAX]
        return "{cannon_form}  NUM   {metadata}".format(
            cannon_form=self.make_cannon_form_str(dic),
            metadata=self.format_dic_metadata(dic.lemma.translation_metadata)
        )

    def format_group(self, dic: DictionaryLemma, forms: List[Tuple[DictionaryKey, InflectionRule]], word: str) -> Tuple[str, str, str]:
        before = "\n".join(
            [pad_to_len(self.infl_entry_line(key, rule, word), 56) + self.format_infl_metadata(rule.metadata)
             for key, rule in sorted(forms, key=self.sort_infls_key)])
        cannon = "\n".join([self.dic_entry_line(key) for key in dic.dictionary_keys]) + "\n"  # cannon_form
        defen = dic.definition
        if all(rule.number_data.number_kind == NumberKind.Ordinal for key, rule in forms):
            defen = pad_to_len(
                " {number}th - (ORD, 'in series'); (a/the) {number}th (part) (fract w/pars?);                  ".format(
                    number=dic.dictionary_keys[0].number_data.numeric_value), 80)
        elif all(rule.number_data.number_kind == NumberKind.Cardinal for key, rule in forms):
            defen = pad_to_len(" {number} - (CARD answers 'how many');".format(number=dic.dictionary_keys[0].number_data.numeric_value),
                               80)
        return before, cannon, defen


class WWPackonFormater(PackonFormater, WWPOSFormater):
    def format_group(self, dic: DictionaryLemma, forms: List[Tuple[DictionaryKey, InflectionRule]], word: str) -> Tuple[str, str, str]:
        if dic.dictionary_keys[0].pronoun_data.declention != 1:
            return WWPOSFormater.format_group(self, dic, forms, word)
        _forms = []
        for key, rule in forms:
            if not any(_rule == rule for _, _rule in _forms):
                _forms.append((key, rule))
        before = "\n".join(
            [pad_to_len(self.infl_entry_line(key, rule, word), 56) + self.format_infl_metadata(rule.metadata)
             for key, rule in sorted(_forms, key=self.sort_infls_key)])

        cannon = self.dic_entry_line(dic.dictionary_keys[0]) + "\n"  # cannon_form
        return before, cannon, dic.definition

    def infl_entry_line(self, dic: DictionaryKey, infl: InflectionRule, word: str) -> str:
        # h.ic                 PRON   3 1 NOM S M
        return "{form}PRON   {decl} {decl_var} {case} {number} {gender}".format(
            form=pad_to_len(infl.make_split_word_form(word) + '-' + dic.packon_data.tackon_str, 21),
            decl=dic.packon_data.declention,
            decl_var=dic.packon_data.declention_variant,
            case=pad_to_len(Case.str_val(infl.packon_data.case).upper(), 3),
            number=Number.str_val(infl.packon_data.number).upper(),
            gender=Gender.str_val(infl.packon_data.gender).upper()
        )

    def dic_entry_line(self, dic: DictionaryKey) -> str:
        # hic, haec, hoc  PRON   [XXXAX]
        cannon_form = self.make_cannon_form_str(dic)
        return "{cannon_form}{pos} {metadata}".format(
            cannon_form=cannon_form,
            pos="" if cannon_form == "" else "  PRON  ",
            metadata=self.format_dic_metadata(dic.lemma.translation_metadata)
        )


class WWFormater(searcher.Formater):
    def __init__(self,
                 lex: Lexicon):
        searcher.Formater.__init__(self, lex)
        self.map = {
            PartOfSpeech.Noun: WWNounFormater(lex),
            PartOfSpeech.Pronoun: WWPronounFormater(lex),
            PartOfSpeech.Verb: WWVerbFormater(lex),
            PartOfSpeech.Adjective: WWAdjectiveFormater(lex),
            PartOfSpeech.Adverb: WWAdverbFormater(lex),
            PartOfSpeech.Preposition: WWPrepositionFormater(lex),
            PartOfSpeech.Conjunction: WWConjunctionFormater(lex),
            PartOfSpeech.Interjection: WWInterjectionFormater(lex),
            PartOfSpeech.Number: WWNumberFormater(lex),
            PartOfSpeech.Packon: WWPackonFormater(lex)
        }
        for pos, formater in self.map.items():
            formater.setup()

    def parse(self, s) -> str:
        m = get_matches(self.lex, s)
        return self.display_entry_query(m)

    def parse_document(self, filename):
        lines_raw = []
        with open(filename) as inp:
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
        for line, ending in zip(lines, endings):
            for word in line.split(" "):
                word = word.strip()
                if word is not "":
                    print(self.parse(word))
            print(ending)

    def parse_and_def(self, s) -> Tuple[str, str]:
        m = self.lex.get_matches(s)

        def extract(fgs: List[FormGroup]):
            r = []
            for fg in fgs:
                r.append(
                    "\n".join([self.map[fg.lemma.part_of_speech].dic_entry_line(fg.lemma)] + ["    " + line for line in
                                                                                              fg.lemma.definition.split("\n")]))
            return r

        l = extract(m.unsyncopated_form_groups) + extract(m.syncopated_form_groups) + (
            [] if not m.two_words else
            extract(m.two_words_query1.unsyncopated_form_groups) + extract(m.two_words_query2.syncopated_form_groups))
        r = "\n".join(l)
        if r != "":
            r += "\n"
        return self.display_entry_query(m), r

    def dictionary_keyword(self, dic: Union[DictionaryLemma, DictionaryKey]) -> str:
        if isinstance(dic, DictionaryLemma):
            return self.map[dic.part_of_speech].dictionary_key_form(dic.dictionary_keys[0])
        else:
            return self.map[dic.part_of_speech].dictionary_key_form(dic)

    def format_suffix_group(self, form_group: FormGroup, word: str) -> Tuple[str, str, str]:
        assert form_group.suffix is not None
        formater_pos_infl = self.map[form_group.suffix.new_pos]
        formater_pos_stem = self.map[form_group.suffix.stem_pos]
        before = "\n".join([pad_to_len(formater_pos_infl.infl_entry_line(
            form_group.suffix.make_fake_dic_key(key),
            rule,
            word), 56) + formater_pos_infl.format_infl_metadata(rule.metadata)
                            for key, rule in sorted(form_group.key_infl_pairs, key=formater_pos_infl.sort_infls_key)])
        cannon = "\n".join([formater_pos_stem.dic_entry_line(key) for key in form_group.lemma.dictionary_keys]) + "\n"  # cannon_form
        defen = form_group.lemma.definition
        return before, cannon, defen

    def display_entry_query(self, query: EntryQuery, no_newline=False) -> str:
        output = []
        if query.two_words:
            assert query.two_words_query1 is not None
            assert query.two_words_query2 is not None
            output.append("Two words            \nMay be 2 words combined ({}+{}) If not obvious, probably incorrect"
                          .format(query.two_words_query1.unsyncopated_word, query.two_words_query2.unsyncopated_word))
            output.append("\n")
            output.append(self.display_entry_query(query.two_words_query1, no_newline=True))
            output.append("\n")
            output.append(self.display_entry_query(query.two_words_query2))
            output.append("\n")
            return "".join(output)

        class FormatStrGroup:
            def __init__(self, forms: str, cannon: str, defens: str, infls: List[InflectionRule]):
                self.forms = forms
                self.cannon = cannon
                self.defens = defens
                self.infls = infls

        def trim_strs(ls_unsync: List[FormatStrGroup], ls_sync: List[FormatStrGroup], word: str):
            # >>              N      3 3 NOM P F
            # >>              N      3 3 NOM P F
            # >>.is              N      3 3 NOM P F                   Early   uncommon
            st = False
            if word == "me":
                ls_unsync = [tup for tup in ls_unsync if not tup.cannon.startswith("meio, meere, mixi, mictus")]
                st = True
            elif word in {"esse", "erit", "erat", "esset", "essent"}:
                ls_sync = [tup for tup in ls_sync if not tup.cannon.startswith("eo, eare, evi, etus")]
                # st = True

            patterns = [
                r"^(\S*)\.ere *V      3 1 PRES PASSIVE IND 2 S *Early *uncommon *\n",
                r"^(\S*)\.um *N      1 1 GEN P F *uncommon *\n",
                r"^(\S*)\.um *N      2 1 GEN P [MN] *uncommon *\n",
                r"^(\S*)\.um *N      4 1 GEN P M *Classic *uncommon *\n",
                r"^(\S*)\.os *N      4 1 GEN S M *uncommon *\n",
                r"^(\S*)\.is *N      3 3 NOM P [CFM] *Early *uncommon *\n",
                r"^(\S*)\.is *N      3 (1|3) NOM P [CFM] *Archaic *\n",
                r"^(\S*)\.is *N      3 \d NOM P [CFM] *\n",
                r"^(\S*)\.is *N      3 \d ACC P [CFM] *uncommon *\n",
                r"^(\S*)\.um *N      2 2 GEN P N *uncommon *\n",
                r"^(\S*)\.i *N      4 1 GEN S M *Archaic *\n",
                r"^(\S*)\.os *N      4 1 GEN S M *Archaic *uncommon *\n",
                r"^(\S*)\.e *N      5 1 DAT S C *Early *uncommon *\n",
                r"^(\S*)\.it *V      8 2 PERF ACTIVE  SUB 3 S *Early *uncommon",
                r"^(\S*)\.it *V      8 2 FUTP ACTIVE  IND 3 S *Early *uncommon",
            ]

            def filter_list(ls: List[FormatStrGroup]) -> List[FormatStrGroup]:
                import re
                nls = []
                for i in range(len(ls)):
                    ls[i].forms += "\n"
                    for p in patterns:
                        if re.search(p, ls[i].forms, flags=re.MULTILINE):
                            ls[i].forms = re.sub(p, "", ls[i].forms, flags=re.MULTILINE)
                    ls[i].forms = ls[i].forms.rstrip("\n")
                    if ls[i].forms != "":
                        nls.append(ls[i])
                return nls

            return filter_list(ls_unsync), filter_list(ls_sync), st

        def output_and_join(ls: List[FormatStrGroup]):
            # nls: List[FormatStrGroup] = ls[:1]  # this will store pairs, but will have doubled cannon groups joined
            # for elem in ls[1:]:
            #     last = nls[-1]
            #     if last.forms[:32] == elem.forms[:32] and last == elem.defens and last.infls == elem.infls:  # alternate stems
            #         nls[-1] = FormatStrGroup(last.forms, last.cannon + elem.cannon, last.defens, last.infls)
            #     elif last.defens == elem.defens: # shared definition
            #         nls[-1] = FormatStrGroup(last.forms, last.cannon, "###", last.infls)
            #         nls.append(elem)
            #     elif ((last.forms.startswith("qu.") and elem.forms.startswith("qu.")) or
            #                     (last.forms.startswith("cu.") and elem.forms.startswith("cu."))):  # removed redundant tags on qui quae quod forms
            #         nls.append(FormatStrGroup(elem.forms, "", elem.defens, elem.infls))
            #     else:
            #         nls.append(elem)
            # ls = nls

            prev = None
            for elem in ls:
                if prev is not None and prev.forms == elem.forms: # and prev[2] == "" and elem[2] == "":
                    output.append(elem.cannon)
                    if elem.defens != "###":
                        output.append(elem.defens)
                        output.append("\n")
                else:
                    output.append(elem.forms)
                    output.append("\n")
                    output.append(elem.cannon)
                    if elem.defens != "###":
                        output.append(elem.defens)
                        output.append("\n")
                prev = elem

        class Temp:
            printed_tackon = False
            printed_prefix = False
            printed_suffix = False

        # FUSE GROUPS AS NESSACCARY
        # 4 things in each format: BEFORE, CANNON, DEF, AFTER
        # groups: List[List[FormGroup]] = []
        # for group in query.form_groups:
        #     if len(groups) > 0 and groups[-1][0].infls == group.infls:
        #         groups[-1].append(group)
        #     else:
        #         groups.append([group])
        # print(groups)
        # ls = []
        def make_ls(form_groups: List[FormGroup], word: str) -> List[FormatStrGroup]:
            ls: List[FormatStrGroup] = []
            for form_group in form_groups:
                if form_group.tackon is not None and not Temp.printed_tackon:
                    output.append(pad_to_len("{}TACKON".format(pad_to_len(form_group.tackon.tackon, 21)), 56))
                    output.append("\n")
                    output.append(form_group.tackon.explination)
                    output.append("\n")
                    Temp.printed_tackon = True
                if form_group.prefix is not None and not Temp.printed_prefix:
                    output.append(pad_to_len("{}PREFIX".format(pad_to_len(form_group.prefix.prefix, 21)), 56))
                    output.append("\n")
                    output.append(form_group.prefix.explination)
                    output.append("\n")
                    Temp.printed_prefix = True
                if form_group.suffix is not None and not Temp.printed_suffix:
                    output.append(pad_to_len("{}SUFFIX".format(pad_to_len(form_group.suffix.suffix, 21)), 56))
                    output.append("\n")
                    output.append(form_group.suffix.explination)
                    output.append("\n")
                    Temp.printed_suffix = True

                if form_group.suffix is not None:
                    before, cannon, defen = self.format_suffix_group(form_group, word)
                else:
                    before, cannon, defen = self.map[form_group.lemma.part_of_speech].format_group(form_group.lemma,
                                                                                                        form_group.key_infl_pairs,
                                                                                                        word)
                ls.append(FormatStrGroup(before, cannon, defen, form_group.key_infl_pairs))
            return ls

        ls_unsync = make_ls(query.unsyncopated_form_groups, query.unsyncopated_word)
        ls_sync = make_ls(query.syncopated_form_groups, query.syncopated_word)
        # for form_group in query.form_groups_syncopy:
        #     if query.suffix is not None:
        #         before, cannon, after, defen = format_suffix_group(form_group, query.word_syncopy)
        #     else:
        #         before, cannon, after, defen = self.map[form_group.dic.part_of_speech].format_group(form_group.dic, form_group.infls, query.word_syncopy)
        #     ls_sync.append([before, cannon, after, defen, form_group.infls])


        ls_unsync, ls_sync, st = trim_strs(ls_unsync, ls_sync, query.unsyncopated_word)
        output_and_join(ls_unsync)

        if len(ls_sync) > 0 and query.syncopated_why is not None:
            output.append(query.syncopated_why)
            output.append("\n")
            output_and_join(ls_sync)
        # for i in range(len(ls)):
        #     if i > 0 and ls[i - 1][0] == ls[i][0] and ls[i - 1][2] == "" and ls[i][2] == "":
        #         # print(ls[i][0], end="\n")
        #         print(ls[i][1], end="")
        #         print(ls[i][2], end="")
        #         print(ls[i][3], end="\n")
        #     else:
        #         print(ls[i][0], end="\n")
        #         print(ls[i][1], end="")
        #         print(ls[i][2], end="")
        #         print(ls[i][3], end="\n")
        # print(query.word)
        if not no_newline:
            output.append(
                ("*" if st else "") if (len(ls_unsync) + len(ls_sync) > 0) else "{}========   UNKNOWN    \n".format(
                    pad_to_len(query.unsyncopated_word, 33)))
            output.append("\n")

        return "".join(output)

def init(path: str, no_cache: bool=False, fast: bool = True) -> Tuple[OldStyle_DICTLINE_Lexicon, WWFormater]:
    WW_LEXICON = (BakedLexicon("BAKED_WW") if fast else OldStyle_DICTLINE_Lexicon("DataFiles/DICTLINE.txt"))
    WW_LEXICON.load(path)

    WW_FORMATER = WWFormater(WW_LEXICON)
    return WW_LEXICON, WW_FORMATER

# from memory_profiler import profile

# @profile()
# def test():
#     from time import time
#     s = time()
#     print("START")
#     WW_LEXICON, WW_FORMATER = init("/home/henry/Desktop/latin_website/PyWhitakersWords/")
#     print("LOADED", time()-s)
#
#     def parse(s) -> str:
#         m = get_matches(WW_LEXICON, s)
#         return WW_FORMATER.display_entry_query(m)
#     for i in range(1000000):
#         s = time()
#         parse("qui")
#         # parse("quifcumque")
#         print("SEARCHED", time() - s)
#
# test()
# m = get_matches(WW_LEXICON, "me")
# for fg in m.unsyncopated_form_groups:
#     print([(key.part_of_speech, key.stems, rule.part_of_speech, rule.ending) for key, rule in fg.key_infl_pairs])
# print(WW_FORMATER.display_entry_query(m))






















# parse_document("/home/henry/Desktop/latin_website/QuickLatin/aeneid_bk4.txt")


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

