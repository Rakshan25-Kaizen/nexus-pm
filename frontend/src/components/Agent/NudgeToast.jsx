import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import useNexusStore from '../../store/useNexusStore';
import { markNudgeRead as markRead } from '../../api/client';

export default function NudgeToast() {
  const { activeNudges, markNudgeRead } = useNexusStore();

  const handleDismiss = async (nudge) => {
    try { await markRead(nudge.id); } catch {}
    markNudgeRead(nudge.id);
  };

  const severityColors = {
    warning: 'bg-amber-900/90 border-amber-700',
    alert: 'bg-red-900/90 border-red-700',
    info: 'bg-blue-900/90 border-blue-700',
  };

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
      <AnimatePresence>
        {activeNudges.slice(0, 3).map((nudge) => (
          <motion.div
            key={nudge.id}
            initial={{ x: 300, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 300, opacity: 0 }}
            className={`p-3 rounded-lg border shadow-xl ${severityColors[nudge.severity] || severityColors.info}`}
          >
            <div className="flex items-start gap-2">
              <span className="text-sm mt-0.5">🧠</span>
              <p className="text-sm flex-1">{nudge.message}</p>
              <button onClick={() => handleDismiss(nudge)} className="text-xs text-gray-300 hover:text-white shrink-0">
                Got it
              </button>
            </div>
            <motion.div
              initial={{ width: '100%' }}
              animate={{ width: '0%' }}
              transition={{ duration: 8, ease: 'linear' }}
              onAnimationComplete={() => handleDismiss(nudge)}
              className="h-0.5 bg-white/30 mt-2 rounded"
            />
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
