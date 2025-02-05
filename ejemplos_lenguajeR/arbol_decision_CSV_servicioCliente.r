# Profesora Mónica Tahan
# Script para probar árboles de decisiones en R.
# se pretende predecir el comportamiento de los vendedores en un área de servicio al cliente
# con datos de pruebas.
# Para este ejemplo se necesita R-part, rpart.plot

# Cargando las librerías:

library(rpart)
library(rpart.plot)
library(readr)
#library(DBI)


# Estableciendo Conexión

#con <- dbConnect(RMySQL::MySQL(), host = "localhost", dbname = "db730151864", username = "root", password = "1234", port = 3306)
#listando las tablas
#dbListTables(con)


#Listando los capos de la tabla ps_order
#dbListFields(con, "ps_order_detail")

servicioCliente <- read_delim("~/Documentos/Clases_Unexpo/Inteligencia_Artificial/ejemplos_R/Servicio_al_cliente.csv", ";", escape_double = FALSE, trim_ws = TRUE)

View(servicioCliente)
# Obteniendo los datos
data<-servicioCliente;
#data<-dbReadTable(con, "ps_order_detail");
View(data)
dim(data) #Para comprobar la dimensión del data frame (37 filas 13 columnas)

#Obteniendo los datos que nos interesan de la muestra
n<-23
m<-14
muestra<-sample(1:nrow(data),size=n,replace=FALSE)
View(muestra)

muestra

#Variables necesarias:

Variables      <-c(1,2,3,4,5,6,9,10,12,13)               # variables elegidas

#Matriz de Entrenamiento
Entrenamiento<-data[muestra,]
View(Entrenamiento)




Entrenamiento  <-Entrenamiento[,Variables]           # tabla entrenamiento
View(Entrenamiento)
muestra_test <-sample(1:nrow(data),size=m,replace=FALSE)
View(muestra_test)
Test<-data[muestra_test,]
Test<-Test [,Variables]           # tabla  Test
View(Test)
# Creación del Árbol de Decisión:

ModeloArbol<-rpart(`Nombre Cliente` ~ `Velocidad Cajas`,data=Entrenamiento)#,parms=list(split="information"))

# Predicción de desafiliaciones en la tabla Test

Prediccion <- predict(ModeloArbol, Test,type="class") # Prediccción en Test
plot(Prediccion, col="lightgreen")

# Datos contenidos en la variable Prediccion

Prediccion



# Grafico de la Predicción
rpart.plot(ModeloArbol, type = 1, extra=100,cex = .6, box.col=c("lightblue", "green"))
