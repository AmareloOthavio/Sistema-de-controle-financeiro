from flask import Flask, render_template, request, redirect, url_for, flash
import fdb

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jqwdbjAHSDBhjBWd8723DWHV5rDWHD4783JHDKJVBWhdj'
host = 'localhost'
database = r'C:\Users\Aluno\Downloads\Banco - Sistema financeiro\SistemaFinanceiro.FDB'
user = 'sysdba'
password = 'sysdba'
con = fdb.connect(host=host, database=database, user=user, password=password)


class Usuario:
    def __init__(self, id_usuario, email, senha, saldo_atual):
        self.id_usuario = id_usuario
        self.email = email
        self.senha = senha
        self.saldo_atual = saldo_atual


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


@app.route('/')
def index():
    cursor1 = con.cursor()
    cursor2 = con.cursor()
    cursor1.execute('SELECT VALOR, DESCRICAO, DATA FROM DESPESAS')
    despesas = cursor1.fetchall()
    cursor2.execute('SELECT VALOR, FONTE, DATA FROM RECEITAS')
    receitas = cursor2.fetchall()

    cursor1.close()
    cursor2.close()
    return render_template('index.html', despesas=despesas, receitas=receitas)


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

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
            con.close()

        # Após o sucesso, redireciona para a página inicial
        return redirect(url_for('index'))

    # Se for um GET, apenas renderize o formulário de cadastro
    return render_template('cadastro.html')


if __name__ == '__main__':
    app.run(debug=True)
