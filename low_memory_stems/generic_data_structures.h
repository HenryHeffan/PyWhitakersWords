
#ifndef SRC_EXPOSED_DATA_STRUCTURES_H_
#define SRC_EXPOSED_DATA_STRUCTURES_H_

//#define DO_ASSERTS

#include "assert.h"
#include "generated.h"
#include <string>

using namespace std;

// Compiling really large files is hard on my computer, and doesnt work on my server. Therefore we break the large
// arrays into blocks. Baking them into the executable gets around the memory speed limits on my server, which allows
// the program to load much faster

// =================================================ArrayView==========================================

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

// =================================================PtrArrayView==========================================

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

// ===========================================BlockedArrayItemBlock==========================================

template <typename T>
class BlockedArrayItemBlock {
public:
    const T *items;
    BlockedArrayItemBlock(const T *items): items(items) {};
};

// ==============================================BlockedArrayView==========================================

template <typename T>
class BlockedArrayView {
private:
    const BlockedArrayItemBlock<T> *blocks;
    const int item_ct;
    const int block_size_exp;
    const int block_size_int;

    //remove this method
    BlockedArrayView<T>& operator=(const BlockedArrayView<T>&);
public:
    BlockedArrayView(const BlockedArrayItemBlock<T> *blocks, const int item_ct, const int block_size_exp): blocks(blocks), item_ct(item_ct), block_size_exp(block_size_exp), block_size_int(1 << block_size_exp) {};
    BlockedArrayView(): blocks(NULL), item_ct(0), block_size_exp(0), block_size_int(1 << 0) {};
    const int len() const;
    const T *_get_index(int index) const ;
};

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

// ===============================================HashTableCell===========================================

template <typename T>
class HashTableCell {
public:
    const T **items; // w_.assign(w, w + len);
    const unsigned short item_ct; // if this is 0, then the cell is empty
    const unsigned int hash;

    HashTableCell(const T **items, const unsigned short item_ct, const unsigned int hash);
    //const char matches(unsigned int hash, const string &s, int key_string_index) const;
};

template <typename T>
HashTableCell<T>::HashTableCell(const T **items, const unsigned short item_ct, const unsigned int hash):
    items(items), item_ct(item_ct), hash(hash) {};

// ===============================================HashTableBlock==========================================
/*
template <typename T>
class HashTableBlock {
public:
    const HashTableCell<T> *cells;
    HashTableBlock(const HashTableCell<T> *cells): cells(cells)  {};
};
*/

// ==================================================HashTable==========================================

template <typename T>
class HashTable {
private:
// TODO migrate this to an BlockedArrayView
    const BlockedArrayView< HashTableCell<T> > array; // will assume load factor is not 100 percent, should be >50

    const unsigned long item_ct_log2;
    const int key_string_index; // this is used for checking the actual string on lookup

    const HashTableCell<T> *get_cell(const string &s) const;

    //remove this method
    HashTable<T>& operator=(const HashTable<T>&);
public:
    HashTable(const BlockedArrayView< HashTableCell<T> > array,
                            const unsigned long item_ct_log2,
                            const int key_string_index);
    HashTable();

    bool has(const string &s) const;
    const PtrArrayView<T> get(const string &s) const;
};

template <typename T>
HashTable<T>::HashTable(const BlockedArrayView< HashTableCell<T> > array, const unsigned long item_ct_log2, const int key_string_index):
    array(array), item_ct_log2(item_ct_log2), key_string_index(key_string_index) {};

template <typename T>
HashTable<T>::HashTable(): array(), item_ct_log2(0), key_string_index(0) {};

static const unsigned int hash_string(const string &str)
{
    unsigned int hash = 5381;
    for(int i = 0; i < str.length(); i++)
        hash = ((hash << 5) + hash) + str[i]; /* hash * 33 + c */
    return hash; // this hash should always have a 0 in the first bit
}

template <typename T>
const HashTableCell<T> *HashTable<T>::get_cell(const string &s) const {
    unsigned int hash = hash_string(s);
    int index = hash & ((1 << this->item_ct_log2) - 1);
    while(1) {
        const HashTableCell<T> *cell = this->array._get_index(index);
        if(cell->item_ct == 0)
            break;
        if(cell->hash == hash && cell->items[0]->_get_cstr_for(this->key_string_index) == s) //cell->matches(hash, s, this->key_string_index))
            return cell;
        index = (index + 1) & ((1 << this->item_ct_log2) - 1);
    }
    return NULL;
}

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



#endif // SRC_EXPOSED_DATA_STRUCTURES_H_