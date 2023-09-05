#importo framework
import os
from flask import Flask
from flask import render_template, request, redirect, session #el request y el redirect son para el formulario
from flaskext.mysql import MySQL
from datetime import datetime
from flask import send_from_directory

#creando aplicacion con la base de datos
app= Flask(__name__)
app.secret_key="admin_activo" #uso de variables de session
mysql=MySQL()

app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='sitio1'
mysql.init_app(app)

#ruta de inicio/escape por default
@app.route('/')
def inicio():
    return render_template('sitio/index.html')

@app.route('/imagenes/<imagen>')
def imagenes(imagen):
    # print(imagen)
    return send_from_directory(os.path.join('templates/sitio/imagenes'),imagen)

@app.route('/css/<estilos>')
def css_link(estilos):
    return send_from_directory(os.path.join('templates/sitio/css'),estilos)



@app.route('/libros')
def libros():

    conexion=mysql.connect() #conexion con la base de datos sql
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM `libros`")
    libros = cursor.fetchall() #trae todos los registros y los guarda en libros
    conexion.commit()

    return render_template('sitio/libros.html', libros=libros)

@app.route('/nosotros')
def nosotros():
    return render_template('sitio/nosotros.html')

@app.route('/admin/')
def admin_index():
    
    if not 'login' in session:
        return redirect('/admin/login')
        
    return render_template('admin/index.html')


@app.route('/admin/login') 
def admin_login():
    return render_template('admin/login.html')


@app.route('/admin/login', methods=['POST']) 
def admin_login_post():

    _usuario=request.form['txtUsuario']
    _password=request.form['txtPassword']
    
    conexion=mysql.connect() #conexion con la base de datos sql
    cursor = conexion.cursor() #conexion busqueda
    cursor.execute("SELECT password FROM `usuarios` WHERE usuario = %s", (_usuario)) #ejecicion de busqueda
    _pass = cursor.fetchone() #trae un solo registro y lo guardo en variable
    conexion.commit()  #guardo los cambios
        
    if not _pass: # o if _pass == None: si no existe o no se admite
        return render_template('admin/login.html', mensaje="Acceso denegado")

    if _password in _pass:
        session['login'] = True # mantiene la sesion abierta
        session['usuario'] = _usuario # nombre a cargo de la sesion
        return redirect('/admin')
   
    return render_template('admin/login.html') #si password no esta en pass entonces me redirije
    

@app.route('/admin/registro')
def admin_registro():
    return render_template('admin/registro.html')


@app.route('/admin/registro', methods=['POST'])#
def admin_registro_post():
    #capturo datos del usuario
    _usuario=request.form['txtUsuario']
    _password=request.form['txtPassword']
    
    if _usuario=='' or _password=='':
        return render_template('admin/registro.html', mensaje1="Ingresa un usuario y/o contraseña válido.")

    sql = "INSERT INTO `usuarios`(`ID`, `usuario`, `password`) VALUES (NULL, %s, %s);" #inserto en la base de datos
    datos = (_usuario, _password) #almaceno datos del usuario en la variable
    
    conexion= mysql.connect() #conexion con DB
    cursor= conexion.cursor() #cursor busqueda
    cursor.execute(sql,datos) #cursor ejecucion   #superpongo datos con sentencia en sql
    conexion.commit() #confirmacion de guardar los movimientos realizados

    return render_template('admin/login.html', mensaje_nuevoUsuario="Usuario creado con éxito!")

    # return redirect('/admin/login') # desp del login hay problemas para usar render_template, recurro a redirect
#-----------------------
@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect('/admin/login')
#-------------------------
@app.route('/admin/libros')
def admin_libros():

    if not 'login' in session:
        return redirect('/admin/login')

    conexion = mysql.connect() #conexion con la base de datos sql
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM `libros`")
    libros = cursor.fetchall()
    conexion.commit()

    return render_template('admin/libros.html', libros=libros)

@app.route('/admin/libros/guardar', methods=['POST'])
def admin_libros_guardar():

    if not 'login' in session:
        return redirect('/admin/login')


    _nombre=request.form['txtNombre']
    _url=request.form['txtURL']
    _archivo=request.files['txtImagen']

    tiempo= datetime.now() #captura el tiempo del momento
    horaActual=tiempo.strftime('%Y%H%M%S') #detallando el formato del tiempo que quiero capturar
   
    if _nombre=='' or _url=='':
        conexion = mysql.connect() #conexion con la base de datos sql
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM `libros`")
        libros = cursor.fetchall()
        conexion.commit()
        return render_template('admin/libros.html', mensaje_invalido="Debe completar todas las casillas",libros=libros)
    
    if _archivo.filename!="":
        nuevoNombre=horaActual+"_"+_archivo.filename
        
        _archivo.save("src/templates/sitio/imagenes/"+nuevoNombre) #guardo nuevo nombre de la imagen

    
    
    sql = "INSERT INTO `libros`(`id`, `nombre`, `imagen`, `url`) VALUES (NULL, %s, %s, %s);"
    datos = (_nombre, nuevoNombre, _url)    
    conexion= mysql.connect() #conexion con DB
    cursor= conexion.cursor() #cursor busqueda
    cursor.execute(sql,datos) #cursor ejecucion   #superpongo datos con sentencia en sql
    conexion.commit() #confirmacion de guardar los movimientos realizados
    
    
    



    return redirect('/admin/libros') #redirecciona a la misma pag

@app.route('/admin/libros/borrar', methods={'POST'})
def admin_libros_borrar():
    if not 'login' in session:
        return redirect('/admin/login')
    
    _id=request.form['txtID']
    # print(_id)
    
    conexion=mysql.connect() #conexion con la base de datos sql
    cursor = conexion.cursor()
    cursor.execute("SELECT imagen FROM `libros`WHERE id = %s", (_id))
    libro = cursor.fetchall() #fetchall me trae todos los datos del registro con la imagen
    conexion.commit()
    # print(libro)

    if os.path.exists("templates/sitio/imagenes/"+str(libro[0][0])): #chequea si existe la ruta y transforma el nombre de imagen (que es un int) en str
        os.unlink("templates/sitio/imagenes/"+str(libro[0][0])) #se hace el borrado

    
    conexion=mysql.connect() #conexion con la base de datos sql
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM `libros` WHERE id = %s", (_id))
    conexion.commit()
    
    return redirect('/admin/libros')

if __name__ =='__main__':
    app.run(debug=True)