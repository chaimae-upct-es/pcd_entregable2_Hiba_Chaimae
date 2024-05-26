from abc import ABC, abstractmethod
import time
import random
import datetime
from functools import reduce
import math

class Exp_Singleton(Exception): # Excepción para errores de Singleton
    pass 

class Arg_Error(Exception):  # Excepción para errores de argumentos
    pass

class Sensor_exp(Exception): # Excepción para errores del sensor
    pass

class Error_ejecucion(Exception): # Excepción para errores de ejecución
    pass



# Patron Singleton
class SystemeLoT:
    _unicaInstancia = None  # Variable de clase para almacenar la única instancia

    @classmethod
    def get_instance(cls): # Método para obtener la instancia única
        if cls._unicaInstancia is None: # Si no existe una instancia
            try:
                cls._unicaInstancia = cls() # Crear una nueva instancia
            except Exception as e:
                raise Exp_Singleton(f" instancia singleton no se ha podido crear : {str(e)}")
        return cls._unicaInstancia # Devolver la instancia única
    
    def _crearsysteme(self): # Método para crear un sistema
        return Systeme()
    
    def _crearSensor(self):  # Método para crear un sensor
        if not isinstance(self, SystemeLoT):
            raise Arg_Error("instancia incorrecta.")
        return Sensor()
    
    
    def iniciar(self, sensor):  # Método para iniciar la observación de temperatura
        if not isinstance(sensor, Sensor): # Verifica que el argumento es una instancia de Sensor
            raise Arg_Error(" sensor debe ser una instancia de Sensor.")
        try:
            return sensor.comenzar_observacion_temp()  # Iniciar la observación de temperatura
        except Sensor_exp as e:
            raise Error_ejecucion(f"Error de inicio: {str(e)}")
    
    def fin(self, sensor): # Método para finalizar la observación de temperatura
            if not isinstance(sensor, Sensor):
                raise Arg_Error("sensor debe ser una instancia de Sensor.")
            try:
                return sensor.fin_observacion_temp()  # Finalizar la observación de temperatura
            except Exception as e:
                raise Error_ejecucion(f"Error de finilizacion: {str(e)}")


 # Patron OBSERVER
class Observer(ABC):  # Clase abstracta para los observadores
    @abstractmethod
    def actualizar(self, evento): # Método abstracto para actualizar los observadores
        pass

    
class Systeme(Observer): # Clase del sistema que implementa el patrón Observer
    def __init__(self):
        super().__init__()
        self._datos = [] # Lista para almacenar datos de temperatura
        self.aumento = Aumentar_temperatura() # Inicializa el manejador de aumento de temperatura
        self.umbral = Umbral(successor=self.aumento, umbral=28) # Inicializa el manejador de umbral
        self.estadisticos = Estadisticos(successor=self.umbral)  # Inicializa el manejador de estadísticos
    
    def actualizar(self, evento): # Método para actualizar el sistema con nuevos datos de temperatura
        self._datos.append(evento) # Agrega el evento a la lista de datos
        print(" nueva temperatura recibida: ", evento) # Imprime el nuevo evento
        self.calculo_estadisticos(self._datos) # Calcula los estadísticos de los datos
    
    def consulta_temp(self): # Método para consultar la última temperatura registrada
        return self._datos[-1][1] # Devuelve la temperatura del último evento
    
    def calculo_estadisticos(self,evento): # Método para calcular los estadísticos de los datos
        d_temp = [] # Lista para almacenar las temperaturas
        if len(evento)>12: # Si hay más de 12 eventos
            for i in evento[-13:]: # Toma los últimos 13 eventos
                d_temp.append(i[1]) # Agrega la temperatura a la lista
        else:
            for i in evento: # Si hay menos de 13 eventos
                d_temp.append(i[1]) # Agrega la temperatura a la lista
        self.estadisticos.manejar(d_temp) # Llama al manejador de estadísticos

class Error_registracion(Exception):  # Excepción para errores de registro
    pass   

class Observable:
    def __init__(self):
        self.observers = []  # Lista para almacenar los observadores

    def registrar_obs(self, observer): # Método para registrar un observador
        if not isinstance(observer, Observer):
            raise Arg_Error("observer debe ser una instancia de Observer")
        try:
            self.observers.append(observer)  # Agrega el observador a la lista
        except Exception as e:
            raise Error_registracion(f"ha producido un error al registrar el observador: {str(e)}")

    def eliminar_obs(self, observer): # Método para eliminar un observador
        if not isinstance(observer, Observer):
            raise Arg_Error("observer debe ser una instancia de Observer.")
        try:
            self.observers.remove(observer) # Elimina el observador de la lista
        except ValueError:
            raise Error_registracion("El observador no está  y no se puede borrar.")

    def notificar_obs(self, evento): # Método para notificar a los observadores
        for observer in self.observers:
            observer.actualizar(evento)   # Llama al método actualizar de cada observador

class Sensor (Observable): 
    def __init__(self):
        super().__init__()
        self.dato = 0 # Inicializa el dato del sensor
        self.ejecucion = False # Inicializa el estado de ejecución

    def leer_temp(self): # Método para leer la temperatura
        return round(random.uniform(-20, 50)) # Devuelve una temperatura aleatoria entre -20 y 50 grados

    
    def comenzar_observacion_temp(self): # Método para comenzar la observación de temperatura
        self.ejecucion = True # Establece el estado de ejecución a True
        while self.ejecucion: # Bucle mientras esté en ejecución
            temps=int(time.time()) # Obtiene el tiempo actual en segundos
            hora = datetime.datetime.fromtimestamp(temps) # Convierte el tiempo en un objeto datetime
            hora = hora.strftime('%Y-%m-%d %H:%M:%S') # Formatea la hora
            temperature = self.leer_temp() # Lee la temperatura
            self.dato = (hora, temperature) # Almacena la hora y la temperatura en el dato
            self.notificar_obs(self.dato) # Notifica a los observadores con el nuevo dato
            time.sleep(5)  # Espera 5 segundos

    def fin_observacion_temp(self): # Método para finalizar la observación de temperatura
        self.ejecucion=False  # Establece el estado de ejecución a False
    


# PATRON Chain of Responsibility
class Error_proceso(Exception): # Excepción para errores de procesamiento
    pass

class Manejador: 
    def __init__(self, successor=None): 
        self.successor = successor

    def manejar(self, data):  # Método para manejar los datos
        try:
            if self.successor:
                self.successor.manejar(data)  # Llama al manejador sucesor si existe
        except Exception as e:
            raise Error_proceso(f"Error en el  procesamiento de  datos de temperatura: {str(e)}")

class Estadisticos(Manejador):
    
    def __init__(self, successor=None):
        super().__init__(successor)
        self.strategies = {
            '\tMedia y Desviacion': Media_Desviacion(), # Inicializa la estrategia Media y Desviacion
            '\tCuantiles': Cuantil(), # Inicializa la estrategia Cuantiles
            '\tMax y Min': Max_Min() # Inicializa la estrategia Max y Min
        }

    def manejar(self, data): # Método para manejar los datos
        if len(data)==13: # Si hay 13 datos
            results = {name: strategy.aplicarAlgoritmo(data) for name, strategy in self.strategies.items()} # Aplica cada estrategia a los datos
            print("Estadísticos calculados en los últimos 60 segundos:") # Imprime los estadísticos calculados
            for clave, value in results.items():
                print(f"{clave}: {value}") # Imprime cada resultado
                
        if self.successor: 
            self.successor.manejar(data) # Llama al manejador sucesor si existe

class Umbral(Manejador):
    def __init__(self, successor=None, umbral=28):
        super().__init__(successor)
        self.umbral = umbral

    def manejar(self, data):
        if data[-1] > self.umbral: # Si la última temperatura supera el umbral
            print(f" La temperatura: {data[-1]}°C supera el umbral de {self.umbral}°C")       
        if self.successor:
            self.successor.manejar(data) # Llama al manejador sucesor si existe

class Aumentar_temperatura(Manejador):
    def __init__(self, successor=None,aumento=10):
        super().__init__(successor)
        self.aumento=aumento
    
    def manejar(self, data):
        if len(data) > 6: # Si hay más de 6 datos
            data=data[-7:]  # Toma los últimos 7 datos
            temp_inicial = data[0] # Obtiene la temperatura inicial
            temp_aumento = list(filter(lambda temp: temp >= temp_inicial + self.aumento, data)) # Filtra las temperaturas que han aumentado más del valor de aumento
            if len(temp_aumento)>0:
                print(f" La temperatura aumentó más de 10°C en los últimos 30 segundos")
        
        if self.successor: 
            self.successor.manejar(data) # Llama al manejador sucesor si existe


# Patron Strategy

class Strategie: 
    def aplicarAlgoritmo(self, dat): # Método abstracto para aplicar el algoritmo
        pass

class Media_Desviacion(Strategie):
    def aplicarAlgoritmo(self, dat):
        if not dat:  
            return None, None
        media = round(reduce(lambda x, y: x + y, dat) / len(dat), 2) # Calcula la media de los datos
        varianza = reduce(lambda x, y: x + y, map(lambda temp: (temp - media) ** 2, dat)) / len(dat) # Calcula la varianza de los datos
        desviacion_tipica = round(math.sqrt(varianza), 2) # Calcula la desviación estándar
        return media, desviacion_tipica # Devuelve la media y la desviación estándar


class Cuantil(Strategie): 
    def aplicarAlgoritmo(self, dat):
        if not dat: 
            return None, None, None
        temp_ord = sorted(dat) # Ordena los datos
        Q1 = temp_ord[int(len(temp_ord) * 0.25)] # Calcula el primer cuartil
        Q2 = temp_ord[int(len(temp_ord) * 0.50)] # Calcula la mediana
        Q3 = temp_ord[int(len(temp_ord) * 0.75)]  # Calcula el tercer cuartil
        return Q1, Q2, Q3 # Devuelve los cuantiles
    
class Max_Min(Strategie):  
    def aplicarAlgoritmo(self, dat):
        if not dat:
            return None, None
        
        maximo = reduce(lambda x, y: x if x > y else y, dat)  # Calcula el máximo de los datos
        minimo = reduce(lambda x, y: x if x < y else y, dat) # Calcula el mínimo de los datos
        return maximo, minimo
    
if __name__ == "__main__":
    
    try:
        sistema = SystemeLoT.get_instance()
        sistema_observador = sistema._crearsysteme()
        sensor = sistema._crearSensor()
        
        sensor.registrar_obs(sistema_observador)
        
        print("Iniciando la observación de temperatura...")
        sistema.iniciar(sensor)
        
        # Esperar un tiempo para recibir algunas lecturas
        time.sleep(60)
        
        print("Finalizando la observación de temperatura...")
        sistema.fin(sensor)
    except Exp_Singleton as e:
        print(f"Error Singleton: {str(e)}")
    except Arg_Error as e:
        print(f"Error de Argumento: {str(e)}")
    except Sensor_exp as e:
        print(f"Error del Sensor: {str(e)}")
    except Error_ejecucion as e:
        print(f"Error de Ejecución: {str(e)}")
    except Error_registracion as e:
        print(f"Error de registracion: {str(e)} ")
    except Error_proceso as e:
        print(f"Error de procesamiento:{str(e)}")