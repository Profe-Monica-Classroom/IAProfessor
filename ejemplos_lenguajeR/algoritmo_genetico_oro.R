#########################################################################################################
# RECURSO ACADÉMICO CREADO POR LA PROFESORA MÓNICA TAHAN CON EL USO DE GOOGLE ANTIGRAVITY               #
# ACADEMY RESOURCE CREATED BY PROFESSOR MÓNICA TAHAN WITH THE USE OF GOOGLE ANTIGRAVITY                 #
# Este script implementa un Algoritmo Genético (GA) para optimizar una estrategia con el Oro (XAUUSD)   #
# This script implements a Genetic Algorithm (GA) to optimize a strategy with Gold (XAUUSD)             #
# Product Owner: Prof. Mónica Tahan                                                                     #
# Autor: Mónica Tahan y Google Antigravity AI                                                           # 
# Author: Mónica Tahan and Google Antigravity AI                                                        #
# Versión: 1.0                                                                                          #
# Version: 1.0                                                                                          #
# Fecha: 03/03/2026                                                                                     # 
# Date: 03/03/2026                                                                                      #
# Licencia: GNU/GPL                                                                                     #
# License: GNU/GPL                                                                                      #
#########################################################################################################

# Instalación del paquete GA si no está disponible
# install.packages("GA")
# install.packages("readr")

library(GA) #genetic algorithm
library(readr) #read csv files

run_genetic_algorithm <- function() {
  cat("Iniciando algoritmo genético para optimizar una estrategia con el Oro (XAUUSD) en R...\n")
  
  # 1. Load data
  # The file is in the parent directory relative to this folder, but since we are working
  # in a context where the user often has the files in the same dir for R experiments:
  train_file <- "C:/Users/Lenovo/Clases_Unexpo/Inteligencia_Artificial/practica_python/IAProfessor/ejemplos_lenguajeR/XAUUSD..1.train.csv"
  
  #if (!file.exists(train_file)) {
    # If not in current, check parent
   # train_file <- "C:/Users/Lenovo/Clases_Unexpo/Inteligencia_Artificial/practica_python/IAProfessor/ejemplos_lenguajeR/XAUUSD..1.train.csv"
  }
  
 # if (!file.exists(train_file)) {
 #   stop(paste("Error: Archivo no encontrado", train_file))
  #}
  
  df <- read_csv(train_file, n_max = 1000) #dataframe for the first 1000 rows
  
  # 2. Prepare data
  X <- as.matrix(df[, c("open", "high", "low", "volume")])
  X <- scale(X)
  
  # Target: 1 if next close > current close, else 0
  n <- nrow(df)
  y <- as.numeric(df$close[2:n] > df$close[1:(n-1)])
  X <- X[1:(n-1), ]
  
  # 3. Fitness Function
  fitness_func <- function(weights) {
    predictions <- as.numeric((X %*% weights) > 0)
    accuracy <- mean(predictions == y)
    return(accuracy)
  }
  
  # 4. Run GA
  cat("Evolution started using GA package...\n")
  
  ga_result <- ga(type = "real-valued", 
                  fitness = fitness_func,
                  lower = rep(-1, 4), 
                  upper = rep(1, 4),
                  popSize = 50, 
                  maxiter = 50,
                  run = 20,
                  seed = 1234)
  
  # 5. Presentation
  cat("Evolution completed!\n")
  
  # Plotting
  plot(ga_result)
  
  cat(paste("\nResult: Best Accuracy achieved:", round(ga_result@fitnessValue * 100, 2), "%\n"))
  cat("Gracias por usar nuestro algoritmo evolutivo!\n")
}

run_genetic_algorithm()
