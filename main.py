from flask import Flask, render_template, request, redirect, url_for, flash, session
import fdb

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jqwdbjAHSDBhjBWd8723DWHV5rDWHD4783JHDKJVBWhdj'
host = 'localhost'
database = r'C:\Users\Aluno\Downloads\Banco - Sistema financeiro\SistemaFinanceiro.FDB'
user = 'sysdba'
password = 'sysdba'


class Usuario:
    def __init__(self, id_usuario, email, senha):
        self.id_usuario = id_usuario
        self.email = email
        self.senha = senha


class Despesa:
    def __init__(self, id_despesa, id_usuario, valor, descricao, data):
        self.id_despesa = id_despesa
        self.id_usuario = id_usuario
        self.valor = valor
        self.descricao = descricao
        self.data = data


class Receita:
    def __init__(self, id_receita, id_usuario, valor, fonte, data):
        self.id_receita = id_receita
        self.id_usuario = id_usuario
        self.valor = valor
        self.fonte = fonte
        self.data = data


""" 
    Função para criar e retornar uma nova conexão com o banco de dados, escolhi
    fazer dessa maneira porque descobri que usando uma simples conexão global
    pode permitir que erros ocorram por ela ser fechada, se corrompendo
    entre as requisições. Percebi isso a partir de um erro em que depois
    de fazer um cadastro, ao retornar para a página inicial dava um erro
    de conexão com o banco de dados.
"""


def conectar_no_banco():
    return fdb.connect(host=host, database=database, user=user, password=password)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email1']
        senha = request.form['senha1']

        con = conectar_no_banco()
        cursor1 = con.cursor()
        cursor1.execute('SELECT ID_USUARIO FROM USUARIOS WHERE EMAIL = ? AND SENHA = ?', (email, senha,))
        usuario = cursor1.fetchone()
        if usuario:
            # Guardando dados localmente no usuário
            session['email'] = email
            session['senha'] = senha
            return redirect(url_for('dashboard'))
        else:
            flash('Erro, nome de usuário ou senha incorretos','error')

    return render_template('index.html')


@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('senha', None)
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    con = conectar_no_banco()
    cursor1 = con.cursor()
    cursor2 = con.cursor()
    cursor3 = con.cursor()

    email = session['email']

    cursor1.execute('SELECT * FROM USUARIOS WHERE EMAIL = ?', (email,))
    usuario = cursor1.fetchone()
    id_usuario = usuario[0]
    nome_usuario = usuario[1]

    con.close()
    return render_template('dashboard.html', nome=nome_usuario)


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        # Guardando dados localmente no usuário
        session['email'] = email
        session['senha'] = senha

        con = conectar_no_banco()  # Cria uma nova conexão
        cursor = con.cursor()

        try:
            # Verificar se já foi criada uma conta neste e-mail
            cursor.execute("SELECT 1 FROM USUARIOS WHERE EMAIL = ?", (email,))
            if cursor.fetchone():  # Se existir algum registro
                flash("Erro: Este e-mail já possui uma conta.", "error")
                return redirect(url_for('cadastrar'))

            # Inserir o novo usuário
            cursor.execute("INSERT INTO USUARIOS (NOME, EMAIL, SENHA) VALUES (?, ?, ?)", (nome, email, senha))
            con.commit()

        except Exception as e:
            # Em caso de erro no banco de dados:
            flash(f"Erro ao cadastrar usuário: {str(e)}", "error")
            return redirect(url_for('cadastrar'))
        finally:
            cursor.close()  # Fechar o cursor
            con.close()  # Fechar a conexão

        # Após o sucesso, redireciona para a página inicial
        return redirect(url_for('index'))

    # Se for um GET, apenas renderiza o formulário de cadastro
    return render_template('cadastro.html')


if __name__ == '__main__':
    app.run(debug=True)
