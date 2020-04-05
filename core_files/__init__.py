
import os
import sys
import base64
import enum
import io
import re
import time

import os
import sys
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# import low_memory_stems
import low_memory_stems
from strip_hints import strip_on_import
strip_on_import(__file__, to_empty=False, no_ast=False, no_colon_move=False,
                only_assigns_and_defs=False, py3_also=False)

# PATH = os.path.dirname(os.path.abspath(__file__))
#
# import test
# import searcher
