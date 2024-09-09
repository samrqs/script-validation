# Documentação do Script de Validação e Atualização de Clientes

## Objetivo

O objetivo deste script é validar e atualizar informações de clientes a partir de dois arquivos Excel: um contendo novos dados e outro com informações já existentes. O script realiza validações de CPF, nome, data de nascimento, e-mail, telefone e endereço, atualiza o arquivo de sistema com novos dados e gera arquivos de saída com clientes válidos e inválidos, além de um arquivo JSON com informações dos clientes.

## Funcionalidades

1. **Validação dos Dados dos Clientes**
   - **CPF:** Verifica se o CPF é válido (composto apenas por dígitos e com 11 caracteres).
   - **Nome:** Verifica se o nome possui pelo menos duas partes e contém apenas caracteres válidos.
   - **Data de Nascimento:** Verifica se o cliente é maior de idade.
   - **E-mail:** Verifica se o e-mail segue o padrão correto.
   - **Telefone:** Verifica se o telefone está no formato esperado.
   - **CEP e Endereço:** Verifica se o CEP é válido usando uma API externa e se corresponde ao endereço fornecido.

2. **Atualização do Arquivo de Sistema**
   - Remove caracteres especiais dos CPFs para uniformizar.
   - Compara os CPFs dos novos dados com os já existentes.
   - Atualiza os dados no arquivo de sistema com as informações mais recentes.

3. **Geração de Arquivo JSON**
   - Cria um arquivo JSON contendo informações dos clientes, tanto novos quanto atualizados, com detalhes formatados e sem acentos.

4. **Geração de Arquivos de Saída**
   - Salva clientes válidos em um arquivo Excel.
   - Salva clientes inválidos em outro arquivo Excel.

## Código

### Funções Utilizadas

- **remove_accents(texto)**
  Remove acentos de um texto para padronização.

- **validate_cpf(cpf)**
  Valida o CPF removendo caracteres especiais e verificando o comprimento.

- **validate_name(nome)**
  Valida o nome para garantir que contém pelo menos duas partes e apenas caracteres permitidos.

- **age_check(data_nascimento)**
  Verifica se a data de nascimento indica que o cliente é maior de idade.

- **validate_email(email)**
  Valida o formato do e-mail com uma expressão regular.

- **validate_tel(telefone)**
  Valida o formato do telefone com uma expressão regular.

- **validate_loc(cep, endereco)**
  Valida o CEP usando uma API externa e verifica se o endereço é válido.

- **update_clients(novos_df, sistema_df)**
  Atualiza o DataFrame do sistema com as informações mais recentes dos clientes.

- **generate_json(clientes, sistema_df)**
  Gera uma lista de dicionários no formato JSON para os clientes.

### Processos Principais

1. **Carregamento dos Dados**
   - Carregamento dos arquivos Excel com novos e antigos dados de clientes.

2. **Validação dos Dados**
   - Itera sobre cada linha dos dados novos, realizando as validações definidas.

3. **Atualização do Sistema**
   - Atualiza o DataFrame do sistema com as informações mais recentes e identifica clientes novos e atualizados.

4. **Geração dos Arquivos de Saída**
   - Salva os clientes válidos e inválidos em arquivos Excel.
   - Gera um arquivo JSON com todas as informações dos clientes.

### Resultados

- **clientes_validos.xlsx:** Contém os clientes cujos dados passaram em todas as validações.
- **clientes_invalidos.xlsx:** Contém os clientes cujos dados não passaram em uma ou mais validações.
- **clientes_validos.json:** Contém todos os clientes com informações formatadas para uso em outros sistemas.