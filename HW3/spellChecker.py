import sys
import itertools
import operator
import re
import random


MAX_DIFFERENCE_ALLOWED = 3

def distRule(char1, char2):
    if char1 == char2:
        return 0
    elif char2 == "#":
        return 1
    else:
        return 1

def minCal(distM, r1, c1):
    up = distM[r1-1][c1]
    left = distM[r1][c1-1]
    upper_left = distM[r1-1][c1-1]
    
    if r1-1 < 0:
        up = 9999
        upper_left = 9999
    if c1-1 < 0:
        left = 9999
        upper_left = 9999
    
    if up == left and left == 9999:
        return distM[r1][c1]
    else:
        return min(up,left,upper_left)


def distCal(str1,str2):
    distMatrix = [[ 0 for i in range(len(str2))] for j in range(len(str1))]

    for letter_1 in range(len(str1)):
        for letter_2 in range(len(str2)):
            distMatrix[letter_1][letter_2] = distRule(str1[letter_1],str2[letter_2]) + minCal(distMatrix,letter_1,letter_2)
    
    return distMatrix[-1][-1]

def tokenization(file):
    tokenized = re.findall(r"\w+|[\.\?\s\;\,\!\n]",file)
    return tokenized

def findSimilar(str_f,dictionary):
    wordLength = len(str_f)

    if wordLength > 0:
        count = 1
        str_sub1 = "\s" + str_f + ".*"
        str_sub2 = "\s" + str_f[:-count] + ".*"
        raw_result = re.findall(str_sub1, dictionary) + re.findall(str_sub2, dictionary)
        while raw_result == []:
            count += 1
            str_subX = "\s" + str_f[:-count] + ".*"
            raw_result = re.findall(str_subX, dictionary)

        
        for word in range(len(raw_result)):
            raw_result[word] = raw_result[word].strip('\n')
        result_approx = [rx for rx in raw_result if abs(len(rx)-wordLength) <= MAX_DIFFERENCE_ALLOWED]
        result_set = set(result_approx)

        if len(result_set) == 0:
            return str_f
        
        result_final = list(result_set)
        # print("Result final: ")
        # print(result_final)
        dist_arr = []
        for i in range(len(result_final)):
            dist_arr.append(distCal(str_f,result_final[i]))

        # print("dist_arr: ")
        # print(dist_arr)

        min_dist = min(dist_arr)
        min_arr = [di for di in range(len(dist_arr)) if dist_arr[di] == min_dist]
        
        word_list = []
        for i in min_arr:
            word_list.append(result_final[i])
    return word_list[:3]

def suggest(file, dictionary):
    file_lines = []
    for lines in file.splitlines():
        file_lines.append(tokenization(lines))

    #print(file_lines)
    tokenizedFile = tokenization(file)
    corrected_file = []
    corrected_line = ""
    for index, line in enumerate(file_lines):
        for word in line:
            if re.search(r'[\.\?\!\s\;\,]',word) != None:
                corrected_line += word
            elif re.findall("\s" + word + "\s", dictionary) == []: 
                print("Line number: " + str(index+1) + ", need correction: " + word)
                corrected_word = findSimilar(word, dictionary)[0]
                #print("after fix: " + corrected_word)
                corrected_line += corrected_word
            else:
                corrected_line += word
        corrected_line += "\n"
        corrected_file.append(corrected_line)
        corrected_line = ""


    return "".join(corrected_file)



def main():
    dict_sys = open("/usr/share/dict/words", "r")
    dictionary = dict_sys.read()
    # file = open(sys.argv[1], "r")
    # file_check = file.read()

    print(re.findall(r"\b([a-z]*[aeiou][aeiou][aeiou])\b",dictionary))
    print(len(re.findall(r"\b([a-z]+[aeiou][aeiou])\b",dictionary)))
    print(len(re.findall(r"\b([a-z]*[aeiou][aeiou])\b",dictionary)))
    # output = suggest(file_check,dictionary)
    # write_to = open("corrected_" + sys.argv[1], "w")
    # write_to.write(output)

if __name__ == '__main__':
    main()
