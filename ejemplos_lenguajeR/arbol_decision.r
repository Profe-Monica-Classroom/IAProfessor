# Profesora Mónica Tahan
# Script para probar árboles de decisiones en R.
# Referencias: http://apuntes-r.blogspot.com/2014/09/predecir-perdida-de-clientes-con-arbol.html
# Tomando la referencia del ártículo mencionado en el link anterior, se pretende predecir pérdidas de clientes
# con datos de pruebas propios de la librerá C50 de R.
# Para este ejemplo se necesita R-part, rpart.plot  y C50.

# Cargando las librerías:

library(C50)
library(rpart)
library(rpart.plot)

# Obteniendo los datos

data(churn);
View(churn)

#Variables necesarias:

View(churnTrain)
View(churnTest)
Variables      <-c(4,7,16,19,17,20)               # variables elegidas
Entrenamiento  <-churnTrain[,Variables]           # tabla entrenamiento, cuyos datos son propios de la librería C50 de R
Test           <-churnTest [,Variables]           # tabla  Test

# Creación del Árbol de Decisión:

ModeloArbol<-rpart(churn ~ .,data=Entrenamiento,parms=list(split="information"))

# Predicción de desafiliaciones en la tabla Test

Prediccion <- predict(ModeloArbol, Test,type="class") # Prediccción en Test
MC         <- table(Test[, "churn"],Prediccion) # Matriz de Confusión

MC

# Datos contenidos en la variable Prediccion

Prediccion

# Valores de la matriz de confusión

MC

# Grafico de la Predicción

rpart.plot(ModeloArbol, type=1, extra=100,cex = .7,
           box.col=c("gray99", "gray88")[ModeloArbol$frame$yval])