import pandas as pd # for data manipulation
import numpy as np # for numerical operations
import matplotlib.pyplot as plt # for plotting
import seaborn as sns # for enhanced visualizations
from sklearn.cluster import KMeans # for K-means clustering
from sklearn.preprocessing import StandardScaler # for data normalization
import os # for file existence check
#########################################################################################################
# RECURSO ACADÉMICO CREADO POR LA PROFESORA MÓNICA TAHAN CON EL USO DE GOOGLE ANTIGRAVITY               #
# ACADEMY RESOURCE CREATED BY PROFESSOR MÓNICA TAHAN WITH THE USE OF GOOGLE ANTIGRAVITY                 #
# Este script es un algoritmo Kmeans aplicado a valores financieros (Oro), para análisis discriminante  #
# This script is an algorithm Kmeans applied to financial values (Gold), for discriminant analysis      #
# Product Owner: Prof. Mónica Tahan                                                                   #
# Autor: Mónica Tahan y Google Antigravity AI                                                           # 
# Author: Mónica Tahan and Google Antigravity AI                                                        #
# Versión: 2.0                                                                                          #
# Version: 2.0                                                                                          #
# Fecha: 03/03/2026                                                                                     # 
# Date: 03/03/2026                                                                                      #
# Licencia: GNU/GPL                                                                                     #
# License: GNU/GPL                                                                                      #
#########################################################################################################


# Global aesthetic configuration (Style similar to ggplot2 but modern)
plt.rcParams['figure.dpi'] = 100
plt.rcParams['font.family'] = 'sans-serif'
sns.set_theme(style="whitegrid", context="talk", palette="viridis")
# Suppress warnings for cleaner output


def run_kmeans_analysis():
    print("🚀 Iniciando el análisis de K-means para precios del oro (XAUUSD)...")

    # 1. Local data loading
    train_file = "XAUUSD..1.train.csv"
    test_file = "XAUUSD..1.test.csv"
    # If files do not exist, print error message and exit
    if not os.path.exists(train_file):
        print(f"❌ Error: Archivo no encontrado {train_file}")
        return

    df_train = pd.read_csv(train_file)
    print(f"📊 Datos cargados: {df_train.shape[0]} registros en entrenamiento.")

    # 2. Procedure
    # Drop 'data' and 'time' (first two columns)
    X_raw = df_train.drop(columns=['data', 'time'])

    # 3. Data Scaling
    scaler = StandardScaler() # use of StandardScaler for normalization
    X_scaled = pd.DataFrame(scaler.fit_transform(X_raw), columns=X_raw.columns) # creating a new DataFrame with scaled data
    print("⚖️ Datos normalizados con StandardScaler.")

    # 4. Método del Codo (Elbow Method)
    print("📈 Calculando el Método del Codo...")
    wcss = []
    k_range = range(1, 21)
    # use of for loop to calculate wcss
    for i in k_range:
        kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=10000, n_init=10, random_state=1234) # use of KMeans with specified parameters
        kmeans.fit(X_scaled) # fitting the model to the scaled data
        wcss.append(kmeans.inertia_) # appending the inertia (wcss) to the list

    # Graphs of the elbow method
    plt.figure(figsize=(12, 7))
    plt.plot(k_range, wcss, marker='o', linestyle='-', color='#1f77b4', linewidth=3, markersize=10, markerfacecolor='#ff7f0e')
    plt.title('Método del Codo: Buscando el K óptimo', fontsize=20, fontweight='bold', pad=20)
    plt.xlabel('Número de Clusters (k)', fontsize=14)
    plt.ylabel('Inercia (WCSS)', fontsize=14)
    plt.xticks(k_range)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    print("💡 Mostrando gráfico del Codo... (Cierre la ventana para continuar)")
    plt.show()

    # 5. Application of K-means (K=15)
    print("🤖 Aplicando K-means con K=15...")
    kmeans_final = KMeans(n_clusters=15, init='k-means++', max_iter=10000, n_init=10, random_state=1234)
    df_clusters = X_scaled.copy()
    df_clusters['cluster'] = kmeans_final.fit_predict(X_scaled)

    # 6. Correlation Matrix using seaborn heatmap
    plt.figure(figsize=(12, 10))
    corr = df_clusters.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool)) # mask to show only one triangle of the matrix
    sns.heatmap(corr, mask=mask, annot=True, cmap='coolwarm', fmt=".2f", center=0, square=True, linewidths=.5, cbar_kws={"shrink": .8}) # use of seaborn heatmap for correlation matrix
    plt.title('Matriz de Correlación: Variables y Clusters', fontsize=20, fontweight='bold', pad=20)
    plt.tight_layout()
    print("💡 Mostrando matriz de correlación... (Cierre la ventana para continuar)")
    plt.show()

    # 7. Visualization of Clusters (Close vs Volume)
    centroids = kmeans_final.cluster_centers_
    close_idx = X_raw.columns.get_loc('close')
    volume_idx = X_raw.columns.get_loc('volume')

    plt.figure(figsize=(14, 8))
    # Use seaborn scatter plot for better aesthetics
    sns.scatterplot(data=df_clusters, x='close', y='volume', hue='cluster', palette='Spectral', alpha=0.6, s=60, edgecolor=None)
    
    # Draw the highlighted centroids
    plt.scatter(centroids[:, close_idx], centroids[:, volume_idx], s=250, c='black', marker='X', label='Centroides', edgecolors='white', linewidth=2)
    
    plt.title('Visualización de Clusters XAUUSD (K=15)', fontsize=22, fontweight='bold', pad=20)
    plt.xlabel('Precio de Cierre (Normalizado)', fontsize=16) # adding x-axis label
    plt.ylabel('Volumen (Normalizado)', fontsize=16) # adding y-axis label
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title='Cluster ID') # adding legend
    plt.grid(True, alpha=0.3) # adding grid to the plot
    plt.tight_layout() # use of tight_layout to adjust the plot
    print("💡 Mostrando visualización final de clusters... (Cierre la ventana para finalizar)")
    plt.show() # use of show to display the plot

    print("\n✨ ¡Proceso completado con éxito, Gracias por usar nuestro algoritmo!")

if __name__ == "__main__":
    run_kmeans_analysis()
