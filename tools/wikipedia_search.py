import wikipedia


def wikipedia_summary(topic,return_num=2):
    """
    The function `wikipedia_summary` takes a topic as input and returns a list of summaries from
    Wikipedia related to that topic. The optional parameter `return_num` specifies the number of
    summaries to return, with a default value of 3.
    """

    k = wikipedia.search(topic)
    ans = []
    for i in k:
        if len(ans) >= return_num:
            break
        try :
            summ = wikipedia.summary(i)
            ans.append(summ)
        except:
            pass
    return ans


if __name__ == "__main__":
    print(wikipedia_summary("CCC(C1=N[C@@H](C2=CC=CC=C2)[C@@H](C3=CC=CC=C3)O1)(CC)C4=N[C@@H](C5=CC=CC=C5)[C@@H](C6=CC=CC=C6)O4"))
