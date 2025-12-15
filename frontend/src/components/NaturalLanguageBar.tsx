'use client';

import React, { useState } from 'react';
import { apiClient } from '@/lib/api';
import { SceneGraph } from '@/lib/types';
import { Send } from 'lucide-react';

interface NaturalLanguageBarProps {
  currentScene: SceneGraph | null;
  onTranslated: (scene: SceneGraph, timestamp: string) => void;
  onError?: (error: string) => void;
}

export const NaturalLanguageBar: React.FC<NaturalLanguageBarProps> = ({
  currentScene,
  onTranslated,
  onError,
}) => {
  const [instruction, setInstruction] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [confidence, setConfidence] = useState<number | null>(null);

  const handleTranslate = async () => {
    if (!instruction.trim() || !currentScene) {
      onError?.('Please enter an instruction and load a scene');
      return;
    }

    setIsLoading(true);
    try {
      const result = await apiClient.translate({
        instruction: instruction.trim(),
        current_scene: currentScene,
        return_patch: true,
      });

      setConfidence(result.confidence);
      onTranslated(result.updated_scene, new Date().toISOString());
      setInstruction('');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to translate instruction';
      onError?.(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleTranslate();
    }
  };

  return (
    <div className="space-y-3">
      <div>
        <label className="block text-sm font-medium mb-2">Natural Language Instructions</label>
        <textarea
          value={instruction}
          onChange={(e) => setInstruction(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="e.g., 'Make the lighting brighter and increase color saturation'"
          disabled={!currentScene || isLoading}
          className="w-full h-24 bg-studio-bg border border-studio-border rounded px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-studio-accent resize-none"
        />
      </div>

      <button
        onClick={handleTranslate}
        disabled={!currentScene || isLoading || !instruction.trim()}
        className={`w-full py-2 rounded px-3 flex items-center justify-center gap-2 font-medium text-sm transition-colors ${
          !currentScene || isLoading || !instruction.trim()
            ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
            : 'bg-studio-accent hover:bg-studio-accent-dark text-white'
        }`}
      >
        {isLoading ? (
          <>
            <span className="inline-block animate-spin">⌛</span>
            Translating...
          </>
        ) : (
          <>
            <Send className="w-4 h-4" />
            Translate to JSON
          </>
        )}
      </button>

      {confidence !== null && (
        <div className="text-xs text-gray-400">
          Translation confidence: {(confidence * 100).toFixed(0)}%
        </div>
      )}
    </div>
  );
};
