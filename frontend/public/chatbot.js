window.addEventListener("load", function () {
  const socket = io();

  const resultDiv = document.getElementById("result");
  const logDiv = document.getElementById("log");
  const responseList = document.getElementById("response-list");
  const startButton = document.getElementById("startButton");
  const userMessage = document.getElementById("userMessage");
  const audioElement = document.getElementById("audio-player");
  let triggerWord = "computer";
  const triggerWordInput = document.getElementById("triggerWordInput");
  const sendMessageButton = document.getElementById("sendMessageButton");
  const speakButton = document.getElementById("speakButton");
  const setSystemPromptButton = document.getElementById(
    "setSystemPromptButton"
  );
  const ttsButton = document.getElementById("ttsButton");
  const utterance = new SpeechSynthesisUtterance("TTS Online");
  const recordingIcon = document.querySelector('.recording-icon');

  let recognition;
  let recordingStarted = false;

  setSystemPromptButton.addEventListener("click", function () {
    const systemPrompt = document.getElementById("systemPrompt").value;
    system_text_string = systemPrompt;
    socket.emit("setSystemPrompt", system_text_string);
  });
  ttsButton.addEventListener("click", function () {
    const ttsValue = document.getElementById("ttsInput").value;
    socket.emit("tts", ttsValue);
  });
  sendMessageButton.addEventListener("click", function () {
    const message = userMessage.value;
    sendMessage(message, true);
    socket.emit("transcript", message);
    userMessage.value = "";
  });
  speakButton.addEventListener("click", function () {
    window.speechSynthesis.speak(utterance);
  });
  startButton.addEventListener("click", function () {
    startRecording();
  });
  triggerWordInput.addEventListener("input", function () {
    const triggerWordValue = triggerWordInput.value;
    triggerWord = triggerWordValue;
  });
  socket.on("response", function (data) {
    sendMessage(data.response, false);
    if (data.audio) {
      audioElement.src = data.audio;
      audioElement.play();
    } else {
      if ("speechSynthesis" in window) {
        const utterance = new SpeechSynthesisUtterance(data);
        window.speechSynthesis.speak(utterance);
      } else {
        console.log("no speechSynthesis");
      }
    }
  });

  function startRecording() {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = function (event) {
      let interim_transcript = "";
      let final_transcript = "";
      let spokenPhrase = "";

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          final_transcript += event.results[i][0].transcript;
        } else {
          interim_transcript += event.results[i][0].transcript;
        }
      }
      if (!final_transcript.toLowerCase().includes(triggerWord)) {
        userMessage.value = final_transcript;
      }
      if (
        final_transcript.toLowerCase().includes(triggerWord) &&
        !recordingStarted
      ) {
        recordingStarted = true;
        userMessage.classList.add("recording"); // add recording class
        recordingIcon.classList.remove('d-none'); // show recording icon
        recordingIcon.style.display = 'block';
        sendMessageButton.innerHTML = "Listening...";
        sendMessageButton.disabled = true;
        sendMessageButton.classList.remove("btn-primary");
        sendMessageButton.classList.add("btn-danger");
      } else if (recordingStarted && final_transcript) {
        spokenPhrase = final_transcript.replace(triggerWord, "").trim();

        if (spokenPhrase) {
          socket.emit("transcript", spokenPhrase);
          sendMessage(spokenPhrase, true);
        }

        recordingStarted = false;
        userMessage.classList.remove("recording"); // remove recording class
        recordingIcon.classList.add('d-none'); // hide recording icon
        recordingIcon.style.display = 'block';
        sendMessageButton.innerHTML = "Send";
        sendMessageButton.disabled = false;
        sendMessageButton.classList.remove("btn-danger");
        sendMessageButton.classList.add("btn-primary");
        userMessage.value = "";
      }

      if (recordingStarted) {
        if (spokenPhrase) {
          socket.emit("transcript", spokenPhrase);
        }
      }
    };

    recognition.onend = function () {
      startRecording();
    };

    recognition.start();
  }

  startRecording();
  // Show the modal dialog when the page loads
  const welcomeModal = new bootstrap.Modal(
    document.getElementById("welcome-modal")
  );
  welcomeModal.show();
});

function sendMessage(message, isUserMessage) {
  // Get the chatbox element
  const chatbox = document.querySelector(".chatbox");

  // Create a new chat message element for the message
  const chatMessage = document.createElement("div");
  chatMessage.classList.add("chat-message", "mb-3");

  // Add appropriate classes based on whether the message is from the user or the other user
  if (isUserMessage) {
    chatMessage.classList.add("chat-right");
  } else {
    chatMessage.classList.add("chat-left");
  }

  // Create a chat bubble element for the message
  const chatBubble = document.createElement("div");
  chatBubble.classList.add("chat-bubble", "p-2");
  chatBubble.innerText = message;

  // Add the chat bubble to the chat message
  chatMessage.appendChild(chatBubble);

  // Add the chat message to the chatbox
  chatbox.appendChild(chatMessage);

  // Scroll to the bottom of the chatbox to show the new message
  chatbox.scrollTop = chatbox.scrollHeight;
}
