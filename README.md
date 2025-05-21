# Score Leaderboard

## \[DSA Project Report]

**Submitted by:**
Arqish Zaria - az09714
Shaheer Qureshi - sq09647

**Course:** Data Structures and Algorithms
**Instructor:** Saba Saeed
**Department:** Computer Science, Habib University

---

## Problem Statement

Modern competitive platforms from large online games and coding contests leaderboards must continuously receive and output millions of score updates all while allowing instant queries for top performers. As the number of participants grows other data structures can slow down, for example inserting scores in already‐sorted order or performing heavy updates on an unbalanced binary search tree can degrade operations to linear time, introducing lag, inconsistencies in rankings and poor user experience.

The core challenge is to design a dynamic data structure that supports insertion of new players, real‐time score updates, deletions and retrieval of top‐scoring participants in guaranteed logarithmic time per operation.

To address this we created the **Score Leaderboard** using the **AVL Tree**. It is a height-balanced binary search tree that maintains the balance level at every node; the heights of left and right subtrees differ by at most 1. When an insertion or deletion violates the balance factor, one or two local rotations restore balance in O(1) time. This ensures responsiveness, fairness, and scalability regardless of input patterns and size.

---

## Significance

### Ordered Storage

* Maintains sorted structure on `(score, name)` keys
* Quick retrieval of the highest score
* Easy player updates
* Deletion of players
* Full descending leaderboard traversal

### Guaranteed Logarithmic Height

* Unbalanced BSTs can degrade to O(n) per operation under sorted inputs
* AVL condition `-1 ≤ |height(left) − height(right)| ≤ 1` ensures tree height O(log n)
* Every insert/search/delete is worst-case O(log n)

---

## Algorithmic Mechanism

### Search

To locate a player by name, start at the root and compare the target key to the node’s key.

* If equal, return the node
* If less, recurse left
* If greater, recurse right
* If null, not present

### Insertion

Standard BST insert using `(score, name)` to find position.

* Rebalance while unwinding recursion
* Update height, compute balance
* Apply rotations (LL, RR, LR, RL) if needed

### Deletion

* Find target node by key
* If two children, swap with in-order successor and delete successor
* Rebalance afterward

### Rotations

* **Right Rotation**: Fix left-heavy imbalance
* **Left Rotation**: Fix right-heavy imbalance
* **Left-Right (LR)** and **Right-Left (RL)**: Handle complex cases

---

## Data Structures and Algorithm Justifications

### Node ADT

Encapsulates a player’s data

* Key: Tuple `(score, name)`
* Fields: Height, left and right child pointers

### Dictionary ADT

* Mutable mapping for field access
* O(1) access for fields like `left`, `right`, `height`

### Balanced Binary Search Tree (AVL Tree) ADT

* Maintains balance condition
* Search: O(log n)
* Insert: O(log n)
* Delete: O(log n)
* Top Players: O(log n + k) for k players

---

## Time and Space Complexity

### Space Complexity

* O(n) nodes
* Each node uses constant space (score, name, height, 2 pointers)
* Recursive operations use stack space O(log n)

### Operation Time Complexity

| Operation         | Time Complexity | Notes                       |
| ----------------- | --------------- | --------------------------- |
| Insert            | O(log n)        | BST insert + 2 rotations    |
| Update            | O(log n)        | Delete + Insert             |
| Delete            | O(log n)        | Locate, swap, rebalance     |
| Retrieve Top N    | O(log n)        | Follow right child pointers |
| Search by Name    | O(n)            | DFS                         |
| Print Leaderboard | O(n)            | Reverse-inorder traversal   |

