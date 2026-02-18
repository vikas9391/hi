// src/App.js
import React, { useState } from "react";
import axios from "axios";

function App() {
  const [listening, setListening] = useState(false);
  const [messages, setMessages] = useState([]);
  const [recognition, setRecognition] = useState(null);

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recog = new SpeechRecognition();
    recog.lang = "en-US";
    recog.continuous = false;
    recog.interimResults = false;

    recog.onstart = () => setListening(true);
    recog.onend = () => setListening(false);

    recog.onresult = async (event) => {
      const transcript = event.results[0][0].transcript;
      setMessages((prev) => [...prev, { sender: "user", text: transcript }]);
      await sendToBackend(transcript);
    };

    recog.start();
    setRecognition(recog);
  };

  const sendToBackend = async (text) => {
    try {
      const res = await axios.post("http://127.0.0.1:8000/api/gemini/", {
        prompt: text,
        action: "chat"
      });
      const reply = res.data.reply;

      setMessages((prev) => [...prev, { sender: "bot", text: reply }]);

      // Text to Speech
      const utter = new SpeechSynthesisUtterance(reply);
      window.speechSynthesis.speak(utter);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>AI Voice Assistant</h2>
      <button onClick={startListening}>
        {listening ? "Listening..." : "🎤 Speak"}
      </button>

      <div style={{ marginTop: "20px" }}>
        {messages.map((msg, i) => (
          <p key={i}><b>{msg.sender}:</b> {msg.text}</p>
        ))}
      </div>
    </div>
  );
}

export default App;
