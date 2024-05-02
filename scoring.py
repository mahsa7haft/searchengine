import indexer
import json
import math
import pickle

# df(t) is the document_frequency of t , the length of posting list of t
# N is the total nuber of documents in the copurs
# inverse document frequency : idf(t) = log(N/df(t))
scores = {}
def calc_tf(freq):
    return 1 + math.log10(freq)

#df = len of posting list
#N = len(corpes)
def calc_idf(n, tf):
    return math.log10(n/tf)
    
def geNumDoc(corpes):
    docids = set()
    for token,posting_list in corpes.items():
        for docid in posting_list.keys():
            if docid != "idf":
                docids.add(docid)
    return len(docids)
    

# change one dictionary to the next
# corpes: token : {docid1: [1,4,3,5,1]}, {docid2: [1,1,1,5]}, ...
# scores: token : {idf: idf score }, {docid1: (idf1, pos_score1)}, {docid2: (idf2, pos_score2)}, ...
def tfid(corpes):
    global scores
    N = geNumDoc(corpes)
    for token, iddict in corpes.items():
        #print(token, '  ')
        #freq is the length of pos_list
        scores[token] = {}
        for id, pos_list in iddict.items():
            freq = len(pos_list)
            temp = set(pos_list)
            #33 is the highest you can get
            p_score = sum(temp) / 33
            scores[token][id] = (calc_tf(freq), p_score)
        scores[token]["idf"] = calc_idf(len(corpes), N)


    with open('scores.pickle','wb') as file:
        pickle.dump(scores, file)

    file.close()
    '''
    with open("scores.json", "w") as outfile:
        json.dump(scores, outfile)
    '''

if __name__ == "__main__":
    with open('output.json') as j:
        corpes = json.load(j)
        tfid(corpes)
    
