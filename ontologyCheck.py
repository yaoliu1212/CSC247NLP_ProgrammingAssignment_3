import jsontrips
import json
ontology_dict = jsontrips.ontology()
# print(ontology_dict['NONHUMAN-ANIMAL']['parent'])
# print(ontology_dict['PHYS-OBJECT']['parent'])
# print(ontology_dict['GEOGRAPHIC-REGION']['parent'])
# print(round(4/14, 3))

file = open('lex-ont.json')
f = json.load(file)
# print(f['BOTTLE']['lf_parent'])

# from 'DOG' to 'NONHUMAN-ANIMAL'
def getParent(testWord):
    return f[testWord]['lf_parent']

# the depth from initial node to ROOT
# input: depth('PHYS-OBJECT')
# output: 3
def depth(initialNode):
    d = 1
    if initialNode == 'ROOT':
        d = 0
        return d
    if ontology_dict[initialNode]['parent'] != 'ROOT':
        d = depth(ontology_dict[initialNode]['parent'])+1
    return d

# input: 'NONHUMAN-ANIMAL'
# ['NONHUMAN-ANIMAL', 'MAMMAL', 'VERTEBRATE', 'ANIMAL', 'ORGANISM', 'NATURAL-OBJECT', 'PHYS-OBJECT', 'REFERENTIAL-SEM', 'ANY-SEM', 'ROOT']
def getTree(initialNode):
    tree = [initialNode]
    if ontology_dict[initialNode]['parent'] != 'ROOT':
        tree += getTree(ontology_dict[initialNode]['parent'])
    else:
        tree.append('ROOT')
    return tree

# print(getParent('IT'))
# print(getTree('NONHUMAN-ANIMAL'))
# print(getTree('POLICE'))
# print(getTree('PERSON-DEFINED-BY-ACTIVITY'))
# print(getTree('ANIMAL'))
# print(getTree('VEHICLE'))
# print(getTree('MALE-CHILD'))
# input: 'DOG', 'HOUSE'
# ['PHYS-OBJECT', 0, 1, 'REFERENTIAL-SEM', 0, 0, 'REFERENTIAL-SEM', 0, 1, 'ANY-SEM', 0, 0, 'ANY-SEM', 0, 1, 'ROOT', 0, 0, 'ROOT', 0, 1]
def findCommon(word1, word2):
    commonParent = []
    # [CONTAINMENT, LODGING]
    start1 = getParent(word1)
    start2 = getParent(word2)
    # len(start1) = 2, r = 0, 1
    list1 = []
    list2 = []
    for r in range(len(start1)):
        list1.append(getTree(start1[r]))
    for i in range(len(start2)):
        list2.append(getTree(start2[i]))

    if start1 == start2:
        return start1
    if start1 != start2:
        for r in range(len(start1)):
            for i in range(len(list1[r])):
                for x in range(len(start2)):
                    for y in range(len(list2[x])):
                        # print(list1[r][i])
                        # print(list2[x][y])
                        if list1[r][i] == list2[x][y]:
                            commonParent.append(list1[r][i])
                            commonParent.append(r)
                            commonParent.append(x)
                            break
    return commonParent
# print(findCommon('DOG', 'HOUSE'))
def finalCommon(list1):
    length = len(list1)
    removeIndex = []
    finalList = []
    fullIndex = []
    for i in range(1, length, 3):
        for r in range(i+3, length, 3):
            # print(i)
            # print(r)
            fullIndex.append(r)
            if list1[i] == list1[r] and list1[i+1]==list1[r+1]:
                removeIndex.append(r)
    keepIndex = list(set(fullIndex) - set(removeIndex))
    finalList.append(list1[0])
    finalList.append(list1[1])
    finalList.append(list1[2])
    for i in range(len(keepIndex)):
        finalList.append(list1[keepIndex[i]-1])
        finalList.append(list1[keepIndex[i]])
        finalList.append(list1[keepIndex[i]+1])
    return finalList
    # print(fullIndex)
    # print(removeIndex)
    # print(keepIndex)

    # return finalList
# print(finalCommon(['REFERENTIAL-SEM', 0, 0, 'REFERENTIAL-SEM', 0, 1, 'ANY-SEM', 0, 0, 'ANY-SEM', 0, 1, 'ROOT', 0, 0, 'ROOT', 0, 1, 'PHYS-OBJECT', 1, 1, 'REFERENTIAL-SEM', 1, 0, 'REFERENTIAL-SEM', 1, 1, 'ANY-SEM', 1, 0, 'ANY-SEM', 1, 1, 'ROOT', 1, 0, 'ROOT', 1, 1]))
# finalCommon(['PHYS-OBJECT', 0, 1, 'REFERENTIAL-SEM', 0, 0, 'REFERENTIAL-SEM', 0, 1, 'ANY-SEM', 0, 0, 'ANY-SEM', 0, 1, 'ROOT', 0, 0, 'ROOT', 0, 1]
