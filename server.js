const express = require('express');
const cors = require('cors');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// Simple in-memory state (lost when server restarts)
let state = {
  shivam: { isOn: false, totalTime: 0, lastUpdate: Date.now() },
  devansh: { isOn: false, totalTime: 0, lastUpdate: Date.now() }
};

// GET state
app.get('/state', (req, res) => {
  res.json(state);
});

// POST state
app.post('/state', (req, res) => {
  const newState = req.body;
  if (newState.shivam && newState.devansh) {
    state = newState;
    state.lastSynced = Date.now();
    res.json({ message: 'State updated successfully' });
  } else {
    res.status(400).json({ error: 'Invalid state format' });
  }
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
