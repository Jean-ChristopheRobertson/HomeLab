const express = require('express');
const axios = require('axios');
const app = express();
const port = 3000;

app.use(express.static('public'));

app.get('/api/dashboard', async (req, res) => {
  try {
    // Call the BFF
    const response = await axios.get('http://bff/dashboard');
    res.json(response.data);
  } catch (error) {
    console.error('Error calling BFF:', error.message);
    res.status(500).json({ error: 'Failed to fetch dashboard data' });
  }
});

app.listen(port, () => {
  console.log(`Frontend app listening on port ${port}`);
});
