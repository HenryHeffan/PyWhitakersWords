
#include "data_structures.h"
#include "assert.h"

//#define DO_ASSERTS

using namespace std;

TranslationMetadata::TranslationMetadata(const char *s) {
    // s is of length 5
    this->age = s[0] - '0'; // TODO
    this->area = s[1];
    this->geo = s[2];
    this->frequency = s[3] - '0'; // TODO
    this->source = s[4];
}

const char *StemGroup::_get_cstr(int i) const
{
    if(i==0) {
        return this->s1;
    } else if(i==1) {
        return this->s2;
    } else if(i==2) {
        return this->s3;
    } else { // if(i==2) {
        return this->s4;
    }
}
const string StemGroup::_get_elem(int i) const
{

    return string(this->_get_cstr(i));
}
StemGroup::StemGroup(const char *s1, const char *s2, const char *s3, const char *s4):
                    s1(s1), s2(s2), s3(s3), s4(s4) {};

DictionaryKey::DictionaryKey(const char *s1, const char *s2, const char *s3, const char *s4, const int part_of_speech,
              const DictData *data, const DictionaryLemma *lemma):
                   stems(s1, s2, s3, s4),
                   part_of_speech(part_of_speech),
                   data(data),
                   lemma(lemma) {}

const NounDictData *DictionaryKey::_property_noun_data() const {
    #ifdef DO_ASSERTS
    assert(this->part_of_speech == PartOfSpeech::Noun);
    #endif
    return static_cast<const NounDictData *>(this->data);
}
const PronounDictData *DictionaryKey::_property_pronoun_data() const {
    #ifdef DO_ASSERTS
    assert(this->part_of_speech == PartOfSpeech::Pronoun);
    #endif
    return static_cast<const PronounDictData *>(this->data);
}
const VerbDictData *DictionaryKey::_property_verb_data() const {
    #ifdef DO_ASSERTS
    assert(this->part_of_speech == PartOfSpeech::Verb);
    #endif
    return static_cast<const VerbDictData *>(this->data);
}
const AdjectiveDictData *DictionaryKey::_property_adjective_data() const {
    #ifdef DO_ASSERTS
    assert(this->part_of_speech == PartOfSpeech::Adjective);
    #endif
    return static_cast<const AdjectiveDictData *>(this->data);
}
const InterjectionDictData *DictionaryKey::_property_interjection_data() const {
    #ifdef DO_ASSERTS
    assert(this->part_of_speech == PartOfSpeech::Interjection);
    #endif
    return static_cast<const InterjectionDictData *>(this->data);
}
const PackonDictData *DictionaryKey::_property_packon_data() const {
    #ifdef DO_ASSERTS
    assert(this->part_of_speech == PartOfSpeech::Packon);
    #endif
    return static_cast<const PackonDictData *>(this->data);
}
const ConjunctionDictData *DictionaryKey::_property_conjunction_data() const {
    #ifdef DO_ASSERTS
    assert(this->part_of_speech == PartOfSpeech::Conjunction);
    #endif
    return static_cast<const ConjunctionDictData *>(this->data);
}
const AdverbDictData *DictionaryKey::_property_adverb_data() const {
    #ifdef DO_ASSERTS
    assert(this->part_of_speech == PartOfSpeech::Adverb);
    #endif
    return static_cast<const AdverbDictData *>(this->data);
}
const PrepositionDictData *DictionaryKey::_property_preposition_data() const {
    #ifdef DO_ASSERTS
    assert(this->part_of_speech == PartOfSpeech::Preposition);
    #endif
    return static_cast<const PrepositionDictData *>(this->data);
}
const NumberDictData *DictionaryKey::_property_number_data() const {
    #ifdef DO_ASSERTS
    assert(this->part_of_speech == PartOfSpeech::Number);
    #endif
    return static_cast<const NumberDictData *>(this->data);
}
//    InterjectionDictData *interjection_data() {
//        assert(this->part_of_speech == PartOfSpeech::Interjection);
//        return static_cast<InterjectionDictData *>(this->data);
//    }

DictionaryKeyView::DictionaryKeyView(
    const DictionaryKey *keys, const unsigned int keys_ct):
    keys(keys), keys_ct(keys_ct) {};

const int DictionaryKeyView::len() const {
    return this->keys_ct;
}
const DictionaryKey *DictionaryKeyView::_get_index(int index) const{
    #ifdef DO_ASSERTS
    assert(index >= 0 && index < this->keys_ct);
    #endif
    return &this->keys[index];
}
const DictionaryKeyView DictionaryKeyView::_get_sub_to_end_array(int start) const{
    #ifdef DO_ASSERTS
    assert(0 <= start && start < this->keys_ct);
    #endif
    return DictionaryKeyView(&this->keys[start], this->keys_ct - start);
}


DictionaryKeyPtrView::DictionaryKeyPtrView(const DictionaryKey **keys, const unsigned int keys_ct):
        keys(keys), keys_ct(keys_ct) {};
const int DictionaryKeyPtrView::len() const {
    return this->keys_ct;
}
const DictionaryKey *DictionaryKeyPtrView::_get_index(int index) const {
    #ifdef DO_ASSERTS
    assert(index >= 0 && index < this->keys_ct);
    #endif
    return this->keys[index];
}
const DictionaryKeyPtrView DictionaryKeyPtrView::_get_sub_to_end_array(int start) const {
    #ifdef DO_ASSERTS
    assert(0 <= start && start < this->keys_ct);
    #endif
    return DictionaryKeyPtrView(&this->keys[start], this->keys_ct - start);
}


DictionaryLemma::DictionaryLemma(
        const int part_of_speech,
        const char *translation_metadata,
        const char *definition, const char *html_data,
        const int index, const DictionaryKey *keys, const int keys_ct, const short baked_dictionary_index):
            part_of_speech(part_of_speech),
            translation_metadata(translation_metadata),
            definition(definition),
            _stored_html_data(html_data),
            dictionary_keys_array(keys),
            dictionary_keys_ct(keys_ct),
            index(index),
            baked_dictionary_index(baked_dictionary_index) { }

    const DictionaryKeyView DictionaryLemma::_property_dictionary_keys() const {
        return DictionaryKeyView(this->dictionary_keys_array, (unsigned int)this->dictionary_keys_ct);
    }
    const string DictionaryLemma::_property_definition() const {
        return string(this->definition);
    }
    const string DictionaryLemma::_property_stored_html_data() const {
        return string(this->_stored_html_data);
    }
    const TranslationMetadata DictionaryLemma::_property_translation_metadata() const {
        return TranslationMetadata(this->translation_metadata);
    }

static const unsigned int hash_string(const string &str)
{
    unsigned int hash = 5381;
    for(int i = 0; i < str.length(); i++)
        hash = ((hash << 5) + hash) + str[i]; /* hash * 33 + c */
    return hash; // this hash should always have a 0 in the first bit
}

HashTableCell::HashTableCell(const DictionaryKey **keys, const unsigned short ct_keys, const unsigned int hash):
    keys(keys), ct_keys(ct_keys), hash(hash) {};

const HashTableCell *HashTable::get_cell(const string &s) const {
    unsigned int hash = hash_string(s);
    int index = hash & ((1 << this->len_log2) - 1);
    while(1) {
        const HashTableCell *cell = &this->blocks[index >> MAX_HASHTABLE_BLOCK_SIZE_EXP].cells[index & (MAX_HASHTABLE_BLOCK_SIZE - 1)];
        if (cell->ct_keys == 0)
            break;
        if(cell->hash == hash) {
            if(cell->keys[0]->stems._get_cstr(key_string_index) == s)
                return cell;
        }

        index = (index + 1) & ((1 << this->len_log2) - 1);
    }
    return NULL;
}
HashTable::HashTable(const HashTableBlock *blocks, const unsigned long len_log2, const int key_string_index):
    blocks(blocks), len_log2(len_log2), key_string_index(key_string_index) {};
HashTable::HashTable(): blocks(NULL), len_log2(0), key_string_index(0) {};

bool HashTable::has(const string &s) const {
    return this->get_cell(s) != NULL;
}
const DictionaryKeyPtrView HashTable::get(const string &s) const {
    const HashTableCell *cell = this->get_cell(s);
    if(cell == NULL) {
        return DictionaryKeyPtrView(NULL, 0);
    }
    return DictionaryKeyPtrView(cell->keys, (unsigned int)(cell->ct_keys));
}


const int DictionaryLemmaListView::len() const {
    return this->lemma_ct;
}
const DictionaryLemma *DictionaryLemmaListView::_get_index(int index) const{
    #ifdef DO_ASSERTS
    assert(index >= 0 && index < this->lemma_ct);
    #endif
    return &this->blocks[index >> MAX_LEMMA_LIST_BLOCK_SIZE_EXP].lemmas[index & (MAX_LEMMA_LIST_BLOCK_SIZE - 1)];;
}


BakedDictionaryStemCollection::BakedDictionaryStemCollection(const HashTable (&lookup_table)[13][4], const DictionaryLemmaListView lemma_vec, const short baked_dictionary_index):
        lookup_table(lookup_table), lemma_vec(lemma_vec), baked_dictionary_index(baked_dictionary_index) { };

const HashTable *BakedDictionaryStemCollection::get_hashtable_for(int pos, int stem_key) const
{
    if(stem_key < 1 || stem_key > 4)
        return NULL;
    return &this->lookup_table[pos][stem_key-1];
}

const void BakedDictionaryStemCollection::load (const string &path) const {
    // does nothing, but for convinience of the interfact
}

extern const BakedDictionaryStemCollection BAKED_WW;
extern const BakedDictionaryStemCollection BAKED_JOINED;
