# LIBRERIAS NECESARIAS:
# NEURALNET, GGPLOT Y MASS
# Predicción de valores de Viviendas en la Ciudad de Boston, con datos de la librería MASS
# Ejemplo tomado de: http://apuntes-r.blogspot.com/2015/12/regresion-con-red-neuronal.html
# -----------------------------------------------------
library(MASS); library(neuralnet); library(ggplot2)
set.seed(65)

datos    <- Boston # Este set de datos pertenece a la librerías MASS, es un conjunto de datos de pruebas que ésta posee
View(datos)
n        <- nrow(datos) # con esta instrucción hacemos una normalización de datos.
n

muestra  <- sample(n, n * .70) # se toma una muestra aleatoria
muestra

train    <- datos[muestra, ] # función de entrenamiento
test     <- datos[-muestra, ] # función de prueba


# NORMALIZACION DE VARIABLES
# -----------------------------------------------------
maxs      <- apply(train, 2, max) #valores máximos para el entrenamiento
mins      <- apply(train, 2, min) #valores mínimos para el entrenamiento

# Mostrando maxs y mins
maxs
mins

datos_nrm <- as.data.frame(scale(datos, center = mins, scale = maxs - mins))
View(datos_nrm)

train_nrm <- datos_nrm[muestra, ]
test_nrm  <- datos_nrm[-muestra, ]

train_nrm
View(test_nrm)


# FORMULA
# -----------------------------------------------------
nms  <- names(train_nrm)

frml <- as.formula(paste("medv ~", paste(nms[!nms %in% "medv"], collapse = " + ")))

nms
frml


# MODELO
# -----------------------------------------------------
modelo.nn <- neuralnet(frml,
                       data          = train_nrm,
                       hidden        = c(7,5), #  especifica una primera capa oculta con 7 neuronas y una segunda capa oculta con 5 neuronas. 
                       threshold     = 0.05,   #  indica que las iteraciones se detendran cuando el "Cambio" del error sea menor a 5% entre una iteracion de optimizacion y otra. Este "Cambio" es calculado como la derivada parcial de la funcion de error respecto a los pesos.
                       algorithm     = "rprop+" # refiere al algoritmo "Resilient Backpropagation", que actualiza los pesos considerando únicamente el signo del cambio, es decir, si el cambio del error es en aumento (+) o disminución (-) entre una iteración y otra.
)
modelo.nn

# PREDICCION
# -----------------------------------------------------
pr.nn   <- compute(modelo.nn,within(test_nrm,rm(medv)))

pr.nn

# se transforma el valor escalar al valor nominal original
medv.predict <- pr.nn$net.result*(max(datos$medv)-min(datos$medv))+min(datos$medv)
medv.real    <- (test_nrm$medv)*(max(datos$medv)-min(datos$medv))+min(datos$medv)

medv.predict
medv.real


# SUMA DE ERROR CUADRATICO
# -----------------------------------------------------
(se.nn <- sum((medv.real - medv.predict)^2)/nrow(test_nrm))


#GRAFICOS
# -----------------------------------------------------
# Errores
qplot(x=medv.real, y=medv.predict, geom=c("point","smooth"), method="lm", 
      main=paste("Real Vs Prediccion. Summa de Error Cuadratico=", round(se.nn,2)))
# Red
plot(modelo.nn)