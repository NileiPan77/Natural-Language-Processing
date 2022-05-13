import sys
import itertools
import operator
import re

def word_count(file, minLength):
    word_dic = {}
    word_list= re.split('[^a-zA-Z]', file) 
    for word in word_list:
        if len(word) > minLength:
            if word in word_dic:
                word_dic[word] += 1
            else:
                word_dic[word] = 1
    
    return word_dic

def extract_firstEndParagraph(file):
    extracted = []
    paraCount = 0
    for line in file: paraCount += 1
    lines = file.split("\n")
    extracted = (lines[0] + lines[-1])
    return extracted

def best_five(minLength, word_dic, extracted):
    list_five = []
    most_occur = dict(sorted(word_dic.items(), key=operator.itemgetter(1),reverse=True))
    for word in extracted.split():
        if word in most_occur and word not in list_five:
            list_five.append(word)
            
    key_list = list(most_occur)
    while(len(list_five) < 5):
        list_five.append(key_list[len(list_five)-1])


    return list_five

def main():

    file = open(sys.argv[1], "r")
    f = file.read()
    minLength = 6
    five_word = best_five(minLength, word_count(f, minLength), extract_firstEndParagraph(f))
    for word in five_word:
        print(word)

    file.close()


if __name__ == '__main__':
    main()

