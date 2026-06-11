# 🐾 Bichano's Pet Shop

Sistema web completo para gerenciamento de Pet Shop desenvolvido com Python e Flask.

O projeto simula uma operação real de pet shop, incluindo catálogo de produtos, agendamento de serviços, gerenciamento de clientes, carrinho de compras e pagamento via Pix.

---

## 🚀 Funcionalidades

### 🛒 Loja Virtual

* Catálogo de produtos
* Carrinho de compras
* Controle de pedidos
* Exibição dinâmica de preços

### 📅 Agendamento

* Agendamento de banho e tosa
* Registro de solicitações
* Interface intuitiva para clientes

### 👥 Gestão de Clientes

* Cadastro de clientes
* Consulta de informações
* Organização de dados

### 💳 Pagamentos

* Integração com Pix
* Geração de QR Code
* Fluxo de compra simplificado

### 📱 Comunicação

* Integração com WhatsApp
* Atendimento facilitado

### 🖼️ Processamento de Imagens

* Geração automática de imagens de produtos
* Inserção dinâmica de preços
* Manipulação de imagens utilizando Pillow

---

## 🏗️ Arquitetura

```text
Cliente
   ↓
Frontend (HTML/CSS)
   ↓
Flask
   ↓
SQLite
   ↓
Produtos | Clientes | Pedidos
```

---

## 🛠️ Tecnologias Utilizadas

### Backend

* Python
* Flask
* SQLite

### Frontend

* HTML5
* CSS3
* JavaScript
* Jinja2

### Bibliotecas

* Pillow
* Python Dotenv

### Ferramentas

* Git
* GitHub
* VS Code

---

## 🔒 Recursos de Segurança

O projeto implementa boas práticas de segurança:

* Validação de IDs
* Proteção contra Path Traversal
* Uso de variáveis de ambiente
* Tratamento de exceções
* Validação de dados recebidos

---

## 📂 Estrutura do Projeto

```text
petshop/
│
├── app.py
├── database.py
├── templates/
│   ├── index.html
│   ├── loja.html
│   ├── clientes.html
│   ├── agenda.html
│   └── contato.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── README.md
```

---

## ⚙️ Instalação

Clone o projeto:

```bash
git clone https://github.com/thiagofoztt-creator/petshop.git
```

Entre na pasta:

```bash
cd petshop
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Configure as variáveis de ambiente:

```env
SECRET_KEY=sua_chave_secreta
```

Execute:

```bash
python app.py
```

---

## 🎯 Conceitos Aplicados

* Desenvolvimento Backend
* Arquitetura MVC
* APIs e Rotas Flask
* Banco de Dados Relacional
* Segurança de Aplicações Web
* Processamento de Imagens
* Integração de Serviços
* Desenvolvimento Full Stack

---

## 📈 Próximas Melhorias

* Sistema de autenticação
* Painel administrativo
* Dashboard de vendas
* Integração com gateways de pagamento
* API REST
* Relatórios gerenciais

---

## 👨‍💻 Autor

Thiago de Almeida Teles

🎓 Ciência da Computação

📧 [thiagofoztt@gmail.com](mailto:thiagofoztt@gmail.com)

🐙 GitHub:
https://github.com/thiagofoztt-creator

🌐 Portfólio:
https://thiagofoztt-creator.github.io/portfolio/

💼 LinkedIn:
https://linkedin.com/in/thiago-de-almeida-teles
