const { Client } = require('whatsapp-web.js');
const qrcode = require('qrcode');
const { spawn } = require('child_process');
const express = require('express');
const http = require('http');
const socketIo = require('socket.io');

// Create Express app
const app = express();
const server = http.createServer(app);
const io = socketIo(server);

// Serve static files
app.use(express.static('public'));

// Store QR code data
let qrCodeData = null;

// Create WhatsApp client
const client = new Client();

// Serve the main page
app.get('/', (req, res) => {
  res.sendFile(__dirname + '/public/index.html');
});

// Socket.io connection
io.on('connection', (socket) => {
  console.log('Client connected');
  
  // Send current QR code if available
  if (qrCodeData) {
    socket.emit('qr', qrCodeData);
  }
  
  socket.on('disconnect', () => {
    console.log('Client disconnected');
  });
});

client.on('ready', () => {
  console.log('Client is ready!');
  qrCodeData = null;
  io.emit('ready');
  start(client);
});

client.on('qr', async (qr) => {
  try {
    // Generate QR code as data URL
    const qrDataUrl = await qrcode.toDataURL(qr);
    qrCodeData = qrDataUrl;
    io.emit('qr', qrDataUrl);
    console.log('QR Code generated and sent to clients');
  } catch (err) {
    console.error('Error generating QR code:', err);
  }
});

function start(client) {
  client.onMessage((message) => {
    // Log the received message
    console.log(`Message received from ${message.from}: "${message.body}"`);
    
    // Always reply to acknowledge receipt
    client.sendText(message.from, `Recebi sua mensagem: "${message.body}"`)
      .then((result) => {
        console.log('Acknowledgment sent successfully');
      })
      .catch((erro) => {
        console.error('Error sending acknowledgment:', erro);
      });
    
    // Process specific commands
    if (message.body === 'Oi' || message.body === 'Olá') {
      client
        .sendText(message.from, 'Olá! Tudo bem com você?')
        .then((result) => {
          console.log('Greeting sent successfully');
        })
        .catch((erro) => {
          console.error('Erro ao enviar mensagem: ', erro);
        });
    } else if (message.body.toLowerCase() === 'quais as minhas tarefas') {
      tarefas(client, message.from);
    }
  });
}

function tarefas(client, contactNumber) {
  // Execute the Python script to get tasks
  const pythonProcess = spawn('python', ['montarDF.py']);
  
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
      client.sendText(contactNumber, 'Desculpe, ocorreu um erro ao buscar suas tarefas.');
    } else {
      // Send the output to the WhatsApp contact
      client.sendText(contactNumber, outputData)
        .then((result) => {
          console.log('Tarefas enviadas com sucesso para:', contactNumber);
        })
        .catch((erro) => {
          console.error('Erro ao enviar tarefas:', erro);
        });
    }
  });
}

// Start the server
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  client.initialize();
});