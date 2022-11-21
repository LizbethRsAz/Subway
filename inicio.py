from flask import Flask, session, render_template, request, redirect, url_for
from flaskext.mysql import MySQL
import pymysql

app = Flask(__name__)
app.secret_key = "cairocoders-ednalan"
 
mysql = MySQL()

@app.route('/informacion')
def informacion():
    return render_template("informacion.html")

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'subway'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
 
@app.route('/add', methods=['POST'])
def add_product_to_cart():
 cursor = None
 try:
  _quantity = int(request.form['quantity'])
  _code = request.form['code']
  # validate the received values
  if _quantity and _code and request.method == 'POST':
   conn = mysql.connect()
   cursor = conn.cursor(pymysql.cursors.DictCursor)
   cursor.execute("SELECT * FROM product WHERE code=%s", _code)
   row = cursor.fetchone()
    
   itemArray = { row['code'] : {'name' : row['name'], 'code' : row['code'], 'quantity' : _quantity, 'price' : row['price'], 'image' : row['image'], 'total_price': _quantity * row['price']}}
    
   all_total_price = 0
   all_total_quantity = 0
    
   session.modified = True
   if 'cart_item' in session:
    if row['code'] in session['cart_item']:
     for key, value in session['cart_item'].items():
      if row['code'] == key:
       old_quantity = session['cart_item'][key]['quantity']
       total_quantity = old_quantity + _quantity
       session['cart_item'][key]['quantity'] = total_quantity
       session['cart_item'][key]['total_price'] = total_quantity * row['price']
    else:
     session['cart_item'] = array_merge(session['cart_item'], itemArray)
 
    for key, value in session['cart_item'].items():
     individual_quantity = int(session['cart_item'][key]['quantity'])
     individual_price = float(session['cart_item'][key]['total_price'])
     all_total_quantity = all_total_quantity + individual_quantity
     all_total_price = all_total_price + individual_price
   else:
    session['cart_item'] = itemArray
    all_total_quantity = all_total_quantity + _quantity
    all_total_price = all_total_price + _quantity * row['price']
    
   session['all_total_quantity'] = all_total_quantity
   session['all_total_price'] = all_total_price
    
   return redirect(url_for('.products'))
  else:
   return 'Error while adding item to cart'
 except Exception as e:
  print(e)
 finally:
  cursor.close() 
  conn.close()
   
@app.route('/product')
def products():
 try:
  conn = mysql.connect()
  cursor = conn.cursor(pymysql.cursors.DictCursor)
  cursor.execute("SELECT * FROM product")
  rows = cursor.fetchall()
  return render_template('product.html', products=rows)
 except Exception as e:
  print(e)
 finally:
  cursor.close() 
  conn.close()
 
@app.route('/empty')
def empty_cart():
 try:
  session.clear()
  return redirect(url_for('.products'))
 except Exception as e:
  print(e)
 
@app.route('/delete/<string:code>')
def delete_product(code):
 try:
  all_total_price = 0
  all_total_quantity = 0
  session.modified = True
   
  for item in session['cart_item'].items():
   if item[0] == code:    
    session['cart_item'].pop(item[0], None)
    if 'cart_item' in session:
     for key, value in session['cart_item'].items():
      individual_quantity = int(session['cart_item'][key]['quantity'])
      individual_price = float(session['cart_item'][key]['total_price'])
      all_total_quantity = all_total_quantity + individual_quantity
      all_total_price = all_total_price + individual_price
    break
   
  if all_total_quantity == 0:
   session.clear()
  else:
   session['all_total_quantity'] = all_total_quantity
   session['all_total_price'] = all_total_price
   
  return redirect(url_for('.products'))
 except Exception as e:
  print(e)
   
def array_merge( first_array , second_array ):
 if isinstance( first_array , list ) and isinstance( second_array , list ):
  return first_array + second_array
 elif isinstance( first_array , dict ) and isinstance( second_array , dict ):
  return dict( list( first_array.items() ) + list( second_array.items() ) )
 elif isinstance( first_array , set ) and isinstance( second_array , set ):
  return first_array.union( second_array )
 return False


# Crud del Cliente
@app.route('/')
def cliente():
    conn = pymysql.connect(host='localhost', user='root', passwd='', db='subway' )
    cursor = conn.cursor()
    cursor.execute('select idCliente, nombre, apellidos, fechanac, sexo, telefono, correo from cliente order by idCliente')
    datos = cursor.fetchall()
    return render_template("index.html", cliente=datos, dat=' ')

@app.route('/cliente_editar/<string:idC>')
def cliente_editar(idC):
    conn = pymysql.connect(host='localhost', user='root', passwd='', db='subway')
    cursor = conn.cursor()
    cursor.execute('select idCliente, nombre, apellidos, fechanac, sexo, telefono, correo from cliente where idCliente = %s', (idC))
    dato = cursor.fetchall()
    return render_template("cliente_edi.html", dat=dato[0])

@app.route('/cliente_fedita/<string:idC>',methods=['POST'])
def cliente_fedita(idC):
    if request.method == 'POST':
        nom=request.form['nombre']
        apell=request.form['apellidos']
        fech=request.form['fechanac']
        sexo=request.form['sexo']
        tel=request.form['telefono']
        correo=request.form['correo']
        conn = pymysql.connect(host='localhost', user='root', passwd='', db='subway')
        cursor = conn.cursor()
        cursor.execute('update cliente set nombre=%s, apellidos=%s, fechanac=%s, sexo=%s, telefono=%s, correo=%s where idCliente=%s', (nom,apell,fech,sexo,tel,correo,idC))
        conn.commit()
    return redirect(url_for('cliente'))

@app.route('/cliente_borrar/<string:idC>')
def cliente_borrar(idC):
    conn = pymysql.connect(host='localhost', user='root', passwd='', db='subway')
    cursor = conn.cursor()
    cursor.execute('delete from cliente where idCliente = {0}'.format(idC))
    conn.commit()
    return redirect(url_for('cliente'))

@app.route('/cliente_agregar')
def cliente_agregar():
    return render_template("cliente_agr.html")
    
@app.route('/cliente_fagrega', methods=['POST'])
def cliente_fagrega():
    if request.method == 'POST':
        nom=request.form['nombre']
        apell=request.form['apellidos']
        fech=request.form['fechanac']
        sexo=request.form['sexo']
        tel=request.form['telefono']
        correo=request.form['correo']
        conn = pymysql.connect(host='localhost', user='root', passwd='', db='subway' )
        cursor = conn.cursor()
        cursor.execute('insert into cliente (nombre, apellidos, fechanac, sexo, telefono, correo) values (%s,%s,%s,%s,%s,%s)',(nom,apell,fech,sexo,tel,correo))
        conn.commit()
        
    return redirect(url_for('cliente'))

# Crud del direccion
@app.route('/contacto')
def direccion():
    conn = pymysql.connect(host='localhost', user='root', passwd='', db='subway' )
    cursor = conn.cursor()
    cursor.execute('select idDireccion, pais, estado, calle, numero, colonia, codigopostal from direccion order by idDireccion')
    datos = cursor.fetchall()
    return render_template("contacto.html", direccion=datos, dat=' ')

@app.route('/direccion_editar/<string:idD>')
def direccion_editar(idD):
    conn = pymysql.connect(host='localhost', user='root', passwd='', db='subway')
    cursor = conn.cursor()
    cursor.execute(' select idDireccion, pais, estado, calle, numero, colonia, codigopostal from direccion where idDireccion = %s', (idD))
    dato = cursor.fetchall()
    return render_template("direccion_edi.html", dat=dato[0])

@app.route('/direccion_fedita/<string:idD>',methods=['POST'])
def direccion_fedita(idD):
    if request.method == 'POST':
        pai=request.form['pais']
        est=request.form['estado']
        call=request.form['calle']
        nume=request.form['numero']
        col=request.form['colonia']
        codp = request.form['codigopostal']
        conn = pymysql.connect(host='localhost', user='root', passwd='', db='subway')
        cursor = conn.cursor()
        cursor.execute('update direccion set pais=%s, estado=%s, calle=%s, numero=%s, colonia=%s, codigopostal=%s where idDireccion=%s', (pai,est,call,nume,col,codp,idD))
        conn.commit()
    return redirect(url_for('direccion'))

@app.route('/direccion_borrar/<string:idD>')
def direccion_borrar(idD):
    conn = pymysql.connect(host='localhost', user='root', passwd='', db='subway')
    cursor = conn.cursor()
    cursor.execute('delete from direccion where idDireccion = {0}'.format(idD))
    conn.commit()
    return redirect(url_for('direccion'))

@app.route('/direccion_agregar')
def direccion_agregar():
 return render_template("direccion_agr.html")
    
@app.route('/direccion_fagrega', methods=['POST'])
def direccion_fagrega():
    if request.method == 'POST':
        pai = request.form['pais']
        est= request.form['estado']
        call = request.form['calle']
        nume = request.form['numero']
        col = request.form['colonia']
        codp = request.form['codigopostal']
        conn = pymysql.connect(host='localhost', user='root', passwd='', db='subway' )
        cursor = conn.cursor()
        cursor.execute('insert into direccion (pais, estado, numero, colonia , calle ,codigopostal) values (%s,%s,%s,%s,%s,%s)',(pai,est,nume,col, call,codp))
        conn.commit()
        
    return redirect(url_for('direccion'))

# Crud de Opiniones
@app.route('/opiniones')
def opiniones():
    conn = pymysql.connect(host='localhost', user='root', passwd='', db='subway' )
    cursor = conn.cursor()
    cursor.execute('select idopiniones, pag, pedido, servicio, menu, calificacion, comentario from opiniones order by idopiniones')
    datos = cursor.fetchall()
    return render_template("opiniones.html", opiniones=datos, dat=' ')

@app.route('/opiniones_borrar/<string:idO>')
def opiniones_borrar(idO):
    conn = pymysql.connect(host='localhost', user='root', passwd='', db='subway')
    cursor = conn.cursor()
    cursor.execute('delete from opiniones where idopiniones = {0}'.format(idO))
    conn.commit()
    return redirect(url_for('opiniones'))

@app.route('/opiniones_agregar')
def opiniones_agregar():
    return render_template("opiniones_agr.html")
    
@app.route('/opiniones_fagrega', methods=['POST'])
def opiniones_fagrega():
    if request.method == 'POST':
        pag=request.form['pag']
        ped=request.form['pedido']
        ser=request.form['servicio']
        menu=request.form['menu']
        cal=request.form['calificacion']
        comenta=request.form['comentario']
        conn = pymysql.connect(host='localhost', user='root', passwd='', db='subway' )
        cursor = conn.cursor()
        cursor.execute('insert into opiniones (pag, pedido, servicio, menu, calificacion, comentario) values (%s,%s,%s,%s,%s,%s)',(pag,ped,ser,menu,cal,comenta))
        conn.commit()
        
    return redirect(url_for('opiniones'))
@app.route('/gracias')
def gracias():
    return render_template("gracias.html")


if __name__ == "__main__":
    app.run(debug=True)