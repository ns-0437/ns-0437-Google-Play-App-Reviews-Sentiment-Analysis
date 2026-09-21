const express = require('express');
const cors = require('cors');
const gplay = require('google-play-scraper');

const app = express();
const port = 3001;

app.use(cors());
app.use(express.json());


app.post('/get-reviews', async (req, res) => {
    const { appId } = req.body;

    // A missing or non-string appId is a client error; without this it reached the scraper and
    // came back as a 500 with an internal message.
    if (typeof appId !== 'string' || appId.trim() === '') {
        return res.status(400).json({ error: 'appId is required and must be a non-empty string' });
    }

    try {
        const reviews = await gplay.reviews({
            appId: appId,
            sort: gplay.sort.NEWEST,
            num: 100
        });
        res.json(reviews.data);
    } catch (error) {
        // google-play-scraper reports an unknown package as an error containing "not found".
        const status = /not found/i.test(error.message) ? 404 : 500;
        res.status(status).json({ error: error.message });
    }
});


app.listen(port, () => {
    console.log(`Scraper Service running at http://localhost:${port}`);
});
