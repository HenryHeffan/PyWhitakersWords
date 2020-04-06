# - *- coding: utf- 8 - *-
try: # this allow both python3 and python2 support
    from typing import Optional, Tuple, Dict, List, Any, Type, Generator, NewType, Union
    from abc import abstractmethod, ABC
    StemGroup = Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]
except ImportError:
    class ABC:
        pass
    def abstractmethod(func):
        return func
    def NewType(n, c):
        return c
import base64

VOWEL_MAP=[('ā', 'a'), ('Ā', 'A'), ('ă', 'a'),             ('á', 'a'),
           ('ē', 'e'), ('Ē', 'E'), ('ĕ', 'e'), ("ë", "e"), ('é', 'e'),
           ('ī', 'i'), ('Ī', 'I'), ('ĭ', 'i'), ('ï', 'i'),
           ('ō', 'o'), ('Ō', 'O'), ('ŏ', 'o'), ("ö", "o"),
           ('ū', 'u'), ('Ū', 'U'), ('ŭ', 'u'), ('ü', 'u'), ('ú', 'u'), ('ù', 'u'),
           ('ȳ', 'y'),             ('ў', 'y'), ('ÿ', 'y'),
           ('^', ''),
           ("œ", "oe"), ("æ", "ae")]

def downgrade_vowels(s: str) -> str:
    for spec, r in VOWEL_MAP:
        # print(spec, r)
        s = s.replace(spec, r)
    return s

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

def strip_spec_chars(s: str) -> str:
    for r, spec in SPEC_CHARS:
        s = s.replace(spec, r)
    return s


def pad_to_len(s: str, l: int) -> str:
    return s + " " * (l - len(s))


def clip_end(s: str, i: int) -> str:
    if i == 0:
        return s
    else:
        return s[:-i]


def joined(stem: str, ending: str) -> str:
    if ending != "":
        return "{}.{}".format(stem, ending)
    else:
        return stem


# for storing and retreiveing utf-8 strings

def store_utf_str(s: str) -> str:
    b64 = base64.b64encode(s.encode('utf-8'))
    return str(b64)[2:-1]
def load_utf_str(s: str) -> str:
    return base64.b64decode(s).decode('utf-8')
