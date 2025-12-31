const express = require('express');
const axios = require('axios');
const path = require('path');
const app = express();
const port = 3000;

// Serve static files from the React build directory
app.use(express.static(path.join(__dirname, 'dist')));

// API Proxy
app.get('/api/dashboard', async (req, res) => {
  try {
    // Call the BFF, forwarding query parameters (lat, lon)
    // In Kubernetes, 'bff' resolves to the service IP
    const response = await axios.get('http://bff/dashboard', { params: req.query });
    res.json(response.data);
  } catch (error) {
    console.error('Error calling BFF:', error.message);
    res.status(500).json({ error: 'Failed to fetch dashboard data' });
  }
});

// Handle client-side routing by serving index.html for all other routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

app.listen(port, () => {
  console.log(`Frontend app listening on port ${port}`);
});
