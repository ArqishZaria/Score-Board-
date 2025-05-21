#to change the tasks file, edit line 94 of main.py & line 254 of avl_pygame_visualizer.py
from helper_functions import *

def insert_player(name):
    global root
    if search_player(root, name): #avoid duplicate insertions
        print(f"Player {name} already exists.")
        return
    root = insert_node(root, name, 0) #inserting player with score 0
    print(f"Inserted player: {name}")

def update_player(name, new_score):
    global root
    player = search_player(root, name) #find the player node
    if player is None: #player not found
        print(f"Player {name} does not exist. Use 'Insert' first.")
        return
    root = delete_node(root, name, player['score']) #delete current node
    root = insert_node(root, name, new_score) #reinsert with new score
    print(f"Updated player {name} to new score {new_score}")

def delete_player(name):
    global root
    player = search_player(root, name) #find the player node
    if player is None: #player not found
        print(f"Player {name} not found.")
        return
    root = delete_node(root, name, player['score']) #delete player node
    print(f"Deleted player: {name}")

def top_players(node, top_score):
    if node is None: #base case
        return []
    result = []    
    if node['score'] == top_score: #if current node has top score
        result.append(node)
    result += top_players(node['left'], top_score) #recursively search left subtree
    result += top_players(node['right'], top_score) #recursively search right subtree
    return result

def get_top_players(root):
    if root is None: #base case
        print("No top players found.")
        return
    current = root
    while current['right']: #find the node with the highest score
        current = current['right']
    top_score = current['score']
    lst= top_players(root, top_score) #get all players with top score
    if lst: #concatenating all the names
        names = [player['name'] for player in lst]
        print("Top Players:", ", ".join(names), f"with score {top_score}")
    else:
        print("No top players found.")

def print_leaderboard(node):
    if node is None: #base case
        return
    print_leaderboard(node['right']) #print right subtree
    print(f"{node['name']}: {node['score']}") #print current node
    print_leaderboard(node['left']) #print left subtree

def search_player(node, name):
    if node is None: #base case
        return None
    if node['name'] == name: #found the player
        return node
    found = search_player(node['left'], name) #search left subtree
    if found is None: #if not found in left subtree, search right subtree
        found = search_player(node['right'], name) #search right subtree
    return found


def save_leaderboard(node, filename):
    if node is None: #base case
        return
    save_leaderboard(node['right'], filename) #save right subtree
    filename.write(f"{node['name']},{node['score']}\n") #save current node
    save_leaderboard(node['left'], filename) #save left subtree

def main():
    global root
    try:
        with open('data.txt', 'r') as f: #load leaderboard from file
            for line in f:
                line = line.strip()
                if line:
                    name, score_str = line.split(',') 
                    score = int(score_str)
                    root = insert_node(root, name, score)
    except FileNotFoundError: #if file does not exist so create a new leaderboard
        print("Data file not found; starting with an empty leaderboard.")
    try:
        with open('tasks,h3.txt', 'r') as f: #load tasks from file
            tasks = f.readlines()
    except FileNotFoundError: #if file does not exist so create a new file
        print("Tasks file not found. Please ensure tasks.txt exists.")
        return
    for t in tasks: #for each task
        parts= [p.strip() for p in t.strip().split(',')]
        task = parts[0].lower()
        name= parts[1] if len(parts) > 1 else None
        score= int(parts[2]) if len(parts) > 2 else None
        if task == "insert": #insert new player
            insert_player(name)
        elif task == "update": #update player's score
            update_player(name, score) 
        elif task == "delete": #delete player
            delete_player(name)
        elif task == "top": #get all the highest score players
            get_top_players(root)            
        elif task == "search": #search for player
            player = search_player(root, name)
            if player:
                print(f"Found player: {player['name']} with score {player['score']}")
            else:
                print("Player",name,"not found.")
        elif task == "leaderboard": #print leaderboard
            print("Leaderboard:")
            print_leaderboard(root)
        else: #invalid task
            print("Unknown task or wrong number of parameters:", task)
        with open('data.txt', 'w') as f: #save leaderboard to file
            save_leaderboard(root, f)        
    print("Task processing complete.")


if __name__ == '__main__':
    main()
print(root)