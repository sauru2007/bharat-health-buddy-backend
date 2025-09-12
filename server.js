import express from 'express';
import dotenv from 'dotenv';
import fetch from 'node-fetch';
import cors from 'cors';

dotenv.config();
const app = express();
app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
  res.send('Bharat Health Buddy API running');
});

// Chat endpoint (dummy for now)
app.post('/api/chat', async (req, res) => {
  const { message, language } = req.body;
  res.json({ reply: `You said (${language}): ${message}` });
});

// Hospitals endpoint (dummy for now)
app.get('/api/hospitals', async (req, res) => {
  res.json([{ name: "AIIMS Delhi", address: "New Delhi" }, { name: "Apollo Hospital", address: "Delhi" }]);
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
