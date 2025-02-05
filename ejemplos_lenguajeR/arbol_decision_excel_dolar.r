# Autor: Prof. Monica Tahan
# Script para probar Arboles de decisiones en R.
# se pretende predecir el comportamiento del Dolar en Venezuela tomando como data informacion obtenida desde Internet
# BID, BCV, Dolar today. PIB, Inflación, Dolar (Mes y Año)
# con datos de pruebas.
# Para este ejemplo se necesita R-part, rpart.plot

# Cargando las librerias:

library(rpart) #Permite hacer el modelo de Arbol
library(rpart.plot) #Pemrite graficar el árbol
library(readr)
#library(DBI)
library(readxl) # Permite abrir archivos tipo excel


# Estableciendo Conexión

#con <- dbConnect(RMySQL::MySQL(), host = "localhost", dbname = "db730151864", username = "root", password = "1234", port = 3306)
#listando las tablas
#dbListTables(con)


#Listando los campos de la tabla
#dbListFields(con, "ps_order_detail")

muestra_dolar_pib_inflacion_trimestral <- read_excel("D:/Clases_Unexpo/Inteligencia_Artificial/ejemplos_R/muestra_dolar_pib_inflacion_trimestral_categorico.xlsx")
View(muestra_dolar_pib_inflacion_trimestral)


# Obteniendo los datos
data<-muestra_dolar_pib_inflacion_trimestral;
#data<-dbReadTable(con, "ps_order_detail");
View(data)
dim(data) #Para comprobar la dimensión del data frame (105 filas 5 columnas)

#Obteniendo los datos que nos interesan de la muestra
n<-74 #training size
m<-31 #testing size

n
m
muestra<-sample(1:nrow(data),size=n,replace=FALSE)

muestra

#Variables necesarias:

Variables<-c(2,4,5,6)               # variables elegidas

#Matriz de Entrenamiento
Entrenamiento<-data[muestra,]
View(Entrenamiento)


dim(Entrenamiento)

Entrenamiento  <-Entrenamiento[,Variables]           # tabla entrenamiento
View(Entrenamiento)
muestra_test <-sample(1:nrow(data),size=m,replace=FALSE)

test<-data[-muestra, ] # función de prueba
View(test)

Test<-test [,Variables]           # tabla  Test
View(Test)
# Creación del Árbol de Decisión:
dim(Test)

ModeloArbol<-rpart(`Mes` ~ `Inflacion`,data=Entrenamiento)#,parms=list(split="information"))

ModeloArbol

# Predicción de desafiliaciones en la tabla Test

Prediccion <- predict(ModeloArbol, Test,type="class") # Prediccción en Test
plot(Prediccion, col="lightgreen")

# Datos contenidos en la variable Prediccion

Prediccion



# Grafico de la Predicción
rpart.plot(ModeloArbol, box.col=c("lightblue", "green"))

rpart.plot(podaModeloArbol, type = 1, extra=100,cex = .6, box.col=c("lightblue", "green"))

