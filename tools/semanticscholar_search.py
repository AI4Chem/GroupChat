from semanticscholar import SemanticScholar

sch = SemanticScholar()

def search_papers_in_semantic_scholar(query,year=None,fields_of_study=None,return_num=10):
    '''Search for papers by keyword in semantic scholar

    :param str query: plain-text search query string.
    :param str year: (optional) restrict results to the given range of \
            publication year.
    :param list fields_of_study: (optional) restrict results to given \
            field-of-study list, using the s2FieldsOfStudy paper field.
    :returns: query results.
    '''
    results = sch.search_paper(query,year,fields_of_study,limit=return_num)
    ans = '\n'.join([item.title for item in results])
    return ans

if __name__ == "__main__":
    print(search_papers_in_semantic_scholar("CCC(C1=N[C@@H](C2=CC=CC=C2)[C@@H](C3=CC=CC=C3)O1)(CC)C4=N[C@@H](C5=CC=CC=C5)[C@@H](C6=CC=CC=C6)O4"))
