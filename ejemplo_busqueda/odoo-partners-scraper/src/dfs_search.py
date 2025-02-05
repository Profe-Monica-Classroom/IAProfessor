import pandas as pd

def load_data(filename):
    df = pd.read_excel(filename)
    return df

def build_graph(df):
    graph = {}
    countries = df['Country'].tolist()
    
    for country in countries:
        graph[country] = set(countries) - {country}
    
    return graph

def dfs(graph, start_node):
    visited = set()
    stack = [start_node]
    result = []

    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            result.append(node)
            stack.extend(graph[node] - visited)
    
    return result

def main():
    filename = 'countries_data.xlsx'
    df = load_data(filename)
    graph = build_graph(df)
    
    start_node = df['Country'].iloc[0]  # Start from the first country in the list
    result = dfs(graph, start_node)
    
    # Create a DataFrame to display the results
    results_df = pd.DataFrame({
        'Visited Nodes': result
    })
    
    print(results_df)

if __name__ == '__main__':
    main()