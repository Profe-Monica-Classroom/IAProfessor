# Clase en Línea Sobre Redes Neuronales de Regresión con R Studio
# Prof. Mónica Tahan. monicatahan@gmail.com. Canal YouTube: http://www.youtube.com/monicatahan 
# Perfil Linkedin: 
# Unexpo Guarenas. Caracas - Venezuela
# LIBRERIAS NECESARIAS:
# NEURALNET, GGPLOT Y MASS
# Predicción de valores de Atención al Cliente
# -----------------------------------------------------

library(MASS); library(neuralnet); library(ggplot2); #library(DBI)
library(readr)
set.seed(65) #genera un numero aleatorio

# Estableciendo Conexión con Una base de datos MYSQL (Nombre DB: Inventarios)

#con <- dbConnect(RMySQL::MySQL(), host = "localhost", dbname = "inventarios", username = "root", password = "1234", port = 3306)

#listando las tablas
#dbListTables(con)


#Listando los campos de la tabla inventario_productos
#dbListFields(con, "inventario_productos")


Servicio_al_cliente <- read_delim("D:/Clases_Unexpo/Inteligencia_Artificial/ejemplos_R/Servicio_al_cliente1.csv", 
                                  delim = ";", escape_double = FALSE, trim_ws = TRUE)
View(Servicio_al_cliente)

# Obteniendo los datos de la tabla a la variable data

#datos<-as.data.frame(dbReadTable(con, "inventario_productos"));  #datos con los cuales se hará la red neuronal
datos<-Servicio_al_cliente;
View(datos)
datosnew<-subset(datos, select = -c(`antiguedad`,`cliente`,`calidadinstalaciones`))
View(datosnew)

n        <- nrow(datosnew) # con esta instrucción hacemos un conteo del número de filas
n
datos <- datosnew
muestra  <- sample(n, n * .800) # se toma una muestra aleatoria
muestra




# NORMALIZACION DE VARIABLES
# -----------------------------------------------------
maxs      <- apply(train, 2, max) #valores máximos para el entrenamiento
mins      <- apply(train, 2, min) #valores mínimos para el entrenamiento

datos_nrm <- as.data.frame(scale(datosnew, center = mins, scale = maxs - mins))

# Mostrando maxs y mins
#View(maxs)

#View(mins)

# Estructura del Conjunto de datos

#str(datos)

train    <- datos_nrm[muestra, ] # función de entrenamiento
View(train)
test     <- datos_nrm[-muestra, ] # función de prueba
View(test)


train_nrm <- train #datos[muestra, ]
test_nrm  <- test #datos[-muestra, ]

View(train_nrm)
View(test_nrm)


# FORMULA
# -----------------------------------------------------
nms  <- names(train_nrm)
ecuacion <- as.formula(paste("as.numeric(edad) ~", paste(nms[!nms %in% "edad"], collapse = " + ")))
ecuacion
str(nms)
str(ecuacion)


# MODELO
# -----------------------------------------------------
modelo.nn <- neuralnet(ecuacion,
                       data          = train_nrm,
                       hidden        = c(4,6), #  especifica una primera capa oculta con 5 neuronas y una segunda capa oculta con 3 neuronas. 
                       threshold     = 0.01,   #  indica que las iteraciones se detendran cuando el "Cambio" del error sea menor a 5% entre una iteracion de optimizacion y otra. Este "Cambio" es calculado como la derivada parcial de la funcion de error respecto a los pesos.
                       algorithm     = "rprop+" # refiere al algoritmo "Resilient Backpropagation", que actualiza los pesos considerando únicamente el signo del cambio, es decir, si el cambio del error es en aumento (+) o disminución (-) entre una iteración y otra.
)
modelo.nn

# PREDICCION
# -----------------------------------------------------
pr.nn   <- compute(modelo.nn,within(test_nrm,rm(edad)))

pr.nn

# se transforma el valor escalar al valor nominal original
inv.predict <- pr.nn$net.result*(max(datos$edad)-min(datos$edad))+min(datos$edad)
inv.real    <- (test_nrm$edad)*(max(datos$edad)-min(datos$edad))+min(datos$edad)

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
plot(modelo.nn)