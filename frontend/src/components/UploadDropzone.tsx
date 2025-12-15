'use client';

import React, { useRef, useState } from 'react';
import { apiClient } from '@/lib/api';
import { SceneGraph } from '@/lib/types';
import { Upload } from 'lucide-react';

interface UploadDropzoneProps {
  onImageAnalyzed: (scene: SceneGraph) => void;
  onError?: (error: string) => void;
}

export const UploadDropzone: React.FC<UploadDropzoneProps> = ({
  onImageAnalyzed,
  onError,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const processFile = async (file: File) => {
    if (!file.type.startsWith('image/')) {
      onError?.('Please upload an image file');
      return;
    }

    setIsLoading(true);
    try {
      const result = await apiClient.analyzeImage(file);
      onImageAnalyzed(result.scene_graph);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to analyze image';
      onError?.(message);
    } finally {
      setIsLoading(false);
      setIsDragging(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      processFile(files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.currentTarget.files;
    if (files && files.length > 0) {
      processFile(files[0]);
    }
  };

  return (
    <div
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onClick={() => fileInputRef.current?.click()}
      className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
        isDragging
          ? 'border-studio-accent bg-studio-bg'
          : 'border-studio-border hover:border-studio-accent/50'
      }`}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        className="hidden"
        disabled={isLoading}
      />

      <Upload className="w-8 h-8 mx-auto mb-2 text-studio-accent" />

      {isLoading ? (
        <>
          <p className="text-sm font-medium">Analyzing image...</p>
          <p className="text-xs text-gray-400 mt-1">Please wait</p>
        </>
      ) : (
        <>
          <p className="text-sm font-medium">Drag & drop image here</p>
          <p className="text-xs text-gray-400 mt-1">or click to browse</p>
        </>
      )}
    </div>
  );
};
