import UnityPy
import glob
import time
from os import path
   
    
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
                    diffList.append(tree["m_Name"])
                    print("Changes")
                    print(tree["m_Name"])
                    
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
    


start_time = time.time()
main = "main"
mod1 = "mod1"
mod2 = "mod2"

mainFiles = search(main)
mod1Files = search(mod1)
mod2Files = search(mod2)

mainEnv = UnityPy.load(main)
modded1Env = UnityPy.load(mod1)

compareMonoBehaviour(mainEnv, modded1Env)
print("My program took", time.time() - start_time, "seconds to run")