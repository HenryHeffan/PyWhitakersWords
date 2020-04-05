from core_files.entry_and_inflections import *
from core_files.utils import *
import io
open = io.open
import re
import enum
# from typing import NewType, Tuple, List, Dict, Optional, Any, Union, Generator
# from abc import abstractmethod
########################################################################################################################
########################################################################################################################
#                                     classes to store the results from queries                                        #
########################################################################################################################
########################################################################################################################


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

# class Match:
#     def __init__(self,
#                  key: DictionaryKey,
#                  rule: InflectionRule,
#                  prefix: Optional[PrefixEntry],
#                  suffix: Optional[SuffixEntry],
#                  tackon: Optional[TackonEntry]):
#         self.key = key
#         self.rule = rule
#         self.prefix = prefix
#         self.suffix = suffix
#         self.tackon = tackon

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

        # for group in self.unsyncopated_form_groups:
        #     print(group.lemma, group.lemma.dictionary_keys[0].stems, group.key_infl_pairs)
        # for group in self.syncopated_form_groups:
        #     print(group.lemma, group.lemma.dictionary_keys[0].stems, group.key_infl_pairs)

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
            # form_group_map[str(group.lemma)][1][1] = group
            # if not str(group.dic) in form_group_map:
            #     form_group_map[str(group.dic)] = []
            # form_group_map[str(group.dic)].append((group, True, query.syncopated_word, query.syncopated_why))
        # print("HI", [group.suffix for group in self.unsyncopated_form_groups], form_group_map.values())
        format_groups = []
        for lemma, fgs in form_group_map.values():
            unsync, sync = fgs[0], fgs[1]
            assert unsync is None or sync is None or \
                   (unsync.suffix == sync.suffix and unsync.prefix == sync.prefix and unsync.tackon == sync.tackon)
            # print("HI2", unsync.suffix if unsync else None, sync.suffix if sync else None)
            format_groups.append(FormGroupS(
                lemma,
                ([(key, rule, self.unsyncopated_word, False) for key, rule in unsync.key_infl_pairs] if unsync is not None else []) +
                ([(key, rule, self.syncopated_word, True) for key, rule in sync.key_infl_pairs] if sync is not None else []),
                unsync.prefix if unsync is not None else sync.prefix,
                unsync.suffix if unsync is not None else sync.suffix,
                unsync.tackon if unsync is not None else sync.tackon
            ))
        return format_groups


def group_dic_infl_pairs(matched_dic_key_infl_rule_pairs: List[Tuple[DictionaryKey, InflectionRule]],
                         prefix: Optional[PrefixEntry],
                         suffix: Optional[SuffixEntry],
                         tackon: Optional[TackonEntry]) -> List[FormGroup]:
    # Also gather up ('qu', None|'cu') and ('aliqu', None|'alicu') pairs
    KEYS = {'qu', 'aliqu', "cum", "cumque", "piam", "que", "dam", "lubet", "libet", "nam", "quam", "vis"}
    lemma_forms_map: Dict[str, Tuple[DictionaryLemma, List[Tuple[DictionaryKey, InflectionRule]]]] = {k: (None, []) for k in KEYS}  # gather the inflection for each dictionary entry
    for dic_key, infl_rule in matched_dic_key_infl_rule_pairs:
        if dic_key.lemma.dictionary_keys[0].stems[0] == 'qu' and dic_key.lemma.dictionary_keys[0].stems[1] in {None, 'cu'}\
                and dic_key.part_of_speech == PartOfSpeech.Pronoun:
            lemma_forms_map['qu'][1].append((dic_key, infl_rule))
        elif dic_key.lemma.dictionary_keys[0].stems[0] == 'qu' and dic_key.lemma.dictionary_keys[0].stems[1] in {None, 'cu'}\
                and dic_key.part_of_speech == PartOfSpeech.Packon:
            lemma_forms_map[dic_key.packon_data.tackon_str][1].append((dic_key, infl_rule))
        elif dic_key.lemma.dictionary_keys[0].stems[0] == 'aliqu' and dic_key.lemma.dictionary_keys[0].stems[1] in {None, 'alicu'}:
            lemma_forms_map['aliqu'][1].append((dic_key, infl_rule))
        else:
            if not dic_key.lemma.index in lemma_forms_map:
                lemma_forms_map[dic_key.lemma.index] = (dic_key.lemma, [])
            lemma_forms_map[dic_key.lemma.index][1].append((dic_key, infl_rule))

    # print("LEMMA FORMS MAP", lemma_forms_map)
    grouped_list = []
    for k, (lemma, forms) in lemma_forms_map.items():
        if len(forms) == 0:
            continue
        if k in KEYS:
            # print("GATHERING", k)
            defs = sorted(list({key.lemma.definition for key, _ in forms if key.lemma.definition}))
            htmls = sorted(list({key.lemma.html_data for key, _ in forms if key.lemma.html_data}))
            if k == 'aliqu':
                fake_key = DictionaryKey(('aliqu', 'alicu', None, None),
                                     PartOfSpeech.Pronoun,
                                     PronounDictData(DeclentionType(1), DeclentionSubtype(0), PronounKind.X))
            elif k == 'qu':
                fake_key = DictionaryKey(('qu', 'cu', None, None),
                                     PartOfSpeech.Pronoun,
                                     PronounDictData(DeclentionType(1), DeclentionSubtype(0), PronounKind.X))
            else:  # if k == 'quPACK':
                d = PackonDictData(DeclentionType(1), DeclentionSubtype(0), PronounKind.X)
                d.tackon_str = forms[0][0].packon_data.tackon_str
                fake_key = DictionaryKey(('qu', 'cu', None, None),
                                     PartOfSpeech.Packon,
                                     d)
            cut_forms = []
            for _, form in forms:
                if not (fake_key, form) in cut_forms:
                    cut_forms.append((fake_key, form))
            pos = PartOfSpeech.Pronoun if k in {'qu', 'aliqu'} else PartOfSpeech.Packon
            grouped_list.append(FormGroup(DictionaryLemma(
                pos,
                [fake_key],
                TranslationMetadata("X X X A O"),
                "\n".join(defs),
                "\n".join(htmls),
                0
            ), cut_forms, prefix, suffix, tackon))
                # tackon if pos != PartOfSpeech.Packon else None
        else:
            grouped_list.append(FormGroup(lemma, sorted(forms, key=lambda x: x[1].index), prefix, suffix, tackon))
    # print("GROUPED LIST", grouped_list)
    #
    # for dic_key, infl_rule in matched_dic_key_infl_rule_pairs:
    #     if not str(dic_key.lemma) in lemma_forms_map:
    #         lemma_forms_map[str(dic_key.lemma)] = (dic_key.lemma, [])
    #     lemma_forms_map[str(dic_key.lemma)][1].append((dic_key, infl_rule))
    # grouped_list = [FormGroup(lemma, sorted(forms, key=lambda x: x[1].index), prefix, suffix, tackon)
    #                 for k, (lemma, forms) in lemma_forms_map.items()]

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

# from QuickLatin.whitakers_words_lexicon import WWLexicon
# print(get_matches(WWLexicon(), "servus", allow_two_words=False).unsyncopated_form_groups)
