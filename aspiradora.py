"""
### Nombre del Programa: Agente Aspiradora                              #
//# Autor: Mónica Tahan                                                 #
//# Versión: 1.0                                                        #
//# Descripción: Algoritmo de Control de Aspiradora (Agente Inteligente)#
##

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# INICIALIZACION DE VARIABLES
"""
#Esto es un comentario de una linea
ir = False # Infrarrojo
proximidad = 100.0 # sensor de proximidad
sucio = False #Variable para saber si esta sucio o no

print ("Soy tu asistente de confianza para mantener limpio tu espacio\n")

entrada = input("Hay obstaculo:? por favor escriba si o no\n")

if entrada == "no":
    ir = False
else:
    ir = True
    print("Aspiradora Detenida por 60 segundos")
    print("Desplazar Aspiradora nuevamente")

while ir == False:

    proximidad = float(input("Indica la distancia del obstáculo con un valor numerico, por ejemplo 5.0: "))

    if proximidad >= 3.0:
        print("Desplazar Aspiradora")
        entrada2 = input("si esta sucio escriba Si, si no lo esta escriba no: ")
        if entrada2 == "no":
            sucio = False
        else:
            sucio = True
        if sucio == True:
            print("Aspirando")
        else:
            print("Deteniendo aspirado")
            print("Cambiando de Cuadricula")
            entrada = input("Hay obstaculo:? por favor escriba si o no: ")
            if entrada == "no":
                ir = False
            else:
                ir = True
    else:
        print("Desplazar Aspiradora")
        proximidad = float(input("Indica la distancia del obstáculo con un valor numerico, por ejemplo 5.0: "))
