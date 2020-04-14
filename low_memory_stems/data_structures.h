
#ifndef SRC_DATA_STRUCTURES_H_
#define SRC_DATA_STRUCTURES_H_

#include "assert.h"
#include "assert.h"
#include <vector>
#include <string>
#include "generated.h"

using namespace std;

class DictionaryLemma;


class TranslationMetadata {
public:
    DictionaryAge age;  //:  = DictionaryAge.from_str(s[0])
    char area;  //: str = s[2]
    char geo;  //: str = s[4]
    DictionaryFrequency frequency;  //:  = DictionaryFrequency.from_str(s[6])
    char source;  //: str = s[8]

    TranslationMetadata(const char *s);

};


class StemGroup {
public:
    const char *s1;
    const char *s2;
    const char *s3;
    const char *s4;

    const char *_get_cstr(int i) const;
    const string _get_elem(int i) const;

    StemGroup(const char *s1, const char *s2, const char *s3, const char *s4);
};


class DictionaryKey {
private:
    const DictData *data;
public:
    const StemGroup stems;
    const PartOfSpeech part_of_speech;
    const DictionaryLemma *lemma;

    DictionaryKey(const char *s1, const char *s2, const char *s3, const char *s4,
                  const PartOfSpeech part_of_speech, const DictData *data, const DictionaryLemma *lemma);

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
};


class DictionaryKeyView {
private:
    const DictionaryKey *keys;
    const unsigned int keys_ct;
public:
    DictionaryKeyView(const DictionaryKey *keys, const unsigned int keys_ct);
    const int len() const;
    const DictionaryKey *_get_index(int index) const;
    const DictionaryKeyView _get_sub_to_end_array(int start) const;
};


class DictionaryKeyPtrView {
private:
    const DictionaryKey **keys;
    const unsigned int keys_ct;
public:
    DictionaryKeyPtrView(const DictionaryKey **keys, const unsigned int keys_ct);
    const int len() const;
    const DictionaryKey *_get_index(int index) const;
    const DictionaryKeyPtrView _get_sub_to_end_array(int start) const;
};


class DictionaryLemma {
    const char *translation_metadata;
    const char *_stored_html_data;
    const char *definition;
    const DictionaryKey *dictionary_keys_array;
    const int dictionary_keys_ct;
public:
    const PartOfSpeech part_of_speech;
    const int index;

    DictionaryLemma(
        PartOfSpeech part_of_speech,
        const char *translation_metadata,
        const char *definition, const char *html_data,
        int index, const DictionaryKey *keys, int keys_ct);

    const DictionaryKeyView _property_dictionary_keys() const;
    const string _property_definition() const;
    const string _property_stored_html_data() const;
    const TranslationMetadata _property_translation_metadata() const;
};


class HashTableCell {
public:
    const DictionaryKey **keys; // w_.assign(w, w + len);
    const unsigned short ct_keys; // if this is 0, then the cell is empty
    const unsigned int hash;

    HashTableCell(const DictionaryKey **keys, const unsigned short ct_keys, const unsigned int hash);
};


class HashTable {
private:
    const HashTableCell *cells; // will assume load factor is not 100 percent, should be >50
    const unsigned long len_log2;
    const int key_string_index; // this is used for checking the actual string on lookup

    const HashTableCell *get_cell(const string &s) const;
public:
    HashTable(const HashTableCell *cells, const unsigned long len_log2, const int key_string_index);
    HashTable();

    bool has(const string &s) const;
    const DictionaryKeyPtrView get(const string &s) const;
};

class BakedDictionaryStemCollection {
private:
    const HashTable lookup_table[13][4]; // const HashTable lookup_table[MAX_PartOfSpeech][4];
    const DictionaryLemma *lemma_vec;
    const int lemma_ct;
public:
    BakedDictionaryStemCollection(const HashTable (&lookup_table)[13][4], const DictionaryLemma *lemma_vec, const int lemma_ct);

    const HashTable *get_hashtable_for(int pos, int stem_key) const;
    const void load (const string &path) const;
};

extern const BakedDictionaryStemCollection BAKED_WW;
extern const BakedDictionaryStemCollection BAKED_JOINED;

#endif

