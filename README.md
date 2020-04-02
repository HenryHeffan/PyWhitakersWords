# PyWhitakersWords
A python implementation of [Whitaker's Words](https://github.com/mk270/whitakers-words), with additional tools, including support for the Lewis & Short Dictionary

Used on my better version of Persius, http://heffan.com/henry/latin/reader/

The program is broken into 3 parts

### High Level Summery
[entry_and_inflections.py](entry_and_inflections.py): has classes for storing dictionary, inflection, addon, and unique entries. These compose a 'Lexicon' More on this class below.

[searcher.py](searcher.py): has functions that take in a lexicon and a string and will find possible "parsings" of that input

[whitakers_words.py](whitakers_words.py): has a class which will load the whitakers words lexicon from DICTLINE, INFLECTS, ADDONS, and UNIQUES. It also includes classes which will format the result from the query in roughly the same style as the original Whitaker's Words

[lewis_and_short_joined_extracter.py](lewis_and_short_joined_extracter.py): takes [lat.ls.perseus-eng2.xml](DataFiles/lat.ls.perseus-eng2.xml), the Lewis and Short Dictionary, and combines in with [DICTLINE.txt](DataFiles/DICTLINE.txt), the Whitaker's Words Dictionary, to produce a file DataFiles/JOINED.txt, which is a json file. This stand alone script must be run before and formater which uses the combined dictionary (namely, [joined_formater_html.py](joined_formater_html.py))

[joined_formater_html.py](joined_formater_html.py): this loads the JOINED.txt file and formats the results of querys in a more readable html format.


### Details of Parser
This primarily consist of the files [entry_and_inflections.py](entry_and_inflections.py) and [searcher.py](searcher.py).

##### entry_and_inflections.py
1. _DictionaryLemma_: This stores one 'meaning' from a dictionary. A DictionaryLemma can have one or more _DictionaryKey_ instances connected to it. This might happen if a verb has one main set of stems, but has a secondary set of stems. For example, amo, amare is usually amavero in the future perfect, but can also be amasso. Each DictionaryKey has up to 4 stems, a part of speach, and some additional data assosiated with that part of speach (e.g. for a Noun, the declention, gender, etc.)

2. _InflectionRule_: This stores one inflection that can be applied to a _DictionaryKey_ to form a word. Each InflectionRule has a 'ending', a part of speach, a stem index, and some additional data assosiated with that part of speach (e.g. for a Noun, the declention, gender, etc.) to determine which kinds of word it applies to.  

   The idea of parsing a word is to try to find a pair of a DictionaryKey and InflectionRule which match and which, when the stem is combined to the ending, produce the desired word. To do this effeciently, we build a lookup table mapping endings to a list of InflectionRules, and we build another lookup table mapping stems to DictionaryKeys. We then try spliting the word at each location, and for each splitting, we try each InflectionRule, and then see if there is any stem that matches it. In theory, this could take a long time, but there is anot a lot over overlap either between endings or between stems, so in practice this runs quite quickly.

3. _TackonEntry_, _SuffixEntry_, _PrefixEntry_: The above is a bit of a lie, because we actually also have to check if there is a tackon (like -que, -ne, -ve, etc.) on the word, or if there is a prefix (prae-, abs-, etc.) or a suffix (like -issime on an adjective to form an adverb). Suffixes are different than Tackons in that Suffixes change the part of speach of the stem they connect to. Usually the prefixed verb is in the dictionary as its own entry, but if it is not, this heps identify more words. Tackons also complete the meaning of "Packons", which are a type of word in the DICTLINE ddictionary which need a tackon to be a complete word. For example (idem, eadem, idem) is put in the genative as euisdem. This is coded in the dictionary as a Packon (i, ea, i) which cojugates like (is, ea, id) but which requires the TACKON -dem to be a fully formed word.

There are some more details, like that this also handles syncopy, does some special regrouping to forms of 'qui', and if no match is found will see if the input can be construed as two words glued together.
