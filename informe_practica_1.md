# Practica 1 - Saturacion del uplink en hora punta en campus

## Objetivo

Se ha dimensionado la capacidad uplink de una celula en una zona exterior de campus durante el cambio de clase. El foco esta en estimar cuantos terminales pueden transmitir simultaneamente antes de alcanzar una carga operativa proxima al limite, considerando mezcla de servicios, movilidad y calidad del control de potencia.

## Hipotesis de calculo

- Sistema WCDMA/UMTS con W = 3.84 MHz.
- Perfiles de servicio de 12.2 kb/s, 32 kb/s y 64 kb/s.
- Velocidades de 3, 15 y 50 km/h.
- Factor de actividad entre 0.40 y 0.70.
- Factor de interferencia intercelular de referencia i = 0.65.
- Umbral objetivo de carga uplink igual a 0.70.
- Dos escenarios: control de potencia eficaz y control de potencia degradado.

El modelo usa una aproximacion clasica de carga uplink. La carga por usuario aumenta cuando sube la tasa binaria, cuando empeora el control de potencia y cuando la movilidad obliga a reservar mas margen frente al desvanecimiento rapido.

## Resultado principal

La capacidad uplink es especialmente sensible a los usuarios de subida intensiva y a la movilidad. En el escenario degradado, la penalizacion es clara incluso con actividad media, porque el requisito efectivo de Eb/N0 aumenta y cada terminal consume mas fraccion del presupuesto de interferencia.

En terminos operativos, la mezcla de servicios importa mas que el numero bruto de terminales. Un grupo pequeno de sesiones de 64 kb/s puede desplazar a muchas sesiones ligeras de 12.2 kb/s, por lo que la admision debe considerar carga proyectada y no solo contador de usuarios conectados.

## Recomendacion para el gestor de red

Se recomienda usar una regla de admision por carga:

1. Admitir sesiones normales mientras la carga estimada sea menor que 0.70.
2. Entre 0.70 y 0.72, permitir solo sesiones ligeras o ya establecidas y posponer nuevas subidas intensivas.
3. A partir de 0.72, bloquear nuevas sesiones de 64 kb/s y forzar reintento diferido para sincronizacion en segundo plano.

Esta politica reduce el riesgo de acercarse al punto de saturacion uplink y protege la experiencia de servicios mas sensibles a retardo y perdida, como audio corto o videollamada breve.

## Discusion tecnica

El uplink es mas sensible que el downlink a la mezcla de usuarios porque cada terminal contribuye directamente a la interferencia agregada en la estacion base. Si el control de potencia no compensa bien las diferencias de trayecto o el canal cambia demasiado rapido, algunos terminales transmiten por encima de lo necesario y elevan el suelo de interferencia para todos.

Ademas, el aumento de velocidad empeora el seguimiento del canal y obliga a reservar margen adicional frente a desvanecimiento rapido. Ese margen se traduce en mayor potencia recibida requerida y, por tanto, en mas carga por usuario. La consecuencia practica es una reduccion del numero maximo de sesiones simultaneas justo en el momento en que la movilidad del campus es mayor.

## Extension opcional

Como paso siguiente, el notebook puede ampliarse con trazas de movilidad reales del campus, diferenciando peatones, bicicletas y vehiculo de mantenimiento para reemplazar la movilidad generica por un mapa mas realista.