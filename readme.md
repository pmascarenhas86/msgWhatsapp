# WhatsApp Bot

A WhatsApp bot for task management and information retrieval.

## Features

- Responds to commands like `!mensalidades`, `!contas`, `!trabalhos`, etc.
- Retrieves data from Google Sheets
- Provides formatted responses for WhatsApp

## Deployment on Render

### Prerequisites

1. A [Render](https://render.com) account
2. A Google Cloud Platform account with Google Sheets API enabled
3. A Google Service Account with access to your Google Sheets

### Setup Steps

1. **Fork or clone this repository**

2. **Set up Google Sheets API**
   - Create a Google Cloud Platform project
   - Enable the Google Sheets API
   - Create a service account and download the credentials JSON file
   - Share your Google Sheets with the service account email

3. **Deploy to Render**
   - Log in to your Render account
   - Click "New" and select "Web Service"
   - Connect your GitHub repository
   - Configure the service:
     - Name: `whatsapp-bot`
     - Environment: `Node`
     - Build Command: `npm install && pip install -r requirements.txt`
     - Start Command: `node index.js`
     - Plan: Free

4. **Set up environment variables**
   - In the Render dashboard, go to your service
   - Navigate to "Environment"
   - Add the following environment variables:
     - `NODE_ENV`: `production`
     - `PYTHONUNBUFFERED`: `1`

5. **Add your Google credentials**
   - In the Render dashboard, go to your service
   - Navigate to "Files & Volumes"
   - Create a new disk with:
     - Name: `whatsapp-session`
     - Mount Path: `/opt/render/project/src`
     - Size: 1 GB
   - Upload your Google credentials JSON file to this disk

6. **Deploy and scan QR code**
   - Deploy your service
   - Once deployed, visit the URL provided by Render
   - Scan the QR code with WhatsApp on your phone
   - The bot will now be connected and ready to respond to commands

## Commands

- `!calendario` – Lista completa com todas as datas importantes do calendário espiritual
- `!mensalidades` – Mostra quem já pagou e quem ainda está em aberto nas mensalidades
- `!contas` – Lista todas as contas pendentes ou quitadas
- `!trabalhos` – Mostra os trabalhos marcados para o mês atual
- `!valores` – Apresenta os valores esperados para arrecadação
- `!arrecadado` – Informa quanto foi arrecadado até o momento
- `!pendente` – Mostra os valores que ainda estão pendentes
- `!total` – Apresenta o balanço geral: arrecadado, pendente e total previsto
- `!ajuda` ou `!comandos` – Mostra a mensagem de ajuda
