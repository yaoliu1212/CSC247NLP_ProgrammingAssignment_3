# import ontologyCheck
# recency?? from the beginning or end
# how to check pro refer to an event
# "they" used to refer events? or only "it"
# it is hard to learn -- it refers to learn

# possible bug: when delete input 1, only left with first sentence!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# preprocessing =====================================================================================================================
import ontologyCheck
import argparse


# with open('input4') as f:
#     lines = f.readlines()

# access: file2discourse(lines)[0][1]
# return: (VERB "ate" ONT::EAT V5)
def file2discourse(readlinesList):
    discourse = []
    for i in readlinesList:
        if i[0] == '"':
            list = []
        elif i[0] == "(":
            list.append(i)
        else:
            discourse.append(list)
    discourse.append(list)
    return discourse
# print(file2discourse(lines))


# input: (VERB "ate" ONT::EAT V5)
# output: {'spec': 'VERB', 'word': 'ate', 'type': 'ONT::EAT', 'DE': 'V5'}
def simpleEntityDictionary(discourseList):
    entityDic = {"spec": "", "word": "", "type": "", "DE": ""}
    # print(type(discourseList)) =============== test for bug!!!!!!!!!!!!!!!!!!!!
    list = discourseList.split()
    # fill the dictionary
    spec = list[0].replace("(", "")
    entityDic["spec"] = spec

    DE = list[len(list)-1].replace(")", "")
    entityDic["DE"] = DE

    type = list[len(list)-2]
    # type = list[len(list)-2].replace("ONT::", "")
    entityDic["type"] = type

    list.pop(0)
    list.pop(len(list)-1)
    list.pop(len(list)-1)
    word = list[0].replace('"', '')
    for i in range(1, len(list)):
        word = word+" "+list[i].replace('"', '')
    entityDic["word"] = word

    return entityDic

def conjoinedEntityDictionary():
    entityDic = {"specGeneral": "", "wordGeneral": "", "typeGeneral": "", "DEGeneral": "", "spec1": "", "word1": "", "type1": "", "DE1": "", "spec2": "", "word2": "", "type2": "", "DE2": ""}

# call: storeDictBack(lines) --- same with file2discourse
# return data
# print(data[0]) -------- first discourse
# print(data[0][1]) --------second entity in first discourse
# print(data[0][2]["spec"]) ------ the "spec" in second entity
def storeDictBack(readlinesList):
    data = file2discourse(readlinesList)
    for i in range(len(data)):
        for j in range(len(data[i])):
            data[i][j] = simpleEntityDictionary(data[i][j])
    return data

# Co-reference Resolution - Refer to Noun =========================================================================================================================
# build a list to store all possible referents before current entity
# the last element in list "possibleNounEntities" is the tested word itself
# indexi, indexj constraint: cannot be verb !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# return: list(all possible noun entities + self), signal (boolean)
def preprocessing(lines, indexi, indexj):
    dataInDict = storeDictBack(lines)
    possibleEntitiesBefore = []
    for i in range(indexi):
        for j in range(len(dataInDict[i])):
            if not dataInDict[i][j]["spec"] == "VERB":
                possibleEntitiesBefore.append(dataInDict[i][j])
            else:
                possibleEntitiesBefore.append("VERB")
        possibleEntitiesBefore.append("sentenceEnd")
    for x in range(indexj+1):
        if not dataInDict[indexi][x]["spec"] == "VERB":
            possibleEntitiesBefore.append(dataInDict[indexi][x])
        else:
            possibleEntitiesBefore.append("VERB")
    if indexj == (len(dataInDict[indexi])-1):
        possibleEntitiesBefore.append("sentenceEnd")
    return possibleEntitiesBefore

def possiblenNounEntities(lines, indexi, indexj, signal = False):
    possibleEntitiesBefore = preprocessing(lines, indexi, indexj)
    if possibleEntitiesBefore[-1] == "sentenceEnd":
        possibleEntitiesBefore.pop(-1)
    # print("1111111111", possibleEntitiesBefore)
    # if the number of all possible entities is less than 3
    # cannot do reflexivity check
    # return list, keep signal = False (still need more check)
    if len(possibleEntitiesBefore) < 3:
        # remove all helper elements: "VERB" & "sentenceEnd"
        while "VERB" in possibleEntitiesBefore:
            possibleEntitiesBefore.remove("VERB")
        while "sentenceEnd" in possibleEntitiesBefore:
            possibleEntitiesBefore.remove("sentenceEnd")
        return possibleEntitiesBefore, signal
    # check reflexivity constraint
    # N([-3]) V([-2]) N([-1])
    # if the last second element = 'VERB', check the tested word ends with "self/selves"
    if possibleEntitiesBefore[-2] == "VERB":
        if not (("self" in possibleEntitiesBefore[-1]["word"]) or ("selves" in possibleEntitiesBefore[-1]["word"])):
            possibleEntitiesBefore.pop(-3)
        else:
            # print("CATCH")
            signal = True
            temp = possibleEntitiesBefore[-3]
            possibleEntitiesBefore.clear()
            possibleEntitiesBefore.append(temp)
    # Centering Constraints

    # remove all helper elements: "VERB" & "sentenceEnd"
    while "VERB" in possibleEntitiesBefore:
        possibleEntitiesBefore.remove("VERB")
    while "sentenceEnd" in possibleEntitiesBefore:
        possibleEntitiesBefore.remove("sentenceEnd")
    # return
    return possibleEntitiesBefore, signal
# print(possiblenNounEntities(lines, 2, 1))
# def centeringConstraint(lines, indexi, indexj):
#     list = preprocessing(lines, indexi, indexj)
#     # print(list)
# centeringConstraint(lines, 1, 2)

def semanticFilter(possibleNounEntities, signal = False):
    # move the dictionary of the last element(tested word) into single variable from list
    testedWord = possibleNounEntities.pop(-1)
    # print("initial list:  ", possibleNounEntities)

    # Exact Match
    # special case 1: We/us
    # condition 1: [] True -> no referent before
    # condition 2: [mutiple] True -> return the recent one as referent
    if testedWord["word"].lower() == "we" or testedWord["word"].lower() == "us":
        signal = True
        for i in reversed(possibleNounEntities):
            if (i["word"].lower() == "we" or i["word"].lower() == "us"):
                temp = i
                possibleNounEntities.clear()
                possibleNounEntities.append(temp)
                signal = True
                return possibleNounEntities, signal
        possibleNounEntities.clear()
        return possibleNounEntities, signal
    # special case 2: I/me
    elif testedWord["word"].lower() == "i" or testedWord["word"].lower() == "me":
        signal = True
        for i in reversed(possibleNounEntities):
            if i["word"].lower() == "i" or i["word"].lower() == "me":
                temp = i
                possibleNounEntities.clear()
                possibleNounEntities.append(temp)
                signal = True
                return possibleNounEntities, signal
        possibleNounEntities.clear()
        return possibleNounEntities, signal
    else:
        tempList = []
        for i in possibleNounEntities:
            if not ((i["word"].lower() == "i") or (i["word"].lower() == "me") or (i["word"].lower() == "we") or (i["word"].lower() == "us")):
                tempList.append(i)
        possibleNounEntities = tempList

    # General case: compare "word" directly
    # choose the most recent matching as referent
    for i in reversed(possibleNounEntities):
        # general matching condition
        if i["word"] == testedWord["word"]:
            temp = i
            possibleNounEntities.clear()
            possibleNounEntities.append(temp)
            signal = True
            return possibleNounEntities, signal

    # Filter by Number(singular or plural)
    # False = singular
    # True = plural (contains "SET" in ["spec"])
    numberTestWord = ("SET" in testedWord["spec"])
    newPossibleNounEntitiesSemantic = []
    for i in possibleNounEntities:
        if ("SET" in i["spec"]) == numberTestWord:
            newPossibleNounEntitiesSemantic.append(i)
    possibleNounEntities = newPossibleNounEntitiesSemantic

    # Filtered by female/male/animal
    # 1.  when tested word shows gender, remove different gender, keep only same/no-gender
    maleTestedWord = ("ONT::MALE-PERSON" == testedWord["type"])
    femaleTestedWord = ("ONT::FEMALE-PERSON" == testedWord["type"])
    tempList1 = []
    tempList2 = []
    tempList3 = []
    # remove different gender, keep same gender/no-gender
    if maleTestedWord:
        for i in possibleNounEntities:
            if not ("ONT::FEMALE-PERSON" == i["type"]):
                tempList1.append(i)
        possibleNounEntities = tempList1
    if femaleTestedWord:
        for i in possibleNounEntities:
            if not ("ONT::MALE-PERSON" == i["type"]):
                tempList2.append(i)
        possibleNounEntities = tempList2
    # remove non-human
    if maleTestedWord or femaleTestedWord:
        for i in possibleNounEntities:
            if not ("ONT::NONHUMAN-ANIMAL" == i["type"]):
                tempList3.append(i)
        possibleNounEntities = tempList3
    # 2.  ANIMAL(PERSON/NONHUMAN-ANIMAL)/not animal
    testedWordOntology = ontologyCheck.getTree(testedWord["type"].replace("ONT::", ""))
    ontologyList = []
    tempListAnimal = []
    for i in possibleNounEntities:
        temp = ontologyCheck.getTree(i["type"].replace("ONT::", ""))
        ontologyList.append(temp)
    # print("ontologyList............", ontologyList)
    if 'ANIMAL' in testedWordOntology:
        for i in range(len(ontologyList)):
            if ("ANIMAL" in ontologyList[i]):
                # print(i)
                tempListAnimal.append(possibleNounEntities[i])
        possibleNounEntities = tempListAnimal
        # print("aaaaaaYES  ", possibleNounEntities)
    else:
        for i in range(len(ontologyList)):
            if not ("ANIMAL" in ontologyList[i]):
                # print(i)
                tempListAnimal.append(possibleNounEntities[i])
        possibleNounEntities = tempListAnimal
        # print("aaaaaaNO  ", tempListAnimal)

    ontologyList2 = []
    tempListPerson = []
    for i in possibleNounEntities:
        temp = ontologyCheck.getTree(i["type"].replace("ONT::", ""))
        ontologyList2.append(temp)
    # print("ontologyList2222222222  ", ontologyList2)
    if 'PERSON' in testedWordOntology:
        for i in range(len(ontologyList2)):
            if ("PERSON" in ontologyList2[i]):
                # print(i)
                tempListPerson.append(possibleNounEntities[i])
        possibleNounEntities = tempListPerson
        # print("pppppppYES  ", possibleNounEntities)
    else:
        for i in range(len(ontologyList2)):
            if not ("PERSON" in ontologyList2[i]):
                # print(i)
                tempListPerson.append(possibleNounEntities[i])
        possibleNounEntities = tempListPerson
        # print("pppppppNO  ", tempListPerson)


    # 3. store all ontology, check if there is exactly match
    # store all possible entities have exact match.
    # return WuPalmer and signal = False


    return possibleNounEntities, signal

# list, signal = possiblenNounEntities(lines, 2, 0)
# print("list", list)
# print("signal", signal)
# semanticFilter(list)

def refer2Event(possibleEntities = 0):
    return
    # check "it" or "the"
    # print("not finished yet")


def referenceResolution(inputFile):
    resultList = []
    # # open files, store each line as an element
    with open(inputFile) as f:
        lines = f.readlines()
    # print(lines)
    # discourseList[][]: [] -> one sentence [] -> one entities(word) in this sentence
    discourseList = file2discourse(lines)
    # print(discourseList)

    # dictList[][]{}: change each word line into dict
    dictList = storeDictBack(lines)
    # print(dictList)
    # centering constraint

    for i in range(len(dictList)):
        for j in range(len(dictList[i])):
            if not (dictList[i][j]["spec"] == "A" or dictList[i][j]["spec"] == "AN" or dictList[i][j]["spec"] == "SOME" or dictList[i][j]["spec"] == "VERB"):
                possibleNounEntityList, signal = possiblenNounEntities(lines, i, j)
                # print("====================================================")
                # print("tested word is:::::", dictList[i][j])
                # print("check1", possibleNounEntityList)
                for a in possibleNounEntityList:
                    for b in range(1, len(resultList), 2):
                        if a["DE"] == resultList[b]:
                            possibleNounEntityList.remove(a)
                # print("check2", possibleNounEntityList)
                # print(signal)
                # handle with the result of possibleNounEntities()
                if (signal == True):
                    if possibleNounEntityList == []:
                        refer2Event()
                    # if not possibleNounEntityList == []:
                    else:
                        # (COREF S2 P1)
                        resultList.append(dictList[i][j]["DE"])
                        resultList.append(possibleNounEntityList[0]["DE"])
                        # return ("(COREF ", dictList[i][j], " ", possibleNounEntityList[0]["DE"], ")")
                if (signal == False):
                    if possibleNounEntityList == []:
                        refer2Event()
                    # if not possibleNounEntityList == []
                    else:
                        tempList1, signal = semanticFilter(possibleNounEntityList)
                        # print("----------------------------------")
                        # print(tempList1)
                        # print(signal)
                        # handle with the result of semanticFilter
                        if (signal == True):
                            # if tempList = empty, signal = True -> no referent
                            # (COREF S2 P1)
                            if not tempList1 == []:
                                resultList.append(dictList[i][j]["DE"])
                                resultList.append(tempList1[0]["DE"])
                            # return ("(COREF ", dictList[i][j], " ", tempList1[0]["DE"], ")")
                        # Signal = False
                        else:
                            if tempList1 == []:
                                # if dictList[i][j]["spec"] =
                                refer2Event()
                            else:
                                resultList.append(dictList[i][j]["DE"])
                                resultList.append(tempList1[-1]["DE"])
                        # else:
                        #     # remove the word that is refered
    # print(resultList)
    return resultList



# referenceResolution('input6')
def format(input, list):
    finalList = []
    with open(input) as f:
        lines = f.readlines()
    discourseList = file2discourse(lines)
    # one sentence
    print("2222", discourseList[0])
    # for i in range(0, len(list), 2):
    #     print(list[i][0])
    #     print(list[i][1])

    for i in range(len(discourseList)):
        templist = []
        for j in range(len(discourseList[i])):
            print(discourseList[i][j][-3])
            print(discourseList[i][j][-4])
            for x in range(0, len(list), 2):
                print(list[x])
                if discourseList[i][j][-3] == list[x][1] and discourseList[i][j][-4] == list[x][0]:
                # if list[j] in discourseList[i][j]:
                #     print(list[x][1])
                    templist.append(list[x])
                    templist.append(list[x+1])

        # for j in range(0, len(list), 2):
        #     print("111", list[j])
        #     print(type(list[j]))
        #     print("222", discourseList[i])
        #     print(type(discourseList[i]))
        #     if list[j] == discourseList[i]:
        #         print("CATCH")
        #         templist.append(list[j])
        #         templist.append(list[j+1])
    finalList.append(templist)
    print(finalList)


format('input1', referenceResolution('input1'))
# remove the impossible entities from the list based on semantic constraints(singular and plural, female/male/non-animate)
# check same
# centering constraint
# recency constraint
# WuPalmer-compare
# We I, special case (only same with We, I, us, me)


# Co-reference Resolution - Refer to Event (Verb) =========================================================================================================================
# each time list is empty
# when the PRO is "it" "that" "this" definites; "these" "those" "they", check refers to verb(action)
# ""


# main =======================================================================
# check signal to decide continue or return referent
# remove signal

# input2: remove entities (and its co-referent) from possibleNounEntities
# input6: a/an/some; the/these (definites) -> check events
# Grammatical role: subject>object

# def openFile(filename):
#     with open(filename, newline='') as f:
#         reader = txt.reader(f)
#         mylist = list(reader)
#     # print(mylist)
#     # print(mylist[1][0])
#     return mylist

parser = argparse.ArgumentParser()
parser.add_argument('input', type= str, default = 'input1')
parser.add_argument('output', type= str, default = 'output1')

args = parser.parse_args()

inputFilename = str(args.input)


def inputName(inputFilename):
    return inputFilename
    # with open(inputFilename) as f:
    #     lines = f.readlines()
    #     return lines

input = inputName(inputFilename)


resultList = referenceResolution(input)
print("result!!!", resultList)
# with open(outputFilename, 'w') as s:
#     s.write("sdf")
#     s.write(resultList)
#     s.write("fdg")
# def keepFormat(input):
#     resultList = referenceResolution(input)
#     print(resultList)
#     return resultList
#
#
# # generate output file
outputFilename = str(args.output)
# list = "adf"
# lsit2 = 'as'
with open(outputFilename, 'w') as f:
    # f.writelines(list)
    # f.write("\n")
    # f.write(lsit2)
    # f.write(resultList)
    for i in range(0, len(resultList), 2):
    # for i in range(le)
        f.write("(COREF ")
        f.writelines(resultList[i])
        f.write(" ")
        f.write(resultList[i+1])
        f.write(")")
        f.write("\n")

# def readGenerate(inputFilename, outputFilename):
#     list = referenceResolution(inputFilename)
