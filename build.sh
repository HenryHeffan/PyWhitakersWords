#!/bin/bash

shopt -s extglob

# Default values of arguments
SHOULD_BAKE=true

# Loop through arguments and process them
for arg in "$@"
do
    case $arg in
        -s|--skip-bake)
        SHOULD_BAKE=false
        shift # Remove --initialize from processing
        ;;
    esac
done

timestamp() {
  date +"%T"
}

# TODO Update includes path stuff
# TODO add skip bake flag
echo "BUILDING - DOING SETUP"
mkdir -p low_memory_stems/build
mkdir -p low_memory_stems/python3
mkdir -p low_memory_stems/python2
(
  cd low_memory_stems/ &&
  (
  if $SHOULD_BAKE
  then
    rm -f build/baked.h build/baked.a build/baked_*.cpp build/baked_*.o
  fi
  ) &&
  echo "GENERATING CODE" &&
  python3.6 generate_code.py $SHOULD_BAKE &&
  cp data_structures.cpp build/data_structures.cpp &&
  cp data_structures.h build/data_structures.h &&
  cp fast_dict_keys.i build/fast_dict_keys.i &&
  cd build/ &&
  (
  if $SHOULD_BAKE
  then
    echo "BAKED COMPILING" &&
    timestamp &&
    for FILE_NAME in baked_*.cpp
     do
       echo "g++ -std=c++0x -c -fpic $FILE_NAME"
       g++ -std=c++0x -c -fpic $FILE_NAME
    done &&
    ar rc baked.a baked_*.o
    timestamp
  fi
  ) &&
  echo "SHARED COMPILING" &&
  g++ -std=c++0x -O3 -c -fpic generated.cpp &&
  g++ -std=c++0x -O3 -c -fpic data_structures.cpp &&
  (
    (
      echo "MAKING PYTHON 3"
      CONFIG_PY3=$(python3.6-config --includes) &&
      swig -c++ -python -py3 fast_dict_keys.i &&
      g++ -std=c++0x -O3 -c -fpic fast_dict_keys_wrap.cxx $CONFIG_PY3 &&
      g++ -std=c++0x -O3 -shared -o _fast_dict_keys.so fast_dict_keys_wrap.o generated.o data_structures.o baked.a &&
      mv _fast_dict_keys.so ../python3/_fast_dict_keys.so &&
      mv fast_dict_keys.py ../python3/fast_dict_keys.py &&
      touch ../python3/__init__.py
    )
    (
      echo "MAKING PYTHON 2"
      CONFIG_PY2=$(python2.7-config --includes)
      swig -c++ -python fast_dict_keys.i &&
      g++ -std=c++0x -O3 -c -fpic fast_dict_keys_wrap.cxx $CONFIG_PY2 &&
      g++ -std=c++0x -O3 -shared -o _fast_dict_keys.so fast_dict_keys_wrap.o generated.o data_structures.o baked.a &&
      mv _fast_dict_keys.so ../python2/_fast_dict_keys.so &&
      mv fast_dict_keys.py ../python2/fast_dict_keys.py &&
      touch ../python2/__init__.py
    )
  )
)
echo "DONE"

python3 -c "import low_memory_stems.python3.fast_dict_keys as f; stem=\"abac\"; print(f.BAKED_WW.get_hashtable_for(int(f.PartOfSpeech.Noun), 1)[stem] if stem in f.BAKED_WW.get_hashtable_for(int(f.PartOfSpeech.Noun), 1) else \"stem not present\")"
