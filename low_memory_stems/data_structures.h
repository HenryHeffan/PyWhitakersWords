
#ifndef SRC_DATA_STRUCTURES_H_
#define SRC_DATA_STRUCTURES_H_

#include "assert.h"
#include <vector>
#include <unordered_map>
#include <string>
#include <fstream>
#include "generated.h"

using namespace std;

class DictionaryLemma;

class TranslationMetadata{
public:
    DictionaryAge age;  //:  = DictionaryAge.from_str(s[0])
    char area;  //: str = s[2]
    char geo;  //: str = s[4]
    DictionaryFrequency frequency;  //:  = DictionaryFrequency.from_str(s[6])
    char source;  //: str = s[8]

    TranslationMetadata() {
        this->age = DictionaryAge::Always;
        this->area = 'X';
        this->geo = 'X';
        this->frequency = DictionaryFrequency::X;
        this->source = 'X';
    }
};
ostream& operator<<(ostream& os, const TranslationMetadata& e);
istream& operator>>(istream& is, TranslationMetadata& e);

class StemGroup{
public:
    string data[4]; // we use 'zzz' to represent a null string
    StemGroup(){
        for(int i = 0; i < 4; i++)
            this->data[i] = "zzz";
    }

    string _get_elem(int i) {
        return this-> data[i];
    }
};
ostream& operator<<(ostream& os, const StemGroup& e);
istream& operator>>(istream& is, StemGroup& e);


class DictionaryKey {
public:
    StemGroup stems;
    PartOfSpeech part_of_speech;
    DictData *data;
    DictionaryLemma *lemma;

    DictionaryKey() {
        this->stems=StemGroup();
        this->part_of_speech=PartOfSpeech::X;
        this->data=NULL;
        this->lemma=NULL;
    }
    DictionaryKey(StemGroup stems, PartOfSpeech part_of_speech, DictData *data) {
        this->stems=stems;
        this->part_of_speech=part_of_speech;
        this->data=data;
        this->lemma=NULL;
    }
    ~DictionaryKey() {
        if (this->data != NULL) {
            delete this->data;
        }
    }

    void inflate_data();
/* PYTHON HELPER
    def make_form(self, infl: Optional['InflectionRule'], default="NULL_FORM") -> str:
    def alternate_form_match(self, o: 'DictionaryKey') -> bool:
*/
    NounDictData *_noun_data() {
        assert(this->part_of_speech == PartOfSpeech::Noun);
        return static_cast<NounDictData *>(this->data);
    }
    PronounDictData *_pronoun_data() {
        assert(this->part_of_speech == PartOfSpeech::Pronoun);
        return static_cast<PronounDictData *>(this->data);
    }
    VerbDictData *_verb_data() {
        assert(this->part_of_speech == PartOfSpeech::Verb);
        return static_cast<VerbDictData *>(this->data);
    }
    AdjectiveDictData *_adjective_data() {
        assert(this->part_of_speech == PartOfSpeech::Adjective);
        return static_cast<AdjectiveDictData *>(this->data);
    }
    InterjectionDictData *_interjection_data() {
        assert(this->part_of_speech == PartOfSpeech::Interjection);
        return static_cast<InterjectionDictData *>(this->data);
    }
    PackonDictData *_packon_data() {
        assert(this->part_of_speech == PartOfSpeech::Packon);
        return static_cast<PackonDictData *>(this->data);
    }
    ConjunctionDictData *_conjunction_data() {
        assert(this->part_of_speech == PartOfSpeech::Conjunction);
        return static_cast<ConjunctionDictData *>(this->data);
    }
//    InterjectionDictData *interjection_data() {
//        assert(this->part_of_speech == PartOfSpeech::Interjection);
//        return static_cast<InterjectionDictData *>(this->data);
//    }
    AdverbDictData *_adverb_data() {
        assert(this->part_of_speech == PartOfSpeech::Adverb);
        return static_cast<AdverbDictData *>(this->data);
    }
    PrepositionDictData *_preposition_data() {
        assert(this->part_of_speech == PartOfSpeech::Preposition);
        return static_cast<PrepositionDictData *>(this->data);
    }
    NumberDictData *_number_data() {
        assert(this->part_of_speech == PartOfSpeech::Number);
        return static_cast<NumberDictData *>(this->data);
    }
};

class DictionaryLemma {
public:
//    def __init__(self,
//                 part_of_speech: PartOfSpeech::
//                 dictionary_keys: List[DictionaryKey],  # the first key is considered the main form usually, but a formatter can choose
//                 translation_metadata: 'TranslationMetadata',
//                 definition: 'str',
//                 html_data: Optional[str],
//                 index: int):
//        # inflection stuff
    PartOfSpeech part_of_speech;
    vector<DictionaryKey*> dictionary_keys;
//        for key in dictionary_keys:
//            assert key.part_of_speech == self.part_of_speech
//            key.lemma = self
    TranslationMetadata translation_metadata;

//        # payload
    string definition;
    string _stored_html_data;
    int index;
    DictionaryLemma(PartOfSpeech part_of_speech, TranslationMetadata translation_metadata, string definition, string html_data, int index) {
        this->part_of_speech=part_of_speech;
        this->dictionary_keys = vector<DictionaryKey*>();
        this->translation_metadata=translation_metadata;
        this->definition=definition;
        this->_stored_html_data=html_data;
        this->rebuild(this->index);
    }
    DictionaryLemma() {
        this->part_of_speech=PartOfSpeech::X;
        this->dictionary_keys = vector<DictionaryKey*>();
        this->translation_metadata=TranslationMetadata();
        this->definition="";
        this->_stored_html_data="";
        this->index=0;
    }
    void rebuild(int index){
        for(int i = 0; i < this->dictionary_keys.size(); i++)
        {
            assert(this->dictionary_keys[i]->part_of_speech == this->part_of_speech);
            this->dictionary_keys[i]->lemma = this;
        }
        this->index = index;
    }
};
/*
class DictionaryKeyListView {
public:
    vector<DictionaryKey *> list;
    DictionaryKeyListView(vector<DictionaryKey *> &list) {
        this->list=list;
    }

    int len() {
        cerr<<"DictionaryKeyListView list len "<<this->list.size()<<endl;
        return this->list.size();
    }
    DictionaryKey *get(int i) {
        cerr<<"DictionaryKeyListView get item "<<i<<" of "<<this->list.size()<<endl;
        return this->list[i];
    }
};
*/
class StringDictKeyMapView {
public:
    unordered_map<string, vector<DictionaryKey *>> *table;
    StringDictKeyMapView(unordered_map<string, vector<DictionaryKey *>> *table) {
        this->table=table;
    }
    ~StringDictKeyMapView(){}

    bool contains(string s) {
        bool res = this->table->find(s) != this->table->end();
//        cerr<<"CHECKING CONTAINS "<<s<<"  "<<res<<" "<<this->table.size()<<endl;
//        for(auto k = this->table.begin(); k != this->table.end(); k++) {
//            cerr<<k->first<<" "<<endl;
//        }
        return res;
    }
    vector<DictionaryKey *> get(string s) {
// bool v = this->contains(s);
//        cerr<<"GETTING "<<s<<", contains?= "<<v<<endl;
        //return DictionaryKeyListView(this->table.find(s)->second);
        return this->table->find(s)->second;
    }
};

class DictionaryStemCollection {
public:
    unordered_map<string, vector<DictionaryKey *>> lookup_table[MAX_PartOfSpeech][4];
    vector<DictionaryLemma *> all_lemmata;
    vector<DictionaryKey *> all_keys;

    DictionaryStemCollection() {
        for(int i = 0; i < MAX_PartOfSpeech; i++)
        {
            for(int j = 0; j < 4; j++) {
                lookup_table[i][j] = unordered_map<string, vector<DictionaryKey *>>();
            }
        }
        all_lemmata = vector<DictionaryLemma *>();
        all_keys = vector<DictionaryKey *>();
    }
    ~DictionaryStemCollection() {
        for(int i = 0; i < all_lemmata.size(); i++)
        {
            delete all_lemmata[i];
        }
        for(int i = 0; i < all_keys.size(); i++)
        {
            delete all_keys[i];
        }
    }

    StringDictKeyMapView get_stem_dict_view_for(int pos, int stem_key)
    {
        return StringDictKeyMapView(&this->lookup_table[pos][stem_key-1]);
    }

    void insert_lemma(DictionaryLemma *lemma, int index);
    friend istream& operator>>(istream& is, DictionaryStemCollection& e);

    void load (string path) {
//        cerr<<"BEGINING LOAD"<<endl;
        ifstream myfile;
        myfile.open (path);
        myfile >> (*this);
    }
//    def __init__(self, path):
//        self.dictionary_keys: List[DictionaryKey] = []
//        self.dictionary_lemmata: List[DictionaryLemma] = []
//        self.stem_map: Dict[Tuple[PartOfSpeech, int], Dict[str, List[DictionaryKey]]] = {}
//    def load(path):
//        pass
//    def stems_for_pos_and_key(pos, stem_key):
//        pass
};

istream& operator>>(istream& is, DictionaryStemCollection& e);

#endif