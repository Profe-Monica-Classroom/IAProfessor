# Profesora Mónica Tahan
# Script para probar árboles de decisiones en R.
# se pretende predecir los artículos que más de van a vender en una tienda online Para ello 
# con datos de pruebas de una tienda online.
# Para este ejemplo se necesita R-part, rpart.plot

# Cargando las librerías:

library(rpart)
library(rpart.plot)
library(DBI)


# Estableciendo Conexión

con <- dbConnect(RMySQL::MySQL(), host = "localhost", dbname = "db730151864", username = "root", password = "1234", port = 3306)
#listando las tablas
dbListTables(con)


#Listando los capos de la tabla ps_order
dbListFields(con, "ps_order_detail")

# Obteniendo los datos

data<-dbReadTable(con, "ps_order_detail");
View(data)
dim(data) #Para comprobar la dimensión del data frame (27 filas 44 columnas)

#Obteniendo los datos que nos interesan de la muestra
n<-15
m<-10
muestra<-sample(1:nrow(data),size=n,replace=FALSE)
View(muestra)

muestra

#Variables necesarias:

Variables      <-c(1,2,6,7,8,14)               # variables elegidas

#Matriz de Entrenamiento
Entrenamiento<-data[muestra,]
View(Entrenamiento)




Entrenamiento  <-Entrenamiento[,Variables]           # tabla entrenamiento, cuyos datos son propios de la librería C50 de R
View(Entrenamiento)
muestra_test <-sample(1:nrow(data),size=m,replace=FALSE)
View(muestra_test)
Test<-data[muestra_test,]
Test<-Test [,Variables]           # tabla  Test
View(Test)
# Creación del Árbol de Decisión:

ModeloArbol<-rpart(product_price ~ .,data=Entrenamiento,parms=list(split="information"))

# Predicción de desafiliaciones en la tabla Test

Prediccion <- predict(ModeloArbol, Test,type="class") # Prediccción en Test
MC         <- table(Test[, "product_price"],Prediccion) # Matriz de Confusión

MC

# Datos contenidos en la variable Prediccion

Prediccion

# Valores de la matriz de confusión

MC

# Grafico de la Predicción

rpart.plot(ModeloArbol, type=1, extra=100,cex = .7,
           box.col=c("gray99", "gray88")[ModeloArbol$frame$yval])