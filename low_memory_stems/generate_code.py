# this file is run directly, so add the proper path
import os
import sys
PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PATH)

from core_files.entry_and_inflections import *

o_cpp = open(PATH + "/low_memory_stems/generated.cpp", "w")
o_h = open(PATH + "/low_memory_stems/generated.h", "w")

def output_enum(c):
    STR_CPP="""
/*
enum class {class_name} {lb}
    {items}
{rb};
*/
static const string {class_name}Strs[] = {lb}{strs}{rb};
string str_val_{class_name}({class_name} e)
{lb}
    return {class_name}Strs[static_cast<int>(e)];
{rb}
ostream& operator<<(ostream& os, const {class_name}& e)
{lb}
    os << {class_name}Strs[static_cast<int>(e)];
    return os;
{rb}
istream& operator>>(istream& is, {class_name}& e) {lb}
    // read from lhs into rhs 
    string l;
    is >> l;
    //cerr << ">>>"<<l <<"<<<\\n";
    for(int i = 0; i < {items_len}; i++)
    {lb}
        if(l == {class_name}Strs[i])
        {lb}
            e = static_cast<{class_name}>(i);
            return is;
        {rb}
    {rb}
    abort();
{rb}"""
    STR_H = """

enum class {class_name} {lb}
    {items}
{rb};
static const int MAX_{class_name} = {items_len};

//static const string {class_name}Strs[] = {lb}{strs}{rb};
ostream& operator<<(ostream& os, const {class_name}& e);
istream& operator>>(istream& is, {class_name}& e);
string str_val_{class_name}({class_name} e);
"""
    assert len(list(c)) == max([int(e) for e in c]) + 1, (c.__name__, len(list(c)), max([int(e) for e in c]) + 1)
    assert len(set(list(c))) == len(list(c)) # so all the elements unque
    assert min([int(e) for e in c]) == 0 # therefore the elemnts are 0 ... item_len-1

    items_len = len(list(c))
    o_cpp.write(STR_CPP.format(
        class_name= c.__name__,
        items = ", ".join(["{} = {}".format(e.name, int(e)) for e in c]),
        strs=", ".join(['"{}"'.format(c.str_val(i)) for i in range(items_len)]),
        items_len=items_len,
        lb="{",
        rb="}"
    ))
    o_h.write(STR_H.format(
        class_name=c.__name__,
        items=", ".join(["{} = {}".format(e.name, int(e)) for e in c]),
        strs=", ".join(['"{}"'.format(c.str_val(e)) for e in c]),
        items_len=len(list(c)),
        lb="{",
        rb="}"
    ))
    # print("""enum("{class_name}"); {class_name}.str_val=property(lambda x: str_val_{class_name}(x))""".format(class_name=c.__name__))


def output_dict(c):
    STR_CPP="""
/*
class {class_name} {lb}
public:
{items}
    friend ostream& operator<<(ostream& os, const {class_name}& dt);
    friend istream& operator>>(istream& is, {class_name}& dt);
{rb};
*/
ostream& operator<<(ostream& os, const {class_name}& e)
{lb}
    os{read_out};
    return os;
{rb}
istream& operator>>(istream& is, {class_name}& e)
{lb}
    is{read_in};
    return is;
{rb}
bool operator==(const {class_name}& a, const {class_name}& b)
{lb}
    return {comp_code};
{rb}"""
    STR_H = """
class {class_name}: public DictData {lb}
public:
{items}
    friend ostream& operator<<(ostream& os, const {class_name}& dt);
    friend istream& operator>>(istream& is, {class_name}& dt);
{rb};

ostream& operator<<(ostream& os, const {class_name}& e);
istream& operator>>(istream& is, {class_name}& e);
bool operator==(const {class_name}& a, const {class_name}& b);
"""
    MP = {"str": "string"}
    CMPO = {"declention": "(int)", "declention_variant": "(int)", "conjugation": "(int)", "conjugation_variant": "(int)"}
    CMPI = {}  #"declention": "(DeclentionType)", "declention_variant": "(DeclentionSubtype)", "conjugation": "(ConjugationType)", "conjugation_variant": "(ConjugationSubtype)"}

    remap_type = lambda x: x if x not in MP else MP[x]
    vals = [(k, v.__name__) for k,v in c.__init__.__annotations__.items() if k!='return']
    o_cpp.write(STR_CPP.format(
        class_name= c.__name__,
        items = "\n".join(["    {} {};".format(remap_type(type), name) for name, type in vals]),
        read_out="".join(["<<({}e.{})<<' '".format("" if name not in CMPO else CMPO[name], name) for name, _ in vals]),
        read_in="".join([">>({}e.{})".format("" if name not in CMPI else CMPI[name], name) for name, _ in vals]),
        comp_code="&&".join(["1"] + ["a.{name}==b.{name}".format(name=name) for name, _ in vals]),
        lb="{",
        rb="}"
    ))
    o_h.write(STR_H.format(
        class_name=c.__name__,
        items="\n".join(["    {} {};".format(remap_type(type), name) for name, type in vals]),
        read_out="".join(["<<({}e.{})<<' '".format("" if name not in CMPO else CMPO[name], name) for name, _ in vals]),
        read_in="".join([">>({}e.{})".format("" if name not in CMPI else CMPI[name], name) for name, _ in vals]),
        comp_code="&&".join(["a.{name}==b.{name}".format(name=name) for name, _ in vals]),
        lb="{",
        rb="}"
    ))

o_h.write("""

#ifndef SRC_GENERATED_H_
#define SRC_GENERATED_H_

#include <iostream>
#include <string>
using namespace std;

class DictData {};""")

for class_name in ["DeclentionType", "DeclentionSubtype", "ConjugationType", "ConjugationSubtype"]:
    o_h.write("""
typedef int {class_name};
""".format(class_name=class_name,
           lb="{",
           rb="}"
           ))
o_cpp.write("""#include "generated.h"
#include <stdio.h>
""")

output_enum(Person)
output_enum(Number)
output_enum(Tense)
output_enum(Voice)
output_enum(Mood)
output_enum(Gender)
output_enum(Case)
output_enum(PartOfSpeech)
output_enum(VerbKind)
output_enum(NounKind)
output_enum(PronounKind)
output_enum(AdjectiveKind)
output_enum(NumberKind)
output_enum(InflectionFrequency)
output_enum(InflectionAge)
output_enum(DictionaryFrequency)
output_enum(DictionaryAge)
#
output_dict(PronounDictData)
output_dict(NounDictData)
output_dict(VerbDictData)
output_dict(PrepositionDictData)
output_dict(InterjectionDictData)
output_dict(AdjectiveDictData)
output_dict(AdverbDictData)
output_dict(ConjunctionDictData)
output_dict(NumberDictData)
output_dict(PackonDictData)

o_h.write("""
#endif
""")