from typing import Tuple, Optional, Any
import xml.etree.ElementTree as ET
from QuickLatin.entry_and_inflections import *
from QuickLatin.whitakers_words import WW_LEXICON, WW_FORMATER
import json


def strip_spec_chars(s):
    for r, spec in SPEC_CHARS:
        s = s.replace(spec, r)
    return s


def downgrade_vowels(s):
    for spec, r in VOWEL_MAP:
        # print(spec, r)
        s = s.replace(spec, r)
    return s


HTML_PREFIX_TEMP = """<!DOCTYPE html>
    <html>
    <head>
      <title>Dictionary</title>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, height=device-height, initial-scale=1">
      <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
      <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
      <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>
    <style>

    .orth {
        color: #000;
        font-weight:bold;
    }
    .itype {
        color: #000;
    }
    .gen {
        color: #000;
    }
    .pos {
        color: #000;
    }
    .etym {
        color: #304030;
    }
    .sense_block {
    }
    .sense_block_1 {
        padding-left: 10px;
    }
    .sense_block_2 {
        padding-left: 25px;
    }
    .sense_block_3 {
        padding-left: 40px;
    }
    .sense_block_4 {
        padding-left: 50px;
    }
    .sense_block_5 {
        padding-left: 60px;
    }
    .sense_heading {
        color: #000
    }
    .quote {
        color: #a09090;
    }
    .bibl {
        color: #90a090;
    }
    .foreign {
        color: #9090a0
    }
    .entryFree {
        color: #676767;
    }
    .hi_ital{
        color: #000;
    }
    </style>
    </head>
    <body>
    <h1>Lewis and Short</h1>
    <h3>Formatted by Henry Heffan</h3>
    Text provided under a CC BY-SA license by Perseus Digital Library, http://www.perseus.tufts.edu, with funding from The National Endowment for the Humanities.
<br>
Data accessed from https://github.com/PerseusDL/lexica/ [date of access].
<br>
<br>"""

VOWEL_MAP=[('ā', 'a'), ('Ā', 'A'), ('ă', 'a'),             ('á', 'a'),
           ('ē', 'e'), ('Ē', 'E'), ('ĕ', 'e'), ("ë", "e"), ('é', 'e'),
           ('ī', 'i'), ('Ī', 'I'), ('ĭ', 'i'), ('ï', 'i'),
           ('ō', 'o'), ('Ō', 'O'), ('ŏ', 'o'), ("ö", "o"),
           ('ū', 'u'), ('Ū', 'U'), ('ŭ', 'u'), ('ü', 'u'), ('ú', 'u'), ('ù', 'u'),
           ('ȳ', 'y'),             ('ў', 'y'), ('ÿ', 'y'),
           ('^', ''),
           ("œ", "oe"), ("æ", "ae")]


# dlmp = {}
# for dic in WW_LEXICON.dictionary_keys:
#     k = None
#     if dic.part_of_speach == PartOfSpeech.Noun:
#         k = (PartOfSpeech.Noun,
#              tuple(dic.stems),
#              dic.noun_data.declention,
#              dic.noun_data.declention_variant,
#              dic.noun_data.gender)
#     elif dic.part_of_speach == PartOfSpeech.Adjective:
#         k = (PartOfSpeech.Adjective,
#              tuple(dic.stems),
#              dic.adjective_data.declention,
#              dic.adjective_data.declention_variant)
#     if k is not None and (k not in dlmp or dic.translation_metadata.freqency > dlmp[k].translation_metadata.freqency):
#         dlmp[k] = dic


SPEC_CHARS = [
    ('ae', '&oelig;'), ('À', '&Agrave;'), ('Á', '&Aacute;'), ('Â', '&Acirc;'), ('Ã', '&Atilde;'),
    ('Ä', '&Auml;'), ('Å', '&Aring;'), ('à', '&agrave;'), ('á', '&aacute;'), ('â', '&acirc;'),
    ('ã', '&atilde;'), ('ä', '&auml;'), ('å', '&aring;'), ('Æ', '&AElig;'), ('æ', '&aelig;'),
    ('ß', '&szlig;'), ('Ç', '&Ccedil;'), ('ç', '&ccedil;'), ('È', '&Egrave;'), ('É', '&Eacute;'),
    ('Ê', '&Ecirc;'), ('Ë', '&Euml;'), ('è', '&egrave;'), ('é', '&eacute;'), ('ê', '&ecirc;'),
    ('ë', '&euml;'), ('ƒ', '&#131;'), ('Ì', '&Igrave;'), ('Í', '&Iacute;'), ('Î', '&Icirc;'),
    ('Ï', '&Iuml;'), ('ì', '&igrave;'), ('í', '&iacute;'), ('î', '&icirc;'), ('ï', '&iuml;'),
    ('Ñ', '&Ntilde;'), ('ñ', '&ntilde;'), ('Ò', '&Ograve;'), ('Ó', '&Oacute;'), ('Ô', '&Ocirc;'),
    ('Õ', '&Otilde;'), ('Ö', '&Ouml;'), ('ò', '&ograve;'), ('ó', '&oacute;'), ('ô', '&ocirc;'),
    ('õ', '&otilde;'), ('ö', '&ouml;'), ('Ø', '&Oslash;'), ('ø', '&oslash;'), ('Œ', '&#140;'),
    ('œ', '&#156;'), ('Š', '&#138;'), ('š', '&#154;'), ('Ù', '&Ugrave;'), ('Ú', '&Uacute;'),
    ('Û', '&Ucirc;'), ('Ü', '&Uuml;'), ('ù', '&ugrave;'), ('ú', '&uacute;'), ('û', '&ucirc;'),
    ('ü', '&uuml;'), ('µ', '&#181;'), ('×', '&#215;'), ('Ý', '&Yacute;'), ('Ÿ', '&#159;'),
    ('ý', '&yacute;'), ('ÿ', '&yuml;'), ('°', '&#176;'), ('†', '&#134;'), ('‡', '&#135;'),
    ('±', '&#177;'), ('«', '&#171;'), ('»', '&#187;'), ('¿', '&#191;'), ('¡', '&#161;'),
    ('·', '&#183;'), ('•', '&#149;'), ('™', '&#153;'), ('©', '&copy;'), ('®', '&reg;'),
    ('§', '&#167;'), ('¶', '&#182;'), ('*', '&ast;'), ("'", '&lsquo;'), ("'", '&rsquo;'),
    ('˘', '&breve;'), ('¯', '&macr;'), ('¯', '&acutemacr;'), ('£', '&pound;'), ('ā', '&amacr;'),
    ('Ā', '&Amacr;'), ('ē', '&emacr;'), ('Ē', '&Emacr;'), ('ī', '&imacr;'), ('Ī', '&Imacr;'),
    ('ō', '&omacr;'), ('Ō', '&Omacr;'), ('ū', '&umacr;'), ('Ū', '&Umacr;'), ('ȳ', '&ymacr;'),
    ('—', '&mdash;'), ('i', '&itilde;'), ('.', '&cj;'), ('"', '&ldquo'), ('"', '&rdquo')
]
# ('<', '&lt;'), # ('>', '&gt;'), #

# TODO commeneted out 'alis' line 2611
# TODO commeneted out 'quidam' lines 158038 to 158060

NOUN_non_3rd_ENDINGS = [
    ('a',      1, 'ae',    2, '(m.|f.|comm.)',  (1, 1)),
    ('ae',     2, 'ārum',  4, '(m.|f.)',        (1, 1)), # TODO restrict plural
    ('[eĕēé]',   1, '[eĕēé]s',    2, 'f.',      (1, 6)),
    ('[eĕēé]s',  2, 'ae',    2, 'm.',           (1, 7)),
    ('[aā]s',  2, 'ae',    2, 'm.',             (1, 8)),
    # ('[ĭiī]us', 2, 'i',     0, 'm.',         (2, 5)), # TODO should only match filius and proper names
    ('[īĭi]us', 2, '[īiĭ]i', 1, 'm.',          (2, 4)),  # TODO maybe 2 1
    ('[ĭiī]um', 2, '[iĭī]i', 1, 'n.',          (2, 4)),  # TODO maybe 2 2
    ('[ĭiī]um', 2, 'i',      0, 'n.',          (2, 4)),  # TODO maybe 2 2
    ('[uŭ]s',  2, 'i',     1, 'm.',         (2, 1)),
    ('[uŭ]s',  2, 'i',     1, 'f.',         (2, 1)),
    ('[eĕēé]us',    2, '[eĕēé]i',  1, 'm.', (2, 1)),
    ('i',      1, 'ōrum',  4, 'm.',         (2, 1)),  # TODO restrict plural
    ('um',     2, 'i',     1, 'n.',         (2, 2)),
    ('a',      1, 'ōrum',  4, 'n.',         (2, 2)),  # TODO restrict plural
    ('er',     0, 'ri',    1, 'm.',         (2, 3)),
    # TODO We will catch (2, 5) in post process based on "filius" or proper names?
    ('[oŏ]s',  2, 'i',     1, '(m.|f.)',     (2, 6)),
    ('ys',      0, 'ўos',  2 , '(m.|f.|n.)', (2, 7)),
    ('on',     2, 'i',     1, 'n.',          (2, 8)),
    ('[ĭīi]on', 2, 'ii',    1, 'n.',         (2, 8)),
    ('us',     2, 'ūs',    2, '(m.|f.|n.)',  (4, 1)),
    ('[uū]',   2, 'ūs',    2, '(m.|f.|n.)',  (4, 2)),
    ('[eĕēé]s',  2, '[eĕēé][iīï]', 2, '(m.|f.|n.)', (5, 1))
]
NOUN_3rd_ENDINGS = [
    ('[aă]',    0, '[ăāa]tis',      2, (3, 1)),
    ('[ăāa]s',  0, '[ăāa]n?[td]is', 2, (3, 1)),
    ('[ăāa]x',  0, '[ăāa][cg]is',   2, (3, 1)),
    ('en',      0, 'ĭnis',          2, (3, 1)),
    ('ens',     0, 'entis',         2, (3, 1)),
    ('[eĕēé]r', 0, '[eĕēé]ris',     2, (3, 1)),
    ('[eĕēé]s', 0, '[eĕēé][td]is',  2, (3, 1)),
    ('ex',      0, '[ĭīi][cg]is',   2, (3, 1)),
    ('[ĭīi]s',  0, '[ĭīi][td]is',   2, (3, 1)),
    ('[ĭīi]s',  0, '[eĕēé]ris',     2, (3, 1)),
    ('[ĭīi]x',  0, '[ĭīi][cg]is',   2, (3, 1)),
    ('[oŏōö]n', 0, '[oŏōö]nt?is',   2, (3, 1)),
    ('[oŏōö]n', 0, 'ntis',          2, (3, 1)),
    ('[oŏōö]',  0, '[oōŏĭ]nis',     2, (3, 1)),
    ('[oŏōö]r', 0, '[oŏōö]ris',     2, (3, 1)),
    ('[oŏō]s',  0, '[oŏōö][dt]is',  2, (3, 1)),
    ('[oŏōö]x', 0, '[oŏōö][cg]is',  2, (3, 1)),
    ('[uŭ]r',   0, '[uŭ]ris',       2, (3, 1)),
    ('us',      0, '[eĕēé]ris',     2, (3, 1)),
    ('es',      2, '[ĭīi]um',       2, (3, 1)),  # TODO restrict plural 3,4?
    ('es',      2, 'um',            2, (3, 1)),  # TODO restrict plural
    # ('a',       0, '[ĭīi]um',       2, (3, -10000)),  # TODO restrict plural
    ('as',      0, '[ăaā][td]is',   2, (3, 1)),
    ('[eĕēé]s', 0, 'is',            2, (3, 3)),
    ('is',      0, 'is',            2, (3, 3)),
    ('[ăāa]ns', 0, '[ăāa]ntis',     2, (3, 3)),
    ('[uŭ]ns',  0, '[uŭ]ntis',      2, (3, 3)),
    ('[eĕē]ns', 0, '[eĕēé]ntis',    2, (3, 3)),
    ('e',       0, 'is',            2, (3, 4)),
    ('al',      0, '[aăā]lis',      2, (3, 4)),
    ('ar',      0, '[aăā]ris',      2, (3, 4)),
    ('as',      0, 'a[td]os',       2, (3, 7)),
    ('cen',     0, 'c[ĭīi]n[ĭīi]s', 2, (3, 1))
]
ADJ_ENDINGS = [
    # clip off starting from the first space (trimming comma's)
    ('[uŭū]s', 2, 'a,? +um\.?', 1, (1, 1)),
    ('i', 1, 'ae, a', 2, (1, 1)),  # TODO deal with plural?
    ('[eĕēé]rus', 2, '[eĕēé]ra, [eĕēé]rum', 1, (1, 1)),

    # TODO how to distinguish (1, 4)
    ('t[eĕēé]r', 0, 't?[eĕēé]ra, t?[eĕēé]rum', 1, (1, 2)),
    ('f[eĕēé]r', 0, 'f?[eĕēé]ra, f?[eĕēé]rum', 1, (1, 2)),
    ('f[eĕēé]r', 0, 'f?[eĕēé]ra, f?ŏrum', 1, (1, 2)),
    ('g[eĕēé]r', 0, 'g[eĕēé]ra, g[eĕēé]rum', 1, (1, 2)),
    ('er', 0, 'ĕra, ĕrum', 1, (1, 2)),
    ('c[eĕēé]r', 0, 'cra, crum', 1, (1, 2)),
    ('t[eĕēé]r', 0, 'tra, trum', 1, (1, 2)),
    ('f[eĕēé]r', 0, 'fra, frum', 1, (1, 2)),
    ('b[eĕēé]r', 0, 'bra, brum', 1, (1, 2)),
    ('g[eĕēé]r', 0, 'gra, grum', 1, (1, 2)),

    # TODO (1, 3) 'nullus'
    # TODO How tell (1, 4) from (1, 2)

    ('[uŭū]s', 2, 'a,? +ud[. ]', 1, (1, 5)),

    # Greek Adjectives
    ('ē', 1, 'ēs', 2, (2, 1)),

    ('[oŏōö]s', 2, '[oŏōö]n', 2, (2, 6)),  # OR (2, 8)? TODO Check clip amounts
    # ('[oŏōö]s',  'i'),  # TODO bin correctly
    # ('[oŏōö]s', 'a, (um|on)'),

    # ('a', 'ae'),  # TODO this is some greek form probably?

    # 3rd decletion
    # 1 ending: probably most of those below
    ('[aăā]n', 0, '[aăā]nis', 2, (3, 1)),
    ('[aăā]r', 0, '[aăā]ris', 2, (3, 1)),
    ('[aăā]s', 0, '[aăā][rt]is', 2, (3, 1)),
    ('[aăā]x', 0, '[aăā][gc]is', 2, (3, 1)),
    ('[aăā]ns', 0, '[aăā]?ntis', 2, (3, 1)),
    ('ens', 0, 'e?ntis', 2, (3, 1)),
    # ('[eĕēé]s', '[iĭī]s'),
    ('[eĕēé]s', 0, '[iĭī][td]is', 2, (3, 1)),
    ('[eĕēé]s', 0, 'p?[eĕēé]dis', 2, (3, 1)),
    # ('[eĕēé]s', '[iĭī]um'), TODO deal with plural?
    ('[eĕēé]ps', 0, '[iĭī]pis', 2, (3, 1)),
    ('[eĕēé]s', 0, '[eĕēé][td]is', 2, (3, 1)),
    ('ex', 0, 'ĭcis', 2, (3, 1)),
    # ('[iĭī]s', '[iĭī]s'),
    ('[iĭī]s', 0, '[iĭī]dis', 2, (3, 1)),
    ('[iĭī]x', 0, '[iĭī]cis', 2, (3, 1)),
    ('[oŏōö]n', 0, '[oŏōö]ntis', 2, (3, 1)),
    ('[oŏōö]ns', 0, '[oŏōö]ntis', 2, (3, 1)),
    ('[oŏōö]r', 0, '[oŏōö]ris', 2, (3, 1)),
    ('[oŏōö]rs', 0, '-?rtis', 2, (3, 1)),
    ('[oŏōö]s', 0, '[oŏōö]tis', 2, (3, 1)),
    ('[oŏōö]x', 0, '[oŏōö]cis', 2, (3, 1)),
    # ('ur', 'ra, rum'),
    # ('ur', 'ŭris'),
    # ('[uŭū]s', 'a'),
    # ('[uŭū]s', 'um'),
    # ('[uŭū]s', 'i'),
    ('[uŭū]s', 0, 'ĕris', 2, (3, 1)),
    ('[uŭū]x', 0, '[uŭū]cis', 2, (3, 1)),
    # ('[uŭū]s', 'ūs'),

    # ('f[eĕēé]r', 'f[eĕēé]ri'),
    # ('g[eĕēé]r', 'g[eĕēé]ri'),

    ('c[oŏōö]rs', 0, 'c[oŏōö]rdis', 2, (3, 1)),
    ('c[oŏōö]rs', 0, 'dis', 2, (3, 1)),
    ('mens', 0, 'mentis', 2, (3, 1)),

    ('lanx', 0, 'lancis', 2, (3, 1)),
    ('lix', 0, 'līcis', 2, (3, 1)),
    ('plex', 0, 'plĭcis', 2, (3, 1)),
    ('ns', 0, 'tis', 2, (3, 1)),
    ('p[eĕēé]s', 0, 'p[eĕēé]dis', 2, (3, 1)),
    ('par', 0, 'păris', 2, (3, 1)),
    ('p[oŏōö]s', 0, 'pŏtis', 2, (3, 1)),
    ('c[oŏōö]lor', 0, 'cŏlōris', 2, (3, 1)),
    ('gr[eĕēé]x', 0, '(gr)?[eĕēé]gis', 2, (3, 1)),
    ('rs', 0, 'rtis', 2, (3, 1)),
    ('dax', 0, 'dācis', 2, (3, 1)),
    ('bris', 0, 'bris', 2, (3, 1)),

    ('ceps', 0, 'c[iĭī]p([iĭī]t)?is', 2, (3, 1)),
    ('t[iĭī]ceps', 0, 't[iĭī]c[iĭī]p[iĭī]s', 2, (3, 1)),
    ('eps', 0, '[iĭī]p[iĭī]tis', 2, (3, 1)),

    ('c[oŏōö]ps', 0, 'c[oŏōö]p[iĭī]s', 2, (3, 1)),
    ('s[oŏōö]rs', 0, 's[oŏōö]rtis', 2, (3, 1)),
    ('seps', 0, 'sĭpis', 2, (3, 1)),
    ('[oŏōö]ps', 0, '[oŏōö]pis', 2, (3, 1)),
    ('lebs', 0, 'lĭbis', 2, (3, 1)),

    # ('g[eĕēé]n[eĕēé]r', 'is'),
    # ('p[eĕēé]r', 'pĕris'),

    # 2 endings
    ('[iĭī]s', 2, 'e', 1, (3, 2)),

    # 3 endings -er -is -e
    ('er', 0, 'ĕris', 2, (3, 3)),
    ('c[eĕēé]r', 0, 'cris, (cr)?e', 2, (3, 3)),
    ('ūc[eĕēé]r', 0, 'ūcris, ūcre', 2, (3, 3)),
    ('t[eĕēé]r', 0, 'tris, tre', 2, (3, 3)),
    ('āc[eĕēé]r', 0, 'ācris, ācre', 2, (3, 3)),
    ('b[eĕēé]r', 0, 'bris', 2, (3, 3)),
    ('ĕber', 0, 'ēbris, ēbre', 2, (3, 3)),
]

# THIS CODE DOES 2 THINGS
# 1) it extracts all the lewis and short entries, and classefies them according to type ==> LEWIS_SHORT.txt
# 2) it then glues the two dictionaries together ==> LSJDL.txt

import re
ct = 0
gct = 0
class Entry:
    @staticmethod
    def unknown(ent) -> 'Entry':
        m = re.match(r"†? *([^.:;,/_(\-' ]*)(( ?-|/|_)([^.;:,/_(\-' ]*))?( ?-([^.;:,/_(\-' ]*))?",
                     "".join(ent.itertext()))

        nkw = downgrade_vowels((m.group(1) +
                                ("" if m.group(4) is None else m.group(4)) +
                                ("" if m.group(6) is None else m.group(6))).lower())
        # self.default_keyword = nkw  # ent.attrib['key']
        return Entry(ent, PartOfSpeech.X, (nkw, None, None, None), None)

        # children = {child.tag: child for child in ent}
        # print(self.key_word, children)
        # THE GOAL IS TO TAKE THE ENTRY AND OUTPUT ONE PartOfSpeach and Declention/Conjugation Information
        # In other words, we want to make this possible to pass to the Whitakers Words engin
        # self.form = Form(children['form'])
        # self.gramGrp = GrammarGroup(children['gramGrp']) if 'gramGrp' in children else None
        # self.sense = Sense(children['sense']) if 'sense' in children else None
    def __init__(self, ent, pos: PartOfSpeech, stems: StemGroup, data: Any):
        self.id = ent.attrib['id']

        m = re.match(r"†? *([^.:;,/_(\-' ]*)(( ?-|/|_)([^.;:,/_(\-' ]*))?( ?-([^.;:,/_(\-' ]*))?",
                     "".join(ent.itertext()))
        nkw = downgrade_vowels((m.group(1) +
                                ("" if m.group(4) is None else m.group(4)) +
                                ("" if m.group(6) is None else m.group(6))).lower())
        self.key_word = nkw  # ent.attrib['key']
        self.default_keyword = nkw
        # okw = re.match(r"([A-Za-z!]*)\d*", self.key_word.lower().replace("/", "")).group(1)
        # print(self.key_word, okw, nkw)
        # assert okw == nkw or okw in {'in', 'super', 'intercisi', 'inter', 'patri', 'per', 'quadri', 'quantulus', 'quarta', 're', 'umi', 'vacue'}
        self.ent = ent
        self.pos = pos
        self.stems = [downgrade_vowels(s).replace(" -", "").replace("-", "") if s is not None else None for s in stems]
        self.data = data

    def extract_html(self) -> str:
        o = []
        level_ct = [0]
        def recurse(e):
            dived = "span"
            if e.tag == "entryFree":
                o.append("<div class=\"entryFree\" id={}>".format(self.id))
                dived = "div"
            elif e.tag == "orth":
                o.append("<span class=\"orth\">")
            elif e.tag == "pos":
                o.append("<span class=\"pos\">")
            elif e.tag == "itype":
                o.append("<span class=\"itype\">")
            elif e.tag == "sense":
                level = int(e.attrib['level'])
                while len(level_ct) > level:
                    level_ct.pop()
                while len(level_ct) < level:
                    level_ct.append(0)
                level_ct[-1]+=1
                ct = level_ct[-1]

                LEVEL_ENDINGS = {
                    "1": [None, "I.", "II.", "III.", "IV.", "V.", "VI.", "VII.", "VIII.", "IX.", "X.",
                               "XI.", "XII.", "XIII.", "XIV.", "XV.", "XVI.", "XVII.", "XVIII.", "XIX.", "XX.",],
                    "2": [None] + ["{})".format(i) for i in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"],
                    "3": [None] + ["{})".format(i) for i in range(1, 100)],
                    "4": [None] + ["{})".format(i) for i in "abcdefghijklmnopqrstuvwxyz"],
                    "5": [None] + ["-"] * 99,
                }
                assert len(LEVEL_ENDINGS[e.attrib['level']]) > ct, (e.attrib['level'], ct, self.key_word)
                ending = LEVEL_ENDINGS[e.attrib['level']][ct]
                o.append("<div class=\"sense_block_{}\" id={} level={}><span class=\"sense_heading\">{}</span> ".format(e.attrib['level'], e.attrib['id'], e.attrib['level'], ending))
                dived = "div"
            elif e.tag == "hi" and e.attrib['rend'] == "ital":
                o.append("<span class=\"hi_ital\">")
            elif e.tag is not None:
                o.append("<span class=\"{}\">".format(e.tag))
            else:
                dived=None

            if e.text:
                if e.tag == "sense":
                    o.append("<span class=\"hi_ital\">")
                    o.append(e.text)
                    o.append("</span>")
                else:
                    o.append(e.text)
            for child in e:
                recurse(child)

            if dived is not None:
                o.append("</{}>".format(dived))
            if e.tail:
                o.append(e.tail)

        recurse(self.ent)
        # o[-1]=o[-1] # remove a trailing "\n"
        return "".join(o).rstrip("\n")

    def header(self):
        s = "".join([pad_to_len(s, 25) if s is not None else " " * 25 for s in ent.stems])
        payload = ""
        if self.pos == PartOfSpeech.Noun:
            payload = "{} {} {} X".format(self.data[0][0], self.data[0][1], (Gender.from_str(self.data[1]) if self.data[1] is not "" else Gender.X).str_val)
        elif self.pos == PartOfSpeech.Adjective:
            payload = "{} {} POS".format(self.data[0], self.data[1])
        elif self.pos == PartOfSpeech.Verb:
            payload = "{} {} {}".format(self.data[0], self.data[1], self.data[2].upper())
        elif self.pos == PartOfSpeech.Adverb:
            payload = "{}".format(self.data[0].str_val.upper())
        elif self.pos == PartOfSpeech.Preposition:
            payload = "X"
        elif self.pos == PartOfSpeech.Conjunction:
            payload = ""
        elif self.pos == PartOfSpeech.Interjection:
            payload = ""
        elif self.pos == PartOfSpeech.X:
            payload = "POS_X"
        else:
            raise ValueError()

        return pad_to_len(s + pad_to_len(self.pos.str_val, 7) + pad_to_len(payload, 17) + "X X X X X", 110)

    def make_lemma(self) -> DictionaryLemma:
        pos_data = None
        short_def = ""
        if self.pos == PartOfSpeech.Noun:
            pos_data = NounDictData(self.data[0][0], self.data[0][1], Gender.from_str(self.data[1]) if self.data[1] is not "" else Gender.X, NounKind.X)
        elif self.pos == PartOfSpeech.Adjective:
            pos_data = AdjectiveDictData(self.data[0], self.data[1], AdjectiveKind.Positive)
        elif self.pos == PartOfSpeech.Verb:
            pos_data = VerbDictData(self.data[0], self.data[1], self.data[2])
        elif self.pos == PartOfSpeech.Adverb:
            pos_data = AdverbDictData(AdjectiveKind.X)
        elif self.pos == PartOfSpeech.Preposition:
            pos_data = PrepositionDictData(Case.X)
        elif self.pos == PartOfSpeech.Conjunction:
            pos_data = ConjunctionDictData()
        elif self.pos == PartOfSpeech.Interjection:
            pos_data = InterjectionDictData()
        elif self.pos == PartOfSpeech.X:
            pos_data = None
        else:
            raise ValueError()
        return DictionaryLemma(self.pos,
                               [DictionaryKey(self.stems, self.pos, pos_data)],
                               TranslationMetadata("X X X X X"),
                               short_def,
                               self.extract_html(),
                               -1)

    # def key(self):
    #     if self.pos == PartOfSpeech.Noun:
    #         return (PartOfSpeech.Noun, tuple(self.stems), self.data[0][0], self.data[0][1], Gender.from_str(self.data[1]) if self.data[1] is not "" else Gender.X)
    #     elif self.pos == PartOfSpeech.Adjective:
    #         return (PartOfSpeech.Adjective, tuple(self.stems), self.data[0], self.data[1])





def parse_entry(ent) -> Optional['Entry']:
    global ct, gct
    SHOW_DONW = True
    assert ent.attrib['type'] in {'main', 'spur', 'hapax', 'greek', 'gloss', 'foreign'}
    if ent.attrib['type'] in {'gloss', 'hapax'}:
        return None
    # if SHOW_DONW:
    #     print("".join(ent.itertext()))

    gct += 1

    base_word = ent[0].text
    if "(" in base_word:  # base_word.startswith("vul") and base_word.endswith("\)") and (base_word[:-2].endswith("\(vol.") or base_word[:-3].endswith("\(vol.")):
        print(base_word)
        base_word = re.match("(.*) \(.*", base_word).group(1)
    whole_line = "".join(ent.itertext())
    whole_line = re.sub(r" ?\([^)]*\)|\^", "", whole_line)[:200]
    # print(whole_line)

    m = re.match("(\S*(, \S+)? (or|and) )+(\S*,.*)", whole_line)
    if m is not None:  # TODO fix hack
        whole_line = m.group(4)

    PATTERN_NOUN_GEN_INDX = 12
    PATTERN_NOUN = r"†? ?((\S*( -(\S*))?){a}) ?[,.] ({b})(([,.](.+,)?)|( .*,))\W?( ?patr(on)?\.)? ({c})(\W| )"

    for a, al, b, bl, c, k in NOUN_non_3rd_ENDINGS:
        m = re.match(PATTERN_NOUN.format(a=a, b=b, c=c), whole_line)
        if m is not None:
            # TODO + group(4) for stem?
            stem_1 = downgrade_vowels(clip_end(m.group(1), al)).lower().replace(" -", "")
            stem_2 = downgrade_vowels(clip_end(m.group(2) + m.group(5), bl)).lower().replace(" -", "")
            gen = m.group(PATTERN_NOUN_GEN_INDX)[0].upper()
            # l=pad_to_len(, 19) +\
            #       pad_to_len(, bl)), 19).lower() +\
            #       " "* (2*19) + "N      " + str(k[0])+ " " + str(k[1]) +" " +
            # if SHOW_DONW:  print("NOUN", k, stem_1, stem_2, gen)  # print(l)
            # if l in LINES:
            #     LINES.remove(l)
            return Entry(ent, PartOfSpeech.Noun, (stem_1, stem_2, None, None), (k, gen))

    # TODO implement restricted words in whitakers words
    # TODO Nouns 3rd Declention include varient 6 (and 8 & 9)
    for a, al, b, bl, k in NOUN_3rd_ENDINGS:
        NEUTER_REMAP = {1: 2, 3: 4}
        m = re.match(PATTERN_NOUN.format(a=a, b=b, c='(n|f|m|comm?)\W'), whole_line)
        if m is not None:
            if m.group(PATTERN_NOUN_GEN_INDX) == "n." and k[1] in NEUTER_REMAP:
                k = (k[0], NEUTER_REMAP[k[1]])

            # l=pad_to_len(downgrade_vowels(clip_end(m.group(1), al)), 19).lower() +\
            #       pad_to_len(downgrade_vowels(clip_end(m.group(2) + m.group(6), bl)), 19).lower() +\
            #       " "* (2*19) + "N      " + str(k[0])+ " " + str(k[1]) +" " + m.group(PATTERN_NOUN_GEN_INDX)[0].upper()
            # if l in LINES:
            #     LINES.remove(l)
            stem_1 = downgrade_vowels(clip_end(m.group(1), al)).lower().replace(" -", "")
            stem_2 = downgrade_vowels(clip_end(m.group(2) + m.group(5), bl)).lower().replace(" -", "")
            gen = m.group(PATTERN_NOUN_GEN_INDX)[0].upper()
            # if SHOW_DONW:  print("NOUN", k, stem_1, stem_2, gen)
            # if SHOW_DONW: print("NOUN", k) # print(l)
            return Entry(ent, PartOfSpeech.Noun, (stem_1, stem_2, None, None), (k, gen))

    m = re.match(
        r"(\S*)[,.]?( ((ord|num|card|distrib|distr|comp|dim|comm|neutr|less|m|n|f)\.)| plur){0,2} +[aA]dj[., ]",
        whole_line)
    if m is not None:
        if SHOW_DONW: print("Simple ADJ", m.group(1))
        return
    # PATTERN ADJ 1/2r"(\S*){a}[,.] {b}(([,.](.+,)?)|( .*,)) adj."
    PATTERN_ADJ = r"((\S*( -\S*)?){a})[,.]? ({b})( \S*)?(([,.](.+,)?)|( .*,))( ((card|ord|num|distrib|distr|comp|dim|comm|neutr|less|m|n|f)\.)| plur)* [aA]dj\."
    for a, al, b, bl, k in ADJ_ENDINGS:
        m = re.match(PATTERN_ADJ.format(a=a, b=b), whole_line)
        if m is not None:
            # if SHOW_DONW:
            # print()
            # PATTERN_ADJ = r"((\S*( -\S*)?){a})[,.]? ({b})( \S*)?(([,.](.+,)?)|( .*,))( ((card|ord|num|distrib|distr|comp|dim|comm|neutr|less|m|n|f)\.)| plur)* [aA]dj\."
            stem_1 = downgrade_vowels(clip_end(m.group(1), al)).lower().replace(" -", "")
            suffix_stem_2 = (m.group(4).split(",")[0].split(" ")[0])
            group_2 = m.group(2) if m.group(2) else ""
            stem_2 = downgrade_vowels(clip_end(group_2 + suffix_stem_2, bl)).lower().replace(" -", "")
            # gen = m.group(PATTERN_NOUN_GEN_INDX)[0].upper()
            # if len(k) != 3:
            #     print(whole_line[:75])
            # if SHOW_DONW: print("ADJ", stem_1, stem_2, k)
            return Entry(ent, PartOfSpeech.Adjective, (stem_1, stem_2, None, None), k)

    # PATTERN_ADJ_3 = r"(\S*){a}( \([^)]*\))?[,.] {b}(([,.](.+,)?)|( .*,)) adj."
    # for a, b in []:
    #     m = re.match(PATTERN_ADJ_3.format(a=a, b=b), whole_line)
    #     if m is not None:
    #         if SHOW_DONW: print("ADJ Decl 3")
    #         return

    # TODO there is work to do with verb stem extraction
    #      - also need to determine TANS and INTRANS maybe, but most in dict, so maybe not

    m = re.match(r"(\S*( -\S*)?)[oō](, no perf.)?(, [aā]re|, āvi|, ātum){1,3}(, 1)?(, l)?, v\.", whole_line)
    if m is not None:
        # TODO no perfect
        base_stem = m.group(1)
        # print("Verb Conj *1:", base_stem, ":", whole_line[:100])
        return Entry(ent, PartOfSpeech.Verb, (base_stem, base_stem,
                                              base_stem+"āv" if m.group(3) is None else None,
                                              base_stem+"āt" if m.group(3) is None else None), (1, 1, VerbKind.X))

    m = re.match(r"(\S*( -\S*)?)[oō]r(, no perf.)?, ([aā]ri|ātus( sum)?)(, 1)?[,.] v\.", whole_line)
    if m is not None:
        base_stem = m.group(1)
        # print("Verb Conj *1:", base_stem, ":", whole_line[:100])
        return Entry(ent, PartOfSpeech.Verb, (base_stem, base_stem,
                                              None,
                                              base_stem + "āt" if m.group(3) is None else None), (1, 1, VerbKind.Dep))

    m = re.match(r"(\S*( -\S*)?)[oō](, no perf.)?(, [ŭu]i)?, (ēre|ēvi|ētum){1,3}(, 2)?, v\.", whole_line)#|ēvi|ētum [ēō]
    if m is not None:
        base_stem = m.group(1)
        # print("Verb Conj *2:", base_stem, ":", whole_line[:100])
        return Entry(ent, PartOfSpeech.Verb, (base_stem, base_stem,
                                              None if m.group(3) is not None else base_stem+("ēv" if m.group(4) is None else 'ŭi'),
                                              base_stem+"ēt" if m.group(3) is None else None), (2, 1, VerbKind.X))  # TODO otum

    m = re.match(r"(\S*( -\S*)?)[oō]r(, no perf.)?, (ēri|ĭtus( sum)?)(, 2)?[,.] v\.", whole_line)#|ētus( sum)?
    if m is not None:
        base_stem = m.group(1)
        # print("Verb Conj *2:", base_stem, ":", whole_line[:100])
        return Entry.unknown(ent)

    m = re.match(r"(\S*( -\S*)?)[oō](, no perf.)?(, [ŭu]i)?, (\S*ĕre){1,3}(, 3)?, v\.", whole_line)#|ēvi|ētum
    if m is not None:
        base_stem = m.group(1)
        # print("Verb Conj *3:", base_stem, ":", whole_line[:100])
        return Entry.unknown(ent)

    m = re.match(r"(\S*( -\S*)?)[oō]r(, no perf.)?, (ĕri)(, 3)?[,.] v\.", whole_line)#|ĭtus( sum)?
    if m is not None:
        base_stem = m.group(1)
        # print("Verb Conj *3:", base_stem, ":", whole_line[:100])
        return Entry.unknown(ent)

    m = re.match(r"(\S*( -\S*)?)[oō](, no perf.)?(, [ŭu]i)?, (\S*īre|īvi|ĭi, ĭtum, īre){1,3}(, 4)?, v\.", whole_line)#|ēvi|ētum
    if m is not None:
        base_stem = m.group(1)
        # print("Verb Conj *4:", base_stem, ":", whole_line[:100])
        return Entry.unknown(ent)

    m = re.match(r"(\S*( -\S*)?)[oō]r(, no perf.)?, (īri)(, 4)?[,.] v\.", whole_line)#|ĭtus( sum)?
    if m is not None:
        base_stem = m.group(1)
        # print("Verb Conj *4:", base_stem, ":", whole_line[:100])
        return Entry.unknown(ent)
    # rumpo\, rūpi\, ruptum 3
    m = re.match(r"(\S*( -\S*)?)[oō](, no perf.)?(, \S{1,10})?(, \S{1,10})?(, \S{1,10}( (and|or) \S{1,10})?)?, ([1234])[,.]? v[. ]", whole_line)
    if m is not None:
        base_stem = m.group(1)
        # print("Verb Conj *{}:".format(m.group(9)), base_stem, ":", whole_line[:100])
        return Entry.unknown(ent)

    m = re.match(r"(\S*( -\S*)?)[oō]r(, no perf.)?(, \S{1,10})?(, \S{1,10})?(, \S{1,10}( (and|or) \S{1,10})?)?, ([1234])[,.]? v[. ]", whole_line)
    if m is not None:
        base_stem = m.group(1)
        # print("Verb Conj *{}:".format(m.group(9)), base_stem, ":", whole_line[:100])
        return Entry.unknown(ent)


    def make_pattern_verb(a, b, c):  # get arround format limitations
        return r"(\S*( -\S*)?)" + a + r".{0,80}[,.] " + b + r"(([,.](.+,)?)|( .*,)) " + c

    m = re.match(make_pattern_verb("o", "(1|āre|āvi|ātum)", 'v\.'), whole_line)
    if m is not None:
        # if SHOW_DONW:
        print("Verb Conj 1:", whole_line[:100])
        return Entry.unknown(ent)

    m = re.match(make_pattern_verb("o", "āre", ''), whole_line)
    if m is not None:
        # if SHOW_DONW:
        print("Verb Conj 1:", whole_line[:100])
        return Entry.unknown(ent)

    m = re.match(make_pattern_verb("or", "(1|[aā]ri)", '(v\.|dep\.)'), whole_line)
    if m is not None:
        # if SHOW_DONW:
        print("Verb Conj 1 Dep:", whole_line[:100])
        return Entry.unknown(ent)

    m = re.match(make_pattern_verb("o", "(2|ēre)", '(v\.| )'), whole_line)
    if m is not None:
        # if SHOW_DONW:
        print("Verb Conj 2:", whole_line[:100])
        return Entry.unknown(ent)
    m = re.match(make_pattern_verb("or", "ēri", ''), whole_line)
    if m is not None:
        # if SHOW_DONW:
        print("Verb Conj 2 Dep:", whole_line[:100])
        return Entry.unknown(ent)

    m = re.match(make_pattern_verb("o", "(3|ĕre)", 'v.'), whole_line)
    if m is not None:
        # if SHOW_DONW:
        print("Verb Conj 3:", whole_line[:100])
        return Entry.unknown(ent)
    m = re.match(make_pattern_verb("o", "ĕre", ''), whole_line)
    if m is not None:
        # if SHOW_DONW:
        print("Verb Conj 3:", whole_line[:100])
        return Entry.unknown(ent)

    m = re.match(make_pattern_verb("o", "(4|[iī]re)", 'v.'), whole_line)
    if m is not None:
        # if SHOW_DONW:
        print("Verb Conj 4:", whole_line[:100])
        return Entry.unknown(ent)

    m = re.match(r"(\S*), adv\.,? v\. (\d\. )?(\S*),?( +(fin|I|II|III|A|B|C|D|P. a)\.?,?)* *$", whole_line)
    if m is not None:
        # if SHOW_DONW:
        print("Adverb Varient")
        return Entry.unknown(ent)
        # return Entry(ent, PartOfSpeech.Adverb, (m.group(1), None, None, None), (AdjectiveKind.Positive, m.group(3), m.group(5)))

    m = re.match(r"(\S*), adv\.", whole_line)
    if m is not None:
        # if SHOW_DONW:
        # print("Adverb", m.group(1))
        print("ADV", whole_line)
        return Entry(ent, PartOfSpeech.Adverb, (m.group(1), None, None, None), (AdjectiveKind.Positive, None, None))

    m = re.match(r"(\S*), interj.", whole_line)
    if m is not None:
        # if SHOW_DONW:
        # print("Interjection")
        return Entry(ent, PartOfSpeech.Interjection, (m.group(1), None, None, None), tuple())
    m = re.match(r"(\S*), conj\.", whole_line)  # TODO altered "cum" to have conjunction in stead of conj to fix incomaitablity. Undo this later
    if m is not None:
        # if SHOW_DONW:
        # print("Conjunction")
        return Entry(ent, PartOfSpeech.Conjunction, (m.group(1), None, None, None), tuple())

    m = re.match(r"(\S*)(us([,.] a)?([,.] um)?[,.]?|ans([,.] antis)?[,.]?|ens([,.] entis)?[,.]?) +(P|Part)\.",
                 whole_line)
    if m is not None:
        if SHOW_DONW: print("Participle")
        return Entry.unknown(ent)

    m = re.match(r"(\S*) (indecl)\.", whole_line)
    if m is not None:
        # if SHOW_DONW: print("Indelc")
        return Entry(ent, PartOfSpeech.Noun, (m.group(1), None, None, None), ((9, 9), ""))
    m = re.match(r"\S \S (indecl)\.", whole_line)
    if m is not None:
        if SHOW_DONW: print("Indelc")
        return Entry.unknown(ent)

    m = re.match(r"(\S*), v\. (\S*)\.?(( init\.?)|( fin\.?))*\s*$", whole_line)
    if m is not None:
        if SHOW_DONW: print("Simple Variant")
        return Entry.unknown(ent)

    m = re.match(r"(\S*)us, a, um, v\. (\S*)\.?( |$)", whole_line)
    if m is not None:
        if SHOW_DONW: print("Simple Variant 2")
        return Entry.unknown(ent)

    m = re.match(r"(\S*), (\S*),( (\S*),){0,3} etc\., v\.", whole_line)
    if m is not None:
        if SHOW_DONW: print("Simple Variant3")
        return Entry.unknown(ent)

    for a, _, b, _, _ in NOUN_3rd_ENDINGS:
        k = r"(\S*){a}, {b}, v\. (\S*)\.?( |$)".format(a=a, b=b)
        m = re.match(k, whole_line)
        if m is not None:
            if SHOW_DONW: print("Variant Noun")
            return Entry.unknown(ent)
    for a, _, b, _, _, _ in NOUN_non_3rd_ENDINGS:
        k = r"(\S*){a}, {b}, v\. (\S*)\.?( |$)".format(a=a, b=b)
        m = re.match(k, whole_line)
        if m is not None:
            if SHOW_DONW: print("Variant Noun")
            return Entry.unknown(ent)

    m = re.match(r"\S, \S, ", whole_line)
    if m is not None:
        if SHOW_DONW: print("Letter")
        return Entry.unknown(ent)

    print("****",whole_line[:150])

    ct += 1
    gct -= 1
    return Entry.unknown(ent)

def get_ls_ents():
    with open('/home/henry/Desktop/latin_website/QuickLatin/DataFiles/lat.ls.perseus-eng2.xml') as f:
        s = strip_spec_chars(f.read())


    root = ET.fromstring(s)
    text = root[1][0]
    ents = []
    for child in text:
        for ent in child:
            if ent.tag == "entryFree":
                e = parse_entry(ent)
                if e is not None:
                    ents.append(e)
    return ents


# we want to make a new dictionary file format. This will compile the old dictionary into the new one.
# This new dictionary will use 1 line to store entries from Whittickers words
# It will delimate line breaks with \n in the string. These should be replaced before displaying

# First, we will read in all the entry (above)

# then, if for any word a keyword in lewis and short exists once and a keyword

ls_ents = get_ls_ents()

# we want to glue these entries together into a DictionaryLemma
# good_ents = [ent for ent in ls_ents if ent is not None and ent.stems[0] not in {"", "-", None, "_i"}]
# good_ents.sort(key=lambda x: x.stems[0].lower())

# new_dic = list(WW_LEXICON.dictionary_list)
ENT_DIC = {}
for ent in ls_ents:
    k = (re.match(r"([a-zA-Z]*)", ent.key_word).group(1), ent.pos.str_val)
    if k not in ENT_DIC:
        ENT_DIC[k] = []
    ENT_DIC[k].append(ent)

ND = set()
for key in WW_LEXICON.dictionary_keys:
    key.html_data = []
    k = (WW_FORMATER.dictionary_keyword(key), key.part_of_speach.str_val)
    k2 = (WW_FORMATER.dictionary_keyword(key), PartOfSpeech.X.str_val)
    if k in ENT_DIC:
        # assert key.html_data is None, (k, key.html_data)
        key.html_data = [ent.extract_html() for ent in ENT_DIC[k]]
        del ENT_DIC[k]
    elif k2 in ENT_DIC:
        # assert key.html_data is None, (k2, key.lemma.html_data)
        key.html_data = [ent.extract_html() for ent in ENT_DIC[k2]]
        del ENT_DIC[k2]

for lemma in WW_LEXICON.dictionary_lemmata:
    htmls = []
    for key in lemma.dictionary_keys:
        for html in key.html_data:
            if html not in htmls:
                htmls.append(html)
    lemma.html_data = "\n".join(htmls)
    ND.add(lemma)

# Now add all the enmatched pairs. But only do this if it is NOT of type X, because those cant be conjugated
for _, ents in ENT_DIC.items():
    for ent in ents:
        if ent.pos != PartOfSpeech.X:
            ND.add(ent.make_lemma()) # (ent.header(), ent)
        else:
            print(ent.default_keyword)


ND = list(ND)
ND.sort(key=lambda x: x.dictionary_keys[0].stems[0] if x.dictionary_keys[0].stems[0] is not None else "zzz")

with open("/home/henry/Desktop/latin_website/QuickLatin/DataFiles/JOINED.txt", "w", encoding='utf-8') as o:
    json.dump([n.to_dict() for n in ND], o, indent=1)

# with open("/home/henry/Desktop/latin_website/QuickLatin/DataFiles/JOINED.txt", "w", encoding='utf-8') as o:
#     for v in ND:
#         if isinstance(v, tuple):
#             header, ent = v
#             # o.write(ent.key_word+" : ")
#             o.write(pad_to_len(header, 110+6*4))
#             o.write(" &&&--&&& ")
#             o.write("")
#             o.write(" &&&--&&& ")
#             o.write(ent.extract_html().replace("\n", " "))
#             o.write("\n")
#         else:
#             dic = v
#             # o.write(WW_FORMATER.dictionary_keyword(dic)+(" > " if not hasattr(dic, "ent") else "+++"))
#             o.write(pad_to_len(dic.line[:19]       + "      " +
#                                dic.line[19:19*2]   + "      " +
#                                dic.line[19*2:19*3] + "      " +
#                                dic.line[19*3:19*4] + "      " +
#                                dic.line[19*4:110], 110+6*4))
#             o.write(" &&&--&&& ")
#             o.write("\\n".join(dic.definition.lines))
#             o.write(" &&&--&&& ")
#             if hasattr(dic, "ent"):
#                 o.write(dic.ent.extract_html().replace("\n", " "))
#             o.write("\n")
# print(len(new_dic))


def generate_html_dic():
    l = []
    for e in ls_ents:
        l.extend(e.extract_html())
        l.append("\n")
    with open("/home/henry/Desktop/latin_website/l_and_s/lewis_and_short_formated.html", "w") as o:
        o.write(HTML_PREFIX_TEMP)
        o.write("".join(l))
        o.write("""</body></html>""")
# generate_html_dic()
