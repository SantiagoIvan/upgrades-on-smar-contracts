# UPGRADES

Prueba de concepto de alguna de las formas de implementar mejoras sobre un smart contract, o si deployaste uno lleno de bugs

Inicialmente hay 3 formas diferentes:

### Parametrizando
Cualquier contrato dependiente o valor que nos interese cambiar en un futuro deberia estar parametrizado
junto con una funcion set para cambiarlo cuando queramos. 
    
    Si bien es bastante simple, no es para nada flexible, y ademas no nos permite modificar la logica del contrato. Otra cosa es que rompe con la descentralizacion, permitiendo que solo 1 admin pueda realizar los cambios

### Migracion
Esta forma sigue mas la filosofia de la inmutabilidad de los contratos, y debido a esto es que implementa un contrato totalmente nuevo sin relacion alguna con el anterior. Va de la mano con esa filosofia de que no deberia haber cambios sobre los contratos para evitar posibles fraudes. 

    Si bien te permite implementar la nueva logica de negocio requerida, es complejo realizar la migracion del todo el estado del contrato anterior al nuevo (ademas de caro). Ademas, a todos los demas usuarios que utilicen este contrato hay que convencerlos de que la nueva implementacion es la V2 y que dejen de utilizar la direccion anterior

### Proxy
La tercera forma es implementando un PRoxy, o Man in the middle, o en este caso Contract-in-the-middle (jajajjjjjj). Como funciona? 
    Se implementan 2 contratos, un contrato Proxy y contrato con la logica de negocio al cual llamaremos contrato Implementacion. Esto va a permitir ejecutar la logica de la Implementacion en el contexto del Proxy, mediante 'delegateCall'. Que quiere decir?
    Todo aquel que quiera interactuar con la Implementacion, en realidad sin darse cuenta va a estar interactuando con el contrato Proxy y este va a redirigir la llamada a la implementacion. el msg. sender va a ser igual al msg.sender original, que origino la llamada, lo mismo con los parametros y datos pasados. Se ejecuta la logica de la Implementacion, pero en el contexto del servidor Proxy. Esto que quiere decir? Que todas las variables y mapas que haya declarada en la Implementacion, en realidad van a estar viviendo en el Proxy, todos los datos estaran alli. En el proxy se declara una variable apuntando al admin, y otra apuntando al contrato Implementacion. De esta forma, si sale una nueva version de nuestro contrato, simplemente cambiamos la direccion de Implementacion.

#### Issues
Esto tiene 2 problemas, o 3 mejor dicho:
1 - *Decentralizacion*

   Si el que hace los cambios es solo 1 admin, estariamos rompiendo con esa decentralizacion. A menos que haya un protocolo de gobierno, y haya un grupo de usuarios votando

2 - *Storage Clashes*

   Colision entre variables. Solidity almacena las variables en spots, por lo que setear un valor de una funcion, en realidad va a modificar el valor de la variable que haya en ese spot. Si yo lanzo nuevas implementaciones, voy a tener en cuenta que no puedo cambiar el orden de las variables / funciones, porque sino se van a generar esas colisiones, y voy a estar sobrescribiendo viejas variables. Recordemos que los datos estaran guardados en el proxy, entonces si yo, en mi nueva implementacion, en el spot 0 cambio la variable por otra, cuando quiera modificar la misma en realidad se estara pisando el valor de la variable que habia antes en ese spot, introduciendo nuevos bugs y un comportamiento totalmente inesperado. (Ver video por si no se entiende) Si se desean agregar nuevas funciones o nuevas variables, se deben ir agregando al final. No podemos reordenar las viejas funcionalidades

3 - *Function Selector Clashes*

   En un contrato, cuando se ejecuta una funcion, se selecciona la funcion a ejecutar mediante una funcion de hash. Esta funcion de hash se basa en el nombre de la funcion y su firma. A esta funcion se la llama Function Selector. Puede ocurrir que diferentes funciones tengan el mismo hash (ver ejemplo en el video). En un contrato comun, ni va a compilar. Pero si tengo un Proxy y un contrato apuntando ? Lo que puede ocurrir en este escenario, es que a la hora de hacer delegateCall, esa funcion tenga el mismo hash que una funcion del Admin que se encuentre en el Proxy, u otra funcion, y se obtenga un comportamiento totalmente erratico.
![image](https://user-images.githubusercontent.com/48731203/160266140-49c9b6ad-7189-4936-ad33-cd71592315f5.png)
![image](https://user-images.githubusercontent.com/48731203/160266152-cde10911-0b6d-475d-9791-03a4c1e43b1c.png)

#### Soluciones
Esto nos lleva a 3 soluciones distintas:

1 - *Transparent Proxy Pattern*

   Admins solo pueden ejecutar logica de admin, en el Proxy, y no pueden por nada en el mundo ejecutar logica de negocio. De esta forma se evita el problema 3, donde podia ocurrir que alguien ejecute funciones de admin por accidente, o cualquier funcion. Los usuarios solo pueden ejecutar logica del contrato de Implementacion y los admins, solo la logica del Proxy

2 - *UUPs*:
    Universal Upgradeable Proxies
    
   Toda esa logica de admin para  upgradear estara incluida en el contrato de Implementacion, por lo tanto, si hay un problema de colision, el compilador no nos dejara compilar el contrato, evitando que ese error llegue a produccion.
   Esto tambien nos ahorra Gas, ya que es una lectura menos que se hace. (no se chequea en el proxy si el que hace la llamada es admin o no)
   Tambien achica el codigo del Proxy.

    Gran problema? Si deployas un contrato, sin ninguna logica de upgrade, literalmente te atascaste solito, y no te va a quedar otra que migrar.

3 - *Diamante*

   Te permite tenes multiples contratos de Implementacion a la vez. Esto tiene sentido si ya la logica de nuestro contrato es muy grande. En ese caso nos conviene fragmentar la logica en diferentes contratos (algo similar a partir el backend en diferentes servicios). De esta forma tendria diferentes contratos encargandose de una tarea en especifico. 
   Nos permite upgradear por servicio, sin necesidadde deployar todo el contrato entero, ahorrandonos dinero, ya que lo que se deploya es mucho mas pequeño que el contrato original.
    
    Contra? Se complejiza la logica del Proxy (encargado de delegar las llamadas a multiples contratos ahora). Todavia no hay un estandar claro sobre como trabajar con los Proxies. Es todo muy nuevo
