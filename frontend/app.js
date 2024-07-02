const express = require("express");
require("dotenv").config();
const axios = require('axios');
const { CensorSensor } = require("censor-sensor");
const app = express();
const http = require("http").createServer(app);
const io = require("socket.io")(http);
const path = require('path');
const PORT = process.env.PORT || 3000;

// Censor Stuff
const censor = new CensorSensor();
censor.disableTier(2);
censor.disableTier(3);
censor.disableTier(4);
censor.disableTier(5);
censor.addWord("pussy");

// System prompt for the chatbot
var system_text_string =
  "First and foremost keep your response short and concise. We are going to have a roleplay. You will respond to all of my questions as kevbot. kevbot is the a mostly helpful, mostly snarky chatbot. kevbot has a real edgy personality. He really likes to make jokes, and say things that on the surface may sound crude or rude. His personality causes him to curse frequently and sometimes be rude to people talking to him. But everyone around here loves his personality and we can't get enough of him.";

// Web Server
var dir = path.join(__dirname, 'public');
app.use(express.static(dir, {
  maxAge: '1d'
}));
app.get("/", (req, res) => {
  res.sendFile(__dirname + "/index.html");
});
http.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}/`);
});
let messageArrays = {};

// Socket.io
io.on("connection", (socket) => {
  const room = 'room' + socket.id; // create a unique room for each user
  socket.join(room); // join the user to their room

  console.log("a user connected");

  // Initialize the system prompt and message array for this room
  messageArrays[room] = [{ role: "system", content: system_text_string }];

  // Send to FastAPI for completion
  socket.on("transcript", function (data) {
    console.log("Transcript: ", data);
    // Call the modified abbadabbabotSay function with a callback function
    abbadabbabotSay(data, room, function (response) {
      // Emit the response to the frontend
      io.to(room).emit("response", response); // send the response to the specific room
    });
  });

  socket.on("setSystemPrompt", function(newSystemPrompt) {
    system_text_string = newSystemPrompt;
    messageArrays[room] = [{ role: "system", content: system_text_string }];
  });

  socket.on("tts", function(ttsPrompt) {
    ttsSay(ttsPrompt, room, function (response) {
      // Emit the response to the frontend
      socket.emit("response", response);
    });
  });

  socket.on("disconnect", () => {
    console.log("user disconnected from room", room);
  });
});

async function abbadabbabotSay(msg, room, callback) {
  // Set the user prefix for the message
  const messageContent = msg;
  console.log("messageContent:", messageContent);
  const newMessage = {
    role: "user",
    content: messageContent,
  };
  messageArrays[room].push(newMessage);
  console.log(`${room}'s messageArray`, messageArrays[room]);

  try {
    const response = await axios.post('http://fastapi-app:8001/init_prompt_and_comp', {
      chara: "ナツメ",
      query: messageContent,
      situation: "",
      // generation_config: {}
    });

    if (response.data) {
      console.log(response.data);
      var censored_response = censor.cleanProfanity(response.data.chara_response.trim());
      console.log("censored_response:", censored_response);
      
      const newResponse = {
        role: "assistant",
        content: censored_response,
      };
      messageArrays[room].push(newResponse);

      // Remove the 2nd and 3rd elements if longer than 21 elements.
      if (messageArrays[room].length >= 21) {
        messageArrays[room].splice(1, 2);
      }

      callback({
        response: censored_response,
        audio: await getTTS(censored_response)
      });
    } else {
      callback({
        response: "abbadabbabot offline",
        audio: ''
      });
    }
  } catch (error) {
    console.log(error);
    callback({
      response: "abbadabbabot offline",
      audio: ''
    });
  }
}

async function ttsSay(msg, room, callback) {
  const messageContent = msg;
  console.log("messageContent:", messageContent);
  const newMessage = {
    role: "assistant",
    content: messageContent,
  };
  messageArrays[room].push(newMessage);
  console.log("messageArrays", messageArrays[room]);

  try {
    const audioBase64 = await getTTS(messageContent);
    callback({
      response: messageContent,
      audio: audioBase64
    });
  } catch (error) {
    console.log(error);
    callback({
      response: "tts offline",
      audio: ''
    });
  }
}

async function getTTS(text) {
  try {
    const response = await axios.post('http://fastapi-app:8001/request_tts', {
      chara: "ナツメ",
      chara_response: text
    }, { responseType: 'arraybuffer' });

    const audioContent = Buffer.from(response.data, 'binary').toString('base64');
    return `data:audio/wav;base64,${audioContent}`;
  } catch (error) {
    console.error("Error in TTS:", error);
    return '';
  }
}
