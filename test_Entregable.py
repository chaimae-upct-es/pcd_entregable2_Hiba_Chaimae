import pytest
from Entregable2 import  SystemeLoT, Sensor, Systeme,Media_Desviacion, Cuantil, Max_Min, Umbral, Aumentar_temperatura,Arg_Error,  Observable


def test_instance():
    """Asegura que solo exista una instancia de la clase Singleton"""
    instance1 = SystemeLoT.get_instance()
    instance2 = SystemeLoT.get_instance()
    assert instance1 is instance2, "Singleton getInstance debe retornar la misma instancia"

def test_temperature():
    """Asegura que se devuelva una temperatura en el rango esperado"""
    sensor = Sensor()
    temperature = sensor.leer_temp()
    assert -20 <= temperature <= 50, "La Temperatura debe incluirse en ese rango"
    
def test_systeme():
    """Asegura que el método actualizar añade los datos correctamente a _datos"""
    systeme = Systeme()
    initial_count = len(systeme._datos)
    systeme.actualizar(('2024-05-08 12:00:00', 25))
    assert len(systeme._datos) == initial_count + 1, "La actualización debe incrementar los datos"


def test_media_desviacion():
    """Asegura que la media y desviación típica se calculan correctamente"""
    strategie = Media_Desviacion()
    dat = [20, 22, 24, 26, 28, 30]
    mean, sd = strategie.aplicarAlgoritmo(dat)
    assert mean == sum(dat) / len(dat), "La media debe ser calculada correctamente"
    assert isinstance(sd, float), "Desviación típica debe ser un tipo float"

def test_cuantil():
    """Asegura que los cuantiles se calculan correctamente"""
    strategie = Cuantil()
    dat = [20, 22, 24, 26, 28, 30]
    q1, q2, q3 = strategie.aplicarAlgoritmo(dat)
    temp_ord = sorted(dat)
    assert q1 == temp_ord[int(len(temp_ord) * 0.25)], "El primer cuantil debe ser calculado correctamente"
    assert q2 == temp_ord[int(len(temp_ord) * 0.50)], "El segundo cuantil debe ser calculado correctamente"
    assert q3 == temp_ord[int(len(temp_ord) * 0.75)], "El tercer cuantil debe ser calculado correctamente"

def test_max_min():
    """Asegura que el máximo y mínimo se calculan correctamente"""
    strategie = Max_Min()
    dat = [20, 22, 24, 26, 28, 30]
    maximo, minimo = strategie.aplicarAlgoritmo(dat)
    assert maximo == max(dat), "El máximo debe ser calculado correctamente"
    assert minimo == min(dat), "El mínimo debe ser calculado correctamente"



def test_error_regestracion():
    """Prueba de Error_regestracion al registrar y eliminar observador incorrectamente"""
    observable = Observable()
    with pytest.raises(Arg_Error):
        observable.registrar_obs("Not an Observer instance")
    with pytest.raises(Arg_Error):
        observable.eliminar_obs("Not an Observer instance")

def test_procesamiento(): 
    systeme = Systeme()
    data = [('2024-05-08 12:00:00', temp) for temp in range(10, 22)]
    for d in data:
        systeme.actualizar(d)
    # Esperamos que haya calculado estadísticas tras suficientes actualizaciones
    assert len(systeme._datos) >= 12, "El calculo estadistico ocurre tras suficientes actualizaciones"
            



def test_notificacion_obs():
    """Verifica que el observador reciba la notificación"""
    sensor = Sensor()
    systeme = Systeme()
    sensor.registrar_obs(systeme)
    sensor.notificar_obs(('2024-05-08 12:00:00', 25))
    assert systeme._datos[-1] == ('2024-05-08 12:00:00', 25), "El observador debe recibir la notificación"

def test_umbral():
    """Verifica que el manejador de umbral funcione correctamente"""
    umbral = Umbral(umbral=28)
    data = [20, 25, 30]
    umbral.manejar(data)
    assert data[-1] > umbral.umbral, "El último valor debe superar el umbral"

def test_aumento_temperatura():
    """Verifica que el manejador de aumento de temperatura funcione correctamente"""
    aumento = Aumentar_temperatura(aumento=10)
    data = [20, 22, 24, 35]
    aumento.manejar(data)
    temp_inicial = data[0]
    temp_aumento = list(filter(lambda temp: temp >= temp_inicial + aumento.aumento, data))
    assert len(temp_aumento) > 0, "Debe haber un aumento significativo en la temperatura"