#importo framework
import os
from flask import Flask
from flask import render_template, request, redirect #el request y el redirect son para el formulario
from flaskext.mysql import MySQL
from datetime import datetime
from flask import send_from_directory

#creando aplicacion con la base de datos
app= Flask(__name__)
mysql=MySQL()

app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='sitio'
mysql.init_app(app)

#ruta de inicio/escape por default
@app.route('/')
def inicio():
    return render_template('sitio/index.html')

@app.route('/imagenes/<imagen>')
def imagenes(imagen):
    # print(imagen)
    return send_from_directory(os.path.join('templates/sitio/imagenes'),imagen)


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
    return render_template('admin/index.html')

@app.route('/admin/login')
def admin_login():
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    return render_template('admin/logout.html')

@app.route('/admin/libros')
def admin_libros():
    conexion=mysql.connect() #conexion con la base de datos sql
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM `libros`")
    libros = cursor.fetchall()
    conexion.commit()
    #print(libros)

    return render_template('admin/libros.html', libros=libros)

@app.route('/admin/libros/guardar', methods=['POST'])
def admin_libros_guardar():
    _nombre=request.form['txtNombre']
    _url=request.form['txtURL']
    _archivo=request.files['txtImagen']

    tiempo= datetime.now() #captura el tiempo del momento
    horaActual=tiempo.strftime('%Y%H%M%S') #detallando el formato del tiempo que quiero capturar

    if _archivo.filename!="":
        nuevoNombre=horaActual+"_"+_archivo.filename
        _archivo.save("templates/sitio/imagenes/"+nuevoNombre)



    sql = "INSERT INTO `libros`(`id`, `nombre`, `imagen`, `url`) VALUES (NULL, %s, %s, %s);"
    datos = (_nombre, nuevoNombre, _url)
    
    conexion= mysql.connect() #conexion con DB
    cursor= conexion.cursor() #cursor busqueda
    cursor.execute(sql,datos) #cursor ejecucion   #superpongo datos con sentencia en sql
    conexion.commit() #confirmacion de guardar los movimientos realizados


    return redirect('/admin/libros') #redirecciona a la misma pag

@app.route('/admin/libros/borrar', methods={'POST'})
def admin_libros_borrar():
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