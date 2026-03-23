import React, { useState } from 'react';
import { Mic } from 'lucide-react';

export default function VoiceInput({ onTranscript }) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) return null;

  const [listening, setListening] = useState(false);
  const [error, setError] = useState(false);

  const handleClick = () => {
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => setListening(true);
    recognition.onresult = (e) => {
      const transcript = e.results[0][0].transcript;
      onTranscript?.(transcript);
      setListening(false);
    };
    recognition.onerror = () => {
      setError(true);
      setListening(false);
      setTimeout(() => setError(false), 2000);
    };
    recognition.onend = () => setListening(false);
    recognition.start();
  };

  return (
    <button
      onClick={handleClick}
      className={`p-2 rounded-lg transition-all ${
        listening ? 'bg-red-500 animate-pulse' : error ? 'bg-gray-700 animate-[shake_0.3s]' : 'bg-gray-700 hover:bg-gray-600'
      }`}
      title={listening ? 'Listening...' : 'Voice input'}
    >
      <Mic size={16} className={listening ? 'text-white' : 'text-gray-400'} />
    </button>
  );
}

