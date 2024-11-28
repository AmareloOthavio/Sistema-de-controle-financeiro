from flask import Flask, render_template, request, redirect, url_for, flash, session
import fdb

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jqwdbjA1HSDB23hjBWd8723DWH_V5HD47283JHDKJVBWhdj'
host = 'localhost'
database = r' C:\Users\Aluno\Downloads\Banco - Sistema financeiro\SistemaFinanceiro.FDB'
user = 'sysdba'
password = 'sysdba'

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


def calcular_receita():
    con = conectar_no_banco()
    cursor = con.cursor()
    cursor.execute('SELECT SUM(VALOR) FROM RECEITAS r WHERE r.ID_USUARIO = ?',
                   (session['id_usuario'],))
    total = cursor.fetchall()
    cursor.close()
    return total[0][0] if total else 0


def calcular_despesa():
    con = conectar_no_banco()
    cursor = con.cursor()
    id_usuario = session['id_usuario']
    cursor.execute('SELECT SUM(VALOR) FROM DESPESAS d WHERE d.ID_USUARIO = ?',
                   (id_usuario,))
    total = cursor.fetchall()
    cursor.close()
    return total[0][0] if total else 0


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
            session['id_usuario'] = usuario[0]
            return redirect(url_for('dashboard'))
        else:
            flash('Erro, nome de usuário ou senha incorretos', 'error')

    return render_template('index.html')


@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('id_usuario', None)
    session.pop('senha', None)
    return redirect(url_for('index'))


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    con = conectar_no_banco()
    if 'id_usuario' not in session:
        flash('Erro, você precisa estar em uma conta', 'error')
        return redirect(url_for('index'))

    if request.method == 'GET':

        cursor1 = con.cursor()
        cursor2 = con.cursor()

        id_usuario = session['id_usuario']
        cursor1.execute('SELECT * FROM USUARIOS WHERE ID_USUARIO = ?', (id_usuario,))
        usuario = cursor1.fetchone()
        nome_usuario = usuario[1]

        cursor2.execute(
            'SELECT ID_DESPESA, VALOR, DESCRICAO, DATA FROM DESPESAS WHERE ID_USUARIO = ? ORDER BY DATA DESC',
            (id_usuario,))
        despesas = cursor2.fetchall()

        cursor1.execute('SELECT ID_RECEITA, VALOR, FONTE, DATA FROM RECEITAS WHERE ID_USUARIO = ? ORDER BY DATA DESC',
                        (id_usuario,))
        receitas = cursor1.fetchall()
        cursor1.close()
        cursor2.close()
        con.close()
        total_receita = calcular_receita()
        total_despesa = calcular_despesa()
        return render_template('dashboard.html', nome=nome_usuario, despesas=despesas,
                               receitas=receitas, total_receita=total_receita, total_despesa=total_despesa)
    elif request.method == 'POST':
        valor = request.form['valor']
        data = request.form['data']
        tipo = request.form['tipo']
        fonte_desc = request.form['fonte_desc']

        cursor3 = con.cursor()

        id_usuario = session['id_usuario']

        if tipo == 'saida':
            flash('Despesa adicionada com sucesso!', 'success')
            cursor3.execute('INSERT INTO DESPESAS (ID_USUARIO, VALOR, DESCRICAO, DATA) VALUES(?, ?, ?, ?)',
                            (id_usuario, valor, fonte_desc, data))
        elif tipo == 'entrada':
            flash('Receita adicionada com sucesso', 'success')
            cursor3.execute('INSERT INTO RECEITAS (ID_USUARIO, VALOR,  FONTE, DATA) VALUES(?, ?, ?, ?)',
                            (id_usuario, valor, fonte_desc, data))
        cursor3.close()
        con.commit()
        con.close()

        return redirect(url_for('dashboard'))


@app.route('/excluir_receita/<int:id_receita>')
def excluir_receita(id_receita):

    if 'id_usuario' not in session:
        flash('Erro, você precisa estar em uma conta', 'error')
        return redirect(url_for('index'))

    con = conectar_no_banco()
    cursor = con.cursor()

    try:
        cursor.execute('DELETE FROM RECEITAS WHERE ID_RECEITA = ?', (id_receita,))
        con.commit()

        flash('Receita excluída com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir a receita: {str(e)}', 'error')
    finally:
        cursor.close()
        con.close()

    return redirect(url_for('dashboard'))


@app.route('/excluir_despesa/<int:id_despesa>')
def excluir_despesa(id_despesa):


    if 'id_usuario' not in session:
        flash('Erro, você precisa estar em uma conta', 'error')
        return redirect(url_for('index'))

    con = conectar_no_banco()
    cursor = con.cursor()

    try:
        cursor.execute('DELETE FROM DESPESAS WHERE ID_DESPESA = ?', (id_despesa,))
        con.commit()

        flash('Despesa excluída com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir a despesa: {str(e)}', 'error')
    finally:
        cursor.close()
        con.close()

    return redirect(url_for('dashboard'))


@app.route('/editar_despesa/<int:id_despesa>', methods=['GET', 'POST'])
def editar_despesa(id_despesa):
    if 'id_usuario' not in session:
        flash('Erro, você precisa estar em uma conta', 'error')
        return redirect(url_for('index'))

    con = conectar_no_banco()
    if request.method == 'POST':
        valor = request.form['valor']
        data = request.form['data']
        fonte_desc = request.form['fonte_desc']
        cursor1 = con.cursor()

        cursor1.execute('UPDATE DESPESAS SET VALOR = ?, DATA = ?, DESCRICAO = ? WHERE ID_DESPESA = ?',
                        (valor, data, fonte_desc, id_despesa))
        con.commit()
        cursor1.close()
        con.close()
        flash('Despesa editada com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    elif request.method == 'GET':

        cursor2 = con.cursor()
        cursor2.execute('SELECT ID_DESPESA, VALOR, DESCRICAO, DATA FROM DESPESAS WHERE ID_DESPESA = ?', (id_despesa,))
        despesas = cursor2.fetchall()
        cursor2.close()
        return render_template('editar.html', tipo='despesa', id=id_despesa, despesas=despesas)


@app.route('/editar_receita/<int:id_receita>', methods=['GET', 'POST'])
def editar_receita(id_receita):

    if 'id_usuario' not in session:
        flash('Erro, você precisa estar em uma conta', 'error')
        return redirect(url_for('index'))

    con = conectar_no_banco()
    if request.method == 'POST':
        valor = request.form['valor']
        data = request.form['data']
        fonte_desc = request.form['fonte_desc']
        cursor1 = con.cursor()

        cursor1.execute('UPDATE RECEITAS SET VALOR = ?, DATA = ?, FONTE = ? WHERE ID_RECEITA = ?',
                        (valor, data, fonte_desc, id_receita))
        con.commit()
        cursor1.close()
        con.close()
        flash('Receita editada com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    elif request.method == 'GET':
        cursor1 = con.cursor()
        cursor1.execute('SELECT ID_RECEITA, VALOR, FONTE, DATA FROM RECEITAS WHERE ID_RECEITA = ?', (id_receita,))
        receitas = cursor1.fetchall()
        cursor1.close()
        return render_template('editar.html', tipo='receita', id=id_receita, receitas=receitas)


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        con = conectar_no_banco()  # Cria uma nova conexão
        cursor = con.cursor()

        try:
            # VALIDAÇÕES
            # Verificar se já foi criada uma conta neste e-mail
            cursor.execute("SELECT 1 FROM USUARIOS WHERE EMAIL = ?", (email,))
            if cursor.fetchone():  # Se existir algum registro
                flash("Erro: Este e-mail já possui uma conta.", "error")
                return redirect(url_for('cadastrar'))

            # VALIDAÇÕES DE SENHA
            simbolos = ['!', '@', '#', '$', '%', '¨', '&', '*', '(', ')', '-', '_', '+', '=', '§', '"', "'",
                        '|', ':', ';', '?', '°', '<', '>', '{', '}', '[', ']', ',', '.', '*', '~', '´', '`',
                        'º', 'ª', '/', '^', '¹', '²', '³', '£', '¢', '¬']
            numeros = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
            numeros_usados = 0
            simbolos_usados = 0
            for simbolo in simbolos:
                if simbolo in senha:
                    simbolos_usados += 1
            for numero in numeros:
                if numero in senha:
                    numeros_usados += 1

            if len(senha) < 8:
                flash('Erro: A senha precisa ter pelo menos 8 caracteres', 'error')
                return redirect(url_for('cadastrar'))
            if simbolos_usados < 1:
                flash('Erro: A senha precisa ter pelo menos 1 símbolo do seu teclado', 'error')
                return redirect(url_for('cadastrar'))
            if numeros_usados < 1:
                flash('Erro: A senha precisa ter pelo menos um número', 'error')
                return redirect(url_for('cadastrar'))

            # Guardando dados localmente no usuário
            session['email'] = email
            session['senha'] = senha
            # Inserir o novo usuário
            cursor.execute("INSERT INTO USUARIOS (NOME, EMAIL, SENHA) VALUES (?, ?, ?)", (nome, email, senha))
            con.commit()
            cursor.execute('SELECT ID_USUARIO FROM USUARIOS WHERE EMAIL = ?', (email,))
            id_usuario = cursor.fetchone()
            session['id_usuario'] = id_usuario

        except Exception as e:
            # Em caso de erro no banco de dados:
            flash(f"Erro ao cadastrar usuário: {str(e)}", "error")
            return redirect(url_for('cadastrar'))
        finally:
            cursor.close()  # Fechar o cursor
            con.close()  # Fechar a conexão

        # Após o sucesso, redireciona para a página inicial
        flash('Conta criada com sucesso!', 'success')
        return redirect(url_for('index'))

    # Se for um GET, apenas renderiza o formulário de cadastro
    return render_template('cadastro.html')


if __name__ == '__main__':
    app.run(debug=True)
