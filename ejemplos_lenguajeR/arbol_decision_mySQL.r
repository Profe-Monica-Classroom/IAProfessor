# Profesora Mónica Tahan
# Script para probar árboles de decisiones en R.
# se pretende predecir los EGRESOS DE INVENTARIO DE PRODUCTO DE UN ALMACÉN
# con datos de pruebas de un Almacén.
# Para este ejemplo se necesita R-part, rpart.plot y DBI

# Cargando las librerías:

library(rpart)
library(rpart.plot)
library(DBI)


# Estableciendo Conexión con Una base de datos MYSQL (Nombre DB: Inventarios)

con <- dbConnect(RMySQL::MySQL(), host = "localhost", dbname = "inventarios", username = "root", password = "1234", port = 3306)

#listando las tablas
dbListTables(con)


#Listando los campos de la tabla inventario_productos
dbListFields(con, "inventario_productos")

# Obteniendo los datos de la tabla a la variable data

data<-dbReadTable(con, "inventario_productos");
View(data)
dim(data) #Para comprobar la dimensión del data frame

#Obteniendo los datos que nos interesan de la muestra
n<-5000 #conteo de filas aleatorias para entrenamiento
m<-3000 #conteo de filas aleatorias para testing

muestra<-sample(1:nrow(data),size=n,replace=FALSE) #toma de muestra aleatoria
View(muestra)

muestra

#Variables necesarias:

Variables      <-c(1,2,3,4,5,6,7,8,9,10)               # variables elegidas segun las columnas del modelo

#Matriz de Entrenamiento

Entrenamiento<-data[muestra,]
View(Entrenamiento)
dim(Entrenamiento)
Entrenamiento  <-Entrenamiento[,Variables]           # tabla entrenamiento, cuyos datos son una muestra aleatoria
View(Entrenamiento)

#Matriz de Testing

muestra_test <-sample(1:nrow(data),size=m,replace=FALSE)
View(muestra_test)
Test<-data[muestra_test,]
Test<-Test [,Variables]           # tabla  Test
View(Test)
dim(Test)

# Creación del Árbol de Decisión:

ModeloArbol<-rpart(costo_total ~ .,data=Entrenamiento,parms=list(split="information"))

# Predicción de EGRESOS de Inventarios en la tabla Test

Prediccion <- predict(ModeloArbol, Test,type="class") # Prediccción en Test
MC         <- table(Test[, "costo_unitario"],Prediccion) # Matriz de Confusión

# Valores de la matriz de confusión
MC

# Datos contenidos en la variable Prediccion

View(Prediccion)
Prediccion

# Grafico de la Predicción

rpart.plot(ModeloArbol, type=1, extra=100,cex = .7,
           box.col=c("gray99", "gray88")[ModeloArbol$frame$yval])