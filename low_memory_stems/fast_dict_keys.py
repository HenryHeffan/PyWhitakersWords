
def get_lib():
    import sys
    if sys.version_info < (3, 0, 0):
        import low_memory_stems.python2.fast_dict_keys as fd
        return fd
    else:
        import low_memory_stems.python3.fast_dict_keys as fd
        return fd
