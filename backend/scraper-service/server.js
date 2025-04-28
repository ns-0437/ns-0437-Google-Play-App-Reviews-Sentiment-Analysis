const express = require('express');
const cors = require('cors');
const gplay = require('google-play-scraper');

const app = express();
const port = 3001;

app.use(cors());
app.use(express.json());

app.post('/get-reviews', async (req, res) => {
    const { appId } = req.body;

    try {
        const reviews = await gplay.reviews({
            appId: appId,
            sort: gplay.sort.NEWEST,
            num: 100
        });
        res.json(reviews.data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(port, () => {
    console.log(`Scraper Service running at http://localhost:${port}`);
});
