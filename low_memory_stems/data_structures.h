
#ifndef SRC_DATA_STRUCTURES_H_
#define SRC_DATA_STRUCTURES_H_

#include "assert.h"
#include "generated.h"
#include "generic_data_structures.h"
#include <string>
#include<iostream>

using namespace std;



class InflectionMetadata {

    ENUM_VAR age; // InflectionAge
    ENUM_VAR frequency; // InflectionFrequency
public:
    InflectionMetadata(const char *data) {
        this->age = data[0] - '0';
        this->frequency = data[1] - '0';
    }

    ENUM_VAR get(int index) {
        if(index == 0) {
            return this->age;
        } else {
            return this->frequency;
        }
    }
};

class InflectionRule {
private:
    const InflData *data;
    const char *_metadata_cstr;
    const char *_ending_cstr;
public:
    const int part_of_speech;
    const int stem_key;
    const int index;

    InflectionRule(const char *_ending_cstr,
                   const int part_of_speech,
                   const InflData *data,
                   const int stem_key,
                   const int index,
                   const char *_metadata_cstr);

    const InflectionMetadata _property_metadata() const;
    const string _property_ending() const;

    const NounInflData *_property_noun_data() const;
    const PronounInflData *_property_pronoun_data() const;
    const VerbInflData *_property_verb_data() const;
    const AdjectiveInflData *_property_adjective_data() const;
    const InterjectionInflData *_property_interjection_data() const;
    const PackonInflData *_property_packon_data() const;
    const ConjunctionInflData *_property_conjunction_data() const;
    const AdverbInflData *_property_adverb_data() const;
    const PrepositionInflData *_property_preposition_data() const;
    const NumberInflData *_property_number_data() const;
    const SupineInflData *_property_supine_data() const;
    const ParticipleInflData *_property_participle_data() const;

    const char *_get_cstr_for(int unneeded_extra_data=0) const; // used in template
};


class DictionaryLemma;

class TranslationMetadata {
public:
    ENUM_VAR age;  //:  = DictionaryAge.from_str(s[0])
    char area;  //: str = s[2]
    char geo;  //: str = s[4]
    ENUM_VAR frequency;  //:  = DictionaryFrequency.from_str(s[6])
    char source;  //: str = s[8]

    TranslationMetadata(const char *s);
};


class StemGroup {
public:
    const char *s1;
    const char *s2;
    const char *s3;
    const char *s4;

    StemGroup(const char *s1, const char *s2, const char *s3, const char *s4);

    const char *_get_cstr(int i) const;
    const string _get_elem(int i) const;

};


class DictionaryKey {
private:
    const DictData *data;
public:
    const DictionaryLemma *lemma;
    const StemGroup stems;
    const int part_of_speech;

    DictionaryKey(const char *s1, const char *s2, const char *s3, const char *s4,
                  const int part_of_speech, const DictData *data, const DictionaryLemma *lemma);

    const NounDictData *_property_noun_data() const;
    const PronounDictData *_property_pronoun_data() const;
    const VerbDictData *_property_verb_data() const;
    const AdjectiveDictData *_property_adjective_data() const;
    const InterjectionDictData *_property_interjection_data() const;
    const PackonDictData *_property_packon_data() const;
    const ConjunctionDictData *_property_conjunction_data() const;
    const AdverbDictData *_property_adverb_data() const;
    const PrepositionDictData *_property_preposition_data() const;
    const NumberDictData *_property_number_data() const;

    const char *_get_cstr_for(int key_string_index) const; // used in template
};


class DictionaryLemma {
    const char *translation_metadata;
    const char *_extra_def;
    const char *definition;
    const DictionaryKey *dictionary_keys_array;
    const int dictionary_keys_ct;
public:
    const int part_of_speech;
    const int index;

    // track which dictionary this lemma is in, in case multiple baked dictionaries are loaded
    // const short baked_dictionary_index;

    DictionaryLemma(
        const int part_of_speech,
        const char *translation_metadata,
        const char *definition, const char *_extra_def,
        const int index, const DictionaryKey *keys, const int keys_ct);

    const ArrayView<DictionaryKey> _property_dictionary_keys() const;
    const string _property_definition() const;
    const string _property_extra_def() const;
    const TranslationMetadata _property_translation_metadata() const;
};


class BakedDictionaryStemCollection {
private:
    const HashTable<DictionaryKey> lookup_table[13][4]; // const HashTable lookup_table[MAX_PartOfSpeech][4];
    const BlockedArrayView<DictionaryLemma> lemma_vec;
public:
    // track which dictionary this lemma is in, in case multiple baked dictionaries are loaded
    //const short baked_dictionary_index;

    BakedDictionaryStemCollection(const HashTable<DictionaryKey> (&lookup_table)[13][4], const BlockedArrayView<DictionaryLemma> lemma_vec);  // , const short baked_dictionary_index);

    const HashTable<DictionaryKey> *get_hashtable_for(int pos, int stem_key) const;
    //const void load (const string &path) const;
};

class BakedInflectionRuleCollection {
public:
    const HashTable<InflectionRule> ending_rule_map;
    const BlockedArrayView<InflectionRule> inflection_rules;

    const InflectionRule **noun_rules;
    const InflectionRule **number_rules;
    const InflectionRule **pronoun_rules;
    const InflectionRule **adjective_rules;
    const InflectionRule **verb_rules;
    const InflectionRule **participle_rules;
    const InflectionRule **adverb_rules;
    const InflectionRule *preposition_rule;
    const InflectionRule *conjunction_rule;
    const InflectionRule *interjection_rule;



    BakedInflectionRuleCollection(const HashTable<InflectionRule> ending_rule_map,
                                  const BlockedArrayView<InflectionRule> inflection_rules,
                                  const InflectionRule **noun_rules,
                                  const InflectionRule **number_rules,
                                  const InflectionRule **pronoun_rules,
                                  const InflectionRule **adjective_rules,
                                  const InflectionRule **verb_rules,
                                  const InflectionRule **participle_rules,
                                  const InflectionRule **adverb_rules,
                                  const InflectionRule *preposition_rule,
                                  const InflectionRule *conjunction_rule,
                                  const InflectionRule *interjection_rule);


     const InflectionRule * get_noun_inflection_rule(ENUM_VAR declention,
                                              ENUM_VAR declention_varient,
                                              ENUM_VAR gender,
                                              ENUM_VAR _case,
                                              ENUM_VAR number) const
    {
        return this->noun_rules[(((declention * 10 + declention_varient) * 10 +
                                gender) * MAX_Gender + _case) * MAX_Case + number];
    }

     const InflectionRule *get_number_inflection_rule(ENUM_VAR declention,
                                               ENUM_VAR declention_varient,
                                               ENUM_VAR gender,
                                               ENUM_VAR _case,
                                               ENUM_VAR number,
                                               ENUM_VAR number_kind) const
    {
        return this->number_rules[((((declention * 10 + declention_varient) * 10 + gender) * MAX_Gender +
                                   _case) * MAX_Case + number) * MAX_Number + number_kind];
    }

     const InflectionRule * get_pronoun_inflection_rule(ENUM_VAR declention,
                                                 ENUM_VAR declention_varient,
                                                 ENUM_VAR gender,
                                                 ENUM_VAR _case,
                                                 ENUM_VAR number) const
    {
        return this->pronoun_rules[(((declention * 10 + declention_varient) * 10 + gender) * MAX_Gender +
                                   _case) * MAX_Case + number];
    }

     const InflectionRule * get_adjective_inflection_rule(ENUM_VAR declention,
                                                   ENUM_VAR declention_varient,
                                                   ENUM_VAR gender,
                                                   ENUM_VAR _case,
                                                   ENUM_VAR number,
                                                   ENUM_VAR adjective_kind) const
    {
        return this->adjective_rules[((((declention * 10 + declention_varient) * 10 + gender) * MAX_Gender +
                                     _case) * MAX_Case + number) * MAX_Number + adjective_kind];
    }

     const InflectionRule *get_verb_inflection_rule(ENUM_VAR conjugation,
                                             ENUM_VAR conjugation_variant,
                                             ENUM_VAR number,
                                             ENUM_VAR person,
                                             ENUM_VAR voice,
                                             ENUM_VAR tense,
                                             ENUM_VAR mood) const
    {
        return this->verb_rules[(((((conjugation * 10 + conjugation_variant) * 10 + number) * MAX_Number +
                                person) * MAX_Person + voice) * MAX_Voice + tense) * MAX_Tense + mood];
    }

     const InflectionRule *get_participle_inflection_rule(ENUM_VAR conjugation,
                                                   ENUM_VAR conjugation_variant,
                                                   ENUM_VAR number,
                                                   ENUM_VAR _case,
                                                   ENUM_VAR voice,
                                                   ENUM_VAR tense) const
    {
        return this->participle_rules[((((conjugation * 10 + conjugation_variant) * 10 + number) * MAX_Number +
                                      _case) * MAX_Case + voice) * MAX_Voice + tense];
    }

     const InflectionRule *get_adverb_inflection_rule(ENUM_VAR adjective_kind_key,
                                               ENUM_VAR adjective_kind_output) const
    {
        return this->adverb_rules[adjective_kind_key * MAX_AdjectiveKind + adjective_kind_output];
    };

     const InflectionRule *get_preposition_inflection_rule() const
    {
        return this->preposition_rule;
    };

    const InflectionRule *get_conjunction_inflection_rule() const
    {
        return this->conjunction_rule;
    };

    const InflectionRule *get_interjection_inflection_rule() const
    {
        return this->interjection_rule;
    };
};

extern const BakedDictionaryStemCollection BAKED_WW;
extern const BakedDictionaryStemCollection BAKED_JOINED;

extern const BakedInflectionRuleCollection BAKED_WW_INFL_RULES;

#endif
