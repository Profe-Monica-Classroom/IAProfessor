# Clase en Línea Sobre Redes Neuronales de Regresión con R Studio
# Prof. Mónica Tahan. monicatahan@gmail.com. Canal YouTube: http://www.youtube.com/monicatahan 
# Perfil Linkedin: 
# Unexpo Guarenas. Caracas - Venezuela
# LIBRERIAS NECESARIAS:
# NEURALNET, GGPLOT Y MASS
# Predicción de valores de Inflación y Dolar en Venezuela
# -----------------------------------------------------

library(MASS); library(neuralnet); library(ggplot2); #library(DBI)
library(readxl)
#set.seed(60) #genera un número aleatorio

# Estableciendo Conexión con Una base de datos MYSQL (Nombre DB Ejemplo: inventarios)

#con <- dbConnect(RMySQL::MySQL(), host = "localhost", dbname = "inventarios", username = "root", password = "1234", port = 3306)

#muestra_dolar_pib_inflacion_trimestral <- read_excel("~/Documentos/Clases_Unexpo/Inteligencia_Artificial/ejemplos_R/muestra_dolar_pib_inflacion_trimestral_categorico.xlsx")
muestra_dolar_pib_inflacion_trimestral<- read_excel("C:/Users/Lenovo/Clases_Unexpo/Inteligencia_Artificial/practica_python/IAProfessor/ejemplos_lenguajeR/muestra_dolar_pib_inflacion_trimestral_categorico.xlsx")

View(muestra_dolar_pib_inflacion_trimestral)
str(muestra_dolar_pib_inflacion_trimestral)

Variables      <-c(3,4,5,6)               # variables elegidas

# Obteniendo los datos de la tabla a la variable data

#datos<-as.data.frame(dbReadTable(con, "inventario_productos"));  #datos con los cuales se hará la red neuronal
datos<-muestra_dolar_pib_inflacion_trimestral;
View(datos)
datos <-datos[,Variables] 
datosnew<-datos
#datosnew<-subset(datos, select = -c(`Dolar`,`PIB`))
View(datosnew)

n        <- nrow(datosnew) # con esta instrucción hacemos un conteo del número de filas
n
datos <- datosnew
muestra  <- sample(n, n * .70) # se toma una muestra aleatoria
str(muestra)

train    <- datosnew[muestra, ] # función de entrenamiento
View(train)
test     <- datosnew[-muestra, ] # función de prueba
View(test)


# NORMALIZACION DE VARIABLES
# -----------------------------------------------------
maxs      <- apply(train, 2, max) #valores máximos para el entrenamiento
mins      <- apply(train, 2, min) #valores mínimos para el entrenamiento

# Mostrando maxs y mins
View(maxs)
maxs

View(mins)
mins
datos_nrm <- as.data.frame(scale(datosnew, center = mins, scale = maxs - mins))
# Estructura del Conjunto de datos

#str(datos)

train_nrm <- datos_nrm[muestra, ]
test_nrm  <- datos_nrm[-muestra, ]

View(train_nrm)
View(test_nrm)
str(test_nrm)

# FORMULA
# -----------------------------------------------------
nms  <- names(train_nrm)
nms
ecuacion <- as.formula(paste("as.numeric(Inflacion) ~", paste(nms[!nms %in% "Inflacion"], collapse = " + ")))
ecuacion
str(nms)
str(ecuacion)


# MODELO
# -----------------------------------------------------
modelo.nn <- neuralnet(ecuacion,
                       data          = train_nrm,
                       hidden        = c(4), #  especifica una primera capa oculta con 5 neuronas y una segunda capa oculta con 3 neuronas. 
                       threshold     = 0.01,   #  indica que las iteraciones se detendran cuando el "Cambio" del error sea menor a 1% entre una iteracion de optimizacion y otra. Este "Cambio" es calculado como la derivada parcial de la funcion de error respecto a los pesos.
                       algorithm     = "rprop+" # refiere al algoritmo "Resilient Backpropagation", que actualiza los pesos considerando únicamente el signo del cambio, es decir, si el cambio del error es en aumento (+) o disminución (-) entre una iteración y otra.
)
modelo.nn

# PREDICCION
# -----------------------------------------------------
pr.nn   <- compute(modelo.nn,within(test_nrm,rm(Inflacion)))
names(pr.nn)

plot(pr.nn$net.result)
pr.nn$neurons


# se transforma el valor escalar al valor nominal original
inv.predict <- pr.nn$net.result*(max(datos$Inflacion)-min(datos$Inflacion))+min(datos$Inflacion)
inv.real    <- (test_nrm$Inflacion)*(max(datos$Inflacion)-min(datos$Inflacion))+min(datos$Inflacion)

plot(inv.predict)

inv.predict
inv.real


# SUMA DE ERROR CUADRATICO
# -----------------------------------------------------
(se.nn <- sum((inv.real - inv.predict)^2)/nrow(test_nrm))


#GRAFICOS
# -----------------------------------------------------
# Errores
qplot(x=inv.real, y=inv.predict, geom=c("point","smooth"), method="lm", 
      main=paste("Real Vs Prediccion. Summa de Error Cuadratico=", round(se.nn,2)))
# Red
plot(modelo.nn, rep="best")
names(modelo.nn)

modelo.nn$err.fct
modelo.nn$act.fct
modelo.nn$startweights
modelo.nn$generalized.weights
modelo.nn$result.matrix