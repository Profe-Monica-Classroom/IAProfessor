# #####################################################
# Autor: Monica Tahan. mtahan@unexpo.edu.ve. Canal YouTube: http://www.youtube.com/monicatahan 
# Perfil Linkedin: 
# CLASIFICACION DE PRECIOS DEL ORO DESDE UNA MUESTRA CSV
# VERSION 1.0
# METODOS EMPLEADOS EN ESTE ALGORITMO: K means
# 
# -----------------------------------------------------

## --------------------------------------------------#
#               NOTA                                 #
##---------------------------------------------------#

## PAQUETES NECESARIOS:
# ------------------------------------------------------


# install.packages("e1071") # SVM packages
# install.packages("ggplot2")
# install.packages("quantmod")
# install.packages("corrplot")
# install.packages("lubridate")
# install.packages("forecast")
# install.packages("tidyverse")
# install.packages("caret") # package for machine learning using kmeans
# install.packages("scale")



library(ggplot2)
library(quantmod)
library(corrplot)
library(e1071)
library(lubridate)
library(tidyverse)
library(forecast)
library(readr)
library(caret)
library(scales)


##XAUUSD_60_real <- read.csv("~/Documentos/CORCARIBE/SVM_SR_MESSIAS/data/XAUUSD..60.csv")
# XAUUSD_60_real <- read.csv("~/Documentos/CORCARIBE/SVM_SR_MESSIAS/data/26_06_2021/XAUUSD..60.csv")
# XAUUSD_60_real <- read.csv("~/Documentos/CORCARIBE/SVM_SR_MESSIAS/data/05_07_2021/XAUUSD..60_M2021.csv")

XAUUSD_60TEST <- read_csv("C:/Users/Lenovo/Clases_Unexpo/Inteligencia_Artificial/practica_python/IAProfessor/ejemplos_lenguajeR/XAUUSD..1.test.csv")
View(XAUUSD_60TEST)
XAUUSD_60_real <- read_csv("C:/Users/Lenovo/Clases_Unexpo/Inteligencia_Artificial/practica_python/IAProfessor/ejemplos_lenguajeR/XAUUSD..1.train.csv")
View(XAUUSD_60_real)



XAUUSD_60<-as.data.frame(XAUUSD_60_real[, -c(1,2)])
View(XAUUSD_60)
str(XAUUSD_60)


head(XAUUSD_60)
XAUUSD_60_scale<-as.data.frame(scale(XAUUSD_60))

XAUUSD_60_scaletest<-as.data.frame(scale(XAUUSD_60TEST[, -c(1,2)]))


XAUUSD_60<-as.data.frame(XAUUSD_60_scale)
XAUUSD_60<-as.data.frame(XAUUSD_60)
str(XAUUSD_60)

## GRAFICANDO DATA SET PRECIO DE CIERRE VERSUS VOLUMEN

ggplot() + geom_point(aes(x = close, y = volume, color = close), data = XAUUSD_60) + ggtitle('Conjunto de Datos')

set.seed(1234)

## PARA SABER CUANTOS CENTROS HACER

wcss <- vector()
for(i in 1:20){
  wcss[i] <- sum(kmeans(XAUUSD_60, i, iter.max=10000)$withinss)
}

##Aplicamos m?todo del Codo para visualizar cu?ntos centroides son:

ggplot() + geom_point(aes(x = 1:20, y = wcss), color = 'blue') + 
  geom_line(aes(x = 1:20, y = wcss), color = 'blue') + 
  ggtitle("Método del Codo") + 
  xlab('Cantidad de Centroides k') + 
  ylab('WCSS')

#APLICAMOS KMEANS PARA 20 CENTROIDES SEGÚN LA GRÁFICA OBTENIDA ANTERIORMENTE

grupos <- kmeans(XAUUSD_60, 15, iter.max=10000) 
grupos$centers
grupos$cluster
XAUUSD_60<-as.data.frame(XAUUSD_60)
#XAUUSD_60<-as.data.frame(XAUUSD_60)
XAUUSD_60$cluster<- grupos$cluster

View(XAUUSD_60)
XAUUSD_60<-as.data.frame(XAUUSD_60)

correlacion<- cor(XAUUSD_60)
corrplot(correlacion)

##GRAFICANDO CENTROIDES CLOSE PRICE VS VOLUME

ggplot() + geom_point(aes(x = close, y = volume, color = cluster), data=XAUUSD_60, size = 2) +
  scale_colour_gradientn(colours=rainbow(4)) +
  geom_point(aes(x = grupos$centers[, 4], y = grupos$centers[, 5]), color = 'black', size = 3) + 
  ggtitle('Clusters de Datos con k = 10 / K-Medios') + 
  xlab('Close Price') + ylab('Volume')