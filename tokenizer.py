import sys
import re

class InvalidInput(Exception):
    pass

stops = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"}
'''
input     String: Text
output    List:   List of token in that file
Run Time  Linear: o(n) where N is the number of words in that file
          the code read from file line to line, splits line by delimiter,
          checks for alpha numeric words and adds the eligible ones to the list
          of tokens.
'''
def tokenize(string):
    delimiter = re.compile("[.:,?;\s'!`\"']+")
    tokens = []
    line = delimiter.split(string)

    for word in line:
        if word.isalnum():
            tokens.append(word.lower())
    return tokens
    
'''
input     List:   List of token in that file , Dictionary
output    Dict:   Dictionary of tokens with their frequencies
Run Time  Linear: o(n) where N is the number of words in that file
          the code read from file line to line, splits line by delimiter,
          checks for alpha numeric words and adds the eligible ones to the list
          of tokens.
'''            
def computeWordFrequencies(tokenDict, tokens):
    temp = []
    for t in tokens:
        if t not in stops:
            temp.append(t)
    for t in temp:
        if t not in tokenDict:
            tokenDict[t] = 1
        else:
            tokenDict[t] +=1
    return tokenDict

'''
input     Dict:   Dictionary of tokens with their frequencies
output    None
Run Time  nlogn: This function uses the python's inbuilt sorted function (Runtime nlogn)
to sort the dictionary first by keyes(alphabetically) then sorts the and saves the dictionary items in
the form of (value, key) by decreasing order in a list of tuples. Then prints them out.
'''     
def printFrequencies(tokenDict):
    temp = sorted(tokenDict.items())
    frequencies = sorted(temp, reverse=True, key=lambda x: x[1])
    for i,j in frequencies:
        print(f'{i}\t{j}')

if __name__ == '__main__':
    print(stops)
    
