import UnityPy
import glob
import time
from os import path, makedirs, remove
    
    
outputPath = "merged"
inputMain = "main"
inputMod1 = "mod1"
inputMod2 = "mod2"

fileList = [outputPath, inputMain, inputMod1, inputMod2]
    
##I have no idea how else I would compare things, maybe line by line?
def compareMonoBehaviour(file1, file2):
    diffList = []
    treeList = []
    nameList = []
    
    ##Assuming that the files are the same structure
    for obj in file1.objects:
        if obj.type.name == "MonoBehaviour":
            tree = obj.read_typetree()
            treeList.append(tree)
            nameList.append(tree["m_Name"])
            
    for obj in file2.objects:
        if obj.type.name == "MonoBehaviour":
            tree = obj.read_typetree()
            if tree["m_Name"] in nameList:
                index = nameList.index(tree["m_Name"])
                if treeList[index] != tree:
                    diffList.append(obj.path_id)
                    
    return diffList

def search(folder):
    fileDic = {}
    
    for filename in glob.iglob(folder + "**/**", recursive = True):
        if path.isfile(filename):
            fileDic[path.basename(filename)] = filename
    
    return fileDic

def compareDirectories(main, mod1, mod2):
    
    similarFiles = []
    uniqueFiles = []
    
    for file in mod1.keys():
        if file in main.keys():
            print("Found in main")
        else:
            print("Error in folder mod1 {} not found".format(file))
            
    for file in mod2.keys():
        if file in main.keys():
            print("Found in main")
        else:
            print("Error in folder mod2 {} not found".format(file))
            
def removeDuplicates(list1, list2):
    newList1 = [] ##Used so we don't have to delete variables while iterating
    duplicates = []
    for i in list1:
        
        if i in list2:
            list2.remove(i)
            duplicates.append(i)
        else:
            newList1.append(i)
            
    return newList1, list2, duplicates

##Edits opened main file with modified mods
def replaceAssets(mainFile, modFile, treeIDs):
    
    treeDic = {}
    
    for obj in modFile.objects:
        if obj.type.name == "MonoBehaviour":
            if obj.path_id in treeIDs:
                tree = obj.read_typetree()
                
                treeDic[tree['m_Name']] = tree
    
    for obj in mainFile.objects:
        if obj.type.name == "MonoBehaviour":
            if obj.path_id in treeIDs:
                tree = obj.read_typetree()
                
                newTree = treeDic[tree['m_Name']]
                obj.save_typetree(newTree)
            
            
def getNameFromPathID(assetbundle, pathID):
    
    for obj in assetbundle.objects:
        if obj.path_id == pathID:
            tree = obj.read_typetree()
            return tree["m_Name"]
        
    return "?"

def getkeys(*argv):
    keyList = []
    compareList = argv[0]
    for key in compareList:
        
        present = True
        
        for arg in argv:
            if key not in arg:
                present = False
                break
            
        if present:
            keyList.append(key)
            
    return keyList
        
    


if __name__ == "__main__":
    start_time = time.time()
    
    for path in fileList:
        if not path.exists(path):
            makedirs(path, 0o666)
        print("Created folder 'main', 'mod1', 'mod2' put unedited in main, and the two mods you want to merge in mod1 and mod2 respectively")
        print("Merged is the output folder")
        input("Once all files are in, press enter to continue...")
    
    main = "main"
    mod1 = "mod1"
    mod2 = "mod2"

    mainFiles = search(main)
    mod1Files = search(mod1)
    mod2Files = search(mod2)
    
    mainKeys = list(mainFiles.keys())
    mod1Keys = list(mod1Files.keys())
    mod2Keys = list(mod2Files.keys())
    
    keys = getkeys(mainKeys, mod1Keys, mod2Keys)
    
    for key in keys:
        
        print(f"Replacing {key}")

        mainFile = mainFiles[key]
        mod1File = mod1Files[key]
        mod2File = mod2Files[key]


        mainEnv = UnityPy.load(mainFile)
        modded1Env = UnityPy.load(mod1File)
        modded2Env = UnityPy.load(mod2File)

        diffList1 = compareMonoBehaviour(mainEnv, modded1Env)
        diffList2 = compareMonoBehaviour(mainEnv, modded2Env)
        cleanDiffList1, cleanDiffList2, duplicates = removeDuplicates(diffList1, diffList2)
        for duplicate in duplicates:
            name = getNameFromPathID(main, duplicate)
            print("Asset {} is different in both mods, and cannot be merged".format(name))
        print(diffList1)
        print(diffList2)
        replaceAssets(mainEnv, modded1Env, diffList1)
        replaceAssets(mainEnv, modded2Env, diffList2)
        
            
        filepath = path.join(outputPath, key)
        with open(filepath, "wb") as f:
            f.write(mainEnv.file.save(packer=(64, 2)))
    
    print("Merging took", time.time() - start_time, "seconds to run")