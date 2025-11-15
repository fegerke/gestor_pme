# gestor_pme

A simplified management system (SaaS) for freelancers and small businesses, built with Python and Django. This is a portfolio project to showcase backend development, database architecture, and custom admin integration.

---

## English (EN)

### 📖 About the Project

This is a complete, multi-tenant management system designed to run as a Software as a Service (SaaS). Each registered 'Empresa' (Company) has its own isolated set of data, including products, clients, and orders. The system is built entirely on the Django framework, with a heavily customized admin interface to provide a rich user experience.

### ✨ Core Features

* **Multi-Tenant Architecture:** Securely isolates data for each company (user).
* **Sales Order Management:** Full CRUD (Create, Read, Update, Delete) for sales orders, with automatic calculations.
* **Dynamic Price Calculations:** Custom JavaScript (`jQuery`) on the admin page that fetches item prices via AJAX based on the selected price table, recalculating totals in real-time.
* **PDF Generation:** Dynamically generates professional sales order PDFs (using `WeasyPrint`) for printing or sending to clients.
* **PIX QR Code Generation:** Generates a BRCode PIX QR Code and "copy-paste" string for each sales order to facilitate payment.
* **Custom Reporting:** Includes a custom sales report view, filterable by date range.
* **Hybrid Pricing System:** A flexible model that allows setting prices by product group/size or by specific item overrides.
* **Rich Form UI:** Uses JavaScript (`jQuery Mask`) for smart form field masking (e.g., CPF, CNPJ, Phone).

### 🛠️ Tech Stack

* **Backend:** Python, Django
* **Database:** PostgreSQL
* **Frontend:** JavaScript (jQuery), HTML, CSS
* **PDF Generation:** WeasyPrint
* **Database Engine:** `django.db.backends.postgresql`
* **File Storage:** `django.conf.urls.static` for media files (logos)

---

## Português (PT-BR)

### 📖 Sobre o Projeto

Um sistema de gestão (SaaS) completo e simplificado para autônomos e pequenas empresas. Este é um projeto de portfólio para demonstrar habilidades em desenvolvimento backend, arquitetura de banco de dados e integração customizada do admin.

O sistema é multi-usuário (multi-tenant), onde cada 'Empresa' cadastrada tem seu próprio conjunto isolado de dados, incluindo produtos, clientes e pedidos. O sistema foi construído inteiramente com o framework Django, com uma interface de administração robustamente customizada para prover uma rica experiência de usuário.

### ✨ Principais Funcionalidades

* **Arquitetura Multi-Tenant:** Isola os dados de forma segura para cada empresa (usuário).
* **Gestão de Pedidos de Venda:** CRUD completo para pedidos, com cálculos automáticos.
* **Cálculo Dinâmico de Preços:** JavaScript (`jQuery`) customizado na página de admin que busca preços de itens via AJAX, baseado na tabela de preço selecionada, recalculando totais em tempo real.
* **Geração de PDFs:** Gera PDFs profissionais de pedidos (usando `WeasyPrint`) para impressão ou envio a clientes.
* **Geração de PIX QR Code:** Gera um QR Code PIX (BRCode) e um "copia e cola" para cada pedido, facilitando o pagamento.
* **Relatórios Customizados:** Inclui uma view de relatório de vendas, com filtro por período.
* **Sistema de Preços Híbrido:** Um modelo flexível que permite precificar por grupo/tamanho de produto ou por item específico.
* **Interface Rica:** Utiliza JavaScript (`jQuery Mask`) para máscaras inteligentes em formulários (ex: CPF, CNPJ, Celular).

### 🛠️ Tecnologias Utilizadas

* **Backend:** Python, Django
* **Banco de Dados:** PostgreSQL
* **Frontend:** JavaScript (jQuery), HTML, CSS
* **Geração de PDF:** WeasyPrint
* **Engine de BD:** `django.db.backends.postgresql`
* **Storage:** `django.conf.urls.static` para arquivos de mídia (logos)

---

### ⚖️ Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
