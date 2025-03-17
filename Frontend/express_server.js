const express = require("express");
const axios = require("axios");
const cors = require("cors");

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Endpoint to process YouTube links
app.post("/api/process-youtube", async (req, res) => {
    try {
        const { url } = req.body;

        if (!url) {
            return res.status(400).json({ error: "YouTube URL is required" });
        }

        // Send the YouTube URL to the external API
        const response = await axios.post("http://localhost:8000/process-youtube", { url });

        res.json(response.data);
    } catch (error) {
        res.status(error.response?.status || 500).json({
            error: "Failed to process YouTube URL",
            details: error.response?.data || error.message
        });
    }
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});

