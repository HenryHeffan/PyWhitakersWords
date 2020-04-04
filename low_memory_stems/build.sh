#!/bin/bash

rm -rf build
mkdir build
rm -f fast_dict_keys.py
rm -f _fast_dict_keys.so

python3 generate_code.py &&
cp data_structures.cpp build/data_structures.cpp &&
cp data_structures.h build/data_structures.h &&
cp fast_dict_keys.i build/fast_dict_keys.i &&
cp generated.cpp build/generated.cpp && rm generated.cpp &&
cp generated.h build/generated.h && rm generated.h && (
cd build &&
swig -c++ -python -py3 fast_dict_keys.i &&
g++ -std=c++1y -O3 -c -fpic fast_dict_keys_wrap.cxx -I/usr/include/python3.6 &&
g++ -std=c++1y -O3 -c -fpic generated.h data_structures.h generated.cpp &&
g++ -std=c++1y -O3 -c -fpic generated.h data_structures.h data_structures.cpp &&
g++ -std=c++11 -O3 -shared -o _fast_dict_keys.so fast_dict_keys_wrap.o data_structures.o generated.o # -g -ggdb
) && cp build/fast_dict_keys.py fast_dict_keys.py && cp build/_fast_dict_keys.so  _fast_dict_keys.so &&
# rm *_wrap.cxx 2>/dev/null

echo "Testing..." &&

(gdb python3.6)<<<"run -c \"import fast_dict_keys;\"
where"

# (cd ..; gdb python3.6)<<<"run -m whitakers_words.py
# where"
