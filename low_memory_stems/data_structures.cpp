#include "data_structures.h"
#include <algorithm>
#include <cctype>
#include <string>
using namespace std;

ostream& operator<<(ostream& os, const StemGroup& e)
{
    for(int i = 0; i < 4; i++)
    {
        os << (e.data[i]=="" ? "xxxxx" : "") << ' ';// == NULL ? "NULL": e.data[i]) ;
    }
    return os;
}
istream& operator>>(istream& is, StemGroup& e) {
    for(int i = 0; i < 4; i++)
    {
        is >> e.data[i];
        if(e.data[i] == "xxxxx")
        {
            e.data[i] = "";
        }
        // if(e.data[i] == "NULL") {
        //     e.data[i] = NULL;
        // }
    }
    return is;
}

ostream& operator<<(ostream& os, const TranslationMetadata& e)
{
    os<<e.age<<' '<<e.area<<' '<<e.geo<<' '<<e.frequency<<' '<<e.source;
    return os;
}
istream& operator>>(istream& is, TranslationMetadata& e) {
    is>>e.age>>e.area>>e.geo>>e.frequency>>e.source;
    return is;
}

void DictionaryKey::inflate_data() {
    if(this->data != NULL) {
        delete this->data;
        this->data = NULL;
    }

    switch(this->part_of_speech) {
        case PartOfSpeech::Verb:
            this->data = new VerbDictData();
            break;
        case PartOfSpeech::Noun:
            this->data = new NounDictData();
            break;
        case PartOfSpeech::Pronoun:
            this->data = new PronounDictData();
            break;
        case PartOfSpeech::Adjective:
            this->data = new AdjectiveDictData();
            break;
        case PartOfSpeech::Adverb:
            this->data = new AdverbDictData();
            break;
        case PartOfSpeech::Conjunction:
            this->data = new ConjunctionDictData();
            break;
        case PartOfSpeech::Preposition:
            this->data = new PrepositionDictData();
            break;
        case PartOfSpeech::Interjection:
            this->data = new InterjectionDictData();
            break;
        case PartOfSpeech::Number:
            this->data = new NumberDictData();
            break;
        case PartOfSpeech::Packon:
            this->data = new PackonDictData();
            break;
    }
}

ostream& operator<<(ostream& os, const DictionaryKey& e)
{
    os<<e.stems<<' '<<e.part_of_speech<<' '<<e.data;
    return os;
}
istream& operator>>(istream& is, DictionaryKey& e) {
    is>>e.stems>>e.part_of_speech;
    e.inflate_data();

    if(e.part_of_speech==PartOfSpeech::Verb) {
        is>>(*static_cast<VerbDictData*>(e.data));
    } else if(e.part_of_speech==PartOfSpeech::Noun) {
        is>>(*static_cast<NounDictData*>(e.data));
    } else if(e.part_of_speech==PartOfSpeech::Pronoun) {
        is>>(*static_cast<PronounDictData*>(e.data));
    } else if(e.part_of_speech==PartOfSpeech::Adjective) {
        is>>(*static_cast<AdjectiveDictData*>(e.data));
    } else if(e.part_of_speech==PartOfSpeech::Adverb) {
        is>>(*static_cast<AdverbDictData*>(e.data));
    } else if(e.part_of_speech==PartOfSpeech::Conjunction) {
        is>>(*static_cast<ConjunctionDictData*>(e.data));
    } else if(e.part_of_speech==PartOfSpeech::Preposition) {
        is>>(*static_cast<PrepositionDictData*>(e.data));
    } else if(e.part_of_speech==PartOfSpeech::Interjection) {
        is>>(*static_cast<InterjectionDictData*>(e.data));
    } else if(e.part_of_speech==PartOfSpeech::Number) {
        is>>(*static_cast<NumberDictData*>(e.data));
    } else if(e.part_of_speech==PartOfSpeech::Packon) {
        is>>(*static_cast<PackonDictData*>(e.data));
    } else {
        cerr << "BAD PART OF SPEACH"<<endl;
        abort();
    }


    /* else if(e.part_of_speech==PartOfSpeech::Participle) {
        ParticipleDictData *n = new ParticipleDictData();
        is>>(*n);
        e.data = n;
    } else if(e.part_of_speech==PartOfSpeech::Supine) {
        SupineDictData *n = new SupineDictData();
        is>>(*n);
        e.data = n;
    }*/
    return is;
}


/*
this->part_of_speech=part_of_speech;
this->translation_metadata=translation_metadata;
this->definition=definition;
this->index
this->dictionary_keys = vector<DictionaryKey*>();

this->definition=definition; // ensure no \n
this->html_data=html_data; // ensure no \n

*/
ostream& operator<<(ostream& os, const DictionaryLemma& e)
{
    os<<e.part_of_speech<<' '<<e.translation_metadata<<' '<<e.index<<' '<<e.dictionary_keys.size();
    for(int i = 0; i < e.dictionary_keys.size(); i++) {
        os<<' '<<e.dictionary_keys[i];
    }
    os<<' '<<e.definition<<'\n'<<e._stored_html_data<<'\n';
    return os;
}
istream& operator>>(istream& is, DictionaryLemma& e)
{
    int len;
    is>>e.part_of_speech>>e.translation_metadata>>e.index>>len;
    for(int i = 0; i < len; i++) {
        DictionaryKey *key = new DictionaryKey();
        is>>(*key);
        e.dictionary_keys.push_back(key);
    }
    getline(is, e.definition);
    getline(is, e._stored_html_data);
    return is;
}

//string subs_in_locs(string stem, vector<int> locs, char replacement):
//    for k in locs:
//        stem = stem[:k] + replacement + stem[k + 1:]
//    return stem

vector<string> alternate_forms_of_stem(string stem) {
    //cerr<<"NEW CALL "<<stem<<"\n";
    for(int i = 0; i < stem.length(); i++)
        stem[i] = tolower(stem[i]);
    //cerr<<"LOWER "<<stem<<"\n";
    vector<int> indx_j = vector<int>();
    vector<int> indx_v = vector<int>();
    for(int i = 0; i < stem.length(); i++) {
        if(stem[i] == 'j')
            indx_j.push_back(i);
        if(stem[i] == 'v' && i!=0)
            indx_v.push_back(i);
    }
    vector<string> re = vector<string>();
    for(unsigned long mask_j = 0; mask_j < (1<<indx_j.size()); mask_j++) {
        for(unsigned long mask_v = 0; mask_v < (1<<indx_v.size()); mask_v++) {
            string nstr = string(stem);
             for(int i = 0; i < indx_j.size(); i++) {
                 if ((mask_j>>i)&1)
                    nstr[indx_j[i]] = 'i';
             }
             for(int i = 0; i < indx_v.size(); i++) {
                 if ((mask_v>>i)&1)
                    nstr[indx_v[i]] = 'u';
             }
             re.push_back(nstr);
        }
    }
    if (stem.size() > 0 && stem[0] == 'u') {
        string alt_form = string(stem);
        alt_form[0] = 'v';
        vector<string> alt_start = alternate_forms_of_stem(alt_form);
        for(int i = 0; i < alt_start.size(); i++)
            re.push_back(alt_start[i]);
    }
    return re;
}

void DictionaryStemCollection::insert_lemma(DictionaryLemma *lemma, int index) {
//def insert_lemma(self, lemma: DictionaryLemma, index: int):
//    # function to generate alternate forms for each stem by applying i,j and u,v substitiutions, and
//    cerr<<"INSERTING LEMMA"<<endl;

    lemma->rebuild(index);
    this->all_lemmata.push_back(lemma);
    for(int key_index = 0; key_index < lemma->dictionary_keys.size(); key_index++) {
        this->all_keys.push_back(lemma->dictionary_keys[key_index]);
        for(int stem_index = 1; stem_index <= 4; stem_index ++)
        {
            string stem_base = lemma->dictionary_keys[key_index]->stems.data[stem_index-1];
//        for , i in zip(key.stems, [1, 2, 3, 4]):
            if (stem_base == "zzz")
                continue;
               vector<string> alt_stems = alternate_forms_of_stem(stem_base);
            for(int i = 0; i < alt_stems.size(); i++) {
                string stem = alt_stems[i];
//                cerr<<"ADDING TO MAP "<<lemma->part_of_speech<<" "<<(stem_index-1)<<endl;
                unordered_map<string, vector<DictionaryKey *>> *mp = &this->lookup_table[static_cast<int>(lemma->part_of_speech)][stem_index-1];
                if ((*mp).find(stem) == (*mp).end()) //not stem in self.stem_map[(lemma.part_of_speach, i)]:
                    (*mp)[stem] = vector<DictionaryKey *>();
                (*mp)[stem].push_back(lemma->dictionary_keys[key_index]);
            }
        }

    }
//    for key in lemma.dictionary_keys:

}
/*
ostream& operator<<(ostream& os, const DictionaryStemCollection& e)
{
    os<<e.part_of_speech<<' '<<e.translation_metadata<<' '<<e.index<<' '<<e.dictionary_keys.size();
    for(int i = 0; i < e.dictionary_keys.size(); i++) {
        os<<' '<<e.dictionary_keys[i];
    }
    os<<' '<<e.definition<<'\n'<<e.html_data<<'\n';
    return os;
}*/
istream& operator>>(istream& is, DictionaryStemCollection& e)
{
//    cerr<<"LOADING!!!!"<<endl;
    while(is.peek() != EOF) {
        DictionaryLemma *lemma = new DictionaryLemma();
        is >> (*lemma);
        e.insert_lemma(lemma, lemma->index);
    }
}
//"/home/henry/Desktop/latin_website/PyWhitakersWords/GeneratedFiles/WW.txt"

