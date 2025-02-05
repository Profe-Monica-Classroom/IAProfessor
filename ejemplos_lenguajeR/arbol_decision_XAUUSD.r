# Profesora Mónica Tahan
# Script para elaborar un árbol de decisiones en R.
# se pretende predecir el comportamiento de la bolsa en ...
# Origen de los Datos: 
# 
# Para este ejemplo se necesita R-part, rpart.plot

# Cargando las librerías:

library(rpart) #Permite hacer el modelo de árbol
library(rpart.plot) #Pemrite graficar el árbol
library(readr)
#library(DBI)
library(readxl) # Permite abrir archivos tipo excel


library(readr)
XAUUSD_240 <- read_delim("~/Descargas/XAUUSD..240.csv", ";", escape_double = FALSE, trim_ws = TRUE)

View(XAUUSD_240)


# Obteniendo los datos
data<-XAUUSD_240;

View(data)
dim(data) #Para comprobar la dimensión del data frame (37 filas 13 columnas)

#Obteniendo los datos que nos interesan de la muestra
n<-1895 #training size
m<-812 #testing size

n
m
muestra<-sample(1:nrow(data),size=n,replace=FALSE)
View(muestra)

muestra

#Variables necesarias:

Variables      <-c(1,2,3,4,5,6)               # variables elegidas

#Matriz de Entrenamiento
Entrenamiento<-data[muestra,]
View(Entrenamiento)


dim(Entrenamiento)

Entrenamiento  <-Entrenamiento[,Variables]           # tabla entrenamiento
View(Entrenamiento)
muestra_test <-sample(1:nrow(data),size=m,replace=FALSE)
View(muestra_test)
muestra_test
Test<-data[muestra_test,]
Test<-Test [,Variables]           # tabla  Test
View(Test)
# Creación del Árbol de Decisión:

ModeloArbol<-rpart(Volume ~ Apertura + Maximo + Minimo + Cierre ,data=Entrenamiento,parms=list(split="information"))

ModeloArbol

# Predicción de desafiliaciones en la tabla Test

Prediccion <- predict(ModeloArbol, Test) # Prediccción en Test
plot(Prediccion, col="lightgreen")

# Datos contenidos en la variable Prediccion

Prediccion



# Grafico de la Predicción
rpart.plot(ModeloArbol, type = 1, extra=100,cex = .6, box.col=c("lightblue", "green"))
