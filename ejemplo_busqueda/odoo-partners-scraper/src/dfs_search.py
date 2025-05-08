import pandas as pd # use pandas to load the data

# Loading excel data
def load_data(filename):
    df = pd.read_excel(filename) #reading the data from the excel file
    return df

# Convert data to a graph
def build_graph(df):
    graph = {} #empty dictionary to store the graph
    countries = df['Country'].tolist() # get the list of countries
    
    # for each country, create a set of other countries
    for country in countries:
        graph[country] = set(countries) - {country} # create a set of countries excluding the current country
    
    return graph

def dfs(graph, start_node):
    visited = set() # Create a set to store the visited nodes
    stack = [start_node] # Create a stack to store the nodes to visit
    result = [] # Create a list to store the visited nodes

    while stack: # While the stack is not empty
        node = stack.pop() # Get the last node from the stack
        if node not in visited: # If the node has not been visited
            visited.add(node) # Add the node to the visited set
            result.append(node) # Add the node to the result list
            stack.extend(graph[node] - visited) # Add the neighbors of the node to the stack
    
    return result

def main():
    filename = 'countries_data.xlsx' # Load the data from the Excel file
    df = load_data(filename) # Load the data from the Excel file
    graph = build_graph(df) # Build the graph from the data extracted from the Excel file
    
    start_node = df['Country'].iloc[0]  # Start from the first country in the list
    result = dfs(graph, start_node)
    
    # Create a DataFrame to display the results
    results_df = pd.DataFrame({
        'Visited Nodes': result
    })
    
    print(results_df)

if __name__ == '__main__':
    main()