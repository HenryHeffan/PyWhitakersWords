# from memory_profiler import profile
# @profile

def run():
    from core_files.searcher import get_matches
    PATH="/home/henry/Desktop/PyWhitakersWords/"

    import core_files.whitakers_words as ww
    import core_files.joined_formater_html as jd
    J_LEX, J_FORM = jd.init(PATH) #, load_html_def_dict=True)
    WW_LEX, WW_FORM = ww.init(PATH)

    for word in ["abacus", "abacti", "abbatissa", "abbatizo", "fato", "prougus", "hi", "a", "qui", "quicumque", "quibus", "praecanto", ""] + \
                ("arma virumque cano troiai qui primus ab oris italiam fato prougus et litora livina"
                 " multi quoque passus et multa bello iamque dum".split(" ")):
        # J_FORM.display_entry_query(get_matches(J_LEX, word))
        WW_FORM.display_entry_query(get_matches(WW_LEX, word))
    for word in ["qui", "quae", "quod", "quidam"]:
        print(word, ":", WW_FORM.dictionary_keyword(get_matches(WW_LEX, word).unsyncopated_form_groups[0].lemma.dictionary_keys[0]))
    print(WW_FORM.display_entry_query(get_matches(WW_LEX, "abbatizo")))
    assert(len(get_matches(WW_LEX, "abbatizo").unsyncopated_form_groups) >= 1)

run()
