## LIBRERIAS REQUERIDAS EN ESTE SCRIPT:
library(RPostgreSQL) # para que utilice el driver de Postgresql
library(ggplot2);
# Para clasificar con rpart
library(rpart)
library(rpart.plot)
# Para clasificar con randomForest
#library(useful)
#library(randomForest)

drv <- dbDriver("PostgreSQL") #llamada al driver de PostgreSQL
con <- dbConnect(drv,dbname="olap_axcosmetics",host="localhost",port=5432,user="finsumos",password="finsumos")
## LISTADO DE LAS TABLAS
dbListTables(con)
##SELECCIÓN DE LOS DATOS

datosax <- dbGetQuery(con, statement = "select id_zona, nombrezona, rubroid, cantidadprodorden, prodfavorite, totalorden from axcosmetics.fact_pedidos");
catalogo<- dbGetQuery(con, statement = "select id_catalogo, campana from axcosmetics.dim_catalogos where id_catalogo >=329 and id_catalogo<=500");
View(datosax)
View(catalogo)

dim(datosax) # establece la dimensión de datosax
summary(datosax) # muestra la estructura de datosax


#Muestra un gráfico de histograma con los datos, respecto al campo id_zona
f1<-hist(datosax$id_zona, main="Histogramas de Ventas", col = "blue", labels=TRUE)
f1
#Correlación de los datos para las columnas mencionadas

cor(datosax[,c("id_zona","cantidadprodorden", "prodfavorite", "totalorden")], use = "complete")


# Para graficar los datos respecto a las variables mencionadas

plot(datosax[,c("id_zona","cantidadprodorden", "prodfavorite", "totalorden")], col="blue")


##f7<-ggplot(datosax, aes(x=id_zona, y=totalorden)) + geom_point(, col="blue")

ggplot(datosax, aes(x=id_zona, y=totalorden)) + geom_point()
ggplot(datosax, aes(x=id_zona, y=totalorden)) + geom_point(aes(size=totalorden), col="blue")

##APLICA UNA FUNCIÓN A CADA CELDA DE UNA MATRIZ IRREGULAR
tapply(datosax$totalorden, datosax$nombrezona, mean)

# RELACIÓN DE ÓRDENES COLOCADAS POR ZONA

ggplot(datosax, aes(x=id_zona, y=totalorden, color=nombrezona)) + geom_point(aes(size=totalorden))


#Obteniendo los datos que nos interesan de la muestra
n<-200000 #conteo de filas aleatorias para entrenamiento
m<-50000 #conteo de filas aleatorias para testing

muestra<-sample(1:nrow(datosax),size=n,replace=FALSE) #toma de muestra aleatoria
#View(muestra)

muestra
#Variables necesarias:

Variables      <-c(1,2,4,5,6)               # variables elegidas segun las columnas del modelo
Variables
#Matriz de Entrenamiento

Entrenamiento<-datosax[muestra,]
View(Entrenamiento)
dim(Entrenamiento)
Entrenamiento  <-Entrenamiento[,Variables]           # tabla entrenamiento, cuyos datos son una muestra aleatoria
View(Entrenamiento)


#Matriz de Testing

muestra_test <-sample(1:nrow(datosax),size=m,replace=FALSE)
View(muestra_test)
Test<-datosax[muestra_test,]
Test<-Test [,Variables]           # tabla  Test
View(Test)
dim(Test)

# Creación del Árbol de Decisión:

ModeloArbol<-rpart(nombrezona ~ .,data=Entrenamiento)#,parms=list(split="information"))
str(ModeloArbol)
View(ModeloArbol$frame)
# Predicción de EGRESOS de Inventarios en la tabla Test

Prediccion <- predict(ModeloArbol, newdata=Test,type="class") # Prediccción en Test
MC         <- table(Test[, "totalorden"],Prediccion) # Matriz de Confusión
plot(Prediccion, col="lightgreen")
# Valores de la matriz de confusión
MC

# Datos contenidos en la variable Prediccion

Prediccion
print(ModeloArbol)
# Grafico de la Predicción

rpart.plot(ModeloArbol, type = 1, extra=100,cex = .6, box.col=c("lightblue", "green"))

summary(ModeloArbol)
printcp(ModeloArbol)
plotcp(ModeloArbol, col="red")

table(Prediccion, Test$nombrezona)
sum(Prediccion ==Test$nombrezona)/length(Test$nombrezona)*100

#PODANDO EL ÁRBOL

podaModeloArbol <- prune(ModeloArbol, cp = ModeloArbol$cptable[which.min(ModeloArbol$cptable[, "xerror"]), "CP"])
podaModeloArbol<- prune(ModeloArbol, cp=0.02)

rpart.plot(podaModeloArbol, type = 1, extra=100,cex = .6, box.col=c("lightblue", "green"))
