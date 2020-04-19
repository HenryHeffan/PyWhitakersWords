
#ifndef SRC_DATA_STRUCTURES_H_
#define SRC_DATA_STRUCTURES_H_

#include "assert.h"
#include "generated.h"
#include <string>

using namespace std;

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
    const char *_extra_def;
    const char *definition;
    const DictionaryKey *dictionary_keys_array;
    const int dictionary_keys_ct;
public:
    const int part_of_speech;
    const int index;

    // track which dictionary this lemma is in, in case multiple baked dictionaries are loaded
    const short baked_dictionary_index;

    DictionaryLemma(
        const int part_of_speech,
        const char *translation_metadata,
        const char *definition, const char *_extra_def,
        const int index, const DictionaryKey *keys, const int keys_ct,
        const short baked_dictionary_index);

    const DictionaryKeyView _property_dictionary_keys() const;
    const string _property_definition() const;
    const string _property_extra_def() const;
    const TranslationMetadata _property_translation_metadata() const;
};


class HashTableCell {
public:
    const DictionaryKey **keys; // w_.assign(w, w + len);
    const unsigned short ct_keys; // if this is 0, then the cell is empty
    const unsigned int hash;

    HashTableCell(const DictionaryKey **keys, const unsigned short ct_keys, const unsigned int hash);
};


class HashTableBlock {
public:
    const HashTableCell *cells;
    HashTableBlock(const HashTableCell *cells): cells(cells)  {};
};

// Compiling really large files is hard on my computer, and doesnt work on my server. Therefore we break the large
// arrays into blocks. Baking them into the executable gets around the memory speed limits on my server, which allows
 // the program to load much faster
extern const int MAX_HASHTABLE_BLOCK_SIZE_EXP;
extern const int MAX_HASHTABLE_BLOCK_SIZE;

extern const int MAX_LEMMA_LIST_BLOCK_SIZE_EXP;
extern const int MAX_LEMMA_LIST_BLOCK_SIZE;

class HashTable {
private:
    const HashTableBlock *blocks; // will assume load factor is not 100 percent, should be >50
    const unsigned long len_log2;
    const int key_string_index; // this is used for checking the actual string on lookup

    const HashTableCell *get_cell(const string &s) const;
public:
    HashTable(const HashTableBlock *blocks, const unsigned long len_log2, const int key_string_index);
    HashTable();

    bool has(const string &s) const;
    const DictionaryKeyPtrView get(const string &s) const;
};


class DictionaryLemmaListBlock {
public:
    const DictionaryLemma *lemmas;
    DictionaryLemmaListBlock(const DictionaryLemma *lemmas): lemmas(lemmas) {};
};

class DictionaryLemmaListView {
private:
    const DictionaryLemmaListBlock *blocks;
    const int lemma_ct;
public:
    DictionaryLemmaListView(const DictionaryLemmaListBlock *blocks, const int lemma_ct): blocks(blocks), lemma_ct(lemma_ct) {};
    const int len() const;
    const DictionaryLemma *_get_index(int index) const;
};

class BakedDictionaryStemCollection {
private:
    const HashTable lookup_table[13][4]; // const HashTable lookup_table[MAX_PartOfSpeech][4];
    const DictionaryLemmaListView lemma_vec;
public:
    // track which dictionary this lemma is in, in case multiple baked dictionaries are loaded
    const short baked_dictionary_index;

    BakedDictionaryStemCollection(const HashTable (&lookup_table)[13][4], const DictionaryLemmaListView lemma_vec, const short baked_dictionary_index);

    const HashTable *get_hashtable_for(int pos, int stem_key) const;
    const void load (const string &path) const;
};

extern const BakedDictionaryStemCollection BAKED_WW;
extern const BakedDictionaryStemCollection BAKED_JOINED;

#endif

