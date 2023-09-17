from duckduckgo_search import DDGS

ddgs = DDGS()

def ddg_text_search(text,return_num=2):
    """
    searching webpages related to text using google
    :param text: text for search
    :param return_num: numbers of webpages results to return
    :return: List of search results
    """
    reuslts = list(ddgs.text(text))
    return reuslts[:return_num]

def ddg_keyword_ask(text,return_num=2):
    """
    get useful keyword explanations from google
    :param text: single keyword for search
    :param return_num: numbers of descriptions to return
    :return: List of search results
    """
    reuslts = list(ddgs.answers(text))
    return reuslts[:return_num]

if __name__ == "__main__":
    print(ddg_text_search("CCC(C1=N[C@@H](C2=CC=CC=C2)[C@@H](C3=CC=CC=C3)O1)(CC)C4=N[C@@H](C5=CC=CC=C5)[C@@H](C6=CC=CC=C6)O4",return_num=16))
