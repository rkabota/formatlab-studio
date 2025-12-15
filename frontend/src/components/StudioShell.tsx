'use client';

import React, { useState, useEffect } from 'react';
import { SceneGraph, TimelineEntry, GenerateResponse } from '@/lib/types';
import { UploadDropzone } from './UploadDropzone';
import { NaturalLanguageBar } from './NaturalLanguageBar';
import { JsonEditor } from './JsonEditor';
import { CompareSlider } from './CompareSlider';
import { Timeline } from './Timeline';
import { DriftMeter } from './DriftMeter';
import { ExportBundleButton } from './ExportBundleButton';

interface StudioShellProps {
  initialScene?: SceneGraph;
}

export const StudioShell: React.FC<StudioShellProps> = ({ initialScene }) => {
  const [currentScene, setCurrentScene] = useState<SceneGraph | null>(initialScene || null);
  const [lastGeneration, setLastGeneration] = useState<GenerateResponse | null>(null);
  const [timeline, setTimeline] = useState<TimelineEntry[]>([]);
  const [activeTab, setActiveTab] = useState<'scene' | 'patch'>('scene');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Handle successful image analysis
  const handleImageAnalyzed = (scene: SceneGraph) => {
    setCurrentScene(scene);
    setError(null);
  };

  // Handle natural language translation
  const handleTranslated = (updatedScene: SceneGraph, timestamp: string) => {
    setCurrentScene(updatedScene);
    addToTimeline({
      timestamp,
      run_id: '',
      seed: 0,
      scene_snapshot: updatedScene,
      patch_summary: 'Natural language translation',
      output_urls: [],
    });
  };

  // Handle generation completion
  const handleGenerated = (result: GenerateResponse) => {
    setLastGeneration(result);
    addToTimeline({
      timestamp: result.timestamp || new Date().toISOString(),
      run_id: result.run_id,
      seed: result.seed,
      scene_snapshot: result.scene_used,
      patch_summary: 'Generated',
      output_urls: result.output_urls,
    });
    setError(null);
  };

  // Add entry to timeline
  const addToTimeline = (entry: TimelineEntry) => {
    setTimeline((prev) => [entry, ...prev]);
  };

  // Handle timeline selection
  const handleTimelineSelect = (entry: TimelineEntry) => {
    setCurrentScene(entry.scene_snapshot);
    setLastGeneration({
      run_id: entry.run_id,
      seed: entry.seed,
      output_urls: entry.output_urls,
      scene_used: entry.scene_snapshot,
      demo_mode: false,
      timestamp: entry.timestamp,
    });
  };

  return (
    <div className="h-screen w-screen bg-studio-bg text-white overflow-hidden flex flex-col">
      {/* Header */}
      <div className="h-16 bg-studio-panel border-b border-studio-border px-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">FormatLab Studio</h1>
          <p className="text-xs text-gray-400">JSON-native visual generation</p>
        </div>
        {error && <div className="text-red-500 text-sm">{error}</div>}
      </div>

      {/* Main Content Area - 4 Panel Layout */}
      <div className="flex-1 overflow-hidden flex gap-panel-gap p-panel-gap">
        {/* Left Panel - Controls & Upload */}
        <div className="w-1/4 bg-studio-panel border border-studio-border rounded flex flex-col overflow-hidden">
          <div className="border-b border-studio-border p-4">
            <h2 className="font-semibold mb-4">Controls</h2>
            <UploadDropzone onImageAnalyzed={handleImageAnalyzed} />
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            <NaturalLanguageBar
              currentScene={currentScene}
              onTranslated={handleTranslated}
              onError={(err) => setError(err)}
            />

            {currentScene && (
              <div className="mt-6 p-3 bg-studio-bg rounded text-sm">
                <h3 className="font-semibold mb-2">Scene Info</h3>
                <div className="space-y-1 text-xs text-gray-300">
                  <p>ID: {currentScene.id}</p>
                  <p>Camera: {currentScene.camera.lens_mm}mm</p>
                  <p>Lighting: Key {currentScene.lighting.key.intensity}</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Center Panel - Preview & Compare */}
        <div className="flex-1 bg-studio-panel border border-studio-border rounded flex flex-col overflow-hidden">
          <div className="border-b border-studio-border p-4">
            <h2 className="font-semibold">Preview</h2>
          </div>

          <div className="flex-1 overflow-hidden">
            {lastGeneration && lastGeneration.output_urls.length > 0 ? (
              <CompareSlider
                beforeImage={null}
                afterImage={lastGeneration.output_urls[0]}
              />
            ) : (
              <div className="h-full flex items-center justify-center text-gray-500">
                <div className="text-center">
                  <p className="text-sm mb-2">No preview yet</p>
                  <p className="text-xs text-gray-600">
                    Upload an image or generate to see preview
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Panel - JSON Editor */}
        <div className="w-1/4 bg-studio-panel border border-studio-border rounded flex flex-col overflow-hidden">
          <div className="border-b border-studio-border p-4 flex gap-2">
            <button
              onClick={() => setActiveTab('scene')}
              className={`px-3 py-1 rounded text-sm ${
                activeTab === 'scene'
                  ? 'bg-studio-accent text-white'
                  : 'bg-studio-bg text-gray-300 hover:bg-gray-700'
              }`}
            >
              Scene
            </button>
            <button
              onClick={() => setActiveTab('patch')}
              className={`px-3 py-1 rounded text-sm ${
                activeTab === 'patch'
                  ? 'bg-studio-accent text-white'
                  : 'bg-studio-bg text-gray-300 hover:bg-gray-700'
              }`}
            >
              Patch
            </button>
          </div>

          <div className="flex-1 overflow-hidden">
            {currentScene ? (
              <JsonEditor scene={currentScene} onSceneUpdate={setCurrentScene} />
            ) : (
              <div className="h-full flex items-center justify-center text-gray-500 text-sm">
                No scene loaded
              </div>
            )}
          </div>

          {currentScene && lastGeneration && (
            <div className="border-t border-studio-border p-3 bg-studio-bg">
              <ExportBundleButton
                scene={currentScene}
                generation={lastGeneration}
              />
            </div>
          )}
        </div>
      </div>

      {/* Bottom Panel - Timeline */}
      <div className="h-32 bg-studio-panel border-t border-studio-border overflow-x-auto">
        <Timeline entries={timeline} onSelectEntry={handleTimelineSelect} />
      </div>
    </div>
  );
};
