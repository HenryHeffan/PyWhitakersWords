
#include "data_structures.h"
#include "assert.h"


using namespace std;

/*


template <typename T>
class ArrayView {
private:
    const T *items;
    const unsigned int item_ct;
public:
    ArrayView(const T *items, const unsigned int item_ct);
    const int len() const;
    const T *_get_index(int index) const;
    const ArrayView<T> _get_sub_to_end_array(int start) const;
};

template <class T>
ArrayView<T>::ArrayView(const T *items, const unsigned int item_ct): items(items), item_ct(item_ct) {};

template <class T>
const int ArrayView<T>::len() const {
    return this->item_ct;
}

template <class T>
const T *ArrayView<T>::_get_index(int index) const{
    #ifdef DO_ASSERTS
    assert(index >= 0 && index < this->item_ct);
    #endif
    return &this->items[index];
}

template <class T>
const ArrayView<T> ArrayView<T>::_get_sub_to_end_array(int start) const{
    #ifdef DO_ASSERTS
    assert(0 <= start && start < this->item_ct);
    #endif
    return ArrayView<T>(&this->items[start], this->item_ct - start);
}


template <typename T>
PtrArrayView<T>::PtrArrayView(const T **items, const unsigned int item_ct): items(items), item_ct(item_ct) {};

template <typename T>
const int PtrArrayView<T>::len() const {
    return this->item_ct;
}

template <typename T>
const T *PtrArrayView<T>::_get_index(int index) const{
    #ifdef DO_ASSERTS
    assert(index >= 0 && index < this->item_ct);
    #endif
    return this->items[index];
}

template <typename T>
const PtrArrayView<T> PtrArrayView<T>::_get_sub_to_end_array(int start) const{
    #ifdef DO_ASSERTS
    assert(0 <= start && start < this->item_ct);
    #endif
    return PtrArrayView<T>(&this->items[start], this->item_ct - start);
}

static const unsigned int hash_string(const string &str)
{
    unsigned int hash = 5381;
    for(int i = 0; i < str.length(); i++)
        hash = ((hash << 5) + hash) + str[i]; // hash * 33 + c
    return hash; // this hash should always have a 0 in the first bit
}

template <typename T>
HashTableCell<T>::HashTableCell(const T **items, const unsigned short item_ct, const unsigned int hash):
    items(items), item_ct(item_ct), hash(hash) {};

template <typename T>
const HashTableCell<T> *HashTable<T>::get_cell(const string &s) const {
    unsigned int hash = hash_string(s);
    int index = hash & ((1 << this->len_log2) - 1);
    while(1) {
        const HashTableCell<T> *cell = &this->blocks[index >> this->max_block_size_exp].cells[index & (this->max_block_size_int - 1)];
        if(cell->ct_keys == 0)
            break;
        if(cell->hash == hash && cell->items[0]->_get_cstr_for(this->key_string_index) == s) //cell->matches(hash, s, this->key_string_index))
            return cell;
        index = (index + 1) & ((1 << this->len_log2) - 1);
    }
    return NULL;
}

template <typename T>
HashTable<T>::HashTable(const HashTableBlock<T> *blocks, const unsigned long len_log2,
                        const int max_block_size_exp, const int key_string_index):
    blocks(blocks), len_log2(len_log2), key_string_index(key_string_index),
    max_block_size_exp(max_block_size_exp), max_block_size_int(1 << max_block_size_exp) {};

template <typename T>
HashTable<T>::HashTable(): blocks(NULL), len_log2(0), key_string_index(0) {};

template <typename T>
bool HashTable<T>::has(const string &s) const {
    return this->get_cell(s) != NULL;
}

template <typename T>
const PtrArrayView<T> HashTable<T>::get(const string &s) const {
    const HashTableCell<T> *cell = this->get_cell(s);
    if(cell == NULL)
        return PtrArrayView<T>(NULL, 0);
    return PtrArrayView<T>(cell->items, (unsigned int)(cell->item_ct));
}

template <typename T>
const int BlockedArrayView<T>::len() const {
    return this->item_ct;
}

template <typename T>
const T *BlockedArrayView<T>::_get_index(int index) const{
    #ifdef DO_ASSERTS
    assert(index >= 0 && index < this->item_ct);
    #endif
    return &this->blocks[index >> this->block_size_exp].items[index & (this->block_size_int - 1)];;
}
*/



InflectionRule::InflectionRule(const char *_ending_cstr,
                   const int part_of_speech,
                   const InflData *data,
                   const int stem_key,
                   const int index,
                   const char *_metadata_cstr): _ending_cstr(_ending_cstr), part_of_speech(part_of_speech),
                   data(data), stem_key(stem_key), index(index), _metadata_cstr(_metadata_cstr) {};

const InflectionMetadata InflectionRule::_property_metadata() const {
    return InflectionMetadata(this->_metadata_cstr);
}
const string InflectionRule::_property_ending() const{
    return string(this->_ending_cstr);
}

const NounInflData *InflectionRule::_property_noun_data() const {
    #ifdef DO_ASSERTS
    assert(this->part_of_speech == PartOfSpeech::Noun);
    #endif
    return static_cast<const NounInflData *>(this->data);
}
const PronounInflData *InflectionRule::_property_pronoun_data() const {
    #ifdef DO_ASSERTS
    assert(this->part_of_speech == PartOfSpeech::Pronoun);
    #endif
    return static_cast<const PronounInflData *>(this->data);
}
const VerbInflData *InflectionRule::_property_verb_data() const {
    #ifdef DO_ASSERTS
    assert(this->part_of_speech == PartOfSpeech::Verb);
    #endif
    return static_cast<const VerbInflData *>(this->data);
}
const AdjectiveInflData *InflectionRule::_property_adjective_data() const {
    #ifdef DO_ASSERTS
    assert(this->part_of_speech == PartOfSpeech::Adjective);
    #endif
    return static_cast<const AdjectiveInflData *>(this->data);
}
const InterjectionInflData *InflectionRule::_property_interjection_data() const {
    #ifdef DO_ASSERTS
    assert(this->part_of_speech == PartOfSpeech::Interjection);
    #endif
    return static_cast<const InterjectionInflData *>(this->data);
}
const PackonInflData *InflectionRule::_property_packon_data() const {
    #ifdef DO_ASSERTS
    assert(this->part_of_speech == PartOfSpeech::Packon);
    #endif
    return static_cast<const PackonInflData *>(this->data);
}
const ConjunctionInflData *InflectionRule::_property_conjunction_data() const {
    #ifdef DO_ASSERTS
    assert(this->part_of_speech == PartOfSpeech::Conjunction);
    #endif
    return static_cast<const ConjunctionInflData *>(this->data);
}
const AdverbInflData *InflectionRule::_property_adverb_data() const {
    #ifdef DO_ASSERTS
    assert(this->part_of_speech == PartOfSpeech::Adverb);
    #endif
    return static_cast<const AdverbInflData *>(this->data);
}
const PrepositionInflData *InflectionRule::_property_preposition_data() const {
    #ifdef DO_ASSERTS
    assert(this->part_of_speech == PartOfSpeech::Preposition);
    #endif
    return static_cast<const PrepositionInflData *>(this->data);
}
const NumberInflData *InflectionRule::_property_number_data() const {
    #ifdef DO_ASSERTS
    assert(this->part_of_speech == PartOfSpeech::Number);
    #endif
    return static_cast<const NumberInflData *>(this->data);
}
const SupineInflData *InflectionRule::_property_supine_data() const {
    #ifdef DO_ASSERTS
    assert(this->part_of_speech == PartOfSpeech::Supine);
    #endif
    return static_cast<const SupineInflData *>(this->data);
}
const ParticipleInflData *InflectionRule::_property_participle_data() const {
    #ifdef DO_ASSERTS
    assert(this->part_of_speech == PartOfSpeech::Participle);
    #endif
    return static_cast<const ParticipleInflData *>(this->data);
}

const char *InflectionRule::_get_cstr_for(int unneeded_extra_data) const // used in template
{
    return this->_ending_cstr;
}


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

const char *DictionaryKey::_get_cstr_for(int key_string_index) const // used in template
{
    return this->stems._get_cstr(key_string_index);
}
//    InterjectionDictData *interjection_data() {
//        assert(this->part_of_speech == PartOfSpeech::Interjection);
//        return static_cast<InterjectionDictData *>(this->data);
//    }
/*

template <typename T>
class ArrayView {
private:
    const T *items;
    const unsigned int item_ct;
public:
    DictionaryKeyView(const T *items, const unsigned int item_ct);
    const int len() const;
    const T *_get_index(int index) const;
    const ArrayView<T> _get_sub_to_end_array(int start) const;
};

template <typename T>
class PtrArrayView {
private:
    const T **items;
    const unsigned int item_ct;
public:
    PtrArrayView(const T **items, const unsigned int item_ct);
    const int len() const;
    const T *_get_index(int index) const;
    const PtrArrayView<T> _get_sub_to_end_array(int start) const;
};
*/
/*
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
*/

/*
InflectionRulePtrView::InflectionRulePtrView(const InflectionRule **rules, const unsigned int rules_ct):
        rules(rules), rules_ct(rules_ct) {};
const int InflectionRulePtrView::len() const {
    return this->rules_ct;
}
const InflectionRule *InflectionRulePtrView::_get_index(int index) const {
    #ifdef DO_ASSERTS
    assert(index >= 0 && index < this->rules_ct);
    #endif
    return this->rules[index];
}
const InflectionRulePtrView InflectionRulePtrView::_get_sub_to_end_array(int start) const {
    #ifdef DO_ASSERTS
    assert(0 <= start && start < this->rules_ct);
    #endif
    return InflectionRulePtrView(&this->rules[start], this->rules_ct - start);
}
*/

DictionaryLemma::DictionaryLemma(
        const int part_of_speech,
        const char *translation_metadata,
        const char *definition, const char *_extra_def,
        const int index, const DictionaryKey *keys, const int keys_ct):
            part_of_speech(part_of_speech),
            translation_metadata(translation_metadata),
            definition(definition),
            _extra_def(_extra_def),
            dictionary_keys_array(keys),
            dictionary_keys_ct(keys_ct),
            index(index) { }

const ArrayView<DictionaryKey> DictionaryLemma::_property_dictionary_keys() const {
    return ArrayView<DictionaryKey>(this->dictionary_keys_array, (unsigned int)this->dictionary_keys_ct);
}
const string DictionaryLemma::_property_definition() const {
    return string(this->definition);
}
const string DictionaryLemma::_property_extra_def() const {
    return string(this->_extra_def);
}
const TranslationMetadata DictionaryLemma::_property_translation_metadata() const {
    return TranslationMetadata(this->translation_metadata);
}


/*
const int DictionaryLemmaListView::len() const {
    return this->lemma_ct;
}
const DictionaryLemma *DictionaryLemmaListView::_get_index(int index) const{
    #ifdef DO_ASSERTS
    assert(index >= 0 && index < this->lemma_ct);
    #endif
    return &this->blocks[index >> MAX_LEMMA_LIST_BLOCK_SIZE_EXP].lemmas[index & (MAX_LEMMA_LIST_BLOCK_SIZE - 1)];;
}*/


BakedDictionaryStemCollection::BakedDictionaryStemCollection(
    const HashTable<DictionaryKey> (&lookup_table)[13][4],
    const BlockedArrayView<DictionaryLemma> lemma_vec):
        lookup_table(lookup_table),
        lemma_vec(lemma_vec) {

};

const HashTable<DictionaryKey> *BakedDictionaryStemCollection::get_hashtable_for(int pos, int stem_key) const
{
    if(stem_key < 1 || stem_key > 4)
        return NULL;
    return &this->lookup_table[pos][stem_key-1];
}



BakedInflectionRuleCollection::BakedInflectionRuleCollection(const HashTable<InflectionRule> ending_rule_map,
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
                                  const InflectionRule *interjection_rule):
        ending_rule_map(ending_rule_map),
        inflection_rules(inflection_rules),
        noun_rules(noun_rules),
        number_rules(number_rules),
        pronoun_rules(pronoun_rules),
        adjective_rules(adjective_rules),
        verb_rules(verb_rules),
        participle_rules(participle_rules),
        adverb_rules(adverb_rules),
        preposition_rule(preposition_rule),
        conjunction_rule(conjunction_rule),
        interjection_rule(interjection_rule) { };
/*
const void BakedDictionaryStemCollection::load (const string &path) const {
    // does nothing, but for convinience of the interfact
}*/





/*
HashTableCell_InflVec::HashTableCell_InflVec(const InflectionRule **rules, const unsigned short ct_rules, const unsigned int hash):
    rules(rules), ct_rules(ct_rules), hash(hash) {};

const HashTableCell_InflVec *HashTable_InflVec::get_cell(const string &s) const {
    unsigned int hash = hash_string(s);
    int index = hash & ((1 << this->len_log2) - 1);
    while(1) {
        const HashTableCell_InflVec *cell = &this->blocks[index >> MAX_HASHTABLE_BLOCK_SIZE_EXP].cells[index & (MAX_HASHTABLE_BLOCK_SIZE - 1)];
        if (cell->ct_rules == 0)
            break;
        if(cell->hash == hash) {
            if(cell->rules[0]->_property_ending() == s)
                return cell;
        }

        index = (index + 1) & ((1 << this->len_log2) - 1);
    }
    return NULL;
}
HashTable_InflVec::HashTable_InflVec(const HashTableBlock_InflVec *blocks, const unsigned long len_log2):
    blocks(blocks), len_log2(len_log2) {};
HashTable_InflVec::HashTable_InflVec(): blocks(NULL), len_log2(0) {};

bool HashTable_InflVec::has(const string &s) const {
    return this->get_cell(s) != NULL;
}
const InflectionRulePtrView HashTable_InflVec::get(const string &s) const {
    const HashTableCell_InflVec *cell = this->get_cell(s);
    if(cell == NULL) {
        return InflectionRulePtrView(NULL, 0);
    }
    return InflectionRulePtrView(cell->rules, (unsigned int)(cell->ct_rules));
}
*/
