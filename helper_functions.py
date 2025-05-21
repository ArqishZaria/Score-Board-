root = None #this is the nested dictionary that will be used to store the AVL tree

def create_node(name, score): #new player with name and score 
    return {"name": name, "score": score, "height": 1, "left": None, "right": None}

def height(node):
    if node is None:
        return 0
    return node['height']

def update_height(node):
    if node:
        node['height'] = 1 + max(height(node['left']), height(node['right']))
        #after insertion or deletion, the height of the node is updated

def get_balance(node):
    if node is None:
        return 0
    return height(node['left']) - height(node['right'])
    #bf (balance factor) is the difference between the height of the left and right subtrees

def right_rotate(y):
    x = y['left'] #the left child of the node to be rotated
    T2 = x['right'] #the right child of the left child of the node to be rotated
    # Perform rotation
    x['right'] = y #the left child of the node to be rotated becomes the new root of the subtree
    y['left'] = T2 # T2 becomes the left child of the node to be rotated
    # Update heights
    update_height(y)
    update_height(x)
    return x

def left_rotate(x):
    y = x['right'] #the right child of the node to be rotated
    T2 = y['left'] #the left child of the right child of the node to be rotated
    # Perform rotation
    y['left'] = x #the right child of the node to be rotated becomes the new root of the subtree
    x['right'] = T2 #T2 becomes the right child of the node to be rotated
    # Update heights
    update_height(x)
    update_height(y)
    return y

def rebalance(node):
    update_height(node)
    balance = get_balance(node)
    if balance > 2: #if the left subtree is taller than the right subtree
        if get_balance(node['left']) < 0:#if the right child of the left subtree is taller than the left child of the left subtree
            node['left'] = left_rotate(node['left'])#LR case
        return right_rotate(node) #LL case
    if balance < -2:#if the right subtree is taller than the left subtree
        if get_balance(node['right']) > 0: #if the right child of the right subtree is taller than the left child of the right subtree
            node['right'] = right_rotate(node['right']) #RL case
        return left_rotate(node) #RR case
    # Balanced
    return node

def insert_node(node, name, score):
    if node is None:
        return create_node(name, score)
    #For players with equal scores, we use name as a tiebreaker to keep names unique.
    if (score, name) < (node['score'], node['name']):
        node['left'] = insert_node(node['left'], name, score)
    elif (score, name) > (node['score'], node['name']):
        node['right'] = insert_node(node['right'], name, score)
    else:
        # Duplicate player name is not inserted again.
        return node
    

    return rebalance(node)

def min_value_node(node):
    min = node
    while min and min['left']: #keeps going left until it reaches the leftmost node
        min = min['left']
    return min

def delete_node(node, name, score):
    lst = []  #tracks the path for rebalancing
    current = node
    if current is None: #if the tree is empty
        return node
    while current is not None: #finds the node to delete
        current_key = (current['score'], current['name']) 
        target_key = (score, name) #key to delete
        if target_key < current_key: #if the key is less than the current node's key go left
            lst.append((current, 'left')) 
            current = current['left'] 
        elif target_key > current_key: #if the key is greater than the current node's key go right
            lst.append((current, 'right'))
            current = current['right']
        else:
            break  # Node found
    if current['left'] is None or current['right'] is None: #if the node has one child or no children
        child = current['left'] or current['right'] 
        if not lst:  # Deleting root
            root = child #root is the only node in the tree
        else: 
            parent, direction = lst[-1]
            parent[direction] = child #the child of the deleted node becomes the child of the parent node
    else: #if the node has two children
        successor = min_value_node(current['right']) #finds the smallest node in the right subtree successore to replace
        temp = current['right'] #temporarily stores the right subtree
        lst.append((current, 'right')) #adds the current node to the lst
        while temp != successor: #find the smallest node
            lst.append((temp,'left'))
            temp = temp['left']
        current['name'], current['score'] = successor['name'], successor['score'] #replaces the node's data with the successor's data
        if lst[-1][0]['left'] == successor: #remove the successor from the lst
            lst[-1][0]['left'] = successor['right']
        else:
            lst[-1][0]['right'] = successor['right']
    while lst: #rebalances the tree
        node, direction = lst[-1] #get the last node in the lst
        del lst[-1] #remove the last node from the lst
        new_subtree = rebalance(node) 
        if lst:
            parent, dir = lst[-1]
            parent[dir] = new_subtree 
        else:
            root = new_subtree #update root
    return root