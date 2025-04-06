const { Client } = require('whatsapp-web.js');
const qrcode = require('qrcode');
const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const { spawn } = require('child_process');

// Create Express app
const app = express();
const server = http.createServer(app);
const io = socketIo(server);

// Serve static files from the public directory
app.use(express.static('public'));

// Create WhatsApp client
const client = new Client({
    puppeteer: {
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--disable-gpu'
        ]
    }
});

const mensagemAjuda = `👋 Olá! Aqui estão os comandos disponíveis e o que cada um retorna:
📅 *!calendario* – Lista completa com todas as datas importantes do calendário espiritual.
💳 *!mensalidades* – Mostra quem já pagou e quem ainda está em aberto nas mensalidades.
📂 *!contas* – Lista todas as contas pendentes ou quitadas.
🧘‍♀️ *!trabalhos* – Mostra os trabalhos marcados para o mês atual.
💰 *!valores* – Apresenta os valores esperados para arrecadação.
📊 *!arrecadado* – Informa quanto foi arrecadado até o momento.
⚠️ *!pendente* – Mostra os valores que ainda estão pendentes.
📈 *!total* – Apresenta o balanço geral: arrecadado, pendente e total previsto.
ℹ️ *!ajuda* ou *!comandos* – Mostra esta mensagem de ajuda.
Fique à vontade para usar qualquer comando. Estou aqui para ajudar! 😊`;

// Store QR code data
let qrCodeData = null;

client.on('ready', () => {
    console.log('Client is ready!');
    io.emit('status', 'Client is ready!');
});

client.on('qr', async (qr) => {
    console.log('New QR code received');
    // Generate QR code as data URL
    qrCodeData = await qrcode.toDataURL(qr);
    io.emit('qr', qrCodeData);
    io.emit('status', 'New QR code received. Please scan with WhatsApp.');
});

// Handle incoming messages
client.on('message', async (message) => {
    // Print message details in terminal
    console.log(`\n--- New Message ---`);
    console.log(`From: ${message.from}`);
    console.log(`Message: ${message.body}`);
    console.log(`Time: ${new Date().toLocaleString()}`);
    console.log(`------------------\n`);
    
    // Process specific commands
    if (message.body === 'Oi' || message.body === 'Olá') {
        client
            .sendMessage(message.from, 'Olá! Tudo bem com você?')
            .then((result) => {
                console.log('Greeting sent successfully');
            })
            .catch((erro) => {
                console.error('Erro ao enviar mensagem: ', erro);
            });
    } else if (message.body.toLowerCase() === '!calendario') {
        // Execute get_agenda_completa() function and send the result
        executePythonCommand(message.from, '--getAgendaCompleta');
    } else if (message.body.toLowerCase() === '!mensalidades') {
        // Execute get_mensalidades() function and send the result
        executePythonCommand(message.from, '--getMensalidades');
    } else if (message.body.toLowerCase() === '!doacoes') {
        // Execute get_doacoes() function and send the result
        executePythonCommand(message.from, '--getDoacoes');
    } else if (message.body.toLowerCase() === '!contas') {
        // Execute get_contas() function and send the result
        executePythonCommand(message.from, '--getContas');
    } else if (message.body.toLowerCase() === '!trabalhos') {
        // Execute get_trabalhos_mes() function and send the result
        executePythonCommand(message.from, '--getTrabalhosMes');
    } else if (message.body.toLowerCase() === '!valores') {
        // Execute get_valores() function and send the result
        executePythonCommand(message.from, '--getValores');
    } else if (message.body.toLowerCase() === '!arrecadado') {
        // Execute get_arrecadado() function and send the result
        executePythonCommand(message.from, '--getArrecadado');
    } else if (message.body.toLowerCase() === '!pendente') {
        // Execute get_pendente() function and send the result
        executePythonCommand(message.from, '--getPendente');
    } else if (message.body.toLowerCase() === '!total') {
        // Execute get_total() function and send the result
        executePythonCommand(message.from, '--getTotal');
    } else if (message.body.toLowerCase() === '!tudo') {
        // Execute all functions and send the result
        executePythonCommand(message.from, '--all');
    } else if (message.body.toLowerCase() === '!ajuda' || message.body.toLowerCase() === '!comandos') {
        client.sendMessage(message.from, mensagemAjuda);
    }
});

// Function to execute Python command and send the result
function executePythonCommand(contactNumber, command) {
    console.log(`Executing Python command: ${command} for ${contactNumber}`);
    
    // Execute the Python script with the specified command
    const pythonProcess = spawn('python', ['montarDF.py', command]);
    
    let outputData = '';
    let errorData = '';
    
    // Collect data from stdout
    pythonProcess.stdout.on('data', (data) => {
        outputData += data.toString();
    });
    
    // Collect data from stderr
    pythonProcess.stderr.on('data', (data) => {
        errorData += data.toString();
    });
    
    // When the process exits
    pythonProcess.on('close', (code) => {
        if (code !== 0) {
            console.error(`Python process exited with code ${code}`);
            console.error(`Error: ${errorData}`);
            client.sendMessage(contactNumber, 'Desculpe, ocorreu um erro ao processar sua solicitação.')
                .then(() => console.log('Error message sent successfully'))
                .catch(err => console.error('Error sending error message:', err));
        } else {
            // Send the output to the WhatsApp contact
            client.sendMessage(contactNumber, outputData)
                .then(() => {
                    console.log(`Command ${command} result sent successfully to:`, contactNumber);
                })
                .catch((erro) => {
                    console.error(`Error sending ${command} result:`, erro);
                });
        }
    });
}

// Socket.io connection
io.on('connection', (socket) => {
    console.log('New client connected');
    socket.emit('status', 'Connected to server');
    
    // Send current QR code if available
    if (qrCodeData) {
        socket.emit('qr', qrCodeData);
    }
    
    socket.on('disconnect', () => {
        console.log('Client disconnected');
    });
});

// Start the server
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
    io.emit('status', `Server running on port ${PORT}`);
});

// Initialize WhatsApp client
client.initialize();