import glob
from my_func import load_pickle

def get_food_list():
    temp = glob.glob('./pred_image/result/labels/*')
    my_file = open(temp[0])
    name_dict = load_pickle()
    food_list = []
    
    for line in my_file.readlines():
        food_list.append(name_dict.get(int(line.split(' ')[0])))     
        
    my_file.close()
    
    return food_list