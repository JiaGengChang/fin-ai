const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');
const path = require('path');

const port = 3000;

const app = express();
app.use(cors());
app.use(express.json());

app.use(express.static(path.join(__dirname, 'frontend')));

app.post('/api/message', (req, res) => {
    const userMessage = req.body.message;
  
    if (!userMessage) {
        return res.status(400).json({ error: 'Message is required' });
    }

    // Run agent.py with user message as input
    exec(`python3 agent.py "${userMessage}"`, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing script: ${error}`);
            return res.status(500).json({ error: 'Internal server error' });
        }

        if (stderr) {
            console.error(`stderr: ${stderr}`);
            return res.status(500).json({ error: 'Internal server error' });
        }
        // Send the output of the Python script as the response
        res.json({ response: stdout.trim() });
    });
});

app.listen(port, () => {
    console.log(`Server is running at http://localhost:${port}`);
});
