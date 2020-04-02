import enum


class TrickKind(enum.IntEnum):
    TC_Internal = 0
    TC_Flip = 1
    TC_Flip_Flop = 2
    TC_Slur = 3


AnyTricks = [
    (0, TrickKind.TC_Internal, "ae", "e"),
    (0, TrickKind.TC_Internal, "bul", "bol"),
    (0, TrickKind.TC_Internal, "bol", "bul"),
    (0, TrickKind.TC_Internal, "cl", "cul"),
    (0, TrickKind.TC_Internal, "cu", "quu"),
    (0, TrickKind.TC_Internal, "f", "ph"),
    (0, TrickKind.TC_Internal, "ph", "f"),
    (0, TrickKind.TC_Internal, "h", ""),
    (0, TrickKind.TC_Internal, "oe", "e"),
    (0, TrickKind.TC_Internal, "vul", "vol"),
    (0, TrickKind.TC_Internal, "vol", "vul"),
    (0, TrickKind.TC_Internal, "uol", "vul")
]


Mediaeval_Tricks  = [
    #  Harrington/Elliott    1.1.1
    (0, TrickKind.TC_Internal, "col", "caul"),
    #  Harrington/Elliott    1.3
    (0, TrickKind.TC_Internal, "e", "ae"),
    (0, TrickKind.TC_Internal, "o", "u"),
    (0, TrickKind.TC_Internal, "i", "y"),
    #  Harrington/Elliott    1.3.1
    (0, TrickKind.TC_Internal, "ism", "sm"),
    (0, TrickKind.TC_Internal, "isp", "sp"),
    (0, TrickKind.TC_Internal, "ist", "st"),
    (0, TrickKind.TC_Internal, "iz", "z"),
    (0, TrickKind.TC_Internal, "esm", "sm"),
    (0, TrickKind.TC_Internal, "esp", "sp"),
    (0, TrickKind.TC_Internal, "est", "st"),
    (0, TrickKind.TC_Internal, "ez", "z"),
    #  Harrington/Elliott    1.4
    (0, TrickKind.TC_Internal, "di", "z"),
    (0, TrickKind.TC_Internal, "f", "ph"),
    (0, TrickKind.TC_Internal, "is", "ix"),
    (0, TrickKind.TC_Internal, "b", "p"),
    (0, TrickKind.TC_Internal, "d", "t"),
    (0, TrickKind.TC_Internal, "v", "b"),
    (0, TrickKind.TC_Internal, "v", "f"),
    (0, TrickKind.TC_Internal, "v", "f"),
    (0, TrickKind.TC_Internal, "s", "x"),
    #  Harrington/Elliott    1.4.1
    (0, TrickKind.TC_Internal, "ci", "ti"),
    #  Harrington/Elliott    1.4.2
    (0, TrickKind.TC_Internal, "nt", "nct"),
    (0, TrickKind.TC_Internal, "s", "ns"),
    #  Others
    (0, TrickKind.TC_Internal, "ch", "c"),
    (0, TrickKind.TC_Internal, "c", "ch"),
    (0, TrickKind.TC_Internal, "th", "t"),
    (0, TrickKind.TC_Internal, "t", "th")
]


Common_Prefixes = ["dis", "ex", "in", "per", "prae", "pro", "re", "si", "sub", "super", "trans"]


TrickTable = {
    'A': [
     (0, TrickKind.TC_Flip_Flop, "adgn", "agn"),
     (0, TrickKind.TC_Flip_Flop, "adsc", "asc"),
     (0, TrickKind.TC_Flip_Flop, "adsp", "asp"),
     (0, TrickKind.TC_Flip_Flop, "arqui", "arci"),
     (0, TrickKind.TC_Flip_Flop, "arqu", "arcu"),
     (0, TrickKind.TC_Flip, "ae", "e"),
     (0, TrickKind.TC_Flip, "al", "hal"),
     (0, TrickKind.TC_Flip, "am", "ham"),
     (0, TrickKind.TC_Flip, "ar", "har"),
     (0, TrickKind.TC_Flip, "aur", "or")
   ],

   'D': [
     (0, TrickKind.TC_Flip, "dampn", "damn"),
     #  OLD p.54,
     (0, TrickKind.TC_Flip_Flop, "dij", "disj"),
     #  OLD p.55,
     (0, TrickKind.TC_Flip_Flop, "dir", "disr"),
     #  OLD p.54,
     (0, TrickKind.TC_Flip_Flop, "dir", "der"),
     #  OLD p.507/54,
     (0, TrickKind.TC_Flip_Flop, "del", "dil")
   ],

   'E': [
     (0, TrickKind.TC_Flip_Flop, "ecf", "eff"),
     (0, TrickKind.TC_Flip_Flop, "ecs", "exs"),
     (0, TrickKind.TC_Flip_Flop, "es", "ess"),
     (0, TrickKind.TC_Flip_Flop, "ex", "exs"),
     (0, TrickKind.TC_Flip, "eid", "id"),
     (0, TrickKind.TC_Flip, "el", "hel"),
     (0, TrickKind.TC_Flip, "e", "ae")
   ],

   'F': [
     (0, TrickKind.TC_Flip_Flop, "faen", "fen"),
     (0, TrickKind.TC_Flip_Flop, "faen", "foen"),
     (0, TrickKind.TC_Flip_Flop, "fed", "foed"),
     (0, TrickKind.TC_Flip_Flop, "fet", "foet"),
     (0, TrickKind.TC_Flip, "f", "ph")
   ], # Try lead then all

   'G': [
     (0, TrickKind.TC_Flip, "gna", "na")
   ],

   'H': [
     (0, TrickKind.TC_Flip, "har", "ar"),
     (0, TrickKind.TC_Flip, "hal", "al"),
     (0, TrickKind.TC_Flip, "ham", "am"),
     (0, TrickKind.TC_Flip, "hel", "el"),
     (0, TrickKind.TC_Flip, "hol", "ol"),
     (0, TrickKind.TC_Flip, "hum", "um")
   ],

   'K': [
     (0, TrickKind.TC_Flip, "k", "c"),
     (0, TrickKind.TC_Flip, "c", "k")
   ],

   'L': [
     (1, TrickKind.TC_Flip_Flop, "lub", "lib")
   ],

   'M': [
     (1, TrickKind.TC_Flip_Flop, "mani", "manu")
   ],

   'N': [
     (0, TrickKind.TC_Flip, "na", "gna"),
     (0, TrickKind.TC_Flip_Flop, "nihil", "nil")
   ],

   'O': [
     (1, TrickKind.TC_Flip_Flop, "obt", "opt"),
     (1, TrickKind.TC_Flip_Flop, "obs", "ops"),
     (0, TrickKind.TC_Flip, "ol", "hol"),
     (1, TrickKind.TC_Flip, "opp", "op"),
     (0, TrickKind.TC_Flip, "or", "aur")
   ],

   'P': [
     (0, TrickKind.TC_Flip, "ph", "f"),
     (1, TrickKind.TC_Flip_Flop, "pre", "prae")
   ],

   #  From Oxford Latin Dictionary p.1835 "sub-"
   'S': [
     (0, TrickKind.TC_Flip_Flop, "subsc", "susc"),
     (0, TrickKind.TC_Flip_Flop, "subsp", "susp"),
     (0, TrickKind.TC_Flip_Flop, "subc", "susc"),
     (0, TrickKind.TC_Flip_Flop, "succ", "susc"),
     (0, TrickKind.TC_Flip_Flop, "subt", "supt"),
     (0, TrickKind.TC_Flip_Flop, "subt", "sust")
   ],

   'T': [
     (0, TrickKind.TC_Flip_Flop, "transv", "trav")
   ],

   'U': [
     (0, TrickKind.TC_Flip, "ul", "hul"),
     (0, TrickKind.TC_Flip, "uol", "vul")
            #  u is not v for this purpose
   ],

   'Y': [
     (0, TrickKind.TC_Flip, "y", "i")
   ],

   'Z': [
     (0, TrickKind.TC_Flip, "z", "di")
   ]
}


SlurTable = {
   'A': [
     (0, TrickKind.TC_Flip_Flop, "abs", "aps"),
     (0, TrickKind.TC_Flip_Flop, "acq", "adq"),
     (0, TrickKind.TC_Flip_Flop, "ante", "anti"),
     (0, TrickKind.TC_Flip_Flop, "auri", "aure"),
     (0, TrickKind.TC_Flip_Flop, "auri", "auru"),
    (0, TrickKind.TC_Slur, "ad", None)
   ],

   'C': [
     (0, TrickKind.TC_Flip, "circum", "circun"),
     (0, TrickKind.TC_Flip_Flop, "con", "com"),
     (0, TrickKind.TC_Flip, "co", "com"),
     (0, TrickKind.TC_Flip, "co", "con"),
     (0, TrickKind.TC_Flip_Flop, "conl", "coll")
   ],

   'I': [
     (1, TrickKind.TC_Slur, "in", None),
     (1, TrickKind.TC_Flip_Flop, "inb", "imb"),
     (1, TrickKind.TC_Flip_Flop, "inp", "imp")
     # for some forms of eo the stem "i" grates with
     # an "is .. ." ending
   ],

   'N': [
     (0, TrickKind.TC_Flip, "nun", "non")
   ],

   'O': [
     (0, TrickKind.TC_Slur, "ob", None)
   ],

   'Q': [
     (0, TrickKind.TC_Flip_Flop, "quadri", "quadru")
   ],

   'S': [
     #  Latham,
     (0, TrickKind.TC_Flip, "se", "ce"),
     #  From Oxford Latin Dictionary p.1835 "sub-"
    (0, TrickKind.TC_Slur, "sub", None)
   ],
}
