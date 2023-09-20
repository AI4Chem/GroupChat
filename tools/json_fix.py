

import re
import json
from half_json.core import JSONFixer

def json_fixer(data: str) -> str:
    # define a mapping of full-width punctuation to half-width punctuation
    punctuation_map = {
        "！": "!",
        "？": "?",
        "。": ".",
        "，": ",",
        "：": ":",
        "；": ";",
        "（": "(",
        "）": ")",
        "【": "[",
        "】": "]",
        "｛": "{",
        "｝": "}",
        "‘": "'",
        "’": "'",
        "“": '"',
        "”": '"',
    }
    # replace each full-width punctuation with its corresponding half-width punctuation
    for full, half in punctuation_map.items():
        data = data.replace(full, half)
    # add / fix missing quotes around keys
    data = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', data)
    # add / fix missing escape characters
    data = data.replace('\\', '\\\\')
    # add / fix missing commas
    data = re.sub(r'(\w)\s*([}\]])', r'\1,\2', data)
    # add / fix missing closing brackets
    stack = [] # a stack to store the opening brackets
    for i, c in enumerate(data):
        if c in '{[': # push the opening bracket to the stack
            stack.append(c)
        elif c in '}]': # pop the matching opening bracket from the stack
            if not stack or stack[-1] != c.replace('}', '{').replace(']', '['):
                return "Invalid input" # return an error if the brackets are not balanced
            stack.pop()
        elif c in '"\'': # toggle the quotation mark flag
            if not stack or stack[-1] not in '"\'':
                stack.append('"')
            else:
                stack.pop()
    # append the missing closing brackets,quotes according to the stack
    while stack:
        top = stack.pop()
        data += top.replace('{', '}').replace('[', ']').replace('"','"').replace("'", "'")
    # remove redundant text out of { }
    data = re.sub(r'^[^{]*|[^}]*$', '', data)
    # add / fix missing quotes around keys
    data = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', data)
    # add / fix missing escape characters
    data = data.replace('\\', '\\\\')
    # add / fix missing commas
    data = re.sub(r'(\w)\s*([}\]])', r'\1,\2', data)
    # add / fix missing closing brackets
    data = re.sub(r'(\w)\s*$', r'\1}', data)
    # replace with double quotes in place of single quotes
    data = data.replace("'", '"')
    # replace with regular double quotes in place of special quote characters like “...”
    data = re.sub(r'[“”]', '"', data)
    # replace with regular spaces in place of special white space characters
    data = re.sub(r'\s', ' ', data)
    # replace with null, true, and false in place of Python constants None, True, and False
    data = re.sub(r'None|True|False', lambda m: m.group(0).lower(), data)
    # clean trailing commas
    data = re.sub(r',\s*([}\]])', r'\1', data)
    # clean comments like /* ... */ and // ...
    data = re.sub(r'/\*.*?\*/|//.*$', '', data, flags=re.DOTALL)
    # clean JSONP notation like callback({ ... })
    data = re.sub(r'\w+\((.*)\)', r'\1', data, flags=re.DOTALL)
    # clean escape characters from an escaped string like {\"stringified\": \"content\"}
    data = re.sub(r'\\(.)', r'\1', data)
    # clean MongoDB data types like NumberLong(2) and ISODate("2022-03-03T05:02:11.111Z")
    data = re.sub(r'NumberLong\((\d+)\)', r'\1', data)
    data = re.sub(r'ISODate\("(.+?)"\)', r'"\1"', data)
    # concatenate strings like "longer text" + "more text on next line"
    data = re.sub(r'"(.+?)"\s*\+\s*"(.+?)"', r'"\1\2"', data)
    # replace any whitespace and newline between } and { with a single newline
    data = re.sub(r'}\s*\n*\s*{', '}\n{', data)
    datalist = data.splitlines()
    data = datalist[0]
    return data
def fixjson(badjson):
    ans0 = json_fixer(badjson)
    ans = JSONFixer().fix(ans0)
    loaded_ans = json.loads(ans.line)
    if loaded_ans is list:
        return json.dumps(loaded_ans[0])
    else:
        return json.dumps(loaded_ans)
    

if __name__ == "__main__":

    print(fixjson('''我觉得你是对的,json返回{"你好'：'测试'''))
    print(fixjson('{"reflection": "The experiment with the parameters [{"base": "CsOPiv", "concentration": "0.1", "ligand": "X-Phos", "solvent": "p-Xylene", "temperature": "105"}] resulted in a yield of 53.63. This indicates that the chosen parameters were effective in producing the desired reaction.", "differential analysis": "In the last two rounds of search, the parameters were selected based on a combination of previous experimental records, pre-training knowledge, and Bayesian optimization suggestions. The analysis of these choices is beyond the scope of the available information."}'))
    print(fixjson('{"param":{"1":"2"}}'))