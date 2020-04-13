#!/bin/bash

timestamp() {
  date +"%T"
}

# TODO Update includes path stuff
# TODO add skip bake flag
echo "BUILDING - DOING SETUP"
rm -rf low_memory_stems/build
rm -rf low_memory_stems/python3
rm -rf low_memory_stems/python2
mkdir low_memory_stems/build
mkdir low_memory_stems/python3
mkdir low_memory_stems/python2
(
  cd low_memory_stems/ &&
  echo "GENERATING CODE" &&
  python3.6 generate_code.py &&
  #mv generated.cpp build/generated.cpp &&
  #mv generated.h build/generated.h &&
  #mv baked.cpp build/baked.cpp &&
  #mv baked.h build/baked.h &&
  cp data_structures.cpp build/data_structures.cpp &&
  cp data_structures.h build/data_structures.h &&
  cp fast_dict_keys.i build/fast_dict_keys.i &&
  cd build/ &&
  echo "BAKED COMPILING" &&
  timestamp &&
  # g++ -std=c++0x -c -fpic generated.h data_structures.h baked.h &&
  for FILE_NAME in baked_*.cpp
   do
     echo "g++ -std=c++0x -c -fpic $FILE_NAME"
     g++ -std=c++0x -c -fpic $FILE_NAME
  done &&
  timestamp &&
  echo "SHARED COMPILING" &&
  g++ -std=c++0x -O3 -c -fpic generated.cpp &&
  g++ -std=c++0x -O3 -c -fpic data_structures.cpp &&
  (
    (
      echo "MAKING PYTHON 3"
      CONFIG_PY3=$(python3.6-config --includes) &&
      swig -c++ -python -py3 fast_dict_keys.i &&
      g++ -std=c++0x -O3 -c -fpic fast_dict_keys_wrap.cxx $CONFIG_PY3 &&
      g++ -std=c++0x -O3 -shared -o _fast_dict_keys.so fast_dict_keys_wrap.o generated.o data_structures.o baked_*.o &&
      mv _fast_dict_keys.so ../python3/_fast_dict_keys.so &&
      mv fast_dict_keys.py ../python3/fast_dict_keys.py &&
      touch ../python3/__init__.py
    )
    (
      echo "MAKING PYTHON 2"
      CONFIG_PY2=$(python2.7-config --includes)
      swig -c++ -python fast_dict_keys.i &&
      g++ -std=c++0x -O3 -c -fpic fast_dict_keys_wrap.cxx $CONFIG_PY2 &&
      g++ -std=c++0x -O3 -shared -o _fast_dict_keys.so fast_dict_keys_wrap.o generated.o data_structures.o baked_*.o &&
      mv _fast_dict_keys.so ../python2/_fast_dict_keys.so &&
      mv fast_dict_keys.py ../python2/fast_dict_keys.py &&
      touch ../python2/__init__.py
    )
  )
)
echo "DONE"

python3 -c "import low_memory_stems.python3.fast_dict_keys as f; stem=\"abac\"; print(f.BAKED_WW.get_hashtable_for(int(f.PartOfSpeech.Noun), 1)[stem] if stem in f.BAKED_WW.get_hashtable_for(int(f.PartOfSpeech.Noun), 1) else \"stem not present\")"
