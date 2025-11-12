const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
const PORT = 3000;

app.use(cors());
app.use(bodyParser.json());

// Endpoint pour créer un serveur Minecraft
app.post('/create-vm', (req, res) => {
  const { username, email, minecraft_version, max_player } = req.body;

  console.log('Nouvelle demande de serveur:', req.body);

  // 🔧 Ici, tu peux intégrer le script réel de création de VM ou serveur
  // Pour le test, on renvoie des valeurs fictives
  const serverData = {
    ip: '123.456.78.90',
    port: 25565,
    connect: `${username.toLowerCase()}.minehost.fr`
  };

  res.json(serverData);
});

app.listen(PORT, () => {
  console.log(`Serveur backend démarré sur http://localhost:${PORT}`);
});
