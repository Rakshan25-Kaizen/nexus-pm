import React from 'react';
import { motion } from 'framer-motion';
import { Bot } from 'lucide-react';

const stateConfigs = {
  idle: { scale: [1, 1.05, 1], color: '#60A5FA', transition: { duration: 3, repeat: Infinity } },
  thinking: { rotate: 360, color: '#60A5FA', transition: { duration: 1, repeat: Infinity, ease: 'linear' } },
  speaking: { scale: [1, 1.1, 1], color: '#34D399', transition: { duration: 0.6, repeat: Infinity } },
  alert: { scale: [1, 1.05, 1], color: '#F59E0B', transition: { duration: 1.5, repeat: Infinity } },
  happy: { scale: [1, 1.2, 1], color: '#10B981', transition: { duration: 0.3 } },
};

export default function AgentAvatar({ size = 40, state = 'idle' }) {
  const config = stateConfigs[state] || stateConfigs.idle;

  return (
    <motion.div
      animate={{ scale: config.scale, rotate: config.rotate }}
      transition={config.transition}
      style={{ width: size, height: size }}
      className="relative flex-shrink-0"
    >
      <svg viewBox="0 0 40 40" width={size} height={size}>
        <defs>
          <radialGradient id={`grad-${state}`} cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor={config.color} stopOpacity="0.3" />
            <stop offset="100%" stopColor={config.color} stopOpacity="0.1" />
          </radialGradient>
        </defs>
        <circle cx="20" cy="20" r="18" fill={`url(#grad-${state})`} stroke={config.color} strokeWidth="2" />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <Bot size={size * 0.45} color={config.color} />
      </div>
    </motion.div>
  );
}
