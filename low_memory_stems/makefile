
all: python3 python2
	echo "all"

regen: %.generated all
	:

python3: build/fast_dict_keys_wrap_p3.o build/generated.o build/data_structures.o build/baked.h
	g++ -std=c++0x -O3 -shared -o build/_fast_dict_keys.so build/fast_dict_keys_wrap_p3.o build/data_structures.o build/generated.o $(wildcard baked_*.o) && \
	mv build/_fast_dict_keys.so python3/_fast_dict_keys.so && \
	touch python3/__init__.py

python2: build/fast_dict_keys_wrap_p2.o build/generated.o build/data_structures.o build/baked.h
	g++ -std=c++0x -O3 -shared -o build/_fast_dict_keys.so build/fast_dict_keys_wrap_p2.o build/data_structures.o build/generated.o $(wildcard baked_*.o) && \
	mv build/_fast_dict_keys.so python3/_fast_dict_keys.so && \
	touch python2/__init__.py

build/fast_dict_keys_wrap_p3.o: build/fast_dict_keys.i build/data_structures.h
	(cd build && \
	CONFIG_PY3=$$(python3.6-config --includes) && \
	swig -c++ -python -py3 fast_dict_keys.i && \
	mv fast_dict_keys.py ../python3/fast_dict_keys.py && \
	g++ -std=c++0x -O3 -c -fpic fast_dict_keys_wrap.cxx $$CONFIG_PY3 && \
	mv fast_dict_keys_wrap.o fast_dict_keys_wrap_p3.o )

build/fast_dict_keys_wrap_p2.o: build/fast_dict_keys.i build/data_structures.h
	(cd build &&\
	CONFIG_PY2=$$(python3.6-config --includes) && \
	swig -c++ -python fast_dict_keys.i && \
	mv fast_dict_keys.py ../python2/fast_dict_keys.py && \
	g++ -std=c++0x -O3 -c -fpic fast_dict_keys_wrap.cxx $$CONFIG_PY2 && \
	mv fast_dict_keys_wrap.o fast_dict_keys_wrap_p2.o )

build/data_structures.o: build/data_structures.h build/data_structures.cpp
	(cd build && g++ -std=c++0x -O3 -c -fpic data_structures.cpp)

build/data_structures.cpp: data_structures.cpp
	cp data_structures.cpp build/data_structures.cpp

build/data_structures.h: data_structures.h
	cp data_structures.h build/data_structures.h

build/fast_dict_keys.i: fast_dict_keys.i
	cp fast_dict_keys.i build/fast_dict_keys.i

%.generated: gen_reset gen_compile gen_dot_o
	g++ -std=c++0x -O3 -c -fpic generated.cpp

build/generated.o: build/generated.cpp
	g++ -std=c++0x -O3 -c -fpic generated.cpp

gen_reset:
	rm -f build/baked.h $(wildcard build/baked_*.cpp) $(wildcard build/baked_*.o) $(wildcard build/baked_*.h) && \
	python3 generate_code.py

gen_compile:
	(echo "g++ -std=c++0x -O3 -c -fpic generated.cpp" && \
	cd build && \
	g++ -std=c++0x -O3 -c -fpic generated.cpp && \
	for FILE in $(wildcard build/baked_*.cpp) ; do \
	echo "g++ -std=c++0x -O0 -c -fpic baked.h $${FILE#"build/"}" && \
	g++ -std=c++0x -O0 -c -fpic baked.h $${FILE#"build/"} ; \
	done)
