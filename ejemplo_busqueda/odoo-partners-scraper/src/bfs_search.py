import pandas as pd # use pandas to load the data
from collections import deque #use deque to implement the queue

def load_data(filename): # Loading excel data
    df = pd.read_excel(filename) # reading the data from the excel file
    return df

def build_graph(df): # Convert data to a graph
    graph = {}
    countries = df['Country'].tolist()
    
    for country in countries:
        graph[country] = set(countries) - {country}
    
    return graph

def bfs(graph, start_node): # Breadth First Search method
    visited = set() # Create a set to store the visited nodes
    queue = deque([start_node]) # Create a queue to store the nodes to visit
    result = [] # Create a list to store the visited nodes

    while queue:
        node = queue.popleft() # Get the first node from the queue
        if node not in visited:
            visited.add(node) # Add the node to the visited set
            result.append(node) # Add the node to the result list
            queue.extend(graph[node] - visited) # Add the neighbors of the node to the queue
    
    return result

def main():
    filename = 'countries_data.xlsx' # Load the data from the Excel file
    df = load_data(filename) # Load the data from the Excel file
    graph = build_graph(df) # Build the graph from the data extracted from the Excel file
    
    start_node = df['Country'].iloc[0]  # Start from the first country in the list
    result = bfs(graph, start_node)
    
    # Create a DataFrame to display the results
    results_df = pd.DataFrame({
        'Visited Nodes': result
    })
    
    print(results_df)

if __name__ == '__main__':
    main()