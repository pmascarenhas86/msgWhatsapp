const { Client } = require('whatsapp-web.js');
const qrcodeTerminal = require('qrcode-terminal');
const { spawn } = require('child_process');

const numerosAutorizados = ['5511974671053', '5511983242565', '5511996667659'];
const comandosRestritos = {
    '!mensalidades': '--mensalidades',
    '!doacoes': '--doacoes',
    '!contas': '--contas',
    '!aniversarios': '--aniversarios'
};

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

client.on('ready', () => {
    console.log('Client is ready!');
});

client.on('qr', (qr) => {
    console.log('QR code received, scan it with your WhatsApp:');
    qrcodeTerminal.generate(qr, { small: true });
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

client.initialize();
