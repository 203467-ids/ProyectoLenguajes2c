import csv
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators

app = Flask(__name__)
app.secret_key = 'mysecretkey'

class LoginForm(FlaskForm):
    username = StringField('Usuario', [validators.DataRequired()])
    password = PasswordField('Contraseña', [
        validators.DataRequired(),
        validators.Length(min=8, max=15),
        validators.Regexp(
            '^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]+$',
            message="La contraseña no cumple con los requisitos."
        )
    ])

class EmailFilterForm(FlaskForm):
    email_pattern = StringField('Expresión Regular para Email', [
        validators.DataRequired(),
        validators.Regexp(
            r'^([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)$',
            message="La expresión regular no coincide con una dirección de correo electrónico válida."
        )
    ])

def buscar_coincidencias_en_csv(campo, valor_pattern):
    matching_items = []
    with open('usuarios.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            correo = row.get('Correo', '')
            if valor_pattern.lower() in correo.lower():
                matching_items.append({'Nombre Contacto': row.get('Nombre Contacto', ''), 'Correo': correo})

    print(f"Matching Items for {campo}:", matching_items)  # Imprimir resultados para depuración
    return matching_items

@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        return render_template('filtro.html', email_form=EmailFilterForm(), matching_items=[])

    return render_template('login.html', form=form)

@app.route('/resultados', methods=['POST'])
def resultados():
    email_form = EmailFilterForm(request.form)

    if request.method == 'POST' and email_form.validate():
        email_pattern = email_form.email_pattern.data
        match = email_pattern.split('@')
        
        if len(match) == 2:
            usuario = match[0]
            dominio = match[1]
            matching_items = buscar_coincidencias_en_csv('Correo', usuario)
            matching_items = [item for item in matching_items if dominio.lower() in item['Correo'].split('@')[1].lower()]
            return render_template('resultados.html', campo='Correo', matching_items=matching_items)

    return redirect(url_for('filtro'))

@app.route('/filtro', methods=['POST'])
def filtro():
    email_form = EmailFilterForm(request.form)

    if request.method == 'POST' and email_form.validate():
        email_pattern = email_form.email_pattern.data
        match = email_pattern.split('@')
        
        if len(match) == 2:
            usuario = match[0]
            dominio = match[1]
            matching_items = buscar_coincidencias_en_csv('Correo', usuario)
            matching_items = [item for item in matching_items if dominio.lower() in item['Correo'].split('@')[1].lower()]
            return render_template('resultados.html', campo='Correo', matching_items=matching_items)

    return render_template('filtro.html', email_form=email_form)

if __name__ == '__main__':
    app.run(debug=True)
