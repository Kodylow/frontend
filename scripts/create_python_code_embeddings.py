import os
from glob import glob

import pandas as pd


def get_function_name(code):
    """
    Extract function name from a line beginning with "def "
    """
    assert code.startswith("def ")
    return code[len("def "): code.index("(")]


def get_until_no_space(all_lines, i) -> str:
    """
    Get all lines until a line outside the function definition is found.
    """
    ret = [all_lines[i]]
    for j in range(i + 1, i + 10000):
        if j < len(all_lines):
            if len(all_lines[j]) == 0 or all_lines[j][0] in [" ", "\t", ")"]:
                ret.append(all_lines[j])
            else:
                break
    return "\n".join(ret)


def get_functions(filepath):
    """
    Get all functions in a Python file.
    """
    whole_code = open(filepath).read().replace("\r", "\n")
    all_lines = whole_code.split("\n")
    for i, l in enumerate(all_lines):
        if l.startswith("def "):
            code = get_until_no_space(all_lines, i)
            function_name = get_function_name(code)
            yield {"code": code, "function_name": function_name, "filepath": filepath}


# get user root directory
root_dir = os.path.expanduser("~")
# note: for this code to work, the openai-python repo must be downloaded and placed in your root directory

# path to code repository directory
code_root = root_dir + "/openai-python"

code_files = [y for x in os.walk(code_root)
              for y in glob(os.path.join(x[0], '*.py'))]
print("Total number of py files:", len(code_files))

if len(code_files) == 0:
    print("Double check that you have downloaded the openai-python repo and set the code_root variable correctly.")

all_funcs = []
for code_file in code_files:
    funcs = list(get_functions(code_file))
    for func in funcs:
        all_funcs.append(func)

print("Total number of functions extracted:", len(all_funcs))
