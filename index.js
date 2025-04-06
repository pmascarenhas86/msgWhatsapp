const { Client } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const { spawn } = require('child_process');

const client = new Client();

client.on('ready', () => {
    console.log('Client is ready!');
});

client.on('qr', qr => {
    qrcode.generate(qr, {small: true});
});

// Handle incoming messages
client.on('message', async (message) => {
    // Print message details in terminal
    console.log(`\n--- New Message ---`);
    console.log(`From: ${message.from}`);
    console.log(`Message: ${message.body}`);
    console.log(`Time: ${new Date().toLocaleString()}`);
    console.log(`------------------\n`);
    
    // Reply with "RECEVIDE" before any other processing
    try {
        await message.reply('RECEVIDE');
        console.log(`Replied with "RECEVIDE" to ${message.from}`);
    } catch (error) {
        console.error('Error sending "RECEVIDE" reply:', error);
    }
    
    // Process specific commands after sending the acknowledgment
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

client.initialize();
