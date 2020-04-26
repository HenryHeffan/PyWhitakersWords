# from memory_profiler import profile
# @profile

from time import time
s = time()

def run():
    global s
    from core_files.searcher import get_matches
    PATH="/home/henry/Desktop/PyWhitakersWords/"

    import core_files.whitakers_words as ww
    import core_files.joined_formater_html as jd
    from low_memory_stems.fast_dict_keys import get_lib
    print("imported", time() - s)
    J_LEX, J_FORM = jd.init(PATH) #, load_html_def_dict=True)
    WW_LEX, WW_FORM = ww.init(PATH)
    print("setup", time() - s)

    for word in ["abacus", "abacti", "abbatissa", "abbatizo", "fato", "prougus", "hi", "a", "qui", "quicumque", "quibus", "praecanto", ""] + \
                ("arma virumque cano troiai qui primus ab oris italiam fato prougus et litora livina"
                 " multi quoque passus et multa bello iamque dum".split(" ")):
        print(time() - s)
        s = time()
        J_FORM.display_entry_query(get_matches(J_LEX, word))
        # print(">{}<".format(get_matches(J_LEX, word).unsyncopated_form_groups[0].lemma.extra_def))
        WW_FORM.display_entry_query(get_matches(WW_LEX, word))
    for word in ["qui", "quae", "quod", "quidam"]:
        pass
        # print(word, ":", WW_FORM.dictionary_keyword(get_matches(WW_LEX, word).unsyncopated_form_groups[0].lemma.dictionary_keys[0]))
    # print(WW_FORM.display_entry_query(get_matches(WW_LEX, "qui")))
    # assert(len(get_matches(WW_LEX, "qui").unsyncopated_form_groups) >= 1)

run()

# l = get_lib()
# l.BAKED_WW_INFL_RULES.get_interjection_inflection_rule()
# print("DOIG ADV")
# l.BAKED_WW_INFL_RULES.get_adverb_inflection_rule(0, 0)
# print("DOING PART")
# l.BAKED_WW_INFL_RULES.get_participle_inflection_rule(0, 0,0 ,0 ,0 ,0)
# aliqu   alicu   PRON   _023678 INDEF   *aliquis
#
# aliqu   alicu   PRON   _013678 ADJECT  *aliqui
# qu      cu      PRON   _013478 ADJECT  *aliqui
#
# qu      cu      PRON   _01479 REL      *qui1
# qu      cu      PRON   _01479 INDEF
# qu      cu      PRON   _01479 ADJECT
#
# qu      cu      PRON   _0269 INTERR    *quis1 and *qui1
#
# qu      zzz     PRON   _234689 INDEF   *quis2
#
# qu      cu      PACK   _01479 REL   cumque    *quicumque
#
# qu      cu      PACK   _0 INTERR   cum        *quicum
#
# qu      cu      PACK   _024679 INDEF   piam   *quispiam
#
# qu      cu      PACK   _0149 ADJECT   que     NONE
# qu      cu      PACK   _02469 INDEF   que     *quisque
# qu      zzz     PACK   _7 ADJECT   que        THESE ARE ALL JUST BOOKKEEPING
#
# qu      cu      PACK   _0149 ADJECT   dam     *quidam
# qu      zzz     PACK   _6 INDEF   dam         THESE ARE ALL JUST BOOKKEEPING
# qu      zzz     PACK   _7 ADJECT   dam        THESE ARE ALL JUST BOOKKEEPING
#
# qu      cu      PACK   _01479 ADJECT   libet  *quilibet and quidlibet are together?
# qu      cu      PACK   _0 INDEF   lubet       VARIENT OF ^^^^^
# qu      cu      PACK   _01469 INDEF   libet   * USES SAME ENTRY ABOVE?
# qu      cu      PACK   _0 ADJECT   lubet      * VARIENT OF ^^^^^
#
# qu      cu      PACK   _01479 ADJECT   nam    * quinam
#
# qu      cu      PACK   _02469 INTERR   nam    *quisnam
#
# qu      cu      PACK   _0269 ADJECT   quam    *quisquam
#
# qu      cu      PACK   _0149 ADJECT   vis     *quivis
# qu      zzz     PACK   _6 INDEF   vis         THESE ARE ALL JUST BOOKKEEPING
# qu      zzz     PACK   _7 ADJECT   vis        THESE ARE ALL JUST BOOKKEEPING
