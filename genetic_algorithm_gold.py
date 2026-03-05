import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

#########################################################################################################
# RECURSO ACADÉMICO CREADO POR LA PROFESORA MÓNICA TAHAN CON EL USO DE GOOGLE ANTIGRAVITY               #
# ACADEMY RESOURCE CREATED BY PROFESSOR MÓNICA TAHAN WITH THE USE OF GOOGLE ANTIGRAVITY                 #
# Este script implementa un Algoritmo Genético (GA) para optimizar una estrategia con el Oro (XAUUSD)    #
# This script implements a Genetic Algorithm (GA) to optimize a strategy with Gold (XAUUSD)             #
# Product Owner: Prof. Mónica Tahan                                                                   #
# Autor: Mónica Tahan y Google Antigravity AI                                                           # 
# Author: Mónica Tahan and Google Antigravity AI                                                        #
# Versión: 1.0                                                                                          #
# Version: 1.0                                                                                          #
# Fecha: 03/03/2026                                                                                     # 
# Date: 03/03/2026                                                                                      #
# Licencia: GNU/GPL                                                                                     #
# License: GNU/GPL                                                                                      #
#########################################################################################################

# Aesthetic configuration
plt.rcParams['figure.dpi'] = 100
sns.set_theme(style="whitegrid", context="talk", palette="magma")

def run_genetic_algorithm():
    print("Iniciando algoritmo genético para optimizar una estrategia con el Oro (XAUUSD)...")

    # 1. Load data
    train_file = "XAUUSD..1.train.csv"
    if not os.path.exists(train_file):
        print(f"Error: No se encontró el archivo {train_file}")
        return

    df = pd.read_csv(train_file)
    # Use a sample for faster demonstration in class
    df = df.iloc[:1000].copy()
    
    # 2. Prepare Features and Target
    # Features: open, high, low, volume
    X = df[['open', 'high', 'low', 'volume']].values
    # Scaled features (simplified)
    X = (X - X.mean(axis=0)) / X.std(axis=0)
    
    # Target: 1 if next close > current close, else 0
    df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
    y = df['target'].values[:-1]
    X = X[:-1]

    # 3. GA Parameters
    pop_size = 50 #population size
    n_weights = X.shape[1]  # 4 weights
    generations = 50 #number of generations
    mutation_rate = 0.1 #mutation rate

    # 4. Fitness Function
    def get_fitness(weights):
        # A simple linear model prediction
        predictions = (np.dot(X, weights) > 0).astype(int) #prediction
        accuracy = np.mean(predictions == y) #accuracy
        return accuracy

    # 5. Initialization
    population = np.random.uniform(-1, 1, (pop_size, n_weights)) #population initialization
    best_fitness_history = [] #best fitness history empty list

    print(f"Evolución iniciada por {generations} generaciones...")

    # 6. Evolutionary Loop
    for gen in range(generations):
        # Evaluation
        fitness_scores = np.array([get_fitness(ind) for ind in population]) #fitness scores
        
        best_fitness = np.max(fitness_scores) #best fitness
        best_fitness_history.append(best_fitness) #best fitness history
        
        # Selection (Tournament)
        new_population = [] #new population empty list
        for _ in range(pop_size): #for each individual in the population
            i, j = np.random.randint(0, pop_size, 2) #randomly select two individuals
            winner = population[i] if fitness_scores[i] > fitness_scores[j] else population[j] #select the winner
            new_population.append(winner) #add the winner to the new population
        population = np.array(new_population) #update the population
        
        # Crossover (Mean Crossover for simplicity in continuous space)
        for i in range(0, pop_size, 2): #for each individual in the population
            if i + 1 < pop_size: #if the individual is not the last one
                child1 = (population[i] + population[i+1]) / 2 + np.random.normal(0, 0.1, n_weights) #create the first child
                child2 = (population[i] + population[i+1]) / 2 - np.random.normal(0, 0.1, n_weights) #create the second child
                population[i], population[i+1] = child1, child2 #update the population
                
        # Mutation
        mask = np.random.rand(*population.shape) < mutation_rate #mutation mask
        population[mask] += np.random.normal(0, 0.2, np.sum(mask)) #mutation

    print("Evolución Completada!")
    best_idx = np.argmax([get_fitness(ind) for ind in population]) #best fitness index
    best_weights = population[best_idx] #best weights
    
    # 7. Visualization
    plt.figure(figsize=(12, 6)) #figure size
    plt.plot(best_fitness_history, color='#e91e63', linewidth=3, marker='o',    markersize=4) #plot the best fitness history
    plt.title('Algoritmo Genético: Evolución de la Aptitud a lo largo de las Generaciones', fontsize=20, fontweight='bold', pad=20) #title
    plt.xlabel('Generación', fontsize=14) #x-axis label
    plt.ylabel('Mejor Precisión (Aptitud)', fontsize=14) #y-axis label
    plt.grid(True, linestyle='--', alpha=0.6) #grid
    plt.tight_layout() #tight layout
    print("Mostrando el gráfico de evolución de la aptitud... (Cerrar la ventana para continuar)")
    plt.show()

    # Weight Importance Plot
    plt.figure(figsize=(10, 6))
    features = ['Open', 'High', 'Low', 'Volume']     #features
    sns.barplot(x=features, y=best_weights, palette="magma") #plot the best weights
    plt.title('Mejores Pesos Optimizados Encontrados por el AG', fontsize=20, fontweight='bold', pad=20) #title
    plt.axhline(0, color='black', linewidth=1) #horizontal line
    plt.tight_layout() #tight layout
    print("Mostrando el gráfico de importancia de pesos... (Cerrar la ventana para continuar)")
    plt.show()

    print(f"\nResultado: Mejor Precisión lograda: {max(best_fitness_history):.2%}")
    print(f"Pesos Optimizados: {best_weights}")
    print("Gracias por usar nuestro algoritmo evolutivo!")

if __name__ == "__main__":
    run_genetic_algorithm()
