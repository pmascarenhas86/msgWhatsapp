const { Client } = require('whatsapp-web.js');
const qrcode = require('qrcode');
const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const { spawn } = require('child_process');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);
const numerosAutorizados = ['5511974671053', '5511983242565', '5511996667659'];
const comandosRestritos = {
    '!mensalidades': '--mensalidades',
    '!doacoes': '--doacoes',
    '!contas': '--contas'
};


app.use(express.static('public'));

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

const mensagemAjuda = `👋 Olá! Aqui estão os comandos disponíveis:
📅 *!agenda* – Mostra as próximas giras e trabalhos do mês atual.
💳 *!mensalidades* – Quem já pagou e quem ainda está devendo.
📂 *!contas* – Contas quitadas do mês.
🎁 *!doacoes* – Mostra as doações registradas.
🧘‍♀️ *!trabalhos* – Lista os trabalhos do mês atual.
ℹ️ *!informacao* – Mostra um resumo geral das informações.
📌 *!ajuda* ou *!comandos* – Mostra esta mensagem.
`;

let qrCodeData = null;

client.on('ready', () => {
    console.log('Client is ready!');
    io.emit('status', 'Client is ready!');
});

client.on('qr', async (qr) => {
    console.log('New QR code received');
    qrCodeData = await qrcode.toDataURL(qr);
    io.emit('qr', qrCodeData);
    io.emit('status', 'QR code recebido. Escaneie com o WhatsApp.');
});

client.on('message', async (message) => {
    const comando = message.body.toLowerCase();
    const remetente = message.from;

    const comandos = {
        '!agenda': '--agenda',
        '!trabalhos': '--trabalhos',
        '!informacao': '--informacao',
        ...comandosRestritos
    };

    if (['oi', 'olá'].includes(comando)) {
        client.sendMessage(remetente, 'Olá! Tudo bem com você?');
    } else if (comando in comandos) {
        // Verifica se o comando é restrito e se o número tem permissão
        if (comando in comandosRestritos && !numerosAutorizados.includes(remetente)) {
            client.sendMessage(remetente, '❌ Desculpe, mas essa informação somente dirigentes têm acesso.');
        } else {
            executePythonCommand(remetente, comandos[comando]);
        }
    } else if (comando === '!ajuda' || comando === '!comandos') {
        client.sendMessage(remetente, mensagemAjuda);
    }
});


function executePythonCommand(contactNumber, command) {
    console.log(`Executando Python: ${command} para ${contactNumber}`);
    const pythonProcess = spawn('python', ['montarDF.py', command]);

    let outputData = '';
    let errorData = '';

    pythonProcess.stdout.on('data', (data) => {
        outputData += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        errorData += data.toString();
    });

    pythonProcess.on('close', (code) => {
        if (code !== 0) {
            console.error(`Erro (${code}): ${errorData}`);
            client.sendMessage(contactNumber, '⚠️ Erro ao processar a solicitação. Tente novamente.');
        } else {
            client.sendMessage(contactNumber, outputData || '✅ Processado com sucesso.');
        }
    });
}

io.on('connection', (socket) => {
    console.log('Novo cliente conectado');
    socket.emit('status', 'Conectado ao servidor');
    if (qrCodeData) socket.emit('qr', qrCodeData);
    socket.on('disconnect', () => console.log('Cliente desconectado'));
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Servidor rodando na porta ${PORT}`);
    io.emit('status', `Servidor rodando na porta ${PORT}`);
});

client.initialize();
