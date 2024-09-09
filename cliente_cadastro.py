import pandas as pd
import json
import re
import requests
from datetime import datetime
import unicodedata

def remove_accents(texto):
    return ''.join(c for c in unicodedata.normalize('NFKD', texto) if not unicodedata.combining(c))


def validate_cpf(cpf):
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11 or cpf == cpf[0] * len(cpf):
        return False
    return True


def validate_name(nome):
    nome = nome.strip()
    partes = nome.split()
    if len(partes) < 2:
        return False
    padrao = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ'\- ]+$")
    return bool(padrao.match(nome))


def age_check(data_nascimento):
    if isinstance(data_nascimento, datetime):
        data_nascimento = data_nascimento
    elif isinstance(data_nascimento, str):
        data_nascimento = datetime.strptime(data_nascimento, '%d/%m/%Y')
    hoje = datetime.now()
    try:
        idade = hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))
        return idade >= 18
    except ValueError:
        return False


def validate_email(email):
    padrao_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(padrao_email, email) is not None


def validate_tel(telefone):
    padrao_telefone = r'^\(\d{2}\) \d{5}-\d{4}$'
    return re.match(padrao_telefone, telefone) is not None


def validate_loc(cep, endereco):
    cep = ''.join(filter(str.isdigit, cep))
    if len(cep) != 8:
        return False, "CEP inválido. Deve ter 8 dígitos."
    url = f'https://viacep.com.br/ws/{cep}/json/'
    response = requests.get(url)
    if response.status_code == 200:
        dados = response.json()
        return not dados.get('erro', False)
    return False


def update_clients(novos_df, sistema_df):
    sistema_df['cpf'] = sistema_df['cpf'].str.replace(r'[.-]', '', regex=True).str.lower()
    novos_df['CPF'] = novos_df['CPF'].str.replace(r'[.-]', '', regex=True).str.lower()

    camps_atualizar = ['nome', 'email', 'telefone', 'endereco', 'cep', 'numero', 'bairro', 'cidade', 'estado']

    for campo in camps_atualizar:
        if campo in sistema_df.columns and campo in novos_df.columns:
            sistema_df[campo] = sistema_df[campo].str.lower().str.strip()
            novos_df[campo] = novos_df[campo].str.lower().str.strip()

    clientes_existentes = novos_df[novos_df['CPF'].isin(sistema_df['cpf'])]
    clientes_novos = novos_df[~novos_df['CPF'].isin(sistema_df['cpf'])]

    for index, cliente in clientes_existentes.iterrows():
        cpf = cliente['CPF']
        idx_sistema = sistema_df[sistema_df['cpf'] == cpf].index[0]
        for campo in camps_atualizar:
            if campo in cliente and campo in sistema_df.columns:
                valor_novo = cliente[campo]
                valor_atual = sistema_df.at[idx_sistema, campo]
                if pd.notna(valor_novo) and valor_novo != valor_atual:
                    print(f"Atualizando {campo} de {cliente['nome']} (CPF: {cpf}): {valor_atual} -> {valor_novo}")
                    sistema_df.at[idx_sistema, campo] = valor_novo

    return sistema_df, clientes_existentes, clientes_novos


def generate_json(clientes, sistema_df):
    lista_json = []

    for index, cliente in clientes.iterrows():

        data_nascimento = cliente["Data de Nascimento"]

        if isinstance(data_nascimento, str):
            data_nascimento = datetime.strptime(data_nascimento, '%d/%m/%Y')

        nome_sem_acentos = remove_accents(cliente['NOME']).strip()
        endereco_sem_acentos = remove_accents(cliente["Endereço"]).strip()
        cidade_sem_acentos = remove_accents(cliente["Cidade"]).strip()
        bairro_sem_acentos = remove_accents(cliente["Bairro"]).strip()
        estado_sem_acentos = remove_accents(cliente["Estado"]).strip()
        tipo = "I" if cliente['CPF'] not in sistema_df['cpf'].values else "A"

        cliente_json = {
            "id": f"{cliente['Faculdade']}-{cliente['CPF']}",
            "agrupador": remove_accents(cliente['Faculdade']).strip(),
            "tipoPessoa": "FISICA",
            "nome": nome_sem_acentos,
            "cpf": cliente['CPF'],
            "dataNascimento": data_nascimento.strftime('%Y-%m-%d'),
            "tipo": tipo,
            "enderecos": [
                {
                    "cep": cliente["CEP"].strip(),
                    "logradouro": endereco_sem_acentos,
                    "bairro": bairro_sem_acentos,
                    "cidade": cidade_sem_acentos,
                    "numero": cliente["Numero"],
                    "uf": estado_sem_acentos
                }
            ],
            "emails": [{"email": cliente["Email"].strip()}],
            "telefones": [{"tipo": "CELULAR", "ddd": cliente["Telefone"][:3].strip('()'), "telefone": cliente["Telefone"][5:].replace('-', '').strip()}],
            "informacoesAdicionais": [
                {"campo": "cpf_aluno", "linha": index, "coluna": cliente.index.get_loc('CPF'), "valor": cliente['CPF']},
                {"campo": "registro_aluno", "linha": index, "coluna": cliente.index.get_loc('RA'), "valor": cliente['RA']},
                {"campo": "nome_aluno", "linha": index, "coluna": cliente.index.get_loc('NOME'), "valor": nome_sem_acentos}
            ]
        }
        lista_json.append(cliente_json)

    return lista_json


# Carregar os arquivos Excel
arquivo = 'dados.xlsx'
df = pd.read_excel(arquivo)
sistema_df = pd.read_excel('sistema.xlsx')

clientes_validos = []
clientes_invalidos = []

for index, linha in df.iterrows():
    cpf = linha["CPF"]
    nome = linha["NOME"]
    dt_nascimento = linha["Data de Nascimento"]
    email = linha["Email"]
    telefone = linha["Telefone"]
    cep = linha["CEP"]
    endereco = linha["Endereço"]

    valid_cpf = validate_cpf(cpf)
    valid_name = validate_name(nome)
    age = age_check(dt_nascimento)
    valid_email = validate_email(email)
    valid_telefone = validate_tel(telefone)
    valid_loc = validate_loc(cep, endereco)

    if all([valid_cpf, valid_name, age, valid_email, valid_telefone, valid_loc]):
        print(f"Cliente {nome} é válido.")
        clientes_validos.append(linha)
    else:
        print(f"Cliente {nome} não é válido.")
        motivos = []
        if not valid_cpf: motivos.append("CPF inválido.")
        if not valid_name: motivos.append("Nome inválido.")
        if not age: motivos.append("Menor de idade.")
        if not valid_email: motivos.append("Email inválido.")
        if not valid_telefone: motivos.append("Telefone inválido.")
        if not valid_loc: motivos.append("Localização inválida.")
        linha['Motivos'] = ', '.join(motivos)
        clientes_invalidos.append(linha)


df_validos = pd.DataFrame(clientes_validos)

sistema_df_atualizado, clientes_existentes, clientes_novos = update_clients(df_validos, sistema_df)

new_clients_json = generate_json(clientes_novos, sistema_df)
update_clients_json = generate_json(clientes_existentes, sistema_df)
all_clients_json = new_clients_json + update_clients_json

with open('clientes_validos.json', 'w') as f:
    json.dump(all_clients_json, f, indent=4)


df_invalidos = pd.DataFrame(clientes_invalidos)
df_invalidos.to_excel('clientes_invalidos.xlsx', index=False)

print(sistema_df_atualizado)