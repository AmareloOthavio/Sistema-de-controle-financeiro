from flask import Flask, render_template, request, redirect
import fdb

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jqwdbjAHSDBhjBWd8723DWHV5rDWHD4783JHDKJVBWhdj'
host = 'localhost'  # ou o IP do servidor onde o Firebird está rodando
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


#@app.route('/')
#def cadastrar():
